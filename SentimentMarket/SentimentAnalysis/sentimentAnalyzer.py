import re
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from unidecode import unidecode
from rapidfuzz import fuzz
import conf
import utils.logger as Logger

class SentimentAnalyzer:
    def __init__(self):
        self.MODEL_NAME = conf.SENTIMENT_MODEL_NAME
        self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_NAME)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.MODEL_NAME)
        self.model.eval()
        self.logger = Logger.get_logger("SentimentAnalyzer")


    def find_entity_positions(self, text: str, entities: list[str]) -> list[dict]:
        positions = []
        text_lower = text.lower()
        
        for entity in entities:
            entity_lower = entity.lower()
            start = 0
            while True:
                pos = text_lower.find(entity_lower, start)
                if pos == -1:
                    break
                positions.append({
                    'entity': entity,
                    'start': pos,
                    'end': pos + len(entity),
                    'text': text[pos:pos + len(entity)]
                })
                start = pos + 1
        positions.sort(key=lambda x: x['start'])
        return positions


    def extract_entity_segment(self, text: str, entity_positions: list[dict], target_entity: str) -> str:
        target_pos = None
        target_index = -1
        
        for i, pos in enumerate(entity_positions):
            if pos['entity'] == target_entity:
                target_pos = pos
                target_index = i
                break
        if target_pos is None:
            return text
        start = target_pos['start']
        if target_index + 1 < len(entity_positions):
            end = entity_positions[target_index + 1]['start']
        else:
            end = len(text)
        segment = text[start:end].strip()
        return segment


    def sentiment_score_for_entity(self, text: str, entity: str, entity_positions: list[dict]) -> float:
        segment = self.extract_entity_segment(text, entity_positions, entity)
        inputs = self.tokenizer(
            segment,
            return_tensors="pt",
            truncation=True,
            max_length=128
        )
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)[0]
        p_neg = probs[0].item()
        p_pos = probs[2].item()

        score = p_pos - p_neg

        return round(score, 3)


    def normalize(self, text: str) -> str:
        text = text.lower()
        text = unidecode(text)
        text = re.sub(r"[’']", "", text)        
        text = re.sub(r"[^a-z0-9\s]", " ", text)  
        return text


    def detect_crypto_entities(self,text: str, crypto_list: list[str],fuzzy_threshold: int = 90) -> set[str]:
        normalized_text = self.normalize(text)
        tokens = normalized_text.split()
        found = set()
        normalized_cryptos = {
            self.normalize(c): c for c in crypto_list
        }
        for token in tokens:
            token_base = token[:-1] if token.endswith("s") else token
            for crypto_norm, crypto_original in normalized_cryptos.items():
                if token_base == crypto_norm:
                    found.add(crypto_original)
                    continue
                if fuzz.ratio(token_base, crypto_norm) >= fuzzy_threshold:
                    found.add(crypto_original)
        return found
    
    def analyze_tweet(self, text: str, cryptos: list[str]) -> dict:
        entities = self.detect_crypto_entities(text, cryptos, fuzzy_threshold=conf.FUZZY_MATCH_THRESHOLD)
        if not entities:
            return {}
        entity_list = list(entities)
        entity_positions = self.find_entity_positions(text, entity_list)
        results = {}
        for entity in entities:
            results[entity] = self.sentiment_score_for_entity(text, entity, entity_positions)
        return results

