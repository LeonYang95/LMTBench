import json
import os.path

import javalang.tokenizer
from tqdm import tqdm

if __name__ == '__main__':
    code_base = os.path.join(os.path.dirname(__file__), '..')

    source_ut_file = os.path.join(code_base, 'outputs/all_uts.jsonl')
    source_uts = {}
    with open(source_ut_file, 'r', encoding='utf-8') as reader:
        for line in reader.readlines():
            item = json.loads(line.strip())
            source_uts[item['bug_id']] = item
            pass

    target_ut_file = os.path.join(code_base, 'outputs/defects4j_inputs.jsonl')
    target_uts = []
    with open(target_ut_file, 'r', encoding='utf-8') as reader:
        for line in reader.readlines():
            item = json.loads(line.strip())
            target_uts.append(item)
            pass
    ret = []
    for instance in tqdm(target_uts):
        bug_id = instance['bug_id']
        test_case = instance['test_case']
        target_ut_tokens = set([tok.value for tok in javalang.tokenizer.tokenize(test_case)])
        top_1_sim = 0
        top_1_id = None
        if bug_id not in source_uts:
            pass
        else:
            for key, source_ut in source_uts[bug_id]['uts'].items():
                if source_ut == test_case:
                    continue
                source_ut_tokens = set([tok.value for tok in javalang.tokenizer.tokenize(source_ut)])
                sim = len(target_ut_tokens.intersection(source_ut_tokens)) / len(
                    target_ut_tokens.union(source_ut_tokens))
                if sim > top_1_sim:
                    top_1_sim = sim
                    top_1_id = key
                pass
            pass
        ret.append({
            'sim': top_1_sim,
            'id': top_1_id if top_1_id else ''
        })

    with open(os.path.join(code_base, 'outputs/in_project-bm25-retrieval_results.jsonl'), 'w',
              encoding='utf-8') as writer:
        for r in ret:
            writer.write(json.dumps(r, ensure_ascii=False) + '\n')
    pass
