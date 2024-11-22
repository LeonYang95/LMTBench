import tree_sitter_java as ts_java
from tree_sitter import Parser, Language

from entities.CodeEntities import Method

# Initialize the parser with the Java language
parser = Parser(Language(ts_java.language()))


def get_modifiers(node):
    """
    Extracts the modifiers from a given node.

    Args:
        node (tree_sitter.Node): The node to extract modifiers from.

    Returns:
        list: A list of modifier texts.
    """
    return [n.text for n in node.children if n.type == 'modifiers']


def parse_methods(class_str: str, file_path: [str | None]) -> list:
    tree = parser.parse(bytes(class_str, 'utf-8'))
    methods = []
    class_decl_nodes = [n for n in tree.root_node.children if n.type == 'class_declaration']
    if len(class_decl_nodes) == 0:
        return methods
    package_decl_node = [n for n in tree.root_node.children if n.type == 'package_declaration'][0]
    pkg_name = package_decl_node.text.decode('utf-8')[:-1].split()[-1].strip()
    class_decl_node = class_decl_nodes[0]
    if len(class_decl_nodes) > 1:
        candidates = [n for n in class_decl_nodes if 'public' in get_modifiers(n)]
        if len(candidates) == 0:
            return methods
        else:
            class_decl_node = candidates[0]
    try:
        class_body = class_decl_node.child_by_field_name('body')
        for child in class_body.children:
            if child.type == 'method_declaration':
                modifiers = []
                modifier_node = [n for n in child.children if n.type == 'modifiers']
                for mod in modifier_node:
                    modifiers.extend([m.strip() for m in mod.text.decode('utf-8').split() if m != ''])
                method_text = child.text.decode('utf-8')
                parameters = [n for n in child.child_by_field_name('parameters').children if
                              n.type not in ['(', ')', ',']]
                return_type = child.child_by_field_name('type').text.decode('utf-8')
                methods.append(Method(
                    name=child.child_by_field_name('name').text.decode('utf-8'),
                    modifiers=modifiers,
                    text=method_text,
                    return_type=return_type,
                    params=[p.text.decode('utf-8') for p in parameters],
                    class_sig=pkg_name + '.' + class_decl_node.child_by_field_name('name').text.decode('utf-8')
                ))
        return methods
    except TypeError:
        return methods
