import os
import sys
import ssl

# Bypass SSL certificate verification for downloads (common macOS python issue)
ssl._create_default_https_context = ssl._create_unverified_context

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from libretranslate.init import boot
from libretranslate.language import load_languages, get_language_with_fallback, translate_with_seeding

# Define 50 rare words that don't normally appear in daily speech
RARE_WORDS = [
    "floccinaucinihilipilification", "antidisestablishmentarianism", "defenestration", "quixotic", "synecdoche",
    "serendipity", "petrichor", "obfuscate", "cacophony", "ephemeral",
    "soliloquy", "juxtaposition", "wanderlust", "superfluous", "garrulous",
    "pulchritudinous", "schadenfreude", "onomatopoeia", "zeitgeist", "verisimilitude",
    "fastidious", "esoteric", "anachronistic", "dichotomy", "epiphany",
    "ubiquitous", "pernicious", "visceral", "surreptitious", "quintessential",
    "recalcitrant", "mellifluous", "plethora", "susurrus", "panacea",
    "liminal", "terpsichorean", "valetudinarian", "hegemony", "pejorative",
    "paradigmatic", "mercurial", "grandiloquent", "inchoate", "sycophant",
    "trenchant", "capricious", "laconic", "splendiferous", "apochromatic"
]

# Common everyday words used as a quick sanity check (seeded vs direct, Korean only)
COMMON_WORDS = [
    "eat", "run", "love", "sleep", "think",
    "walk", "happy", "angry", "beautiful", "cold",
    "fast", "house", "water", "dream", "friend",
    "light", "dark", "strong", "kind", "brave"
]

TARGET_LANGS = ["es", "fr", "de", "it", "pt", "ko"]

LANG_NAMES = {
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ko": "Korean",
}


def translate_direct(word, translator):
    """Translate directly without seeding (raw model output)."""
    try:
        return translator.translate(word)
    except Exception as e:
        return f"[ERROR: {str(e)}]"


def print_common_words_comparison(ko_translator):
    """Quick sanity check: seeded vs direct on everyday words, Korean only."""
    if ko_translator is None:
        print("\nKorean translator not available; skipping common-words test.")
        return

    print(f"\n{'Word':<15} {'Seeded':<20} {'Direct':<20} {'Different?'}")
    print("-" * 70)
    for word in COMMON_WORDS:
        seeded = translate_with_seeding(word, "en", "ko", ko_translator)
        direct = translate_direct(word, ko_translator)
        diff = "✅ DIFFERENT" if seeded.strip().lower() != direct.strip().lower() else "same"
        print(f"{word:<15} {seeded:<20} {direct:<20} {diff}")


def main():
    from argostranslate import package as _pkg
    installed_codes = {p.from_code for p in _pkg.get_installed_packages()} | \
                      {p.to_code   for p in _pkg.get_installed_packages()}
    needed = {"en", "es", "fr", "de", "it", "pt", "ko"}
    needs_install = not needed.issubset(installed_codes)

    print(f"Installed lang codes: {sorted(installed_codes)}")
    if needs_install:
        missing = needed - installed_codes
        print(f"Missing models for: {missing} — downloading...")
        boot(load_only=["en", "es", "fr", "de", "it", "pt", "ko"], install_models=True)
    else:
        print("All models already installed — skipping download.")
        boot(load_only=["en", "es", "fr", "de", "it", "pt", "ko"])

    languages = load_languages()
    src_lang = get_language_with_fallback("en", languages)

    if src_lang is None:
        print("Error: English language model not found.")
        sys.exit(1)

    # Pre-fetch translators for all target languages
    translators = {}
    for lang_code in TARGET_LANGS:
        tgt_lang = get_language_with_fallback(lang_code, languages)
        if tgt_lang is None:
            print(f"  WARNING: Model for '{lang_code}' not found.")
            translators[lang_code] = None
        else:
            t = src_lang.get_translation(tgt_lang)
            if t is None:
                print(f"  WARNING: No translator found for en→{lang_code}.")
            translators[lang_code] = t

    # ----------------------------------------------------------------
    # Build results: for each word, store seeded + direct per language
    # ----------------------------------------------------------------
    results = []

    print(f"\nTranslating {len(RARE_WORDS)} rare words (seeded + direct) across {len(TARGET_LANGS)} languages...\n")
    for idx, word in enumerate(RARE_WORDS, 1):
        row = {"#": idx, "word": word}
        for lang_code in TARGET_LANGS:
            t = translators.get(lang_code)
            if t is None:
                row[f"{lang_code}_seeded"] = "[N/A]"
                row[f"{lang_code}_direct"] = "[N/A]"
            else:
                row[f"{lang_code}_seeded"] = translate_with_seeding(word, "en", lang_code, t)
                row[f"{lang_code}_direct"] = translate_direct(word, t)
        results.append(row)
        print(f"[{idx:2d}/50] {word}")

    # ----------------------------------------------------------------
    # Write the main full comparison table
    # ----------------------------------------------------------------
    report_dir = "/Users/bipinkumarrai/.gemini/antigravity/brain/309572f0-b6b7-4ee7-a934-895f54f1fc30"
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, "rare_words_results.md")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Rare Words Translation Report\n\n")
        f.write("Translation of 50 rare English words across **Spanish, French, German, Italian, Portuguese, and Korean**.\n\n")
        f.write("Each language has two sub-columns: **Seeded** (context-seeding workaround) vs **Direct** (raw model output).\n\n")
        f.write("---\n\n")

        # ------- Per-language comparison tables --------
        for lang_code in TARGET_LANGS:
            lang_name = LANG_NAMES[lang_code]
            f.write(f"## {lang_name} ({lang_code})\n\n")
            f.write(f"| # | English Word | Seeded | Direct | Changed? |\n")
            f.write(f"| --- | --- | --- | --- | --- |\n")
            for row in results:
                seeded = row[f"{lang_code}_seeded"]
                direct = row[f"{lang_code}_direct"]
                changed = "✅" if seeded.strip().lower() != direct.strip().lower() else "—"
                f.write(f"| {row['#']} | **{row['word']}** | {seeded} | {direct} | {changed} |\n")
            f.write("\n")

        # ------- Full overview table (seeded only) --------
        f.write("---\n\n")
        f.write("## Full Overview (Seeded Translations)\n\n")
        headers = ["#", "English Word"] + [f"{LANG_NAMES[lc]} ({lc})" for lc in TARGET_LANGS]
        f.write("| " + " | ".join(headers) + " |\n")
        f.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
        for row in results:
            vals = [str(row["#"]), f"**{row['word']}**"] + [row[f"{lc}_seeded"] for lc in TARGET_LANGS]
            f.write("| " + " | ".join(vals) + " |\n")
        f.write("\n")

    print(f"\n✅ Report written to: {report_path}")

    # Also print a quick Korean comparison to stdout
    print("\n--- Korean: Seeded vs Direct (first 20 words) ---\n")
    print(f"{'Word':<35} {'Seeded':<30} {'Direct':<30} {'Different?'}")
    print("-" * 105)
    for row in results[:20]:
        s = row["ko_seeded"]
        d = row["ko_direct"]
        diff = "YES ✅" if s.strip().lower() != d.strip().lower() else "same"
        print(f"{row['word']:<35} {s:<30} {d:<30} {diff}")

    # Quick sanity check on everyday words, reusing the Korean translator built above
    print_common_words_comparison(translators.get("ko"))


if __name__ == "__main__":
    main()