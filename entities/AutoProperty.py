class PrivateAttribute:
    def __init__(self, name):
        self.private_name = '_' + name  # 对应的私有属性名

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.private_name)


def autowired_properties(cls):
    for name in list(cls.__dict__):
        # 找到所有以单下划线开头的属性，且不是特殊方法
        if name.startswith('_') and not name.startswith('__') and not callable(getattr(cls, name)):
            public_name = name[1:]  # 去掉下划线前缀
            setattr(cls, public_name, PrivateAttribute(public_name))
    return cls


