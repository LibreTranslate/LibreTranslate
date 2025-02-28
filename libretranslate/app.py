import io
import math
import os
import re
import tempfile
import uuid
from datetime import datetime
from functools import wraps
from html import unescape
from timeit import default_timer

import argostranslatefiles
from argostranslatefiles import get_supported_formats
from flask import Blueprint, Flask, Response, abort, jsonify, render_template, request, send_file, session, url_for, make_response
from flask_babel import Babel
from flask_session import Session
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint
from translatehtml import translate_html
from werkzeug.exceptions import HTTPException
from werkzeug.http import http_date
from werkzeug.utils import secure_filename

from libretranslate import flood, remove_translated_files, scheduler, secret, security, storage
from libretranslate.language import detect_languages, improve_translation_formatting
from libretranslate.locales import (
    _,
    _lazy,
    get_alternate_locale_links,
    get_available_locale_codes,
    get_available_locales,
    gettext_escaped,
    gettext_html,
    lazy_swag,
)

from .api_keys import Database, RemoteDatabase
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

def get_req_secret():
    if request.is_json:
        json = get_json_dict(request)
        ak = json.get("secret")
    else:
        ak = request.values.get("secret")

    return ak


def get_json_dict(request):
    d = request.get_json()
    if not isinstance(d, dict):
        abort(400, description=_("Invalid JSON format"))
    return d


def get_remote_address():
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0].split(",")[0]
    else:
        ip = request.remote_addr or "127.0.0.1"

    return ip


def get_req_limits(default_limit, api_keys_db, db_multiplier=1, multiplier=1):
    req_limit = default_limit

    if api_keys_db:
        api_key = get_req_api_key()

        if api_key:
            api_key_limits = api_keys_db.lookup(api_key)
            if api_key_limits is not None:
                req_limit = api_key_limits[0] * db_multiplier

    return int(req_limit * multiplier)


def get_char_limit(default_limit, api_keys_db):
    char_limit = default_limit

    if api_keys_db:
        api_key = get_req_api_key()

        if api_key:
            api_key_limits = api_keys_db.lookup(api_key)
            if api_key_limits is not None:
                if api_key_limits[1] is not None:
                    char_limit = api_key_limits[1]

    return char_limit


def get_routes_limits(args, api_keys_db):
    default_req_limit = args.req_limit
    if default_req_limit == -1:
        # TODO: better way?
        default_req_limit = 9999999999999

    def minute_limits():
        return "%s per minute" % get_req_limits(default_req_limit, api_keys_db)

    def hourly_limits(n):
        def func():
          decay = (0.75 ** (n - 1))
          return "{} per {} hour".format(get_req_limits(args.hourly_req_limit * n, api_keys_db, int(os.environ.get("LT_HOURLY_REQ_LIMIT_MULTIPLIER", 60) * n), decay), n)
        return func

    def daily_limits():
        return "%s per day" % get_req_limits(args.daily_req_limit, api_keys_db, int(os.environ.get("LT_DAILY_REQ_LIMIT_MULTIPLIER", 1440)))

    res = [minute_limits]

    if args.hourly_req_limit > 0:
      for n in range(1, args.hourly_req_limit_decay + 2):
        res.append(hourly_limits(n))

    if args.daily_req_limit > 0:
        res.append(daily_limits)

    return res

