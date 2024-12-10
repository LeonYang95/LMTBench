import os
import subprocess
import sys

sys.path.extend(['.', '..'])
from utils.JavaAnalyzer import *


def file_by_sig(method_signature):
    cls_sig = method_signature.split('::')[0]
    sig_tks = cls_sig.split('.')
    pkg_path = os.path.sep.join(sig_tks[:-1])
    cls_path = sig_tks[-1] + '.java'
    return os.path.join(pkg_path, cls_path)


def dir_by_pkg(method_signature):
    cls_sig = method_signature.split('::')[0]
    sig_tks = cls_sig.split('.')
    pkg_path = os.path.sep.join(sig_tks[:-1])
    return pkg_path


if __name__ == '__main__':
    code_base = '/Users/yanglin/Documents/Projects/data/defects4j/d4j_projects/Chart_10/fixed'
    src_dir = 'source'
    test_dir = 'tests'
    cur_dir = os.getcwd()
    os.chdir(code_base)
    res = subprocess.run(f'defects4j export -p tests.trigger', shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    if res.returncode != 0:
        pass
    else:
        bug_trigger_tests = res.stdout.decode('utf-8').strip().split('\n')
        for tc_signature in bug_trigger_tests:
            test_class_file = os.path.join(code_base, test_dir, file_by_sig(tc_signature))

            # in case there is a junit in package
            if 'junit' in tc_signature:
                tc_signature = tc_signature.replace('junit.', '')
                pass

            source_package_dir = os.path.join(code_base, src_dir, dir_by_pkg(tc_signature))
            test_class_name = tc_signature.split('::')[0].split('.')[-1]
            if os.path.exists(test_class_file) and os.path.exists(source_package_dir):
                source_class_file = None
                for entry in os.listdir(source_package_dir):
                    if entry.endswith('.java') and entry.split('.')[0] in test_class_name:
                        source_class_file = os.path.join(source_package_dir, entry)
                        break
                    pass
                if not source_class_file:
                    logger.warning(f'No source class file found for {tc_signature}.')
                    continue
                    pass

                with open(test_class_file, 'r', encoding='utf-8') as reader:
                    test_class = reader.read()
                with open(source_class_file, 'r', encoding='utf-8') as reader:
                    source_class = reader.read()
                tc_invoked_methods = extract_method_invocation(test_class, target_class_name=test_class_name,
                                                               target_method_name=tc_signature.split('::')[-1])
                src_cls_obj = parse_class_object_from_file_content(source_class,
                                                                   source_class_file.split(os.path.sep)[-1].split('.')[
                                                                       0])
                test_cls_obj = parse_class_object_from_file_content(test_class,test_class_name)
                defined_methods = set([m.name for _, m in src_cls_obj.methods.items()])
                intersection_of_methods = tc_invoked_methods.intersection(defined_methods)
                if len(intersection_of_methods) == 1:
                    # 找到了待测函数
                    # 字段：待测函数，包括函数定义和函数体
                    jsondict = {
                        'bug_id':'Chart_10',
                        'version':'fixed',
                        'focal_method_signature': '',
                        'test_case_signature': tc_signature,
                        'test_file': test_class_file,
                        'source_file': source_class_file,
                        'focal_method': '',  # focal method
                        'test_case': '',  # test method
                        'test_class': {
                            'imports': [],  # 引用
                            'fields': [],  # 定义的属性
                            'methods': [],  # 定义的函数
                            'text': ''  # 完整的测试类
                        }

                    }

                pass
            else:
                logger.warning(f'Either {test_class_file} or {source_package_dir} does not exist.')
                continue
                pass
            pass
        pass
    pass
