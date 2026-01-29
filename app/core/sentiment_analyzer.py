"""Sentiment analysis using transformers (BERTimbau)."""

from typing import Dict, List
from app.utils.logger import logger

# Optional imports for ML model
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    logger.warning("transformers/torch not installed. Using rule-based sentiment analysis.")


class SentimentAnalyzer:
    """Sentiment analyzer for Brazilian Portuguese."""
    
    def __init__(self):
        self.model_name = "neuralmind/bert-base-portuguese-cased"
        self.tokenizer = None
        self.model = None
        if HAS_TRANSFORMERS:
            try:
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
                self._load_model()
            except Exception as e:
                logger.error(f"Error initializing transformers: {e}")
                self.model = None
        else:
            self.model = None
    
    def _load_model(self):
        """Load the sentiment analysis model."""
        if not HAS_TRANSFORMERS:
            return
        try:
            logger.info(f"Loading sentiment model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name,
                num_labels=3  # positive, neutral, negative
            )
            self.model.to(self.device)
            self.model.eval()
            logger.info("Sentiment model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading sentiment model: {e}")
            # Fallback to simple rule-based approach
            self.model = None
    
    async def analyze(self, text: str, context: str = "general") -> Dict:
        """Analyze sentiment of text."""
        if not text:
            return {
                "sentiment": "neutral",
                "score": 0.0,
                "emotions": [],
                "requires_human": False,
                "urgency_level": "normal"
            }
        
        # Use ML model if available
        if self.model:
            return await self._analyze_with_model(text, context)
        else:
            return await self._analyze_rule_based(text, context)
    
    async def _analyze_with_model(self, text: str, context: str) -> Dict:
        """Analyze using BERT model."""
        try:
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            ).to(self.device)
            
            # Predict
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Get scores
            scores = predictions[0].cpu().numpy()
            negative_score = float(scores[0])
            neutral_score = float(scores[1])
            positive_score = float(scores[2])
            
            # Determine sentiment
            max_idx = scores.argmax()
            sentiment_labels = ["negative", "neutral", "positive"]
            sentiment = sentiment_labels[max_idx]
            
            # Calculate overall score (-1 to 1)
            score = positive_score - negative_score
            
            # Detect emotions and urgency
            emotions = self._detect_emotions(text, sentiment, score)
            requires_human = self._requires_human(sentiment, score, emotions)
            urgency_level = self._get_urgency_level(sentiment, score, emotions)
            
            return {
                "sentiment": sentiment,
                "score": float(score),
                "emotions": emotions,
                "requires_human": requires_human,
                "urgency_level": urgency_level
            }
        except Exception as e:
            logger.error(f"Error in model-based sentiment analysis: {e}")
            return await self._analyze_rule_based(text, context)
    
    async def _analyze_rule_based(self, text: str, context: str) -> Dict:
        """Fallback rule-based sentiment analysis."""
        text_lower = text.lower()
        
        # Negative indicators
        negative_words = [
            "não", "problema", "erro", "ruim", "péssimo", "horrível",
            "absurdo", "reclamação", "insatisfeito", "cancelar",
            "devolver", "reembolso", "processo", "advogado"
        ]
        
        # Positive indicators
        positive_words = [
            "obrigado", "obrigada", "ótimo", "excelente", "perfeito",
            "gostei", "satisfeito", "recomendo", "parabéns"
        ]
        
        # Urgency indicators
        urgency_words = [
            "urgente", "urgência", "imediatamente", "agora",
            "já", "rápido", "emergência"
        ]
        
        # Count matches
        negative_count = sum(1 for word in negative_words if word in text_lower)
        positive_count = sum(1 for word in positive_words if word in text_lower)
        urgency_count = sum(1 for word in urgency_words if word in text_lower)
        
        # Determine sentiment
        if negative_count > positive_count:
            sentiment = "negative"
            score = -0.7 if negative_count > 2 else -0.4
        elif positive_count > negative_count:
            sentiment = "positive"
            score = 0.7 if positive_count > 2 else 0.4
        else:
            sentiment = "neutral"
            score = 0.0
        
        # Detect emotions
        emotions = []
        if "frustrado" in text_lower or "irritado" in text_lower:
            emotions.append("frustrated")
        if "bravo" in text_lower or "raiva" in text_lower:
            emotions.append("angry")
        if urgency_count > 0:
            emotions.append("urgent")
        
        requires_human = sentiment == "negative" and (negative_count > 2 or urgency_count > 0)
        urgency_level = "high" if urgency_count > 0 else ("medium" if negative_count > 1 else "normal")
        
        return {
            "sentiment": sentiment,
            "score": float(score),
            "emotions": emotions,
            "requires_human": requires_human,
            "urgency_level": urgency_level
        }
    
    def _detect_emotions(self, text: str, sentiment: str, score: float) -> List[str]:
        """Detect specific emotions in text."""
        emotions = []
        text_lower = text.lower()
        
        if sentiment == "negative":
            if score < -0.7:
                emotions.append("angry")
            if "frustrado" in text_lower or "esperando" in text_lower:
                emotions.append("frustrated")
            if "urgente" in text_lower or "agora" in text_lower:
                emotions.append("urgent")
        
        return emotions
    
    def _requires_human(self, sentiment: str, score: float, emotions: List[str]) -> bool:
        """Determine if human intervention is required."""
        if sentiment == "negative" and score < -0.6:
            return True
        if "urgent" in emotions:
            return True
        if "angry" in emotions or "frustrated" in emotions:
            return True
        return False
    
    def _get_urgency_level(self, sentiment: str, score: float, emotions: List[str]) -> str:
        """Determine urgency level."""
        if "urgent" in emotions or (sentiment == "negative" and score < -0.8):
            return "high"
        elif sentiment == "negative" and score < -0.5:
            return "medium"
        else:
            return "normal"


# Global instance
sentiment_analyzer = SentimentAnalyzer()
