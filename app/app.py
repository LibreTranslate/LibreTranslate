from flask import Flask, render_template, jsonify, request, abort, send_from_directory
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint
from langdetect import detect_langs
from langdetect import DetectorFactory
from pkg_resources import resource_filename
DetectorFactory.seed = 0 # deterministic

def get_remote_address():
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr or '127.0.0.1'

    return ip

def create_app(char_limit=-1, req_limit=-1, batch_limit=-1, ga_id=None, debug=False, frontend_language_source="en", frontend_language_target="en", frontend_timeout=500):
    from app.init import boot
    boot()

    from app.language import languages
    app = Flask(__name__)

    # For faster access
    language_map = {}
    for l in languages:
        language_map[l.code] = l.name

    if debug:
        app.config['TEMPLATES_AUTO_RELOAD'] = True

    # Map userdefined frontend languages to argos language object.
    if frontend_language_source == "auto":
        frontend_argos_language_source = type('obj', (object,), {
            'code': 'auto',
            'name': 'Auto Detect'
        })
    else:
        frontend_argos_language_source = next(iter([l for l in languages if l.code == frontend_language_source]), None)

    frontend_argos_language_target = next(iter([l for l in languages if l.code == frontend_language_target]), None)

    # Raise AttributeError to prevent app startup if user input is not valid.
    if frontend_argos_language_source is None:
        raise AttributeError(f"{frontend_language_source} as frontend source language is not supported.")
    if frontend_argos_language_target is None:
        raise AttributeError(f"{frontend_language_target} as frontend target language is not supported.")

    if req_limit > 0:
        from flask_limiter import Limiter
        limiter = Limiter(
            app,
            key_func=get_remote_address,
            default_limits=["%s per minute" % req_limit]
        )

    @app.errorhandler(400)
    def invalid_api(e):
        return jsonify({"error": str(e.description)}), 400

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": str(e.description)}), 500

    @app.errorhandler(429)
    def slow_down_error(e):
        return jsonify({"error": "Slowdown: " + str(e.description)}), 429

    @app.route("/")
    def index():
        return render_template('index.html', gaId=ga_id, frontendTimeout=frontend_timeout)

    @app.route("/languages")
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
        return jsonify([{'code': l.code, 'name': l.name} for l in languages])

    # Add cors
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin','*')
        response.headers.add('Access-Control-Allow-Headers', "Authorization, Content-Type")
        response.headers.add('Access-Control-Expose-Headers', "Authorization")
        response.headers.add('Access-Control-Allow-Methods', "GET, POST")
        response.headers.add('Access-Control-Allow-Credentials', "true")
        response.headers.add('Access-Control-Max-Age', 60 * 60 * 24 * 20)
        return response


    @app.route("/translate", methods=['POST'])
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
        """

        if request.is_json:
            json = request.get_json()
            q = json.get('q')
            source_lang = json.get('source')
            target_lang = json.get('target')
        else:
            q = request.values.get("q")
            source_lang = request.values.get("source")
            target_lang = request.values.get("target")

        if not q:
            abort(400, description="Invalid request: missing q parameter")
        if not source_lang:
            abort(400, description="Invalid request: missing source parameter")
        if not target_lang:
            abort(400, description="Invalid request: missing target parameter")

        batch = isinstance(q, list)

        if batch and batch_limit != -1:
          batch_size = len(q)
          if batch_limit < batch_size:
            abort(400, description="Invalid request: Request (%d) exceeds text limit (%d)" % (batch_size, batch_limit))

        if char_limit != -1:
            if batch:
              chars = sum([len(text) for text in q])
            else:
              chars = len(q)

            if char_limit < chars:
              abort(400, description="Invalid request: Request (%d) exceeds character limit (%d)" % (chars, char_limit))

        if source_lang == 'auto':
            candidate_langs = list(filter(lambda l: l.lang in language_map, detect_langs(q)))

            if len(candidate_langs) > 0:
                candidate_langs.sort(key=lambda l: l.prob, reverse=True)

                if debug:
                    print(candidate_langs)

                source_lang = next(iter([l.code for l in languages if l.code == candidate_langs[0].lang]), None)
                if not source_lang:
                    source_lang = 'en'
            else:
                source_lang = 'en'

            if debug:
                print("Auto detected: %s" % source_lang)

        src_lang = next(iter([l for l in languages if l.code == source_lang]), None)
        tgt_lang = next(iter([l for l in languages if l.code == target_lang]), None)

        if src_lang is None:
            abort(400, description="%s is not supported" % source_lang)
        if tgt_lang is None:
            abort(400, description="%s is not supported" % target_lang)

        translator = src_lang.get_translation(tgt_lang)

        try:
          if batch:
            return jsonify({"translatedText": [translator.translate(text) for text in q] })
          else:
            return jsonify({"translatedText": translator.translate(q) })
        except Exception as e:
            abort(500, description="Cannot translate text: %s" % str(e))

    @app.route("/frontend/settings")
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
        return jsonify({'charLimit': char_limit,
                        'frontendTimeout': frontend_timeout,
                        'language': {
                            'source': {'code': frontend_argos_language_source.code, 'name': frontend_argos_language_source.name},
                            'target': {'code': frontend_argos_language_target.code, 'name': frontend_argos_language_target.name}}
                       })

    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "LibreTranslate"

    @app.route("/spec")
    def spec():
        return jsonify(swag)

    SWAGGER_URL = '/docs'  # URL for exposing Swagger UI (without trailing '/')
    API_URL = '/spec'

    # Call factory function to create our blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL
    )

    app.register_blueprint(swaggerui_blueprint)

    return app
