import sys

sys.path.extend(['.', '..'])
import os
import json
from loguru import logger
from config import content_path, d4j_project_base

NOT_JAVA_FILES = [
    'module-info',
    'package-info.java'
]


def traverse_files(dir_path: str, required_postfix=''):
    """
    This function is used to traverse a directory and return all files with a specified postfix.

    Parameters:
    dir_path (str): The path to the directory to be traversed.
    required_postfix (str): The postfix of the files to be returned. Default is '.java'.

    Returns:
    list: A list of file paths in the directory that end with the required postfix.
          If the required postfix is an empty string, it returns all file paths in the directory.

    Raises:
    FileNotFoundError: If the directory does not exist.
    """
    file_paths = []
    if not os.path.exists(dir_path):
        logger.error(f"Directory {dir_path} does not exist, please check")
        raise FileNotFoundError(f"Directory {dir_path} does not exist, please check")
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if required_postfix != '':
                if any([file.startswith(x) for x in NOT_JAVA_FILES]):
                    continue
                cur_file_path = os.path.join(root, file)
                if cur_file_path.endswith(required_postfix):
                    file_paths.append(cur_file_path)
                else:
                    continue
            else:
                file_paths.append(os.path.join(root, file))

    return file_paths


def read_file_with_UTF8(in_file: str):
    """
    This function is used to read a file with UTF-8 encoding. If the file does not exist, a FileNotFoundError is raised.
    If a UnicodeDecodeError is encountered while reading the file with UTF-8 encoding, it tries to read the file with ISO8859-1 encoding.
    If a UnicodeDecodeError is encountered again, the error is logged and the exception is raised.

    Parameters:
    in_file (str): The path to the input file.

    Returns:
    str: The content of the file if the file exists and no UnicodeDecodeError is encountered.
         If a UnicodeDecodeError is encountered while reading the file with UTF-8 encoding, it tries to return the content of the file with ISO8859-1 encoding.

    Raises:
    FileNotFoundError: If the in_file does not exist.
    UnicodeDecodeError: If a UnicodeDecodeError is encountered while reading the file with both UTF-8 and ISO8859-1 encoding.
    """
    if not os.path.exists(in_file):
        logger.error(f"File {in_file} does not exist, please check")
        raise FileNotFoundError(f"File {in_file} does not exist, please check")
    try:
        with open(in_file, 'r', encoding='utf-8') as reader:
            content = reader.read()
    except UnicodeDecodeError as uee:
        logger.warning(f"File {in_file} failed parsing in UTF-8 encoding, try with ISO8859-1...")
        try:
            with open(in_file, 'r', encoding='ISO8859-1') as reader:
                content = reader.read()
        except UnicodeDecodeError as uee:
            logger.error(f'File {in_file} failed parsing. Unknown Encoding.')
            raise uee
    return content


def write_test_files(target_path: str, content):
    if not os.path.exists(os.path.dirname(target_path)):
        raise FileNotFoundError(f"The folder of {target_path} does not exist.")
    else:
        if os.path.exists(target_path):
            logger.warning(f"Target file exists, override.")
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content)


def load_jsonl_file(in_file: str):
    instances = []
    with open(in_file, 'r', encoding='utf-8') as reader:
        for line in reader.readlines():
            line = line.strip()
            if line == '':
                continue
            instances.append(json.loads(line))
    return instances


def load_jsonl_file_as_dict(file_path) -> dict:
    if not os.path.exists(file_path):
        logger.error(f'Target JSONL file {file_path} does not exist.')
        return {}
    else:
        res = {}
        with open(file_path, 'r', encoding='utf-8') as reader:
            for line in reader.readlines():
                line = line.strip()
                if line == '':
                    continue
                else:
                    d = json.loads(line)
                    res[d['id']] = d
        return res


def write_test_class(bug_id, version, content):
    test_file_dir, test_file_path = _get_test_class_path(bug_id, version)
    if not os.path.exists(test_file_dir):
        os.makedirs(test_file_dir)
    with open(test_file_path, "w", encoding="utf-8") as writer:
        writer.write(content)
    pass


def _get_test_class_path(bug_id, version):
    if content_path[bug_id]["test"][0] != "/":
        test_base = content_path[bug_id]["test"]
    else:
        test_base = content_path[bug_id]["test"][1:]
    test_base_dir = os.path.join(d4j_project_base, bug_id, version, test_base)

    # 单列一个路径，防止影响已有的测试用例
    test_file_dir = os.path.join(str(test_base_dir), 'org/llm')
    res_file_path = os.path.join(str(test_file_dir), "LLMTests.java")
    return test_file_dir, res_file_path
