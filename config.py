import os
import yaml

LMTBench_HOME = os.path.join(os.path.dirname(__file__))
with open(os.path.join(LMTBench_HOME,'config/basic_config.yaml'),'r',encoding='utf-8') as reader:
    conf = yaml.load(reader, yaml.FullLoader)
    pass
