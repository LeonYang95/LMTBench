import os
import yaml
import json

LMTBench_HOME = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(LMTBench_HOME,'config/basic_config.yaml'),'r',encoding='utf-8') as reader:
    conf = yaml.load(reader, yaml.FullLoader)
    pass

with open(os.path.join(LMTBench_HOME, "bug_path_mapping.json"), "r") as f:
    content_path = json.load(f)

d4j_project_base = '/Users/yanglin/Documents/Projects/data/defects4j/d4j_projects'
