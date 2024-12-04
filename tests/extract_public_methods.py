import os.path
import sys

sys.path.extend(['.', '..'])
from tqdm import tqdm
from loguru import logger
from utils.FileUtils import traverse_files
from utils.JavaAnalyzer import parse_class_object_from_file_content
from utils.TestRunner import mvn_test, mvn_compile

if __name__ == '__main__':
    base = '/Users/yanglin/Documents/Projects/data/UTPairs/jfreechart/src/main/java'
    files = traverse_files(dir_path=base, required_postfix='.java')
    logger.info(f'Found {len(files)} files in {base}')
    methods = []
    for file in tqdm(files, desc='Parsing files'):
        with open(file, 'r', encoding='utf-8') as reader:
            methods.extend(parse_class_object_from_file_content(reader.read(), file))
    logger.info(f'Found {len(methods)} methods in total, start filtering.')
    public_methods = [method for method in methods if 'public' in method.modifiers]
    logger.info(f'Public methods: {len(public_methods)}')
    test_code_base = '/Users/yanglin/Documents/Projects/data/UTPairs/jfreechart/src/test/java'
    project_root = '/Users/yanglin/Documents/Projects/data/UTPairs/jfreechart'
    for method in methods:
        relative_test_file_loc = '/'.join(method.belonged_class.split('.')[:-1]) + '/LLMTests.java'
        print(relative_test_file_loc)
        test_file_loc = os.path.join(test_code_base, relative_test_file_loc)
        # if not os.path.exists(os.path.dirname(test_file_loc))
        with open(test_file_loc, 'w', encoding='utf-8') as writer:
            writer.write(
                'package org.jfree.chart;\nimport org.junit.jupiter.api.Test;\nimport static org.junit.jupiter.api.Assertions.*;\npublic class LLMTests{\n @Test\nvoid testa(){\nassertTrue(true);\n}\n}')
            pass
        test_class = '.'.join(method.belonged_class.split('.')[:-1]) + '.LLMTests'
        test_method = 'testa'
        compilable_results = mvn_compile(directory=project_root)
        if compilable_results['result'] == 'success':
            execution_results = mvn_test(directory=project_root, test_class=test_class, test_method=test_method)
            print(execution_results)
        else:
            logger.info(f'UT for method {method.signature} failed compilation.')
        break
    pass
