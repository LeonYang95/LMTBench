import sys

sys.path.extend(['.', '..'])

from hashlib import md5


class Field:
    # ==== Methods ====
    def __init__(self, modifier: str, name: str, type: str, value: [None | str] = None, docstring: [None | str] = None,
                 text: str = ''):
        self._modifier = modifier
        self._name = name
        self._type = type
        self._value = value
        self._docstring = docstring
        self._text = text

    # Properties
    def __str__(self):
        return self.signature

    def __hash__(self):
        return md5(str(self).encode('utf-8')).hexdigest()

    @property
    def short_definition(self):
        ret = self.modifier if self.modifier else ''
        ret += self.type + ' ' + self.name
        if self.value:
            ret += ' = ' + self.value
        return ret

    @property
    def signature(self):
        return self.type + '#' + self.name

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def value(self):
        return self._value

    @property
    def docstring(self):
        return self._docstring

    @property
    def modifier(self):
        return self._modifier

    @property
    def text(self):
        return self._text


class Method:
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

    # Properties and inherited methods
    def __str__(self):
        return self._text

    def __hash__(self):
        return md5(str(self).encode('utf-8')).hexdigest()

    @property
    def short_definition(self):
        return self.modifier + ' ' + self.return_type + ' ' + self.name + '(' + ','.join(
            [p.short_definition for p in self.parameters]) + ');'

    @property
    def signature(self):
        return (
                self.return_type + ' ' +
                self.belonged_class + '#' +
                self.name + '(' +
                ','.join([p.signature for p in self.parameters]) +
                ')'
        )

    @property
    def name(self):
        return self._name

    @property
    def modifier(self):
        return self._modifier

    @property
    def text(self):
        return self._text

    @property
    def belonged_class(self):
        return self._belonged_class

    @property
    def return_type(self):
        return self._return_type

    @property
    def parameters(self):
        return self._parameters

    @property
    def is_constructor(self):
        return self._is_constructor

    @property
    def docstring(self):
        return self._docstring


class Class:
    # ==== Methods ====
    def __init__(self, package_name: str, name: str, modifier: str, text: str, docstring: [None | str] = '',
                 imports: list[str] = None, superclass: str = '', interface: str = ''):
        self._name = name
        self._modifier = modifier
        self._text = text
        self._package_name = package_name
        self._fields = {}
        self._methods = {}
        self._docstring = docstring
        self._imports = imports
        self._superclass = superclass
        self._interface = interface

    def add_method(self, method: Method):
        self._methods[method.signature] = method
        pass

    def add_field(self, field: Field):
        self._fields[field.signature] = field
        pass

    # Property and inherited methods
    def __str__(self):
        return self.signature

    def __hash__(self):
        return md5(str(self).encode('utf-8')).hexdigest()

    @property
    def signature(self):
        return self.package_name + '.' + self.name

    @property
    def public_methods(self):
        return [m for _, m in self.methods.items() if 'public' in m.modifier]

    @property
    def name(self):
        return self._name

    @property
    def modifier(self):
        return self._modifier

    @property
    def text(self):
        return self._text

    @property
    def methods(self):
        return self._methods

    @property
    def fields(self):
        return self._fields

    @property
    def package_name(self):
        return self._package_name

    @property
    def docstring(self):
        return self._docstring

    @property
    def imports(self):
        return self._imports

    @property
    def superclass(self):
        return self._superclass

    @property
    def interface(self):
        return self._interface
