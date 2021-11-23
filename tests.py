import ast
import pytest

from main import Visitor


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


def test_import_assign():
    code = """import mylib; M = mylib.pkg"""
    co = ast.parse(code)
    v = Visitor()
    v.visit(co)
    assert "M" in v.remapped
    assert v.remapped["M"] == "mylib.pkg"


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
    ("getattr(mylib.pkg, 'func')()", "mylib.pkg.func")])
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
    assert "mylib.a" in v.nets.values()
    assert "mylib.pkg.b" in v.nets.values()


#code = "getattr(mylib.pkg, 'c')(True, pretrained=False)"
#code = "getattr(getattr(mylib, 'pkg'), 'c')()"
#code = "{'a': mylib.a.d, 'b': mylib.b}"
code = "import mylib; M = mylib.pkg; M()"

#with open('/Users/fmassa/github/detr/util/box_ops.py', 'r') as f:
#with open('/Users/fmassa/github/detr/models/backbone.py', 'r') as f:
#    code = f.read()

co = ast.parse(code)

if True:
    #print(ast.dump(co))

    v = Visitor("mylib")
    v.visit(co)
    #print(v.remapped)
    #print(v.called)
    #print(list(v.nets.values()))
    v.report()


if False:
    import glob
    files = glob.glob('/Users/fmassa/github/detr/**/*.py', recursive=True)

    v = Visitor("torchvision")

    for fname in files:
        with open(fname, 'r') as f:
            code = f.read()
        co = ast.parse(code)
        v.visit(co)

    v.report()
