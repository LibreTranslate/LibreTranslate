import linguars
from functools import lru_cache

class Language:
  def __init__(self, code, confidence):
    self.code = code
    self.confidence = float(confidence)

  def __str__(self):
    return ("code: {:<9} confidence: {:>5.1f} ".format(
                self.code,
                self.confidence))

@lru_cache(maxsize=None)
def load_detector(langcodes = ()):
  languages = []
  for lc in langcodes:
    try:
      languages.append(linguars.Language.from_iso_code_639_1(lc))
    except Exception as e:
      print(f"{lc} is not supported by lingua")
      pass # Not supported
  
  return linguars.LanguageDetector(languages=languages)


class Detector:
  def __init__(self, langcodes = ()):
    self.detector = load_detector(langcodes)

  def detect(self, text):
    top_3_choices = self.detector.confidence(text)[:3]
    if top_3_choices[0][1] == 0:
      return [Language("en", 0)]
    return [Language(lang.iso_code_639_1, round(conf * 100)) for lang, conf in top_3_choices]

