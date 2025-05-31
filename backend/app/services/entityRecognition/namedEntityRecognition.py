from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

class NamedEntityRecognition:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("Babelscape/wikineural-multilingual-ner")
        self.model = AutoModelForTokenClassification.from_pretrained("Babelscape/wikineural-multilingual-ner")
        self.nlp = pipeline("ner", model=self.model, tokenizer=self.tokenizer, grouped_entities=True)

    def recognize(self, text: str):
        return self.nlp(text)