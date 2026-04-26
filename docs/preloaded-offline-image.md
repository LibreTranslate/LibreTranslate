# Preloaded Offline Docker Image

This is an optional deployment example for users who prefer preloaded models.

This guide describes how to build a LibreTranslate Docker image with translation models already included inside the container.

This is useful for environments where downloading models during startup is not preferred or unavailable.

Examples:

- offline servers
- restricted corporate networks
- air-gapped systems
- faster first startup
- predictable deployments

---

## Benefits

Using a preloaded image provides:

- no model downloads on first run
- faster startup time
- deterministic deployments
- easier backup and migration
- portable ready-to-run container images

---

## Folder Structure

Create a local folder named:

```text
models/
```

Place Argos Translate model folders inside it.

Example:

```text
models/
 ├── translate-en_ru-1_9/
 ├── translate-ru_en-1_9/
 ├── translate-en_zh-1_9/
 └── translate-zh_en-1_9/
```

---

## Preloader Dockerfile

Use the included Dockerfile: [Dockerfile.preloaded](../Dockerfile.preloaded)

---

## Compose Example

Use the included file: [docker-compose.big.yml](../docker-compose.big.yml)

---

## Build Image

```bash
docker compose -f docker-compose.big.yml build
```

---

## Run Container

```bash
docker compose -f docker-compose.big.yml up -d
```

---

## Open Web UI

```text
http://localhost:5000
```

---

## Notes

- `LT_UPDATE_MODELS=false` disables downloading models during startup.
- `LT_LOAD_ONLY` limits loaded languages to reduce memory usage.
- You may include any supported language models.

---

## Example Use Cases

- Russian / English / Chinese offline translator
- Internal translation API
- Local automation pipelines
- Secure private infrastructure

---

## Disclaimer

This is an optional deployment pattern and does not modify the default LibreTranslate behavior.
