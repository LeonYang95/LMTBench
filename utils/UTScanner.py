import hashlib
import os
import subprocess
import sys
import json
import pickle
from tqdm import tqdm
sys.path.extend(['.', '..'])
from utils.JavaAnalyzer import *
from utils.FileUtils import traverse_files

d4j_project_home = '/Users/yanglin/Documents/Projects/data/defects4j/d4j_projects'

def extract_uts(bug_id, paths):
    res = {
        'bug_id':bug_id,
        'uts':{}
    }
    target_project_dir = os.path.join(d4j_project_home, bug_id, 'fixed')
    if not os.path.exists(target_project_dir):
        logger.warning(f'Fixed version of bug id {bug_id} does not exist.')
        return None
    test_dir = paths['test']
    test_file_candidates = traverse_files(os.path.join(target_project_dir, test_dir), '.java')
    for file in tqdm(test_file_candidates, desc=f'{bug_id}'):
        try:
            with open(file, 'r',encoding='utf-8') as reader:
                file_content = reader.read()
            test_class_obj = parse_class_object_from_file_content(file_content)

            if not test_class_obj:
                # logger.warning(f'No valid class found for {file}')
                continue

            if 'TestCase' in test_class_obj.superclass:
                # junit 3, test cases should have a method name start with 'test'
                for sig, method_obj in test_class_obj.methods.items():
                    if method_obj.name.startswith('test'):
                        res['uts'][hashlib.md5(sig.encode('utf-8')).hexdigest()] = pickle.loads(pickle.dumps(method_obj.text))
                        pass
                    pass
                pass
            else:
                # Junit 4, test cases should have an annotation of @Test
                for sig, method_obj in test_class_obj.methods.items():
                    if '@Test' in method_obj.modifier:
                        res['uts'][hashlib.md5(sig.encode('utf-8')).hexdigest()] = pickle.loads(pickle.dumps(method_obj.text))
                        pass
                    pass
                pass
        except UnicodeDecodeError:
            logger.warning(f'{file} failed to read due to encoding issue.')
            continue
            pass
        pass
    return res


if __name__ == '__main__':
    code_base = os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
    with open(os.path.join(code_base,'bug_path_mapping.json'),'r') as r:
        bug_paths = json.load(r)
    output_writer = open(os.path.join(code_base,'outputs/all_uts.jsonl'),'w',encoding='utf-8')
    for bug_id, paths in tqdm(bug_paths.items()):
        jsondict = extract_uts(bug_id, paths)
        if jsondict:
            output_writer.write(json.dumps(jsondict, ensure_ascii=False) + '\n')
    output_writer.close()
    pass
