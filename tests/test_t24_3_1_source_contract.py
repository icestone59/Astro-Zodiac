import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_api_app_imports_bearer_dependency():
    tree = ast.parse((ROOT / "api_app.py").read_text(encoding="utf-8"))
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.module == "api_security"
        for alias in node.names
    }
    assert "extract_bearer_token" in imports


def test_get_user_uses_bearer_dependency():
    tree = ast.parse((ROOT / "api_app.py").read_text(encoding="utf-8"))
    fn = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "_get_user"
    )
    source = ast.unparse(fn)
    assert "Depends(extract_bearer_token)" in source


def test_me_route_depends_on_get_user():
    tree = ast.parse((ROOT / "api_app.py").read_text(encoding="utf-8"))
    route = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "api_me"
    )
    source = ast.unparse(route)
    assert "Depends(_get_user)" in source


def test_bearer_openapi_contract_exists():
    security = (ROOT / "api_security.py").read_text(encoding="utf-8")
    assert 'scheme_name="BearerAuth"' in security
    assert "HTTPBearer(" in security
    assert "WWW-Authenticate" in security
