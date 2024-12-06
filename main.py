import sys

sys.path.extend(['.', '..'])

import os
import json
import argparse
from loguru import logger
from utils.Pipeline import static_analyze, generate_unit_tests, post_processing

code_base = os.path.abspath(os.path.dirname(__file__))


def load_arg_params():
    parser = argparse.ArgumentParser(description='LLM-based unit test generation.')
    parser.add_argument('--project', type=str, help='Project name.')
    parser.add_argument('--project-path', type=str, help='Path to the repository code base.',required=True)
    parser.add_argument('--config-file', type=str, default=f"{code_base}/config/basic_config.yaml",
                        help='Path to the configuration file', required=True)
    parser.add_argument('--source-code-path', type=str, default=f"src/main",
                        help='Relative path from the project path to the source code. By default, it is set as src/main')
    parser.add_argument('--test-code-path', type=str, default=f"src/test",
                        help='Relative path from the project path to the test code. By default, it is set as src/test')
    parser.add_argument('--output-file', type=str, default=f"outputs/default.jsonl",
                        help='Path of the JSONL file to store the generated test classes.')
    args = parser.parse_args()
    return args


def record_final_test_classes(results: list[dict], output_file: str):
    output_base = os.path.dirname(output_file)
    if not os.path.exists(output_base):
        os.makedirs(output_base)
    with open(output_file, 'w', encoding='utf-8') as writer:
        for item in results:
            writer.write(json.dumps(item, ensure_ascii=False) + '\n')
    pass


if __name__ == '__main__':
    args = load_arg_params()
    logger.info('==== Received Arguments ====')
    for attr_name in dir(args):
        if attr_name.startswith('_'): continue
        logger.info(f"{attr_name}: {getattr(args, attr_name)}")
    logger.info('==== Received Arguments ====')

    # 进行静态解析，提取待测函数和相关字段内容
    logger.info(f'Start static analysis for {args.project} project. ({args.project_path})')
    classes = static_analyze(code_base=args.project_path, source_code_path=args.source_code_path)
    logger.info(
        f'Found {len(classes)} classes with {sum([len(c.public_methods) for c in classes])} methods in total after static program analysis. Start generating test classes for the methods.')
    # 组装提示词，并且进行大模型调用
    generated_test_classes = generate_unit_tests(classes)
    logger.info('Generation finished, start post processing.')
    # 后处理
    results = post_processing(generated_test_classes)
    record_final_test_classes(results, args.output_file)
    logger.info('All Done')
    pass
