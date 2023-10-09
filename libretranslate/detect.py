# Originally adapted from https://github.com/aboSamoor/polyglot/blob/master/polyglot/base.py

import unicodedata

import pycld2 as cld2


class UnknownLanguageError(Exception):
  pass

class Language:
  def __init__(self, choice):
    name, code, confidence, bytesize = choice
    self.code = code
    self.name = name
    self.confidence = float(confidence)
    self.read_bytes = int(bytesize)

  def __str__(self):
    return ("name: {:<12}code: {:<9}confidence: {:>5.1f} "
            "read bytes:{:>6}".format(self.name, self.code,
                                    self.confidence, self.read_bytes))

  @staticmethod
  def from_code(code):
    return Language(("", code, 100, 0))


class Detector:
  """ Detect the language used in a snippet of text."""

  def __init__(self, text, quiet=False):
    """ Detector of the language used in `text`.
    Args:
      text (string): unicode string.
    """
    self.__text = text
    self.reliable = True
    """False if the detector used Best Effort strategy in detection."""
    self.quiet = quiet
    """If true, exceptions will be silenced."""
    self.detect(text)

  @staticmethod
  def supported_languages():
    """Returns a list of the languages that can be detected by pycld2."""
    return [name.capitalize() for name,code in cld2.LANGUAGES if not name.startswith("X_")]

  def detect(self, text):
    """Decide which language is used to write the text.
    The method tries first to detect the language with high reliability. If
    that is not possible, the method switches to best effort strategy.
    Args:
      text (string): A snippet of text, the longer it is the more reliable we
                     can detect the language used to write the text.
    """
    try:
      reliable, index, top_3_choices = cld2.detect(text, bestEffort=False)
    except cld2.error as e:
      if "input contains invalid UTF-8" in str(e):
        # Fix for https://github.com/LibreTranslate/LibreTranslate/issues/514
        # related to https://github.com/aboSamoor/polyglot/issues/71#issuecomment-707997790
        text = ''.join([l for l in text if unicodedata.category(str(l))[0] not in ('S', 'M', 'C')])
        reliable, index, top_3_choices = cld2.detect(text, bestEffort=False)
      else:
        raise e

    if not reliable:
      self.reliable = False
      reliable, index, top_3_choices = cld2.detect(text, bestEffort=True)

      if not self.quiet and not reliable:
        raise UnknownLanguageError("Try passing a longer snippet of text")

    self.languages = [Language(x) for x in top_3_choices]
    self.language = self.languages[0]
    return self.language

  def __str__(self):
    text = f"Prediction is reliable: {self.reliable}\n"
    text += "\n".join([f"Language {i+1}: {str(l)}"
                        for i,l in enumerate(self.languages)])
    return text
