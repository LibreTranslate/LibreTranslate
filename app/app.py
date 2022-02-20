import io
import os
import tempfile
import uuid
from functools import wraps
from html import unescape

import argostranslatefiles
from argostranslatefiles import get_supported_formats
from flask import (Flask, abort, jsonify, render_template, request, send_file,
                   url_for)
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint
from translatehtml import translate_html
from werkzeug.utils import secure_filename

from app import flood, remove_translated_files, security
from app.language import detect_languages, transliterate

from .api_keys import Database
from .suggestions import Database as SuggestionsDatabase


def get_version():
    try:
        with open("VERSION") as f:
            return f.read().strip()
    except:
        return "?"


def get_upload_dir():
    upload_dir = os.path.join(tempfile.gettempdir(), "libretranslate-files-translate")

    if not os.path.isdir(upload_dir):
        os.mkdir(upload_dir)

    return upload_dir


def get_req_api_key():
    if request.is_json:
        json = get_json_dict(request)
        ak = json.get("api_key")
    else:
        ak = request.values.get("api_key")

    return ak


def get_json_dict(request):
    d = request.get_json()
    if not isinstance(d, dict):
        abort(400, description="Invalid JSON format")
    return d


def get_remote_address():
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0].split(",")[0]
    else:
        ip = request.remote_addr or "127.0.0.1"

    return ip


def get_req_limits(default_limit, api_keys_db, multiplier=1):
    req_limit = default_limit

    if api_keys_db:
        api_key = get_req_api_key()

        if api_key:
            db_req_limit = api_keys_db.lookup(api_key)
            if db_req_limit is not None:
                req_limit = db_req_limit * multiplier

    return req_limit


def get_routes_limits(default_req_limit, daily_req_limit, api_keys_db):
    if default_req_limit == -1:
        # TODO: better way?
        default_req_limit = 9999999999999

    def minute_limits():
        return "%s per minute" % get_req_limits(default_req_limit, api_keys_db)

    def daily_limits():
        return "%s per day" % get_req_limits(daily_req_limit, api_keys_db, 1440)

    res = [minute_limits]

    if daily_req_limit > 0:
        res.append(daily_limits)

    return res


