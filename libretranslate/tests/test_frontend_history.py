import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest


def _template_path():
    for candidate in (
        Path(__file__).resolve().parents[1] / "templates" / "app.js.template",
        Path.cwd() / "libretranslate" / "templates" / "app.js.template",
    ):
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("Could not locate app.js.template")


TEMPLATE_PATH = _template_path()


def template_source():
    return TEMPLATE_PATH.read_text(encoding="utf-8")


def method_source(source, name):
    """Return the JavaScript source of a Vue method, including its body."""
    match = re.search(r"\n            %s: function\s*\([^)]*\)\s*\{" % re.escape(name), source)
    assert match is not None, "Could not find method %s in %s" % (name, TEMPLATE_PATH)

    depth = 0
    for index in range(match.end() - 1, len(source)):
        char = source[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[match.start() + 1:index + 1]

    raise AssertionError("Unbalanced braces in method %s" % name)


def test_update_query_param_replaces_history_entry():
    """Updating the URL must not add history entries (issue #1043)."""
    method = method_source(template_source(), "updateQueryParam")

    assert "history.replaceState(" in method
    assert "history.pushState(" not in method


def test_frontend_never_pushes_history_entries_for_query_params():
    source = template_source()

    assert "pushState(" not in source
    assert "window.location.hash = " not in source


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not available")
def test_back_button_is_not_trapped_by_translation_updates():
    """Exercise updateQueryParam in Node and assert it never grows history."""
    method = method_source(template_source(), "updateQueryParam")
    method = method.replace("updateQueryParam: function", "const updateQueryParam = function", 1)

    script = "\n".join([
        "const calls = [];",
        "const location = { pathname: '/', search: '', hash: '' };",
        "global.window = { location };",
        "global.history = {",
        "  replaceState(state, title, url) {",
        "    calls.push({ kind: 'replace', url });",
        "    const hashIndex = url.indexOf('#');",
        "    const withoutHash = hashIndex === -1 ? url : url.slice(0, hashIndex);",
        "    const queryIndex = withoutHash.indexOf('?');",
        "    location.search = queryIndex === -1 ? '' : withoutHash.slice(queryIndex);",
        "    location.hash = hashIndex === -1 ? '' : url.slice(hashIndex);",
        "  },",
        "  pushState(state, title, url) { calls.push({ kind: 'push', url }); },",
        "};",
        method,
        "updateQueryParam('source', 'en');",
        "updateQueryParam('target', 'es');",
        "updateQueryParam('q', 'hello world');",
        "console.log(JSON.stringify({ calls, search: location.search, hash: location.hash }));",
    ])

    result = subprocess.run(
        ["node", "-e", script],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr

    output = json.loads(result.stdout)
    assert output["calls"], "updateQueryParam did not update the URL"
    assert {call["kind"] for call in output["calls"]} == {"replace"}
    assert "source=en" in output["search"]
    assert "target=es" in output["search"]
    assert "q=" not in output["search"]
    assert output["hash"] == "#q=hello%20world"