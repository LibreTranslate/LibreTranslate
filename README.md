# LibreTranslate

[Try it online!](https://libretranslate.com) | [API Docs](https://docs.libretranslate.com) | [Community Forum](https://community.libretranslate.com/) | [Bluesky](https://bsky.app/profile/libretranslate.com)

[![Python versions](https://img.shields.io/pypi/pyversions/libretranslate)](https://pypi.org/project/libretranslate) [![Run tests](https://github.com/LibreTranslate/LibreTranslate/workflows/Run%20tests/badge.svg)](https://github.com/LibreTranslate/LibreTranslate/actions?query=workflow%3A%22Run+tests%22) [![Build and Publish Docker Image](https://github.com/LibreTranslate/LibreTranslate/actions/workflows/publish-docker.yml/badge.svg)](https://github.com/LibreTranslate/LibreTranslate/actions/workflows/publish-docker.yml) [![Publish package](https://github.com/LibreTranslate/LibreTranslate/actions/workflows/publish-package.yml/badge.svg)](https://github.com/LibreTranslate/LibreTranslate/actions/workflows/publish-package.yml) [![Awesome Humane Tech](https://raw.githubusercontent.com/humanetech-community/awesome-humane-tech/main/humane-tech-badge.svg?sanitize=true)](https://codeberg.org/teaserbot-labs/delightful-humane-design)

Free and Open Source Machine Translation API, entirely self-hosted. Unlike other APIs, it doesn't rely on proprietary software such as Google or Azure to perform translations. Instead, its translation engine is powered by the open source [Argos Translate](https://github.com/argosopentech/argos-translate) library.

This fork adds optional [Ollama](https://ollama.com/) integration, allowing you to use LLM-based translation models such as [Translategemma](https://ollama.com/library/translategemma) as an alternative translation backend.

![Translation](https://github.com/user-attachments/assets/457696b5-dbff-40ab-a18e-7bfb152c5121)

## Getting Started

- [Quickstart](https://docs.libretranslate.com/)
- [Usage Instructions](https://docs.libretranslate.com/guides/api_usage/)
- [Community Resources](https://docs.libretranslate.com/community/resources/)

## Ollama LLM Translation

### Prerequisites

- A running [Ollama](https://ollama.com/) instance
- The Translategemma model pulled into Ollama:
  ```bash
  ollama pull translategemma
  ```

### Configuration

Enable the feature via CLI arguments or environment variables:

| CLI Argument | Environment Variable | Default | Description |
|---|---|---|---|
| `--ollama` | `LT_OLLAMA_ENABLED=true` | `false` | Enable the Ollama translation backend |
| `--ollama-host` | `LT_OLLAMA_HOST` | `http://localhost:11434` | Ollama API URL |
| `--ollama-model` | `LT_OLLAMA_MODEL` | `translategemma` | Model to use for translation |

**Example:**

```bash
libretranslate --ollama --ollama-host http://localhost:11434 --ollama-model translategemma
```

Or with environment variables:

```bash
LT_OLLAMA_ENABLED=true LT_OLLAMA_HOST=http://localhost:11434 libretranslate
```

### Usage

When Ollama is enabled, a toggle switch labeled **"LLM Translation (Ollama)"** appears in the web UI between the language selectors and the text fields. Users can switch between the standard Argos Translate engine and the Ollama-backed LLM translation at any time. The preference is stored in the browser and persists across page reloads.

The feature can also be used via the API by adding `use_ollama=true` to the `/translate` request:

```bash
curl -X POST http://localhost:5000/translate \
  -d "q=Hello world&source=en&target=de&use_ollama=true"
```

## Credits

This work is largely possible thanks to [Argos Translate](https://github.com/argosopentech/argos-translate), which powers the translation engine.

## License

[GNU Affero General Public License v3](https://www.gnu.org/licenses/agpl-3.0.en.html)

## Trademark

See [Trademark Guidelines](https://github.com/LibreTranslate/LibreTranslate/blob/main/TRADEMARK.md)

