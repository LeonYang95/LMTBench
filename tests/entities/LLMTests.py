import sys
sys.path.extend(['.', '..'])

from config import conf

from entities.LLM import DeepSeek
model = DeepSeek(conf)
messages = [{
    'role':'user',
    'content':"Hello World!"
}]
response = model.get_response(messages)
print(response)