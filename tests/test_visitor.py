import ast
import pytest

from pylibstats import Visitor


@pytest.mark.parametrize("code,mapped,remapped", [
    ("import mylib", "mylib", "mylib"),
    ("import mylib.pkg as P", "P", "mylib.pkg"),
    ("from mylib.pkg import func", "func", "mylib.pkg.func"),
    ("from mylib.pkg.subpkg import func", "func", "mylib.pkg.subpkg.func"),
    ("from mylib.pkg import func as F", "F", "mylib.pkg.func")],
    ids=["basic_import", "import_rename", "fromimport", "fromimport3" ,"fromimport_rename"])
def test_import_mapping(code, mapped, remapped):
    co = ast.parse(code)
    v = Visitor()
    v.visit(co)
    assert mapped in v.remapped
    assert v.remapped[mapped] == remapped


def test_import_assign_call():
    code = "import mylib; M = mylib.pkg; M()"
    co = ast.parse(code)
    v = Visitor()
    v.visit(co)
    assert "M" in v.remapped
    assert v.remapped["M"] == "mylib.pkg"
    assert "mylib.pkg" in v.called


@pytest.mark.parametrize("code,called", [
    ("import mylib; mylib.func()", "mylib.func"),
    ("from mylib.pkg import func; func()", "mylib.pkg.func"),
    ("import mylib.pkg as T; T.func()", "mylib.pkg.func"),
    ("import mylib.pkg as T; T.subpkg.func()", "mylib.pkg.subpkg.func")])
def test_called(code, called):
    co = ast.parse(code)
    v = Visitor()
    v.visit(co)
    assert called in v.called


@pytest.mark.parametrize("code,called", [
    ("getattr(mylib, 'func')()", "mylib.func"),
    ("getattr(mylib.pkg, 'func')()", "mylib.pkg.func"),
    ("getattr(mylib, variable)()", "mylib.{?}"),
    ("getattr(mylib, a.b.c)()", "mylib.{?}")])
def test_getattr_in_call(code, called):
    co = ast.parse(code)
    v = Visitor()
    v.visit(co)
    assert called in v.called


def test_attr_shows():
    code = "res = {'a': mylib.a, 'b': mylib.pkg.b}"
    co = ast.parse(code)
    v = Visitor()
    v.visit(co)
    assert "mylib.a" in v.attrs.values()
    assert "mylib.pkg.b" in v.attrs.values()
