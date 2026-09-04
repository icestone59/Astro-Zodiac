import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def parse():
    return ast.parse((ROOT / "api_app.py").read_text(encoding="utf-8"))


def test_bearer_scheme_is_declared():
    src = (ROOT / "api_app.py").read_text(encoding="utf-8")
    assert '"BearerAuth"' in src or "'BearerAuth'" in src
    assert '"scheme": "bearer"' in src or "'scheme': 'bearer'" in src


def test_custom_openapi_is_present():
    tree = parse()
    names = {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert "_custom_openapi" in names


def test_protected_route_paths_are_explicit():
    src = (ROOT / "api_app.py").read_text(encoding="utf-8")
    assert '"/api/v1/me"' in src
    assert '"/api/v1/analysis/free"' in src
    assert '"/api/v1/entitlements/{feature}"' in src
    assert 'operation["security"]' in src


def test_authentication_dependency_still_used():
    tree = parse()
    src = ast.unparse(tree)
    assert "Depends(extract_bearer_token)" in src
    assert "resolve_session" in src
