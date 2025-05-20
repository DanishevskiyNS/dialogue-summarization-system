import json
import requests
import openai

class SummarizationModule:
    def __init__(self, config):
        self.config = config

        with open(config.prompt_path, "r") as f:
            self.prompt = json.load(f)

        if 'format' in self.prompt:
            self.structured_outputs = True
        else:
            self.structured_outputs = False

    def summarize(self, dialogue: str) -> str:
        """Создаёт общий реферат всей беседы."""
    

class OllamaSummarizer(SummarizationModule):
    def __init__(self, config):
        super().__init__(config)

    def get_promt(self, dialogue: str) -> str:
        prompt = self.prompt.format(DIalogue=dialogue)
        return prompt

    def summarize(self, dialogue: str) -> str:
        if self.structured_outputs:
            summary = self.run_structured_output(dialogue)
        else:
            summary = self.run_general_output(dialogue)
        return summary
    
    def run_structured_output(self, dialogue: str) -> dict:
        payload = {
            "model": self.config.model,
            "prompt": self.get_promt(dialogue),
            "stream": False,
            "format": self.prompt['format'],
            "temperature": self.config.temperature
        }
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(self.config.url, headers=headers, data=json.dumps(payload))
        response = json.loads(response['response'])
        return response['summary']
    
    def run_general_output(self, dialogue: str) -> str:
        payload = {
            "model": self.config.model,
            "prompt": self.get_promt(dialogue),
            "stream": False,
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(self.config.url, headers=headers, data=json.dumps(payload))
        return response['response']


class OpenAISummarizer(SummarizationModule):
    def __init__(self, config):
        super().__init__(config)
        openai.api_key = self.config.api_key

    def get_prompt(self, dialogue: str) -> str:
        return self.prompt.format(DIalogue=dialogue)

    def summarize(self, dialogue: str) -> str:
        if self.structured_outputs:
            return self.run_structured_output(dialogue)
        else:
            return self.run_general_output(dialogue)

    def run_structured_output(self, dialogue: str) -> dict:
        prompt = self.get_prompt(dialogue)

        response = openai.ChatCompletion.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": self.prompt.get("system", "You are a helpful assistant.")},
                {"role": "user", "content": prompt}
            ],
            temperature=self.config.temperature,
            response_format="json"  # если ты используешь функцию structured output с json_mode
        )
        
        return response.choices[0].message["content"]  # предполагается, что ответ — JSON-строка, которую можно распарсить отдельно

    def run_general_output(self, dialogue: str) -> str:
        prompt = self.get_prompt(dialogue)

        response = openai.ChatCompletion.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": self.prompt.get("system", "You are a helpful assistant.")},
                {"role": "user", "content": prompt}
            ],
            temperature=self.config.temperature
        )
        
        return response.choices[0].message["content"]
