import sys

from entities.CodeEntities import Method

sys.path.extend(['.', '..'])
import unittest
from entities.AutoProperty import autowired_properties


@autowired_properties
class Person:
    _name = None
    _age = None

    def __init__(self, name="默认姓名", age=0):
        self._name = name
        self._age = age


class TestPrivateAttribute(unittest.TestCase):
    def test_case_1(self):
        p = Person("王五", 0)
        self.assertEqual("王五", p.name)

    def test_case_2(self):
        m = Method(
            name='a',
            modifiers='public',
            text='public void a(){}',
            return_type='void',
            params=[],
            class_sig='com.test',
        )
        self.assertEqual('void com.test#a()', m.signature)


if __name__ == '__main__':
    unittest.main()
