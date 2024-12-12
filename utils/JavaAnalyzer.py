import tree_sitter_java as ts_java
from loguru import logger
from tree_sitter import Parser, Language, Node

from entities.CodeEntities import Method, Class, Field

# Initialize the parser with the Java language
parser = Parser(Language(ts_java.language()))


def get_modifier(node: Node) -> str:
    return ' '.join([n.text.decode('utf-8') for n in node.children if n.type == 'modifiers'])


def _find_package_name(root_node: Node) -> str:
    # 查找 package 定义
    package_decl_node = next(filter(lambda n: n.type == 'package_declaration', root_node.children))

    if package_decl_node:
        try:
            assert isinstance(package_decl_node, Node)
            assert package_decl_node.child(1).type == 'scoped_identifier'  # 防止 magic number 出错
            pkg_name = package_decl_node.child(1).text.decode('utf-8')
        except AssertionError:
            # just in case.
            logger.error(
                f'Package declaration node is not as expected. Expected: package_declaration, got: {package_decl_node.type}; Expected child type: scoped_identifier, got: {package_decl_node.child(1).type}.')
            pkg_name = ''
        pass
    else:
        pkg_name = ''

    return pkg_name


def _find_class_declaration_node(root_node: Node, target_class_name: [str | None]) -> [None | Node]:
    # 查找目标类定义节点
    class_decl_node = None
    class_decl_nodes = [n for n in root_node.children if n.type == 'class_declaration']
    if target_class_name:
        # 如果有目标类的名字（根据文件名获得），那么根据名字查找，应该只有一个，用 next 获取
        class_decl_node = next(
            filter(lambda n: n.child_by_field_name('name').text.decode('utf-8') == target_class_name, class_decl_nodes),
            None)
    elif len(class_decl_nodes) >= 1:
        # 没有设定目标名字，默认取第一个 public 且非 abstract 的 class node。Interface 是另外的节点定义类型，在过滤 class_declaration 时已经过滤掉了。
        for node in class_decl_nodes:
            modifiers = next(filter(lambda n: n.child.type == 'modifiers', node.children), None)
            if modifiers:
                modifier_text = modifiers.text.decode('utf-8')
                if 'public' in modifier_text and 'abstract' not in modifier_text:
                    class_decl_node = node
                    break

    # 判断是否找到
    if not class_decl_node:
        logger.warning(f'Class declaration not found. Please refer to the debug information for debugging.')
        logger.debug(root_node.text.decode('utf-8'))

    return class_decl_node


def _find_imports(root_node: Node) -> list[str]:
    import_nodes = [n for n in root_node.children if n.type == 'import_declaration']
    return [n.text.decode('utf-8') for n in import_nodes] if import_nodes else []


def method_decl_node_to_method_obj(node: Node, pkg_name: str, class_name: str, ) -> Method:
    """
    Converts a method declaration node to a Method object.

    Args:
        node (Node): The method declaration node.
        pkg_name (str): The package name of the class containing the method.
        class_name (str): The name of the class containing the method.

    Returns:
        Method: An object representing the method.
    """
    docstring = node.prev_sibling.text.decode('utf-8') if node.prev_sibling.type == 'block_comment' else ''
    modifier = get_modifier(node)
    method_text = node.text.decode('utf-8')
    parameter_nodes = [n for n in node.child_by_field_name('parameters').children if n.type not in ['(', ')', ',']]
    parameters = []
    for p in parameter_nodes:
        if p.child_by_field_name('name') and p.child_by_field_name('type'):
            parameters.append(
                Field(
                    name=p.child_by_field_name('name').text.decode('utf-8'),
                    type=p.child_by_field_name('type').text.decode('utf-8'),
                    modifier='',
                    value='',
                    docstring=''
                ))
        else:
            parameters.append(
                Field(
                    name=p.text.decode('utf-8'),
                    type='',
                    modifier='',
                    value='',
                    docstring='',
                    text=p.text.decode('utf-8')
                )
            )

    return_type = node.child_by_field_name('type').text.decode('utf-8')
    return Method(
        name=node.child_by_field_name('name').text.decode('utf-8'),
        modifier=modifier,
        text=method_text,
        return_type=return_type,
        params=parameters,
        class_sig=pkg_name + '.' + class_name,
        docstring=docstring
    )


