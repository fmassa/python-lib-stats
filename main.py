import ast
from collections import defaultdict


class Visitor(ast.NodeVisitor):
    def __init__(self, library_name='torchvision'):
        super().__init__()
        self.library_name = library_name
        self.remapped = {}
        # self.modules = set()
        self.called = defaultdict(int)

    def visit_Import(self, node):
        for n in node.names:
            if n.asname:
                self.remapped[n.asname] = n.name
            else:
                # self.modules.add(n.name)
                self.remapped[n.name] = n.name
            # print(n.name, n.asname)

    def visit_ImportFrom(self, node):
        module = node.module
        #print(module)
        for n in node.names:
            name = module + '.' + n.name
            if n.asname:
                self.remapped[n.asname] = name
            else:
                #self.modules.add(name)
                self.remapped[n.name] = name
            #print(n.name, n.asname)

    def visit_Call(self, node):
        #print(ast.dump(node))
        func = node.func
        try:
            if isinstance(func, ast.Name):
                self.called[self.remapped[func.id]] += 1
            elif isinstance(func, ast.Attribute):
                sts = []
                while isinstance(func, ast.Attribute):
                    sts.append(func.attr)
                    func = func.value
                assert isinstance(func, ast.Name)
                sts = reversed(sts)
                name = ".".join([self.remapped[func.id]] + list(sts))
                self.called[name] += 1
        except Exception:
            print('oups')



code = """
import torchvision
from torchvision.models import resnet50
import torchvision.transforms as T

M = torchvision.models

model = resnet50(pretrained=True)
transform = T.Resize(50)

res = T.functional.resize(img, 50)

m2 = getattr(torchvision.models, 'resnet50', 'alexnet')(pretrained=True)
"""

#with open('/Users/fmassa/github/detr/util/box_ops.py', 'r') as f:
#with open('/Users/fmassa/github/detr/models/backbone.py', 'r') as f:
#    code = f.read()

co = ast.parse(code)

print(ast.dump(co))

v = Visitor()
v.visit(co)
print(v.remapped)
print(v.called)
