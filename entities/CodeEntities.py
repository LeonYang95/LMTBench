class Method():
    def __init__(self, name, modifiers, text, return_type, params, class_sig):
        self._name = name
        self._modifiers = modifiers
        self._text = text
        self._belonged_class = class_sig
        self._return_type = return_type
        self._parameters = params

    @property
    def signature(self):
        return self.return_type + ' ' + self.belonged_class + '#' + self.name + '(' + ','.join(self.parameters) + ')'

    def __str__(self):
        return self._text

    @property
    def name(self):
        return self._name

    @property
    def modifiers(self):
        return self._modifiers

    @property
    def text(self):
        return self._text

    @property
    def return_type(self):
        return self._return_type

    @property
    def belonged_class(self):
        return self._belonged_class

    @property
    def parameters(self):
        return self._parameters
