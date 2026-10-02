"""
Campus scene templates for LibreTranslate.

This module provides bilingual (zh/ru) templates for common university
scenarios: class notifications, exam announcements, emails to teachers,
courseware titles, etc.

Templates are stored as JSON with {variable} placeholders. The module loads
the template data, exposes the list of available templates, and renders a
filled-in bilingual pair given a template id and a dict of variables.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional

_DEFAULT_TEMPLATES_FILE = os.path.join(
    os.path.dirname(__file__), "templates_scene", "campus_templates.json"
)


class TemplateNotFoundError(Exception):
    pass


class SceneTemplate:
    """A single bilingual template."""

    def __init__(self, template_id: str, data: Dict[str, Any]):
        self.id = template_id
        self.name_zh = data.get("name", {}).get("zh", template_id)
        self.name_ru = data.get("name", {}).get("ru", template_id)
        self.description_zh = data.get("description", {}).get("zh", "")
        self.description_ru = data.get("description", {}).get("ru", "")
        self.variables: List[str] = data.get("variables", [])
        self.zh: str = data.get("zh", "")
        self.ru: str = data.get("ru", "")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": {"zh": self.name_zh, "ru": self.name_ru},
            "description": {"zh": self.description_zh, "ru": self.description_ru},
            "variables": self.variables,
        }

    def render(self, variables: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Fill in the placeholders and return a {zh, ru} dict."""
        variables = variables or {}
        # Provide empty string for any missing variable.
        safe_vars = {v: str(variables.get(v, "")) for v in self.variables}
        # Also allow extra variables that may appear in the template text.
        for k, v in variables.items():
            safe_vars.setdefault(k, str(v))
        return {
            "zh": _format(self.zh, safe_vars),
            "ru": _format(self.ru, safe_vars),
        }


def _format(template: str, variables: Dict[str, str]) -> str:
    """Replace {name} placeholders safely (no KeyError on missing keys)."""
    def replace(match):
        key = match.group(1)
        return variables.get(key, match.group(0))
    return re.sub(r"\{(\w+)\}", replace, template)


class TemplateManager:
    """Loads and manages scene templates."""

    def __init__(self, templates_file: str = _DEFAULT_TEMPLATES_FILE):
        self._templates: Dict[str, SceneTemplate] = {}
        self._load(templates_file)

    def _load(self, path: str):
        if not os.path.isfile(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        templates = data.get("templates", {})
        for tid, tdata in templates.items():
            if isinstance(tdata, dict):
                self._templates[tid] = SceneTemplate(tid, tdata)

    def list_templates(self) -> List[Dict[str, Any]]:
        return [t.to_dict() for t in self._templates.values()]

    def get(self, template_id: str) -> SceneTemplate:
        if template_id not in self._templates:
            raise TemplateNotFoundError(f"Template '{template_id}' not found")
        return self._templates[template_id]

    def render(self, template_id: str, variables: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        return self.get(template_id).render(variables)

    def count(self) -> int:
        return len(self._templates)


# Module-level singleton.
_manager: Optional[TemplateManager] = None


def setup(templates_file: Optional[str] = None) -> TemplateManager:
    global _manager
    if templates_file:
        _manager = TemplateManager(templates_file)
    else:
        _manager = TemplateManager()
    return _manager


def get_manager() -> TemplateManager:
    global _manager
    if _manager is None:
        _manager = TemplateManager()
    return _manager