def filter_unique(seq, extra):
    seen = set({extra, ""})
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def create_app(args):
    from libretranslate.init import boot

    boot(args.load_only, args.update_models, args.force_update_models)

    from libretranslate.language import load_languages

    swagger_url = args.url_prefix + "/docs"  # Swagger UI (w/o trailing '/')
    api_url = args.url_prefix + "/spec"

    bp = Blueprint('Main app', __name__)

    storage.setup(args.shared_storage)

    if not args.disable_files_translation:
        remove_translated_files.setup(get_upload_dir())
    languages = load_languages()
    language_pairs = {}
    for lang in languages:
        language_pairs[lang.code] = sorted([l.to_lang.code for l in lang.translations_from])

    # Map userdefined frontend languages to argos language object.
    if args.frontend_language_source == "auto":
        frontend_argos_language_source = type(
            "obj", (object,), {"code": "auto", "name": _("Auto Detect")}
        )
    else:
        frontend_argos_language_source = next(
            iter([l for l in languages if l.code == args.frontend_language_source]),
            None,
        )
    if frontend_argos_language_source is None:
        frontend_argos_language_source = languages[0]


    language_target_fallback = languages[1] if len(languages) >= 2 else languages[0]

    if args.frontend_language_target == "locale":
      def resolve_language_locale():
          loc = get_locale()
          language_target = next(
              iter([l for l in languages if l.code == loc]), None
          )
          if language_target is None:
            language_target = language_target_fallback
          return language_target

      frontend_argos_language_target = resolve_language_locale
    else:
      language_target = next(
          iter([l for l in languages if l.code == args.frontend_language_target]), None
      )
      if language_target is None:
        language_target = language_target_fallback
      frontend_argos_language_target = lambda: language_target

    frontend_argos_supported_files_format = []

    for file_format in get_supported_formats():
        for ff in file_format.supported_file_extensions:
            frontend_argos_supported_files_format.append(ff)

    api_keys_db = None

    if args.req_limit > 0 or args.api_keys or args.daily_req_limit > 0 or args.hourly_req_limit > 0:
        api_keys_db = None
        if args.api_keys:
            api_keys_db = RemoteDatabase(args.api_keys_remote) if args.api_keys_remote else Database(args.api_keys_db_path)

        from flask_limiter import Limiter

        def limits_cost():
          req_cost = getattr(request, 'req_cost', 1)
          if args.req_time_cost > 0:
            return max(req_cost, int(math.ceil(getattr(request, 'duration', 0) / args.req_time_cost)))
          else:
            return req_cost

        limiter = Limiter(
            key_func=get_remote_address,
            default_limits=get_routes_limits(
                args, api_keys_db
            ),
            storage_uri=args.req_limit_storage,
            default_limits_deduct_when=lambda req: True, # Force cost to be called after the request
            default_limits_cost=limits_cost,
            strategy="moving-window",
        )
    else:
        from .no_limiter import Limiter

        limiter = Limiter()

    if not "gunicorn" in os.environ.get("SERVER_SOFTWARE", ""):
      # Gunicorn starts the scheduler in the master process
      scheduler.setup(args)

    flood.setup(args)
    secret.setup(args)

    measure_request = None
    gauge_request = None
    if args.metrics:
      if os.environ.get("PROMETHEUS_MULTIPROC_DIR") is None:
          default_mp_dir = os.path.abspath(os.path.join("db", "prometheus"))
          if not os.path.isdir(default_mp_dir):
            os.mkdir(default_mp_dir)
          os.environ["PROMETHEUS_MULTIPROC_DIR"] = default_mp_dir

      from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Gauge, Summary, generate_latest, multiprocess

      @bp.route("/metrics")
      @limiter.exempt
      def prometheus_metrics():
        if args.metrics_auth_token:
          authorization = request.headers.get('Authorization')
          if authorization != "Bearer " + args.metrics_auth_token:
            abort(401, description=_("Unauthorized"))

        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
        return Response(generate_latest(registry), mimetype=CONTENT_TYPE_LATEST)

      measure_request = Summary('libretranslate_http_request_duration_seconds', 'Time spent on request', ['endpoint', 'status', 'request_ip', 'api_key'])
      measure_request.labels('/translate', 200, '127.0.0.1', '')

      gauge_request = Gauge('libretranslate_http_requests_in_flight', 'Active requests', ['endpoint', 'request_ip', 'api_key'], multiprocess_mode='livesum')
      gauge_request.labels('/translate', '127.0.0.1', '')

    def access_check(f):
        @wraps(f)
        def func(*a, **kw):
            ip = get_remote_address()

            if flood.is_banned(ip):
                abort(403, description=_("Too many request limits violations"))

            if args.api_keys:
                ak = get_req_api_key()
                if ak and api_keys_db.lookup(ak) is None:
                    abort(
                        403,
                        description=_("Invalid API key"),
                    )
                else:
                  need_key = False
                  key_missing = api_keys_db.lookup(ak) is None

                  if (args.require_api_key_origin
                      and key_missing
                      and not re.match(args.require_api_key_origin, request.headers.get("Origin", ""))
                  ):
                    need_key = True

                  req_secret = get_req_secret()
                  if (args.require_api_key_secret
                    and key_missing
                    and not secret.secret_match(req_secret)
                  ):
                    need_key = True
                    if secret.secret_bogus_match(req_secret):
                      abort(make_response(jsonify({
                        'translatedText': secret.get_emoji(),
                        'alternatives': [],
                        'detectedLanguage': { 'confidence': 100, 'language': 'en' }
                      }), 200))

                  if need_key:
                    description = _("Please contact the server operator to get an API key")
                    if args.get_api_key_link:
                        description = _("Visit %(url)s to get an API key", url=args.get_api_key_link)
                    abort(
                        400,
                        description=description,
                    )
            return f(*a, **kw)

        if args.metrics:
          @wraps(func)
          def measure_func(*a, **kw):
              start_t = default_timer()
              status = 200
              ip = get_remote_address()
              ak = get_req_api_key() or ''
              g = gauge_request.labels(request.path, ip, ak)
              try:
                g.inc()
                return func(*a, **kw)
              except HTTPException as e:
                status = e.code
                raise e
              finally:
                request.duration = max(default_timer() - start_t, 0)
                measure_request.labels(request.path, status, ip, ak).observe(request.duration)
                g.dec()
          return measure_func
        else:
          @wraps(func)
          def time_func(*a, **kw):
            start_t = default_timer()
            try:
              return func(*a, **kw)
            finally:
              request.duration = max(default_timer() - start_t, 0)
          return time_func

    @bp.errorhandler(400)
    def invalid_api(e):
        return jsonify({"error": str(e.description)}), 400

    @bp.errorhandler(500)
    def server_error(e):
        return jsonify({"error": str(e.description)}), 500

    @bp.errorhandler(429)
    def slow_down_error(e):
        flood.report(get_remote_address())
        return jsonify({"error": _("Slowdown:") + " " + str(e.description)}), 429

    @bp.errorhandler(403)
    def denied(e):
        return jsonify({"error": str(e.description)}), 403

    @bp.route("/")
    @limiter.exempt
    def index():
        if args.disable_web_ui:
            abort(404)

        langcode = request.args.get('lang')
        if langcode and langcode in get_available_locale_codes(not args.debug):
            session.update(preferred_lang=langcode)

        resp = make_response(render_template(
            "index.html",
            gaId=args.ga_id,
            frontendTimeout=args.frontend_timeout,
            api_keys=args.api_keys,
            get_api_key_link=args.get_api_key_link,
            web_version=os.environ.get("LT_WEB") is not None,
            version=get_version(),
            swagger_url=swagger_url,
            available_locales=sorted([{'code': l['code'], 'name': _lazy(l['name'])} for l in get_available_locales(not args.debug)], key=lambda s: s['name']),
            current_locale=get_locale(),
            alternate_locales=get_alternate_locale_links()
        ))

        if args.require_api_key_secret:
          resp.set_cookie('r', '1')

        return resp

    @bp.route("/js/app.js")
    @limiter.exempt
    def appjs():
      if args.disable_web_ui:
        abort(404)

      api_secret = ""
      bogus_api_secret = ""
      if args.require_api_key_secret:
        bogus_api_secret = secret.get_bogus_secret_b64()

        if 'User-Agent' in request.headers and request.cookies.get('r'):
          api_secret = secret.get_current_secret_js()
        else:
          api_secret = secret.get_bogus_secret_js()
        
      response = Response(render_template("app.js.template",
            url_prefix=args.url_prefix,
            get_api_key_link=args.get_api_key_link,
            api_secret=api_secret,
            bogus_api_secret=bogus_api_secret), content_type='application/javascript; charset=utf-8')

      if args.require_api_key_secret:
        response.headers['Last-Modified'] = http_date(datetime.now())
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'

      return response

    @bp.get("/languages")
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
                  targets:
                    type: array
                    items:
                      type: string
                    description: Supported target language codes
        """
        return jsonify([{"code": l.code, "name": _lazy(l.name), "targets": language_pairs.get(l.code, [])} for l in languages])

    # Add cors
    @bp.after_request
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

    @bp.post("/translate")
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
            name: alternatives
            schema:
              type: integer
              default: 0
              example: 3
            required: false
            description: Preferred number of alternative translations 
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
            num_alternatives = int(json.get("alternatives", 0))
        else:
            q = request.values.get("q")
            source_lang = request.values.get("source")
            target_lang = request.values.get("target")
            text_format = request.values.get("format")
            num_alternatives = request.values.get("alternatives", 0)

        if not q:
            abort(400, description=_("Invalid request: missing %(name)s parameter", name='q'))
        if not source_lang:
            abort(400, description=_("Invalid request: missing %(name)s parameter", name='source'))
        if not target_lang:
            abort(400, description=_("Invalid request: missing %(name)s parameter", name='target'))
        
        try:
            num_alternatives = max(0, int(num_alternatives))
        except ValueError:
            abort(400, description=_("Invalid request: %(name)s parameter is not a number", name='alternatives'))

        if args.alternatives_limit != -1 and num_alternatives > args.alternatives_limit:
            abort(400, description=_("Invalid request: %(name)s parameter must be <= %(value)s", name='alternatives', value=args.alternatives_limit))

        if not request.is_json:
            # Normalize line endings to UNIX style (LF) only so we can consistently
            # enforce character limits.
            # https://www.rfc-editor.org/rfc/rfc2046#section-4.1.1
            q = "\n".join(q.splitlines())

        char_limit = get_char_limit(args.char_limit, api_keys_db)

        batch = isinstance(q, list)

        if batch and args.batch_limit != -1:
            batch_size = len(q)
            if args.batch_limit < batch_size:
                abort(
                    400,
                    description=_("Invalid request: request (%(size)s) exceeds text limit (%(limit)s)", size=batch_size, limit=args.batch_limit),
                )

        src_texts = q if batch else [q]

        if char_limit != -1:
            for text in src_texts:
                if len(text) > char_limit:
                    abort(
                        400,
                        description=_("Invalid request: request (%(size)s) exceeds text limit (%(limit)s)", size=len(text), limit=char_limit),
                    )

        if batch:
            request.req_cost = max(1, len(q))

        if source_lang == "auto":
            candidate_langs = detect_languages(src_texts)
            detected_src_lang = candidate_langs[0]
        else:
            detected_src_lang = {"confidence": 100.0, "language": source_lang}

        src_lang = next(iter([l for l in languages if l.code == detected_src_lang["language"]]), None)

        if src_lang is None:
            abort(400, description=_("%(lang)s is not supported", lang=source_lang))

        tgt_lang = next(iter([l for l in languages if l.code == target_lang]), None)

        if tgt_lang is None:
            abort(400, description=_("%(lang)s is not supported",lang=target_lang))

        if not text_format:
            text_format = "text"

        if text_format not in ["text", "html"]:
            abort(400, description=_("%(format)s format is not supported", format=text_format))

        try:
            if batch:
                batch_results = []
                batch_alternatives = []
                for text in q:
                    translator = src_lang.get_translation(tgt_lang)
                    if translator is None:
                        abort(400, description=_("%(tname)s (%(tcode)s) is not available as a target language from %(sname)s (%(scode)s)", tname=_lazy(tgt_lang.name), tcode=tgt_lang.code, sname=_lazy(src_lang.name), scode=src_lang.code))

                    if text_format == "html":
                        translated_text = unescape(str(translate_html(translator, text)))
                        alternatives = [] # Not supported for html yet
                    else:
                        hypotheses = translator.hypotheses(text, num_alternatives + 1)
                        translated_text = unescape(improve_translation_formatting(text, hypotheses[0].value))
                        alternatives = filter_unique([unescape(improve_translation_formatting(text, hypotheses[i].value)) for i in range(1, len(hypotheses))], translated_text)

                    batch_results.append(translated_text)
                    batch_alternatives.append(alternatives)
                
                result = {"translatedText": batch_results}

                if source_lang == "auto":
                    result["detectedLanguage"] = [detected_src_lang] * len(q)
                if num_alternatives > 0:
                    result["alternatives"] = batch_alternatives

                return jsonify(result)
            else:
                translator = src_lang.get_translation(tgt_lang)
                if translator is None:
                    abort(400, description=_("%(tname)s (%(tcode)s) is not available as a target language from %(sname)s (%(scode)s)", tname=_lazy(tgt_lang.name), tcode=tgt_lang.code, sname=_lazy(src_lang.name), scode=src_lang.code))

                if text_format == "html":
                    translated_text = unescape(str(translate_html(translator, q)))
                    alternatives = [] # Not supported for html yet
                else:
                    hypotheses = translator.hypotheses(q, num_alternatives + 1)
                    translated_text = unescape(improve_translation_formatting(q, hypotheses[0].value))
                    alternatives = filter_unique([unescape(improve_translation_formatting(q, hypotheses[i].value)) for i in range(1, len(hypotheses))], translated_text)

                result = {"translatedText": translated_text}

                if source_lang == "auto":
                    result["detectedLanguage"] = detected_src_lang
                if num_alternatives > 0:
                    result["alternatives"] = alternatives

                return jsonify(result)
        except Exception as e:
            raise e
            abort(500, description=_("Cannot translate text: %(text)s", text=str(e)))

    @bp.post("/translate_file")
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
              id: translate-file
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
            abort(403, description=_("Files translation are disabled on this server."))

        source_lang = request.form.get("source")
        target_lang = request.form.get("target")
        file = request.files['file']
        char_limit = get_char_limit(args.char_limit, api_keys_db)

        if not file:
            abort(400, description=_("Invalid request: missing %(name)s parameter", name='file'))
        if not source_lang:
            abort(400, description=_("Invalid request: missing %(name)s parameter", name='source'))
        if not target_lang:
            abort(400, description=_("Invalid request: missing %(name)s parameter", name='target'))

        if file.filename == '':
            abort(400, description=_("Invalid request: empty file"))

        if os.path.splitext(file.filename)[1] not in frontend_argos_supported_files_format:
            abort(400, description=_("Invalid request: file format not supported"))

        src_lang = next(iter([l for l in languages if l.code == source_lang]), None)

        if src_lang is None and source_lang != "auto":
            abort(400, description=_("%(lang)s is not supported", lang=source_lang))

        tgt_lang = next(iter([l for l in languages if l.code == target_lang]), None)

        if tgt_lang is None:
            abort(400, description=_("%(lang)s is not supported", lang=target_lang))

        try:
            filename = str(uuid.uuid4()) + '.' + secure_filename(file.filename)
            filepath = os.path.join(get_upload_dir(), filename)

            file.save(filepath)

            # Not an exact science: take the number of bytes and divide by
            # the character limit. Assuming a plain text file, this will
            # set the cost of the request to N = bytes / char_limit, which is
            # roughly equivalent to a batch process of N batches assuming
            # each batch uses all available limits
            if char_limit > 0:
                request.req_cost = max(1, int(os.path.getsize(filepath) / char_limit))

            if source_lang == "auto":
                src_texts = argostranslatefiles.get_texts(filepath)
                candidate_langs = detect_languages(src_texts)
                detected_src_lang = candidate_langs[0]
                src_lang = next(iter([l for l in languages if l.code == detected_src_lang["language"]]), None)
                if src_lang is None:
                    abort(400, description=_("%(lang)s is not supported", lang=detected_src_lang["language"]))

            translated_file_path = argostranslatefiles.translate_file(src_lang.get_translation(tgt_lang), filepath)
            translated_filename = os.path.basename(translated_file_path)

            return jsonify(
                {
                    "translatedFileUrl": url_for('Main app.download_file', filename=translated_filename, _external=True)
                }
            )
        except Exception as e:
            abort(500, description=e)

    @bp.get("/download_file/<string:filename>")
    def download_file(filename: str):
        """
        Download a translated file
        """
        if args.disable_files_translation:
            abort(400, description=_("Files translation are disabled on this server."))

        filepath = os.path.join(get_upload_dir(), filename)
        try:
            checked_filepath = security.path_traversal_check(filepath, get_upload_dir())
            if os.path.isfile(checked_filepath):
                filepath = checked_filepath
        except security.SuspiciousFileOperationError:
            abort(400, description=_("Invalid filename"))

        return_data = io.BytesIO()
        with open(filepath, 'rb') as fo:
            return_data.write(fo.read())
        return_data.seek(0)

        download_filename = filename.split('.')
        download_filename.pop(0)
        download_filename = '.'.join(download_filename)

        return send_file(return_data, as_attachment=True, download_name=download_filename)

    @bp.post("/detect")
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
              example: What language is this?
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
                    format: integer
                    minimum: 0
                    maximum: 100
                    description: Confidence value
                    example: 100
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
        if request.is_json:
            json = get_json_dict(request)
            q = json.get("q")
        else:
            q = request.values.get("q")

        if not q:
            abort(400, description=_("Invalid request: missing %(name)s parameter", name='q'))

        return jsonify(detect_languages(q))

    @bp.route("/frontend/settings")
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
        target_lang = frontend_argos_language_target()

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
                        "name": _lazy(frontend_argos_language_source.name),
                    },
                    "target": {
                        "code": target_lang.code,
                        "name": _lazy(target_lang.name),
                    },
                },
            }
        )

    @bp.post("/suggest")
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
            abort(403, description=_("Suggestions are disabled on this server."))

        if request.is_json:
            json = get_json_dict(request)
            q = json.get("q")
            s = json.get("s")
            source_lang = json.get("source")
            target_lang = json.get("target")
        else:
            q = request.values.get("q")
            s = request.values.get("s")
            source_lang = request.values.get("source")
            target_lang = request.values.get("target")

        if not q:
            abort(400, description=_("Invalid request: missing %(name)s parameter", name='q'))
        if not s:
            abort(400, description=_("Invalid request: missing %(name)s parameter", name='s'))
        if not source_lang:
            abort(400, description=_("Invalid request: missing %(name)s parameter", name='source'))
        if not target_lang:
            abort(400, description=_("Invalid request: missing %(name)s parameter", name='target'))

        SuggestionsDatabase().add(q, s, source_lang, target_lang)
        return jsonify({"success": True})

    app = Flask(__name__)

    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_FILE_DIR"] = os.path.join("db", "sessions")
    app.config["JSON_AS_ASCII"] = False
    Session(app)

    if args.debug:
        app.config["TEMPLATES_AUTO_RELOAD"] = True
    if args.url_prefix:
        app.register_blueprint(bp, url_prefix=args.url_prefix)
    else:
        app.register_blueprint(bp)

    limiter.init_app(app)

    swag = swagger(app)
    swag["info"]["version"] = get_version()
    swag["info"]["title"] = "LibreTranslate"

    @app.route(api_url)
    @limiter.exempt
    def spec():
        return jsonify(lazy_swag(swag))

    app.config["BABEL_TRANSLATION_DIRECTORIES"] = 'locales'

    def get_locale():
        override_lang = request.headers.get('X-Override-Accept-Language')
        if override_lang and override_lang in get_available_locale_codes():
            return override_lang
        return session.get('preferred_lang', request.accept_languages.best_match(get_available_locale_codes()))

    Babel(app, locale_selector=get_locale)

    app.jinja_env.globals.update(_e=gettext_escaped, _h=gettext_html)

    # Call factory function to create our blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(swagger_url, api_url)
    if args.url_prefix:
        app.register_blueprint(swaggerui_blueprint, url_prefix=swagger_url)
    else:
        app.register_blueprint(swaggerui_blueprint)

    return app
