import ast
from collections import defaultdict


class Visitor(ast.NodeVisitor):
    def __init__(self, library_name='torchvision'):
        super().__init__()
        self.library_name = library_name
        self.remapped = {}
        self.called = defaultdict(list)

    def visit_Import(self, node):
        for n in node.names:
            if n.asname:
                self.remapped[n.asname] = n.name
            else:
                self.remapped[n.name] = n.name

    def visit_ImportFrom(self, node):
        module = node.module
        for n in node.names:
            name = module + '.' + n.name
            if n.asname:
                self.remapped[n.asname] = name
            else:
                self.remapped[n.name] = name

    def visit_Call(self, node):
        #print(ast.dump(node))
        self.generic_visit(node)
        if _getattr_with_const(self, node):
            return
        func = node.func
        try:
            if isinstance(func, ast.Name):
                name = func.id
                if name in self.remapped:
                    name = self.remapped[name]
                self.called[name] += node.args
            elif isinstance(func, ast.Attribute):
                sts = []
                while isinstance(func, ast.Attribute):
                    sts.append(func.attr)
                    func = func.value
                assert isinstance(func, ast.Name)
                sts = reversed(sts)
                name = ".".join([self.remapped[func.id]] + list(sts))
                self.called[name] += node.args
            else:
                print(ast.dump(node))
        except Exception:
            print('oups')

    def visit_Name(self, node):
        if node.id == self.library_name:
            print("found")

    def visit(self, node):
        if _is_nested_attribute_and_name(node):
            nid, sts = _nested_attribute_and_name(node)
            print(nid, sts, node)
            return
        return super().visit(node)

def _is_nested_attribute_and_name(node):
    while isinstance(node, ast.Attribute):
        node = node.value
    return isinstance(node, ast.Name)

def _nested_attribute_and_name(node):
    sts = []
    while isinstance(node, ast.Attribute):
        sts.append(node.attr)
        node = node.value
    assert isinstance(node, ast.Name)
    sts = list(reversed(sts))
    return node.id, sts


def _getattr_with_const(self, base_node):
    """
    finds the pattern getattr(mylib, 'const
    """
    if not isinstance(base_node, ast.Call):
        return False
    node = base_node.func
    if not isinstance(node, ast.Call):
        return False
    if not (isinstance(node.func, ast.Name) and node.func.id == "getattr"):
        return False
    if not _is_nested_attribute_and_name(node.args[0]):
        return False
    name, sts = _nested_attribute_and_name(node.args[0])
    if name in self.remapped:
        name = self.remapped[name]
    name = ".".join([name] + sts)
    name = name + "." + node.args[1].value
    self.called[name] += base_node.args
    return True
