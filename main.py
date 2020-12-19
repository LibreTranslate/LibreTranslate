import argparse
from flask import Flask, render_template, jsonify, request, abort, send_from_directory
from app.language import languages
from app.init import boot

parser = argparse.ArgumentParser(description='LibreTranslate - Free and Open Source Translation API')
parser.add_argument('host', type=str,
                    help='Hostname', default="127.0.0.1")
parser.add_argument('port', type=int,
                    help='Port', default=5000)
args = parser.parse_args()

boot()
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.errorhandler(400)
def invalid_api(e):
    return jsonify({"error": str(e.description)}), 400

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": str(e.description)}), 500

@app.route("/")
def index():
    return send_from_directory('static', 'index.html')


@app.route("/languages")
def langs():
	return jsonify([{'code': l.code, 'name': l.name } for l in languages])

@app.route("/translate", methods=['POST'])
def translate():

	q = request.values.get("q")
	source_lang = request.values.get("source")
	target_lang = request.values.get("target")

	if not q:
		abort(400, description="Invalid request: missing q parameter")
	if not source_lang:
		abort(400, description="Invalid request: missing source parameter")
	if not target_lang:
		abort(400, description="Invalid request: missing target parameter")


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


if __name__ == "__main__":
    app.run(host=args.host)
