from ast import AST
from ast import Self

def print_readable_ast(tree, level = 0, inline = False):

    def indent(source_string, level = 1, lstrip_first = False):
        indentation = '    '
        out = '\n'.join((level * indentation) + i for i in source_string.splitlines())
        if lstrip_first:
            return out.lstrip()
        return out

    def is_node(node):
        return isinstance(node, AST) and hasattr(node, 'to_tuple')

    if is_node(tree):
        attrs = tree.to_tuple()
        
        if len(attrs) <= 1:
            print(indent(f'{tree.class_name}()', level, inline))
        else:
            print(indent(f'{tree.class_name}(', level, inline))
            for key, value in attrs:
                if key == 'class_name':
                    continue
                print(indent(key + '=', level + 1), end='')
                print_readable_ast(value, level + 1, True)
            print(indent(')', level))

    elif isinstance(tree, (tuple, list)):
        braces = '()' if isinstance(tree, tuple) else '[]'
        if len(tree) == 0:
            print(braces)
        else:
            print(indent(braces[0], level, inline))
            for obj in tree:
                print_readable_ast(obj, level + 1)
            print(indent(braces[1], level))

    else:
        print(indent(repr(tree), level, inline))
