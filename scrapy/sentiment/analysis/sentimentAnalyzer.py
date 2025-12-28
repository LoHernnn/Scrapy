import re
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from unidecode import unidecode

import scrapy.config.settings as conf
import scrapy.utils.logger as Logger

class SentimentAnalyzer:
    """Analyze sentiment of tweets mentioning cryptocurrencies using ABSA (Aspect-Based Sentiment Analysis).
    
    Employs a DeBERTa-based transformer model for aspect-level sentiment classification,
    enhanced with domain-specific financial keyword patterns for crypto market terminology.
    Supports multi-entity detection and clause-level sentiment attribution.
    """
    
    def __init__(self):
        """Initialize sentiment analyzer with pre-trained model and financial keyword dictionaries."""
        self.MODEL_NAME = conf.SENTIMENT_MODEL_NAME
        self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_NAME)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.MODEL_NAME)
        self.model.eval()
        self.logger = Logger.get_logger("SentimentAnalyzer")

        self.COMPARATORS = ["while", "but", "whereas", "however", "although", "though"]
        
        self.UNDERPERFORM_PATTERNS = set([
            "sits out", "underperform", "lags behind", "misses rally", "fails to rally", 
            "left behind", "down", "wiped out", "liquidation", "losses", "-$", 
            "traded down", "heavy sells", "nasty discount", "loss", "dump", 
            "liquidations", "forced selling", "tax liabilities", "sell-off", 
            "redemption pressure", "slippage", "market panic", "bankruptcy", 
            "default", "margin call", "price crash", "drawdown", "underwater positions", 
            "capitulation", "whales selling", "debt unwind", "protocol exploit", 
            "rug pull", "hack", "security breach", "bearish", "rejection", "weakness", 
            "falling", "plunge", "collapse", "decline", "downtrend", "blood bath", 
            "support broken", "key level lost", "sell pressure", "trapped longs", 
            "fud", "panic selling", "stop loss hunt", "cascading liquidations", 
            "delisting", "scam", "ponzi", "fraud", "manipulation", "wash trading", 
            "spoofing", "regulatory action", "investigation", "lawsuit", "enforcement", 
            "sanctions", "network congestion", "failed transaction", "chain halt", 
            "validator slashing", "depeg", "bank run", "insolvency", "frozen withdrawals", 
            "trading suspended", "massive outflow", "capital flight", "redemptions", 
            "selling climax", "weak hands", "retail capitulation", "institutional exit", 
            "de-risking", "risk-off", "broken promise", "delayed launch", "vaporware", 
            "ghost chain", "abandoned project", "death spiral", "negative funding", 
            "premium collapse", "exit scam", "honeypot", "token unlock", "exit pump", 
            "sell the news", "rekt", "down bad", "hfsp", "cope", "goblin town", 
            "it's over", "ngmi", "diminishing returns", "exit liquidity", "larp", 
            "stay poor", "bagholder", "poverty", "liquidated", "guuh", "bloody", 
            "bottomless", "slow rug", "paper hands", "📉", "🩸", "💀", "🤮", "🐻", 
            "🥀", "💸", "🆘", "🤡", "🔴", "open short", "shorting", "heavily shorted",
            "forced selling", "capitulation", "liquidated longs","exchange inflows", "depeg" , 
            "exit liquidity", "secondary market discount"
        ])

        self.OUTPERFORM_PATTERNS = set([
            "record highs", "all time high", "up %", "profits", "gains", "surge", "spike", "+$", 
            "market cap has jumped", "demand for", "adoption of", "increased by", "growth in", 
            "record high market cap", "bullish", "strong performance", "positive momentum", 
            "buying pressure", "institutional inflows", "recovery", "price rally", "moon", 
            "market confidence", "liquidity injection", "protocol upgrade", "staking rewards", 
            "airdrops", "yield farming", "increased TVL", "partnership", "strategic investment", 
            "token burn", "network growth", "breakout", "new ath", "parabolic", "explosive growth", 
            "to the moon", "bullish divergence", "golden cross", "support holding", 
            "accumulation", "smart money buying", "whale accumulation", "massive inflow", 
            "record volume", "breakthrough", "milestone reached", "listing announcement", 
            "exchange listing", "tier 1 exchange", "coinbase listing", "binance listing", 
            "institutional adoption", "etf approval", "regulatory clarity", "legal victory", 
            "compliance achieved", "mainnet launch", "beta live", "product release", 
            "ecosystem expansion", "scaling solution", "layer 2 integration", "bridge deployment", 
            "cross chain", "interoperability", "composability", "developer activity", 
            "github commits", "active development", "audit passed", "security enhanced", 
            "deflationary", "buyback", "burn mechanism", "supply shock", "scarcity narrative", 
            "store of value", "digital gold", "inflation hedge", "safe haven", "network effect", 
            "viral growth", "user adoption", "dau increase", "transaction volume surge", 
            "validator growth", "node expansion", "decentralization improving", "hash rate increase", 
            "trading volume spike", "liquidity depth", "tight spread", "market maker activity", 
            "derivatives launch", "futures premium", "perpetual funding positive", 
            "options interest", "institutional grade", "custody solution", "regulatory approved", 
            "compliant infrastructure", "strategic reserve", "treasury allocation", 
            "corporate adoption", "payment integration", "celebrity endorsement", 
            "influencer backing", "media coverage", "trending", "community growth", 
            "engaged holders", "diamond hands", "hodl mentality", "conviction buy", 
            "short squeeze", "price discovery", "wagmi", "lfg", "moon mission", "send it", 
            "up only", "pamp", "generational bottom", "smart money", "frontrunning", 
            "max bidding", "full send", "moonbound", "bull flag", "undervalued", 
            "cheap sats", "chads buying", "printing", "shredding", "beastly", 
            "parabolic move", "blue chip", "🚀", "📈", "💎", "🔥", "🐂", "🌕", 
            "👑", "🤑", "⚡", "🟢", "open long", "longing", "doubled down on longs", 
            "whale accumulation", "institutional buy", "smart money buying", "spot buying", "supply crunch",
            "price rises", "ability to rise", "rotation into",
        ])

    def split_clauses(self, text):
        """Split text into clauses based on comparative conjunctions.
        
        Searches for comparative conjunctions (but, while, however, etc.) and
        splits the text to isolate sentiment for different entities mentioned.
        
        Args:
            text (str): Input text to split
            
        Returns:
            tuple: (left_clause, right_clause) or (full_text, "") if no comparator found
        """
        text_lower = text.lower()
        for c in self.COMPARATORS:
            if f" {c} " in f" {text_lower} ":
                parts = text_lower.split(c, 1)
                return parts[0].strip(), parts[1].strip()
        return text_lower, ""

    def financial_sentiment_adjustment(self, text: str, score: float) -> float:
        """Adjust sentiment score using domain-specific financial keyword patterns.
        
        Applies density-based adjustments using bearish and bullish crypto market terminology.
        Uses square root normalization to prevent short texts from saturating the score.
        
        Args:
            text (str): Text to analyze
            score (float): Base sentiment score from model
            
        Returns:
            float: Adjusted score clamped to [-1.0, 1.0]
        """
        words = text.lower().split()
        word_count = len(words)
        if word_count == 0: return score

        neg_matches = sum(1 for p in self.UNDERPERFORM_PATTERNS if p in text.lower())
        pos_matches = sum(1 for p in self.OUTPERFORM_PATTERNS if p in text.lower())

        neg_density = neg_matches / (word_count ** 0.5)
        pos_density = pos_matches / (word_count ** 0.5)

        adjustment_factor = 0.5 
        score -= (neg_density * adjustment_factor)
        score += (pos_density * adjustment_factor)

        if "-" in text and "$" in text:
            score -= 0.2
            
        return max(min(score, 1.0), -1.0)

    def sentiment_score_for_entity(self, text: str, entity: str) -> float:
        """Calculate aspect-based sentiment score for a specific cryptocurrency entity.
        
        Uses DeBERTa ABSA model to extract entity-specific sentiment from text,
        enhanced with financial keyword adjustments. Handles comparative clauses
        to attribute sentiment correctly when multiple entities are mentioned.
        
        Args:
            text (str): Tweet or text content
            entity (str): Cryptocurrency name/symbol to analyze
            
        Returns:
            float: Sentiment score from -1.0 (very negative) to 1.0 (very positive)
        """
        left, right = self.split_clauses(text)
        clause = left if entity.lower() in left else (right if entity.lower() in right else text)
        
        inputs = self.tokenizer(clause, entity, return_tensors="pt", truncation=True, max_length=128)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)[0]
        
        p_neg = probs[0].item()
        p_pos = probs[2].item()
        p_neu = probs[1].item()
        
        score = (p_pos - p_neg) * (1 - p_neu)

        score = self.financial_sentiment_adjustment(clause, score)
        
        return round(score, 3)
    
    def normalize(self, text: str) -> str:
        """Normalize text by lowercasing, removing URLs, and collapsing whitespace.
        
        Args:
            text (str): Raw text to normalize
            
        Returns:
            str: Normalized text
        """
        text = text.lower()
        text = re.sub(r"(https?://\S+|www\.\S+)", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def detect_crypto_entities(self, text: str, crypto_list: list[str]) -> dict:
        """Detect cryptocurrency mentions and their positions in text.
        
        Performs case-insensitive exact matching with word boundary detection
        to avoid false positives from partial matches.
        
        Args:
            text (str): Text to search
            crypto_list (list[str]): List of cryptocurrency names/symbols to detect
            
        Returns:
            dict: Dictionary mapping detected crypto names to list of position dictionaries
                containing 'start', 'end', and 'text' keys
        """
        found = {}
        text_lower = text.lower()
        normalized_cryptos = {self.normalize(c): c for c in crypto_list}
        
        for crypto_norm, crypto_original in normalized_cryptos.items():
            start = 0
            while True:
                pos = text_lower.find(crypto_norm, start)
                if pos == -1:
                    break
                is_word_boundary_start = pos == 0 or not text_lower[pos-1].isalnum()
                is_word_boundary_end = pos + len(crypto_norm) >= len(text_lower) or not text_lower[pos + len(crypto_norm)].isalnum()
                if is_word_boundary_start and is_word_boundary_end:
                    if crypto_original not in found:
                        found[crypto_original] = []
                    found[crypto_original].append({'start': pos, 'end': pos + len(crypto_norm), 'text': text[pos:pos + len(crypto_norm)]})
                start = pos + 1
        return found

    def analyze_tweet(self, text: str, cryptos: list[str]) -> dict:
        """Analyze sentiment for all cryptocurrency mentions in a tweet.
        
        Detects all crypto entities in the text and calculates individual
        sentiment scores for each one using aspect-based sentiment analysis.
        
        Args:
            text (str): Tweet content to analyze
            cryptos (list[str]): List of cryptocurrency names/symbols to search for
            
        Returns:
            dict: Dictionary mapping crypto names to sentiment scores [-1.0 to 1.0],
                or empty dict if no cryptos detected
        """
        crypto_positions = self.detect_crypto_entities(text, cryptos)
        if not crypto_positions:
            return {}
        
        results = {}
        for entity in crypto_positions.keys():
            results[entity] = self.sentiment_score_for_entity(text, entity)
        return results
