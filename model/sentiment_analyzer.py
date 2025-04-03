from transformers import BertTokenizer, BertForSequenceClassification
import torch

class SentimentAnalyzer:
    def __init__(self):
        self.model_name = "ProsusAI/finbert"
        self.tokenizer = BertTokenizer.from_pretrained(self.model_name)
        self.model = BertForSequenceClassification.from_pretrained(self.model_name)

    def analyze(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)

        with torch.no_grad():
            outputs = self.model(**inputs)

        sentiment_map = {0: "Negative", 1: "Neutral", 2: "Positive"}
        sentiment = sentiment_map[torch.argmax(outputs.logits, dim=1).item()]
        return sentiment
