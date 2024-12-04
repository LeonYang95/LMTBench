import sys

sys.path.extend(['.', '..'])
from entities.CodeEntities import Method, Class
from entities.LLM import DeepSeek
from abc import ABC
from config import conf


class AbsGenerator(ABC):
    pass


class BasicGenerator(AbsGenerator):
    _model = DeepSeek(conf)
    predefined_imports = ["import org.junit.Test;",
           "import org.junit.Assert;",
           "import org.junit.Before;",
           "import org.junit.After; ",
           "import static org.junit.Assert.*;",
           "import org.junit.Ignore;",
           "import org.junit.BeforeClass;",
           "import org.junit.AfterClass;",
           "import org.junit.runner.RunWith;",
           "import org.junit.runners.JUnit4;",
           "import org.junit.Rule;",
           "import org.junit.rules.ExpectedException;",
           "import static org.mockito.Mockito.*;",
           "import static org.hamcrest.MatcherAssert.assertThat;",
           "import static org.hamcrest.Matchers.*;",]

    @property
    def model(self):
        return self._model

    def generate(self, **data):
        focal_method_instance = data['method_instance']
        focal_class_instance = data['class_instance']
        messages = [{
            'role': 'user',
            'content': self.base_instruction(focal_method_instance=focal_method_instance,
                                             focal_class_instance=focal_class_instance)
        }]
        prefix = 'Here is the test class that targets at achieving the maximum coverage.\n```java\n'
        prefix += '\n'.join([f"import {imp};" for imp in focal_class_instance.imports])
        prefix += '\n'.join(self.predefined_imports)
        prefix += f"\n\npublic class {focal_class_instance.name}Tests {{\n"
        response = self.model.get_response_with_prefix(messages, prefix)

        return response

    def base_instruction(self, focal_method_instance: Method, focal_class_instance: Class):
        focal_method = str(focal_method_instance)
        focal_method_name = focal_method_instance.name
        focal_method_signature = focal_method_instance.signature
        focal_method_parameters = [p.signature for p in focal_method_instance.parameters]

        focal_class_name = focal_class_instance.name
        focal_class = str(focal_class_instance)
        focal_class_imports = focal_class_instance.imports
        focal_class_fields = list(focal_class_instance.fields.values())
        focal_class_other_methods = [m for m in focal_class_instance.public_methods if
                                     m.signature != focal_method_signature]

        # 使用模型自带的System Prompt

        prompt = "Your Task is to write some unit tests, I will give you some contextual information, and the method you are going to test is at the end of the instruction.\n"
        prompt += '\n```\n'  # Comment style
        prompt += f'// The method is defined in the {focal_class} class, Here are the defined fields and methods in the class:\n'
        prompt += f'public class {focal_class_name} {focal_class_instance.superclass} {focal_class_instance.interface} ' + '{\n'
        fields_str = '\n'.join([f.text for f in focal_class_fields])
        prompt += f'{fields_str}\n'
        focal_class_other_methods_str = '\n'.join([m.short_definition for m in focal_class_other_methods])
        prompt += f'{focal_class_other_methods_str}\n}}\n\n'
        prompt += '// Below is the details of the method you are going to test:\n'
        prompt += f'{focal_method}\n'
        prompt += '\n```\n'  # Comment style
        prompt += "Please write some unit tests in Java 1.7 and JUnit 4 with maximizing both branch and line coverage.\n"

        return prompt
