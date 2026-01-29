"""Response humanization for Brazilian Portuguese."""

from typing import Dict, Optional
from datetime import datetime
import random
from app.utils.logger import logger


class Humanizer:
    """Humanize AI responses to sound more natural."""
    
    def __init__(self):
        self.greetings_morning = [
            "Bom dia",
            "Bom dia!",
            "Olá, bom dia"
        ]
        self.greetings_afternoon = [
            "Boa tarde",
            "Boa tarde!",
            "Olá, boa tarde"
        ]
        self.greetings_evening = [
            "Boa noite",
            "Boa noite!",
            "Olá, boa noite"
        ]
        
        self.empathy_phrases = [
            "Fico feliz em ajudar",
            "Entendo perfeitamente",
            "Claro, vou te ajudar",
            "Sem problemas",
            "Por supuesto"
        ]
        
        self.closing_phrases = [
            "Estou à disposição",
            "Qualquer dúvida, é só chamar",
            "Espero ter ajudado",
            "Fico à disposição para mais informações"
        ]
    
    async def humanize(
        self,
        ai_response: str,
        tone: str = "friendly",
        customer_sentiment: Optional[str] = None,
        time_context: Optional[str] = None
    ) -> Dict:
        """Humanize an AI-generated response."""
        try:
            personalization_elements = []
            humanized = ai_response.strip()
            
            # Add greeting based on time
            greeting = self._get_greeting(time_context)
            if greeting:
                humanized = f"{greeting}! {humanized}"
                personalization_elements.append("greeting")
            
            # Add empathy for negative sentiment
            if customer_sentiment == "negative":
                empathy = random.choice(self.empathy_phrases)
                # Insert after greeting
                if greeting:
                    humanized = humanized.replace(
                        f"{greeting}! ",
                        f"{greeting}! {empathy}. "
                    )
                else:
                    humanized = f"{empathy}. {humanized}"
                personalization_elements.append("empathy")
            
            # Adjust tone
            if tone == "friendly":
                humanized = self._make_friendly(humanized)
                personalization_elements.append("friendly_tone")
            elif tone == "formal":
                humanized = self._make_formal(humanized)
                personalization_elements.append("formal_tone")
            
            # Add emoji for friendly tone
            if tone == "friendly" and customer_sentiment != "negative":
                emoji = random.choice(["😊", "👍", "✨"])
                # Add emoji at the end or after greeting
                if "!" in humanized[:20]:
                    humanized = humanized.replace("!", f"! {emoji}", 1)
                else:
                    humanized = f"{humanized} {emoji}"
                personalization_elements.append("emoji")
            
            # Vary sentence structure (simple variation)
            humanized = self._vary_structure(humanized)
            
            # Add closing for longer responses
            if len(humanized) > 100 and tone == "friendly":
                closing = random.choice(self.closing_phrases)
                humanized = f"{humanized}\n\n{closing}!"
                personalization_elements.append("closing")
            
            return {
                "humanized_response": humanized,
                "tone_applied": tone,
                "personalization_elements": personalization_elements
            }
        except Exception as e:
            logger.error(f"Error humanizing response: {e}")
            return {
                "humanized_response": ai_response,
                "tone_applied": tone,
                "personalization_elements": []
            }
    
    def _get_greeting(self, time_context: Optional[str]) -> Optional[str]:
        """Get appropriate greeting based on time."""
        if time_context:
            if time_context == "morning":
                return random.choice(self.greetings_morning)
            elif time_context == "afternoon":
                return random.choice(self.greetings_afternoon)
            elif time_context == "evening":
                return random.choice(self.greetings_evening)
        
        # Auto-detect from current time
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return random.choice(self.greetings_morning)
        elif 12 <= hour < 18:
            return random.choice(self.greetings_afternoon)
        elif 18 <= hour < 24:
            return random.choice(self.greetings_evening)
        
        return None
    
    def _make_friendly(self, text: str) -> str:
        """Make text more friendly."""
        # Replace formal phrases with friendly ones
        replacements = {
            "É necessário": "Precisa",
            "É preciso": "Precisa",
            "Deve-se": "Você pode",
            "Recomenda-se": "Recomendo"
        }
        
        for formal, friendly in replacements.items():
            if formal in text:
                text = text.replace(formal, friendly, 1)
        
        return text
    
    def _make_formal(self, text: str) -> str:
        """Make text more formal."""
        # Replace casual phrases with formal ones
        replacements = {
            "Precisa": "É necessário",
            "Você pode": "É possível",
            "Recomendo": "Recomenda-se"
        }
        
        for casual, formal in replacements.items():
            if casual in text:
                text = text.replace(casual, formal, 1)
        
        return text
    
    def _vary_structure(self, text: str) -> str:
        """Vary sentence structure to avoid repetition."""
        # Simple variation: avoid starting multiple sentences the same way
        sentences = text.split(". ")
        if len(sentences) > 2:
            # Add some variation (simple implementation)
            pass  # Could be enhanced with more sophisticated NLP
        
        return text


# Global instance
humanizer = Humanizer()
