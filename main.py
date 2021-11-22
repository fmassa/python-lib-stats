import ast
from collections import defaultdict


class Visitor(ast.NodeVisitor):
    def __init__(self, library_name=None):
        super().__init__()
        if library_name is None:
            library_name = ""
        self.library_name = library_name
        self.remapped = {}
        self.called = defaultdict(list)
        self.nets = {}

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
        self.generic_visit(node)
        if _getattr_with_const(self, node):
            return
        func = node.func
        if func in self.nets:
            name = self.nets[func]
            self.called[name] += node.args
        # all other cases are not supported for now

    def visit(self, node):
        if _is_nested_attribute_and_name(node):
            nid, sts = _nested_attribute_and_name(node)
            if nid in self.remapped:
                nid = self.remapped[nid]
            self.nets[node] = ".".join([nid] + sts)
            return
        return super().visit(node)

    def visit_Assign(self, node):
        self.generic_visit(node)
        if not isinstance(node.targets[0], ast.Name):
            return
        name = node.targets[0].id
        if node.value in self.nets:
            new_name = self.nets[node.value]
            self.remapped[name] = new_name

    def report(self):
        print("Imports")
        print(set([x for x in self.remapped.values() if x.startswith(self.library_name)]))
        print("Calls")
        print(set([x for x in self.called.keys() if x.startswith(self.library_name)]))
        print("Attrs")
        print(set([x for x in self.nets.values() if x.startswith(self.library_name)]))


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
    if isinstance(node.args[1], ast.Name):
        v = "{" + node.args[1].id + "}"
    else:
        v = node.args[1].value
    name = name + "." + v
    self.called[name] += base_node.args
    return True
