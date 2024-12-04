import sys

sys.path.extend(['.', '..'])

from hashlib import md5
from entities.AutoProperty import autowired_properties


@autowired_properties
class Field:
    # ==== Attributes ====
    _name = None
    _type = None
    _value = None
    _docstring = None
    _modifier = None

    # ==== Methods ====
    def __init__(self, modifier: str, name: str, type: str, value:[None|str]=None, docstring: [None | str] = None):
        self._modifier = modifier
        self._name = name
        self._type = type
        self._value = value
        self._docstring = docstring

    @property
    def signature(self):
        return self.type + '#' + self.name

    def __str__(self):
        return self.signature

    def __hash__(self):
        return md5(str(self).encode('utf-8')).hexdigest()


@autowired_properties
class Method:
    # ==== Attributes ====
    _name = None
    _modifier = None
    _text = None
    _belonged_class = None
    _return_type = None
    _parameters = None
    _is_constructor = False
    _docstring = None

    # ==== Methods ====
    def __init__(self, name: str, modifier: str, text: str, return_type: str, params: list[Field], class_sig: str,
                 docstring: [None | str] = None):
        self._name = name
        self._modifier = modifier
        self._text = text
        self._belonged_class = class_sig
        self._return_type = return_type
        self._parameters = params
        self._is_constructor = False
        self._docstring = docstring

    def set_constructor(self):
        self._is_constructor = True

    @property
    def signature(self):
        return (
                self.return_type + ' ' +
                self.belonged_class + '#' +
                self.name + '(' +
                ','.join([p.signature for p in self.parameters]) +
                ')'
        )
    def __str__(self):
        return self._text

    def __hash__(self):
        return md5(str(self).encode('utf-8')).hexdigest()


@autowired_properties
class Class:
    # ==== Attributes ====
    _name = None
    _modifier = None
    _text = None
    _methods = {}
    _fields = {}
    _package_name = None
    _docstring = ''
    _imports = []

    # ==== Methods ====
    def __init__(self, package_name:str, name:str, modifier:str, text:str, docstring: [None | str] = None, imports:list[str] = None):
        self._name = name
        self._modifier = modifier
        self._text = text
        self._package_name = package_name
        if docstring:
            self._docstring = docstring
        if imports:
            self._imports = imports

    @property
    def signature(self):
        return self.package_name + '.' + self.name

    def add_method(self, method: Method):
        self._methods[method.signature] = method
        pass

    def add_field(self, field: Field):
        self._fields[field.signature] = field
        pass

    def __str__(self):
        return self.signature

    def __hash__(self):
        return md5(str(self).encode('utf-8')).hexdigest()

    @property
    def public_methods(self):
        return [m for _,m in self.methods.items() if 'public' in m.modifier]

