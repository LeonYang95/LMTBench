import pickle
from abc import abstractmethod, ABC

from loguru import logger
from openai import OpenAI


class LLM(ABC):
    @abstractmethod
    def get_response(self, messages) -> str:
        pass

    @abstractmethod
    def get_response_with_prefix(self, messages, prefix) -> str:
        pass

    pass


class DeepSeek(LLM):
    def __init__(self, config):
        super().__init__()
        try:
            self.api_key = config['llm']['key']
            self.base_url = config['llm']['api']
            self.temperature = config['llm']['temperature']
            self.top_p = config['llm']['top_p']
            self.max_tokens = config['llm']['max_tokens']
            self.model = config['llm']['model']
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        except Exception:
            logger.error("Error loading configuration: llm.key or llm.api, please check the configuration file.")
            exit(-1)

    def get_response(self, messages):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False,
            temperature=self.temperature,
            top_p=self.top_p,
            max_tokens=self.max_tokens,
        )
        return response.choices[0].message.content

    def get_response_with_prefix(self, messages, prefix='```java\nassertEquals('):
        new_message = pickle.loads(pickle.dumps(messages))
        fim_url = self.base_url + '/beta'
        extend_client = OpenAI(api_key=self.api_key, base_url=fim_url)
        new_message.append({
            'role': 'assistant',
            'content': prefix,
            'prefix': True
        })
        response = extend_client.chat.completions.create(
            model=self.model,
            messages=new_message,
            temperature=self.temperature,
            top_p=self.top_p,
            max_tokens=self.max_tokens,
        )
        return prefix + response.choices[0].message.content
