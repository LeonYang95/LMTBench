# LLM4UT
This is a project of LLM-based unit test generation.
For a given Java project, LLM4UT generates unit tests for each **public** method in the project, one test class for each method.

## Program Structure
The program is structured as follows:
- `config` folder contains the configuration file.
- `entities` folder contains some classes that are used to represent the entities in the program.
- `tests` folder contains some tests to verfiy the correctness of some functionalities.
- `utils` folder contains some utility classes that are used in the program.
- `config.py` is responsible for reading config files (.yaml file) into dicts for reference.
- `main.py` is the main entrance of the project.


## Environment Requirements
Please refer to `requirements.txt` file for the necessary packages.

    pip install -r requirements.txt

If the installation failed due to incompatible versions, please directly use 

    pip install <required_package>

where `<required_package>` is the name of the package to be installed.


### Quick Start
1. Copy `config.yaml` as `my_config.yaml`. Please remember the name, as it will be used later in the execution command.
```
cd config
cp config.yaml my_config.yaml
```
2. Open `my_config.yaml`, and change the following configuration settings.
```yaml
base:
  project_home: /path/to/LLM4UT
llm:
  model: "Your Model"
  key: "Empty Key"
  api: "http://link_to.openai_api:server"
  temperature: 1.0
  top_p: 0.95
  max_tokens: 4096
```
3. For debugging, please go to the [utils/Pipeline.py](https://github.com/LeonYang95/LMTBench/blob/aec2f899e8b8eced8dbb654139c69ddea4379a65/utils/Pipeline.py) file, and set the value of `debug` to `True` (line 11). It will only run 2 methods in one class to verify that the script works fine.

4. Run `main.py` with proper parameters following the instruction.
```shell
LLM-based unit test generation.

options:
  -h, --help            show this help message and exit
  --project PROJECT     Project name.
  --project-path PROJECT_PATH
                        Path to the repository code base.
  --config-file CONFIG_FILE
                        Path to the configuration file.
  --source-code-path SOURCE_CODE_PATH
                        Relative path from the project path to the source code. By default, it is set as src/main
  --test-code-path TEST_CODE_PATH
                        Relative path from the project path to the test code. By default, it is set as src/test
  --output-file OUTPUT_FILE
                        Path of the JSONL file to store the generated test classes.
```
4. Find the generated test classes in the `output-file` file.



