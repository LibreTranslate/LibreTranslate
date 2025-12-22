from libretranslate.storage import get_storage
import hashlib
import json
import gzip

cache = None
def get_translation_cache():
    return cache

class TranslationCache:
    def __init__(self, translation_cache_aks):
        self.enabled = len(translation_cache_aks) > 0
        self.api_keys = [ak for ak in translation_cache_aks if ak.lower() != "all"]
        self.cache_all = "all" in [ak.lower() for ak in translation_cache_aks]
        self.expire = 604800 # 7 days
        self.storage = get_storage()

        assert self.storage is not None, "Storage is none"

    def should_check(self, ak):
        return self.enabled and (self.cache_all or ak in self.api_keys)

    def hit(self, src_texts, source_lang, target_lang, text_format, num_alternatives):
        text_blob = "|".join(src_texts) if isinstance(src_texts, list) else src_texts
        fingerprint = f"{text_blob}:{source_lang}:{target_lang}:{text_format}:{num_alternatives}"
        cache_key = "tcache_" + hashlib.md5(fingerprint.encode('utf-8')).hexdigest()

        cached = self.storage.get_str(cache_key, raw=True)
        if len(cached) == 0:
            cached = None

        if cached is not None:
            try:
                cached = gzip.decompress(cached).decode('utf-8')
            except Exception as e:
                print(str(e))

        return cache_key, cached

    def cache(self, cache_key, content):
        try:
            if isinstance(content, dict):
                content = json.dumps(content)
                compressed = gzip.compress(content.encode('utf-8'))
                
            self.storage.set_str(cache_key, compressed, self.expire)
        except Exception as e:
            print(str(e))

def setup(translation_cache_aks):
    global cache
    
    cache = TranslationCache(translation_cache_aks)
    return cache