from flask import Flask, render_template, jsonify, request, abort, send_from_directory
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint
from flask_limiter.util import get_remote_address


def create_app(char_limit=-1, req_limit=-1, ga_id=None, debug=False):
    from app.init import boot
    from app.language import languages

    boot()
    app = Flask(__name__)

    if debug:
        app.config['TEMPLATES_AUTO_RELOAD'] = True

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
        return render_template('index.html', gaId=ga_id)

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
            content:
              application/json:
                schema:
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
                      charLimit:
                        type: string
                        description: Character input limit for this language (-1 indicates no limit)
          429:
            description: Slow down
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    error:
                      type: string
                      description: Reason for slow down
        """
        return jsonify([{'code': l.code, 'name': l.name, 'charLimit': char_limit } for l in languages])

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
              type: string
              example: Hello world!
            required: true
            description: Text to translate
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
            content:
              application/json:
                schema:
                type: object
                properties:
                  translatedText:
                    type: string
                    description: Translated text
          400:
            description: Invalid request
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    error:
                      type: string
                      description: Error message
          500:
            description: Translation error
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    error:
                      type: string
                      description: Error message
          429:
            description: Slow down
            content:
              application/json:
                schema:
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

        if char_limit != -1:
            q = q[:char_limit]

        src_lang = next(iter([l for l in languages if l.code == source_lang]), None)
        tgt_lang = next(iter([l for l in languages if l.code == target_lang]), None)

        if src_lang is None:
            abort(400, description="%s is not supported" % source_lang)
        if tgt_lang is None:
            abort(400, description="%s is not supported" % target_lang)

        translator = src_lang.get_translation(tgt_lang)
        try:
            return jsonify({"translatedText": translator.translate(q) })
        except Exception as e:
            abort(500, description="Cannot translate text: %s" % str(e))


    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "LibreTranslate"

    @app.route("/spec")
    def spec():
        return jsonify(swag)

    SWAGGER_URL = '/docs'  # URL for exposing Swagger UI (without trailing '/')
    API_URL = 'http://petstore.swagger.io/v2/swagger.json'  # Our API url (can of course be a local resource)

    # Call factory function to create our blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        "",
        config={  # Swagger UI config overrides
            'app_name': "LibreTranslate",
            "spec": swag
        }
    )

    app.register_blueprint(swaggerui_blueprint)

    return app