def field_decl_node_to_field_obj(node: Node) -> [Field | None]:
    """
    Converts a field declaration node to a Field object.

    Args:
        node (Node): The field declaration node.

    Returns:
        Field | None: An object representing the field, or None if no declarator is found.
    """
    docstring = node.prev_sibling.text.decode('utf-8') if node.prev_sibling.type == 'block_comment' else ''
    modifier = get_modifier(node)
    type = node.child_by_field_name('type').text.decode('utf-8')
    declarator = node.child_by_field_name('declarator')
    if declarator:
        name = declarator.child_by_field_name('name').text.decode('utf-8')
        value_node = declarator.child_by_field_name('value')
        value = value_node.text.decode('utf-8') if value_node else ''
        return Field(
            docstring=docstring,
            name=name,
            modifier=modifier,
            type=type,
            value=value,
            text=node.text.decode('utf-8')
        )
    else:
        logger.warning(f"No declarator found for {node.text.decode('utf-8')}")
        return None


def parse_class_object_from_file_content(file_content: str, target_class_name: [str | None]) -> [Class | None]:
    """
    Parses the class object from the given file content.

    Args:
        file_content (str): The content of the file to parse.
        target_class_name (str | None): The name of the target class to find. If None, the first public non-abstract class is used.

    Returns:
        Class | None: An object representing the class, or None if the class declaration is not found.
    """
    tree = parser.parse(bytes(file_content, 'utf-8'))
    pkg_name = _find_package_name(tree.root_node)
    class_decl_node = _find_class_declaration_node(tree.root_node, target_class_name)
    imports = _find_imports(tree.root_node)
    if not class_decl_node:
        return None

    superclass_node = class_decl_node.child_by_field_name('superclass')
    if superclass_node:
        superclass = class_decl_node.child_by_field_name('superclass').text.decode('utf-8')
    else:
        superclass = ''

    super_interface_node = class_decl_node.child_by_field_name('interfaces')
    if super_interface_node:
        interface = class_decl_node.child_by_field_name('interfaces').text.decode('utf-8')
    else:
        interface = ''

    class_obj = Class(
        package_name=pkg_name,
        name=class_decl_node.child_by_field_name('name').text.decode('utf-8'),
        modifier=get_modifier(class_decl_node),
        text=class_decl_node.text.decode('utf-8'),
        imports=imports,
        interface=interface,
        superclass=superclass
    )

    class_body = class_decl_node.child_by_field_name('body')
    for child in class_body.children:
        if child.type == 'method_declaration':
            # 只接受块注释的 docstring
            method_obj = method_decl_node_to_method_obj(child, pkg_name, class_obj.name)
            class_obj.add_method(method_obj)
        elif child.type == 'field_declaration':
            field_obj = field_decl_node_to_field_obj(child)
            if field_obj: class_obj.add_field(field_obj)
            pass

    return class_obj


def _find_invoked_method_names(method_decl_node:Node)-> set[str]:
    invocation_nodes = set()
    query = Language(ts_java.language()).query("(method_invocation name: (_) @name)")
    cand_nodes = query.captures(method_decl_node)
    if 'name' not in cand_nodes:
        return set()
    for node in cand_nodes['name']:
        invocation_nodes.add(node.text.decode('utf-8'))
    return invocation_nodes


def extract_method_invocation(file_content: str, target_class_name: [None | str] = None,
                              target_method_name: [None | str] = None) -> set:
    tree = parser.parse(bytes(file_content, 'utf-8'))
    method_invocations = set()
    cls_decl_node = _find_class_declaration_node(tree.root_node, target_class_name)
    if cls_decl_node:
        cls_body_node = cls_decl_node.child_by_field_name('body')
        for child in cls_body_node.children:
            if child.type == 'method_declaration':
                method_name = child.child_by_field_name('name').text.decode('utf-8')
                if target_method_name and method_name == target_method_name:
                    method_invocations = _find_invoked_method_names(child)
                    break
    return method_invocations
    pass
