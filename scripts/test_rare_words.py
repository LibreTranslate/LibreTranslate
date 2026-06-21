import os
import sys
import json
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

TARGET_LANGS = ["es", "fr", "de", "it", "pt"]

def main():
    print("Booting LibreTranslate and installing models for: en, es, fr, de, it, pt...")
    # This downloads and installs packages if not present by using install_models=True
    boot(load_only=["en", "es", "fr", "de", "it", "pt"], install_models=True)

    languages = load_languages()
    src_lang = get_language_with_fallback("en", languages)
    
    if src_lang is None:
        print("Error: English language model not found.")
        sys.exit(1)

    results = []

    print(f"Translating {len(RARE_WORDS)} rare words...")
    for idx, word in enumerate(RARE_WORDS, 1):
        row = {"#": idx, "English Word": word}
        for lang_code in TARGET_LANGS:
            tgt_lang = get_language_with_fallback(lang_code, languages)
            if tgt_lang is None:
                row[lang_code] = "[N/A - lang model missing]"
                continue
            
            translator = src_lang.get_translation(tgt_lang)
            if translator is None:
                row[lang_code] = "[N/A - translator missing]"
                continue
            
            try:
                translated = translate_with_seeding(word, "en", lang_code, translator)
                row[lang_code] = translated
            except Exception as e:
                row[lang_code] = f"[ERROR: {str(e)}]"
        
        results.append(row)
        print(f"[{idx}/{len(RARE_WORDS)}] Translated '{word}'")

    # Generate Markdown Table
    headers = ["#", "English Word", "Spanish (es)", "French (fr)", "German (de)", "Italian (it)", "Portuguese (pt)"]
    markdown_lines = []
    markdown_lines.append("| " + " | ".join(headers) + " |")
    markdown_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

    for row in results:
        line_vals = [
            str(row["#"]),
            f"**{row['English Word']}**",
            row.get("es", ""),
            row.get("fr", ""),
            row.get("de", ""),
            row.get("it", ""),
            row.get("pt", "")
        ]
        markdown_lines.append("| " + " | ".join(line_vals) + " |")

    markdown_table = "\n".join(markdown_lines)
    
    # Write report file
    report_dir = "/Users/bipinkumarrai/.gemini/antigravity/brain/309572f0-b6b7-4ee7-a934-895f54f1fc30"
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, "rare_words_results.md")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Rare Words Translation Report\n\n")
        f.write("This report presents the translation of 50 English words that don't normally appear in daily speech, across Spanish, French, German, Italian, and Portuguese.\n\n")
        f.write("## Methodology\n")
        f.write("Translations were evaluated using LibreTranslate's core translation engine with context-seeding applied to improve single-word translations.\n\n")
        f.write("## Results\n\n")
        f.write(markdown_table)
        f.write("\n")

    print(f"\nReport generated successfully at: {report_path}")
    print("Printing results to stdout:\n")
    print(markdown_table)

if __name__ == "__main__":
    main()
