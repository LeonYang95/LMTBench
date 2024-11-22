import os
import subprocess
from sys import stdin

from loguru import logger

compile_error_prefix = "[ERROR] COMPILATION ERROR :"
build_failure_info ='BUILD FAILURE'

def mvn_compile(directory:str):
    # 构建命令
    mvn_command = f"mvn test"

    # 改变到指定目录
    os.chdir(directory)

    # 运行命令
    result = subprocess.run('javac -version', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if '1.8' in result.stderr:
        logger.error('Wrong jdk version: %s' % result.stderr.strip())
        exit(-1)
    result = subprocess.run(mvn_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # 收集输出和错误信息
    stdout = result.stdout
    stderr = result.stderr

    # 检查结果
    compile_result = 'success'
    error_lines = []
    if compile_error_prefix in stdout:
        compile_result = 'compilation failure'
        candidate_lines = stdout.split('\n')
        record = False
        for i in range(len(candidate_lines)):
            line = candidate_lines[i]
            if line.startswith(compile_error_prefix):
                i+=1
                record = True
            if record and line.startswith('[INFO]'):
                tokens = line.strip().split()
                try:
                    assert tokens[-1] == 'errors'
                    assert len(error_lines) == tokens[1]
                    break
                except AssertionError:
                    continue
            if record:
                if line.startswith('[ERROR]'):
                    error_lines.append(line)
                    pass
                pass
            pass
        pass
    return {
        "directory": directory,
        "result": compile_result,
        "stdout": stdout,
        "stderr": stderr,
        'error_lines':error_lines,
    }

def mvn_test(directory:str, test_class:[str|None], test_method:[str|None]):
    # 构建命令
    if test_class and test_method:
        mvn_command = f"mvn clean org.jacoco:jacoco-maven-plugin:prepare-agent test -Dtest={test_class}#{test_method}"
        pass
    else:
        mvn_command = f"mvn clean org.jacoco:jacoco-maven-plugin:prepare-agent test"

    jacoco_report_command = 'mvn org.jacoco:jacoco-maven-plugin:report'
    # 改变到指定目录
    os.chdir(directory)

    # 运行命令
    result = subprocess.run('javac -version', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if '1.8' in result.stderr:
        logger.error('Wrong jdk version: %s' % result.stderr.strip())
        exit(-1)
    result = subprocess.run(mvn_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    _ = subprocess.run(jacoco_report_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # 收集输出和错误信息
    stdout = result.stdout
    stderr = result.stderr

    # 检查结果
    jacoco_report_output = os.path.join(directory, 'target/site/jacoco/jacoco.xml')
    if "BUILD SUCCESS" in stdout:
        assert os.path.exists(jacoco_report_output)
        test_result = "Passed"
    elif "BUILD FAILURE" in stdout or "Tests run:" in stdout and "Failures:" in stdout:
        if not os.path.exists(jacoco_report_output):
            test_result = "Failed Compilation"
            pass
        else:
            test_result = 'Failed Execution'
    else:
        logger.error('Unknown results of mvn test. Please check')
        exit(-1)

    return {
        "directory": directory,
        "test_class": test_class,
        "test_method": test_method,
        "result": test_result,
        "stdout": stdout,
        "stderr": stderr
    }
