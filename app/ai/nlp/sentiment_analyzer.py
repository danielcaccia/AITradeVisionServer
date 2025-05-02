import torch
import os

from transformers import BertTokenizer, BertForSequenceClassification
from dotenv import load_dotenv

load_dotenv()

FINBERT_API_KEY = os.getenv("PROSUS_AI_API_KEY")

class SentimentAnalyzer:
    def __init__(self):
        self.model_name = "ProsusAI/finbert"
        self.tokenizer = BertTokenizer.from_pretrained(self.model_name, use_auth_token=FINBERT_API_KEY)
        self.model = BertForSequenceClassification.from_pretrained(self.model_name, use_auth_token=FINBERT_API_KEY)

    def analyze(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)

        with torch.no_grad():
            outputs = self.model(**inputs)

        probs = torch.nn.functional.softmax(outputs.logits, dim=1).squeeze().tolist()

        sentiment_map = {
            0: "negative",
            1: "neutral",
            2: "positive"
        }
        
        max_index = int(torch.argmax(outputs.logits, dim=1).item())
        label = sentiment_map[max_index]

        return {
            "label": label,
            "positive": probs[2],
            "neutral": probs[1],
            "negative": probs[0]
        }
