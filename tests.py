import ast
import pytest

from main import Visitor


@pytest.mark.parametrize("code,mapped,remapped", [
    ("import mylib", "mylib", "mylib"),
    ("import mylib.pkg as P", "P", "mylib.pkg"),
    ("from mylib.pkg import func", "func", "mylib.pkg.func"),
    ("from mylib.pkg import func as F", "F", "mylib.pkg.func")],
    ids=["basic_import", "import_rename", "fromimport", "fromimport_rename"])
def test_import_mapping(code, mapped, remapped):
    co = ast.parse(code)
    v = Visitor()
    v.visit(co)
    assert mapped in v.remapped
    assert v.remapped[mapped] == remapped


@pytest.mark.skip()
def test_import_assign():
    code = r"""
import mylib

M = mylib.pkg
    """
    co = ast.parse(code)
    v = Visitor()
    v.visit(co)
    assert "M" in v.remapped
    assert v.remapped["M"] == "mylib.pkg"

#test_import_assign()


code = """
import mylib
from mylib.pkg import func
import mylib.pkg as T

M = mylib.pkg

model = func(pretrained=True)
transform = T.Resize(50)

res = T.functional.resize(img, 50)

m2 = getattr(mylib.pkg, 'resnet101', 'alexnet')(pretrained=True)
"""

#with open('/Users/fmassa/github/detr/util/box_ops.py', 'r') as f:
#with open('/Users/fmassa/github/detr/pkg/backbone.py', 'r') as f:
#    code = f.read()

co = ast.parse(code)

#print(ast.dump(co))

v = Visitor()
v.visit(co)
#print(v.remapped)
print(v.called)
