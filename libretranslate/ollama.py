import json
import logging
from urllib import request as urllib_request
from urllib.error import URLError

logger = logging.getLogger(__name__)

# Map ISO language codes to full language names for the LLM prompt
LANG_NAMES = {
    "en": "English",
    "ar": "Arabic",
    "az": "Azerbaijani",
    "ca": "Catalan",
    "cs": "Czech",
    "da": "Danish",
    "de": "German",
    "el": "Greek",
    "eo": "Esperanto",
    "es": "Spanish",
    "fa": "Persian",
    "fi": "Finnish",
    "fr": "French",
    "ga": "Irish",
    "he": "Hebrew",
    "hi": "Hindi",
    "hu": "Hungarian",
    "id": "Indonesian",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "ms": "Malay",
    "nb": "Norwegian",
    "nl": "Dutch",
    "pl": "Polish",
    "pt": "Portuguese",
    "pb": "Portuguese",
    "ro": "Romanian",
    "ru": "Russian",
    "sk": "Slovak",
    "sv": "Swedish",
    "th": "Thai",
    "tl": "Filipino",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "vi": "Vietnamese",
    "zh": "Chinese",
    "zt": "Chinese",
}


def get_lang_name(code):
    return LANG_NAMES.get(code, code)


def translate_ollama(text, source_lang, target_lang, host, model):
    """Translate text using an Ollama model.

    Args:
        text: The text to translate.
        source_lang: Source language code (e.g. "en").
        target_lang: Target language code (e.g. "de").
        host: Ollama API host URL (e.g. "http://localhost:11434").
        model: Ollama model name (e.g. "translategemma").

    Returns:
        The translated text as a string.

    Raises:
        Exception: If the Ollama API is unreachable or returns an error.
    """
    src_name = get_lang_name(source_lang)
    tgt_name = get_lang_name(target_lang)

    prompt = f"<2{target_lang}> {text}"

    url = f"{host.rstrip('/')}/api/generate"
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
    }).encode("utf-8")

    req = urllib_request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib_request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except URLError as e:
        raise Exception(f"Ollama API not reachable at {host}: {e}") from e

    if "error" in body:
        raise Exception(f"Ollama API error: {body['error']}")

    translated = body.get("response", "").strip()
    if not translated:
        raise Exception("Ollama returned an empty translation")

    return translated
