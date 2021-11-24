import ast
from collections import defaultdict


class Visitor(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.remapped = {}
        self.called = defaultdict(list)
        self.attrs = {}

        self.import_count = defaultdict(int)
        self.call_count = defaultdict(int)
        self.access_count = defaultdict(int)

    def visit_Import(self, node: ast.AST):
        for n in node.names:
            if n.asname:
                self.remapped[n.asname] = n.name
            else:
                self.remapped[n.name] = n.name
            self.import_count[n.name] += 1

    def visit_ImportFrom(self, node: ast.AST):
        module = node.module
        if module is None:
            module = "{local_import}"
        for n in node.names:
            name = module + '.' + n.name
            if n.asname:
                self.remapped[n.asname] = name
            else:
                self.remapped[n.name] = name

            self.import_count[name] += 1

    def visit_Call(self, node: ast.AST):
        self.generic_visit(node)
        args = node.args
        if _is_getattr_call(node):
            func = node.func.args[0]
            if func in self.attrs:
                name = self.attrs[func]
                n1 = node.func.args[1]
                v = None
                if n1 in self.attrs:
                    v = "{?}"
                elif isinstance(n1, ast.Constant):
                    v = node.func.args[1].value
                if v is None:
                    # print("Unsupported", ast.dump(n1))
                    pass
                else:
                    name = name + "." + v
                    self.called[name] += args
                    self.call_count[name] += 1
                    return

        func = node.func
        if func in self.attrs:
            name = self.attrs[func]
            self.called[name] += args
            self.call_count[name] += 1
        # all other cases are not supported for now

    def visit_Assign(self, node: ast.AST):
        self.generic_visit(node)
        # easy cases
        if not isinstance(node.targets[0], ast.Name):
            return
        name = node.targets[0].id
        if node.value in self.attrs:
            new_name = self.attrs[node.value]
            self.remapped[name] = new_name

    def visit(self, node: ast.AST):
        if _is_nested_attribute_and_name(node):
            nid, sts = _nested_attribute_and_name(node)
            if nid in self.remapped:
                nid = self.remapped[nid]
            self.attrs[node] = ".".join([nid] + sts)
            self.access_count[self.attrs[node]] += 1
            return
        return super().visit(node)


def _is_nested_attribute_and_name(node: ast.AST) -> bool:
    while isinstance(node, ast.Attribute):
        node = node.value
    return isinstance(node, ast.Name)


def _nested_attribute_and_name(node: ast.AST):
    sts = []
    while isinstance(node, ast.Attribute):
        sts.append(node.attr)
        node = node.value
    assert isinstance(node, ast.Name)
    sts = list(reversed(sts))
    return node.id, sts


def _is_getattr_call(base_node: ast.AST) -> bool:
    """
    finds the pattern getattr(mylib, 'const')()
    """
    if not isinstance(base_node, ast.Call):
        return False
    node = base_node.func
    if not isinstance(node, ast.Call):
        return False
    if not (isinstance(node.func, ast.Name) and node.func.id == "getattr"):
        return False
    return True
