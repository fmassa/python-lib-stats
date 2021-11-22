import ast
import pytest

from main import Visitor


@pytest.mark.parametrize("code,mapped,remapped", [
    ("import torchvision", "torchvision", "torchvision"),
    ("import torchvision.transforms as T", "T", "torchvision.transforms"),
    ("from torchvision.models import resnet50", "resnet50", "torchvision.models.resnet50"),
    ("from torchvision.models import resnet50 as R", "R", "torchvision.models.resnet50")],
    ids=["basic_import", "import_rename", "fromimport", "fromimport_rename"])
def test_import_mapping(code, mapped, remapped):
    co = ast.parse(code)
    v = Visitor()
    v.visit(co)
    assert mapped in v.remapped
    assert v.remapped[mapped] == remapped


def test_basic_import():
    code = "import torchvision"
    co = ast.parse(code)
    v = Visitor()
    v.visit(co)
    assert "torchvision" in v.remapped
    assert v.remapped["torchvision"] == "torchvision"

def test_import_rename():
    code = "import torchvision.transforms as T"
    co = ast.parse(code)
    v = Visitor()
    v.visit(co)
    assert "T" in v.remapped
    assert v.remapped["T"] == "torchvision.transforms"

def test_fromimport():
    code = "from torchvision.models import resnet50"
    co = ast.parse(code)
    v = Visitor()
    v.visit(co)
    assert "resnet50" in v.remapped
    assert v.remapped["resnet50"] == "torchvision.models.resnet50"

def test_fromimport_rename():
    code = "from torchvision.models import resnet50 as R"
    co = ast.parse(code)
    v = Visitor()
    v.visit(co)
    assert "R" in v.remapped
    assert v.remapped["R"] == "torchvision.models.resnet50"


@pytest.mark.skip()
def test_import_assign():
    code = r"""
import torchvision

M = torchvision.models
    """
    co = ast.parse(code)
    v = Visitor()
    v.visit(co)
    assert "M" in v.remapped
    assert v.remapped["M"] == "torchvision.models"

#test_import_assign()


code = """
import torchvision
from torchvision.models import resnet50
import torchvision.transforms as T

M = torchvision.models

model = resnet50(pretrained=True)
transform = T.Resize(50)

res = T.functional.resize(img, 50)

m2 = getattr(torchvision.models, 'resnet101', 'alexnet')(pretrained=True)
"""

#with open('/Users/fmassa/github/detr/util/box_ops.py', 'r') as f:
#with open('/Users/fmassa/github/detr/models/backbone.py', 'r') as f:
#    code = f.read()

co = ast.parse(code)

#print(ast.dump(co))

v = Visitor()
v.visit(co)
#print(v.remapped)
print(v.called)
