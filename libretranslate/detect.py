
from langdetect import DetectorFactory

DetectorFactory.seed = 0

from langdetect import detect_langs
from lexilang.detector import detect as lldetect


class Language:
  def __init__(self, code, confidence):
    self.code = code
    self.confidence = float(confidence)

  def __str__(self):
    return (f"code: {self.code:<9} confidence: {self.confidence:>5.1f} ")

def check_lang(langcodes, lang):
  return normalized_lang_code(lang) in langcodes

def normalized_lang_code(lang):
  code = lang.lang
  # Handle zh-cn
  if code.startswith("zh"):
    code = "zh"
  return code

class Detector:
  def __init__(self, langcodes = ()):
    self.langcodes = langcodes

  def detect(self, text):
    if len(text) < 20:
      code, conf = lldetect(text, self.langcodes)
      if conf > 0:
        return [Language(code, round(conf * 100))]

    top_3_choices = [lang for lang in detect_langs(text) if check_lang(self.langcodes, lang)][:3]
    if not len(top_3_choices):
      return [Language("en", 0)]
    if top_3_choices[0].prob == 0:
      return [Language("en", 0)]

    return [Language(normalized_lang_code(lang), round(lang.prob * 100)) for lang in top_3_choices]

