import hashlib
import json
import os
import re
import subprocess
import sys

from loguru import logger
from tqdm import tqdm

sys.path.extend(['.', '..'])
from utils.JavaAnalyzer import extract_assertion_from_response

boolean_expected_value = ['assertTrue', 'assertFalse']
nullable_expected_value = ['assertNull', 'assertNotNull']

if __name__ == '__main__':
    input_file = '/Users/yanglin/Documents/Projects/UTGen_LLM/outputs/first_round_multiple_responses-NaiveGenerator-results.jsonl'
    d4j_project_base = '/Users/yanglin/Documents/Projects/data/defects4j/d4j_projects'

    comparison_file = '/Users/yanglin/Documents/Projects/UTGen_LLM/outputs/defects4j_inputs.jsonl'
    comparison_group = []
    with open(comparison_file, 'r', encoding='utf-8') as reader:
        for line in reader.readlines():
            comparison_group.append(json.loads(line.strip()))
    passed = 0
    total = 0
    corrected = 0
    with open(input_file, 'r', encoding='utf-8') as reader:
        for line in tqdm(reader.readlines()):
            total += 1
            instance = json.loads(line.strip())
            comparison_instance = comparison_group[instance['id']]
            assert hashlib.md5(comparison_instance['focal_method'].encode('utf-8')).hexdigest() == hashlib.md5(
                instance['focal_method'].encode('utf-8')).hexdigest()
            bug_id = comparison_instance['bug_id']
            if bug_id in ['Mockito_18', 'Mockito_1']:
                total -= 1
                continue
            if bug_id!='Csv_14':continue
            test_case_file = comparison_instance['test_file']
            expected_value = instance['expected_value']
            # 替换掉原本的测试断言
            generated_assertion = extract_assertion_from_response(instance['responses'][0])
            is_correct = False
            if expected_value in generated_assertion:
                corrected += 1
                is_correct = True
            if expected_value in boolean_expected_value or expected_value in nullable_expected_value:
                new_test_case = instance['test_prefix'].replace('<AssertionPlaceHolder>', generated_assertion)
            else:
                new_test_case = re.sub('assertEquals\(<expected_value>,.*?\);', generated_assertion,
                                       instance['test_prefix'])
            new_test_class = comparison_instance['test_class']['text'].replace(comparison_instance['test_case'],
                                                                               new_test_case)
            try:
                # write_test_class(bug_id, 'fixed', new_test_class)
                logger.info(f'bug id :{bug_id}')
                with open(test_case_file, 'w', encoding='utf-8') as writer:
                    writer.write(new_test_class)
                os.chdir(os.path.join(d4j_project_base, bug_id, 'fixed'))
                ret = subprocess.run('defects4j test', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                res_output = ret.stdout.decode('utf-8')
                if res_output == 'Failing tests: 0\n':
                    passed += 1
                else:
                    if is_correct:
                        logger.error(f'{bug_id}')
                        print(ret.stderr.decode('utf-8'))
            finally:
                # No matter what, write back the original class.
                # write_test_class(bug_id, 'fixed', comparison_instance['test_class']['text'])
                with open(test_case_file, 'w', encoding='utf-8') as writer:
                    writer.write(comparison_instance['test_class']['text'])

    logger.info(f'Accuracy: {corrected} / {total} = {corrected / total:.2%}')
    logger.info(f'Pass Rate: {passed} / {total} = {passed / total:.2%}')
    pass