def create_app(args):
    from app.init import boot

    boot(args.load_only)

    from app.language import languages

    app = Flask(__name__)

    if args.debug:
        app.config["TEMPLATES_AUTO_RELOAD"] = True

    if not args.disable_files_translation:
        remove_translated_files.setup(get_upload_dir())

    # Map userdefined frontend languages to argos language object.
    if args.frontend_language_source == "auto":
        frontend_argos_language_source = type(
            "obj", (object,), {"code": "auto", "name": "Auto Detect"}
        )
    else:
        frontend_argos_language_source = next(
            iter([l for l in languages if l.code == args.frontend_language_source]),
            None,
        )

    frontend_argos_language_target = next(
        iter([l for l in languages if l.code == args.frontend_language_target]), None
    )

    frontend_argos_supported_files_format = []

    for file_format in get_supported_formats():
        for ff in file_format.supported_file_extensions:
            frontend_argos_supported_files_format.append(ff)

    # Raise AttributeError to prevent app startup if user input is not valid.
    if frontend_argos_language_source is None:
        frontend_argos_language_source = languages[0]
    if frontend_argos_language_target is None:
        if len(languages) >= 2:
            frontend_argos_language_target = languages[1]
        else:
            frontend_argos_language_target = languages[0]

    api_keys_db = None

    if args.req_limit > 0 or args.api_keys or args.daily_req_limit > 0:
        api_keys_db = Database() if args.api_keys else None

        from flask_limiter import Limiter

        limiter = Limiter(
            app,
            key_func=get_remote_address,
            default_limits=get_routes_limits(
                args.req_limit, args.daily_req_limit, api_keys_db
            ),
        )
    else:
        from .no_limiter import Limiter

        limiter = Limiter()

    if args.req_flood_threshold > 0:
        flood.setup(args.req_flood_threshold)

    def access_check(f):
        @wraps(f)
        def func(*a, **kw):
            ip = get_remote_address()

            if flood.is_banned(ip):
                abort(403, description="Too many request limits violations")
            else:
                if flood.has_violation(ip):
                    flood.decrease(ip)

            if args.api_keys:
                ak = get_req_api_key()
                if (
                    ak and api_keys_db.lookup(ak) is None
                ):
                    abort(
                        403,
                        description="Invalid API key",
                    )
                elif (
                    args.require_api_key_origin
                    and api_keys_db.lookup(ak) is None
                    and request.headers.get("Origin") != args.require_api_key_origin
                ):
                    abort(
                        403,
                        description="Please contact the server operator to obtain an API key",
                    )

            return f(*a, **kw)

        return func

    @app.errorhandler(400)
    def invalid_api(e):
        return jsonify({"error": str(e.description)}), 400

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": str(e.description)}), 500

    @app.errorhandler(429)
    def slow_down_error(e):
        flood.report(get_remote_address())
        return jsonify({"error": "Slowdown: " + str(e.description)}), 429

    @app.errorhandler(403)
    def denied(e):
        return jsonify({"error": str(e.description)}), 403

    @app.route("/")
    @limiter.exempt
    def index():
        if args.disable_web_ui:
            abort(404)

        return render_template(
            "index.html",
            gaId=args.ga_id,
            frontendTimeout=args.frontend_timeout,
            api_keys=args.api_keys,
            web_version=os.environ.get("LT_WEB") is not None,
            version=get_version()
        )

    @app.route("/javascript-licenses", methods=["GET"])
    @limiter.exempt
    def javascript_licenses():
        if args.disable_web_ui:
            abort(404)

        return render_template("javascript-licenses.html")

    @app.route("/languages", methods=["GET", "POST"])
    @limiter.exempt
    def langs():
        """
        Retrieve list of supported languages
        ---
        tags:
          - translate
        responses:
          200:
            description: List of languages
            schema:
              id: languages
              type: array
              items:
                type: object
                properties:
                  code:
                    type: string
                    description: Language code
                  name:
                    type: string
                    description: Human-readable language name (in English)
          429:
            description: Slow down
            schema:
              id: error-slow-down
              type: object
              properties:
                error:
                  type: string
                  description: Reason for slow down
        """
        return jsonify([{"code": l.code, "name": l.name} for l in languages])

    # Add cors
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add(
            "Access-Control-Allow-Headers", "Authorization, Content-Type"
        )
        response.headers.add("Access-Control-Expose-Headers", "Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Access-Control-Max-Age", 60 * 60 * 24 * 20)
        return response

    @app.route("/translate", methods=["POST"])
    @access_check
    def translate():
        """
        Translate text from a language to another
        ---
        tags:
          - translate
        parameters:
          - in: formData
            name: q
            schema:
              oneOf:
                - type: string
                  example: Hello world!
                - type: array
                  example: ['Hello world!']
            required: true
            description: Text(s) to translate
          - in: formData
            name: source
            schema:
              type: string
              example: en
            required: true
            description: Source language code
          - in: formData
            name: target
            schema:
              type: string
              example: es
            required: true
            description: Target language code
          - in: formData
            name: format
            schema:
              type: string
              enum: [text, html]
              default: text
              example: text
            required: false
            description: >
              Format of source text:
               * `text` - Plain text
               * `html` - HTML markup
          - in: formData
            name: api_key
            schema:
              type: string
              example: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
            required: false
            description: API key
        responses:
          200:
            description: Translated text
            schema:
              id: translate
              type: object
              properties:
                translatedText:
                  oneOf:
                    - type: string
                    - type: array
                  description: Translated text(s)
          400:
            description: Invalid request
            schema:
              id: error-response
              type: object
              properties:
                error:
                  type: string
                  description: Error message
          500:
            description: Translation error
            schema:
              id: error-response
              type: object
              properties:
                error:
                  type: string
                  description: Error message
          429:
            description: Slow down
            schema:
              id: error-slow-down
              type: object
              properties:
                error:
                  type: string
                  description: Reason for slow down
          403:
            description: Banned
            schema:
              id: error-response
              type: object
              properties:
                error:
                  type: string
                  description: Error message
        """
        if request.is_json:
            json = get_json_dict(request)
            q = json.get("q")
            source_lang = json.get("source")
            target_lang = json.get("target")
            text_format = json.get("format")
        else:
            q = request.values.get("q")
            source_lang = request.values.get("source")
            target_lang = request.values.get("target")
            text_format = request.values.get("format")

        if not q:
            abort(400, description="Invalid request: missing q parameter")
        if not source_lang:
            abort(400, description="Invalid request: missing source parameter")
        if not target_lang:
            abort(400, description="Invalid request: missing target parameter")

        batch = isinstance(q, list)

        if batch and args.batch_limit != -1:
            batch_size = len(q)
            if args.batch_limit < batch_size:
                abort(
                    400,
                    description="Invalid request: Request (%d) exceeds text limit (%d)"
                                % (batch_size, args.batch_limit),
                )

        if args.char_limit != -1:
            if batch:
                chars = sum([len(text) for text in q])
            else:
                chars = len(q)

            if args.char_limit < chars:
                abort(
                    400,
                    description="Invalid request: Request (%d) exceeds character limit (%d)"
                                % (chars, args.char_limit),
                )

        if source_lang == "auto":
            source_langs = []
            if batch:
                auto_detect_texts = q
            else:
                auto_detect_texts = [q]

            overall_candidates = detect_languages(q)

            for text_to_check in auto_detect_texts:
                if len(text_to_check) > 40:
                    candidate_langs = detect_languages(text_to_check)
                else:
                    # Unable to accurately detect languages for short texts
                    candidate_langs = overall_candidates
                source_langs.append(candidate_langs[0]["language"])

                if args.debug:
                    print(text_to_check, candidate_langs)
                    print("Auto detected: %s" % candidate_langs[0]["language"])
        else:
            if batch:
                source_langs = [source_lang for text in q]
            else:
                source_langs = [source_lang]

        src_langs = [next(iter([l for l in languages if l.code == source_lang]), None) for source_lang in source_langs]

        for idx, lang in enumerate(src_langs):
            if lang is None:
                abort(400, description="%s is not supported" % source_langs[idx])

        tgt_lang = next(iter([l for l in languages if l.code == target_lang]), None)

        if tgt_lang is None:
            abort(400, description="%s is not supported" % target_lang)

        if not text_format:
            text_format = "text"

        if text_format not in ["text", "html"]:
            abort(400, description="%s format is not supported" % text_format)

        try:
            if batch:
                results = []
                for idx, text in enumerate(q):
                    translator = src_langs[idx].get_translation(tgt_lang)

                    if text_format == "html":
                        translated_text = str(translate_html(translator, text))
                    else:
                        translated_text = translator.translate(transliterate(text, target_lang=source_langs[idx]))

                    results.append(unescape(translated_text))
                return jsonify(
                    {
                        "translatedText": results
                    }
                )
            else:
                translator = src_langs[0].get_translation(tgt_lang)

                if text_format == "html":
                    translated_text = str(translate_html(translator, q))
                else:
                    translated_text = translator.translate(transliterate(q, target_lang=source_langs[0]))
                return jsonify(
                    {
                        "translatedText": unescape(translated_text)
                    }
                )
        except Exception as e:
            abort(500, description="Cannot translate text: %s" % str(e))

    @app.route("/translate_file", methods=["POST"])
    @access_check
    def translate_file():
        """
        Translate file from a language to another
        ---
        tags:
          - translate
        consumes:
         - multipart/form-data
        parameters:
          - in: formData
            name: file
            type: file
            required: true
            description: File to translate
          - in: formData
            name: source
            schema:
              type: string
              example: en
            required: true
            description: Source language code
          - in: formData
            name: target
            schema:
              type: string
              example: es
            required: true
            description: Target language code
          - in: formData
            name: api_key
            schema:
              type: string
              example: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
            required: false
            description: API key
        responses:
          200:
            description: Translated file
            schema:
              id: translate
              type: object
              properties:
                translatedFileUrl:
                  type: string
                  description: Translated file url
          400:
            description: Invalid request
            schema:
              id: error-response
              type: object
              properties:
                error:
                  type: string
                  description: Error message
          500:
            description: Translation error
            schema:
              id: error-response
              type: object
              properties:
                error:
                  type: string
                  description: Error message
          429:
            description: Slow down
            schema:
              id: error-slow-down
              type: object
              properties:
                error:
                  type: string
                  description: Reason for slow down
          403:
            description: Banned
            schema:
              id: error-response
              type: object
              properties:
                error:
                  type: string
                  description: Error message
        """
        if args.disable_files_translation:
            abort(403, description="Files translation are disabled on this server.")

        source_lang = request.form.get("source")
        target_lang = request.form.get("target")
        file = request.files['file']

        if not file:
            abort(400, description="Invalid request: missing file parameter")
        if not source_lang:
            abort(400, description="Invalid request: missing source parameter")
        if not target_lang:
            abort(400, description="Invalid request: missing target parameter")

        if file.filename == '':
            abort(400, description="Invalid request: empty file")

        if os.path.splitext(file.filename)[1] not in frontend_argos_supported_files_format:
            abort(400, description="Invalid request: file format not supported")

        source_langs = [source_lang]
        src_langs = [next(iter([l for l in languages if l.code == source_lang]), None) for source_lang in source_langs]

        for idx, lang in enumerate(src_langs):
            if lang is None:
                abort(400, description="%s is not supported" % source_langs[idx])

        tgt_lang = next(iter([l for l in languages if l.code == target_lang]), None)

        if tgt_lang is None:
            abort(400, description="%s is not supported" % target_lang)

        try:
            filename = str(uuid.uuid4()) + '.' + secure_filename(file.filename)
            filepath = os.path.join(get_upload_dir(), filename)

            file.save(filepath)

            translated_file_path = argostranslatefiles.translate_file(src_langs[0].get_translation(tgt_lang), filepath)
            translated_filename = os.path.basename(translated_file_path)

            return jsonify(
                {
                    "translatedFileUrl": url_for('download_file', filename=translated_filename, _external=True)
                }
            )
        except Exception as e:
            abort(500, description=e)

    @app.route("/download_file/<string:filename>", methods=["GET"])
    def download_file(filename: str):
        """
        Download a translated file
        """
        if args.disable_files_translation:
            abort(400, description="Files translation are disabled on this server.")

        filepath = os.path.join(get_upload_dir(), filename)
        try:
            checked_filepath = security.path_traversal_check(filepath, get_upload_dir())
            if os.path.isfile(checked_filepath):
                filepath = checked_filepath
        except security.SuspiciousFileOperation:
            abort(400, description="Invalid filename")

        return_data = io.BytesIO()
        with open(filepath, 'rb') as fo:
            return_data.write(fo.read())
        return_data.seek(0)

        download_filename = filename.split('.')
        download_filename.pop(0)
        download_filename = '.'.join(download_filename)

        return send_file(return_data, as_attachment=True, attachment_filename=download_filename)

    @app.route("/detect", methods=["POST"])
    @access_check
    def detect():
        """
        Detect the language of a single text
        ---
        tags:
          - translate
        parameters:
          - in: formData
            name: q
            schema:
              type: string
              example: Hello world!
            required: true
            description: Text to detect
          - in: formData
            name: api_key
            schema:
              type: string
              example: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
            required: false
            description: API key
        responses:
          200:
            description: Detections
            schema:
              id: detections
              type: array
              items:
                type: object
                properties:
                  confidence:
                    type: number
                    format: float
                    minimum: 0
                    maximum: 1
                    description: Confidence value
                    example: 0.6
                  language:
                    type: string
                    description: Language code
                    example: en
          400:
            description: Invalid request
            schema:
              id: error-response
              type: object
              properties:
                error:
                  type: string
                  description: Error message
          500:
            description: Detection error
            schema:
              id: error-response
              type: object
              properties:
                error:
                  type: string
                  description: Error message
          429:
            description: Slow down
            schema:
              id: error-slow-down
              type: object
              properties:
                error:
                  type: string
                  description: Reason for slow down
          403:
            description: Banned
            schema:
              id: error-response
              type: object
              properties:
                error:
                  type: string
                  description: Error message
        """
        if flood.is_banned(get_remote_address()):
            abort(403, description="Too many request limits violations")

        if request.is_json:
            json = get_json_dict(request)
            q = json.get("q")
        else:
            q = request.values.get("q")

        if not q:
            abort(400, description="Invalid request: missing q parameter")

        return jsonify(detect_languages(q))

    @app.route("/frontend/settings")
    @limiter.exempt
    def frontend_settings():
        """
        Retrieve frontend specific settings
        ---
        tags:
          - frontend
        responses:
          200:
            description: frontend settings
            schema:
              id: frontend-settings
              type: object
              properties:
                charLimit:
                  type: integer
                  description: Character input limit for this language (-1 indicates no limit)
                frontendTimeout:
                  type: integer
                  description: Frontend translation timeout
                apiKeys:
                  type: boolean
                  description: Whether the API key database is enabled.
                keyRequired:
                  type: boolean
                  description: Whether an API key is required.
                suggestions:
                  type: boolean
                  description: Whether submitting suggestions is enabled.
                supportedFilesFormat:
                  type: array
                  items:
                    type: string
                  description: Supported files format
                language:
                  type: object
                  properties:
                    source:
                      type: object
                      properties:
                        code:
                          type: string
                          description: Language code
                        name:
                          type: string
                          description: Human-readable language name (in English)
                    target:
                      type: object
                      properties:
                        code:
                          type: string
                          description: Language code
                        name:
                          type: string
                          description: Human-readable language name (in English)
        """
        return jsonify(
            {
                "charLimit": args.char_limit,
                "frontendTimeout": args.frontend_timeout,
                "apiKeys": args.api_keys,
                "keyRequired": bool(args.api_keys and args.require_api_key_origin),
                "suggestions": args.suggestions,
                "filesTranslation": not args.disable_files_translation,
                "supportedFilesFormat": [] if args.disable_files_translation else frontend_argos_supported_files_format,
                "language": {
                    "source": {
                        "code": frontend_argos_language_source.code,
                        "name": frontend_argos_language_source.name,
                    },
                    "target": {
                        "code": frontend_argos_language_target.code,
                        "name": frontend_argos_language_target.name,
                    },
                },
            }
        )

    @app.route("/suggest", methods=["POST"])
    @access_check
    def suggest():
        """
        Submit a suggestion to improve a translation
        ---
        tags:
          - feedback
        parameters:
          - in: formData
            name: q
            schema:
              type: string
              example: Hello world!
            required: true
            description: Original text
          - in: formData
            name: s
            schema:
              type: string
              example: ¡Hola mundo!
            required: true
            description: Suggested translation
          - in: formData
            name: source
            schema:
              type: string
              example: en
            required: true
            description: Language of original text
          - in: formData
            name: target
            schema:
              type: string
              example: es
            required: true
            description: Language of suggested translation
        responses:
          200:
            description: Success
            schema:
              id: suggest-response
              type: object
              properties:
                success:
                  type: boolean
                  description: Whether submission was successful
          403:
            description: Not authorized
            schema:
              id: error-response
              type: object
              properties:
                error:
                  type: string
                  description: Error message
        """
        if not args.suggestions:
            abort(403, description="Suggestions are disabled on this server.")

        q = request.values.get("q")
        s = request.values.get("s")
        source_lang = request.values.get("source")
        target_lang = request.values.get("target")

        SuggestionsDatabase().add(q, s, source_lang, target_lang)
        return jsonify({"success": True})

    swag = swagger(app)
    swag["info"]["version"] = "1.3.0"
    swag["info"]["title"] = "LibreTranslate"

    @app.route("/spec")
    @limiter.exempt
    def spec():
        return jsonify(swag)

    SWAGGER_URL = "/docs"  # URL for exposing Swagger UI (without trailing '/')
    API_URL = "/spec"

    # Call factory function to create our blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)

    app.register_blueprint(swaggerui_blueprint)

    return app
