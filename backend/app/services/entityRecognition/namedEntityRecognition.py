from .providers.gpt import GPT

class EntitiyRecognizer:
    def __init__(self):
        self.inference_provider = GPT()

    def recognize(self, text: str):
        return self.inference_provider.recognize(text)