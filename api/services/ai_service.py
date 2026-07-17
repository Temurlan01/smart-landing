import logging
from openai import OpenAI
from django.conf import settings
import json

logger = logging.getLogger('api')


class AIService:
    """Сервис для работы с AI (Google Gemini через OpenAI SDK)"""

    _api_disabled = False

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.client = None
        if self.api_key:
            # Ссылка должна заканчиваться строго на /v1beta/openai/
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )

    @classmethod
    def _is_permanent_error(cls, error: Exception) -> bool:
        error_text = str(error).lower()
        permanent_markers = (
            'insufficient_quota',
            'invalid_api_key',
            'incorrect api key',
            'api_key_invalid',
            'error code: 401',
            'error code: 403',
        )
        return any(marker in error_text for marker in permanent_markers)

    @classmethod
    def _handle_api_error(cls, operation: str, error: Exception) -> None:
        if cls._is_permanent_error(error):
            cls._api_disabled = True
            logger.warning(
                f"Ресурсы ИИ отключены ({operation}), далее используется fallback. Причина: {error}"
            )
            return
        logger.error(f"AI {operation} Error: {error}")

    def _extract_json(self, text: str) -> str:
        """
        Надежно находит и вырезает JSON-объект из ответа ИИ,
        игнорируя любые markdown-обертки вроде ```json ... ```
        """
        import re
        # Ищем от первой '{' до последней '}' включая их, захватывая любые переносы строк (\n)
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return match.group(0)
        return text.strip()

    def analyze_sentiment(self, text: str) -> dict:
        """Анализирует тональность комментария"""

        if not self.api_key or not self.client or AIService._api_disabled:
            if not self.api_key:
                logger.warning("OpenAI/Gemini API key not configured")
                print("!!! РАБОТАЕТ FALLBACK (ИИ ОТКЛЮЧЕН ИЛИ НЕТ КЛЮЧА) !!!")
            return self._fallback_sentiment_analysis(text)

        try:
            prompt = f"""Analyze the sentiment of this 
            comment: "{text}"
            
            Respond ONLY with a valid JSON object. Do not include any explanations or markdown.
            
            Example: {{"sentiment": "negative", "score": 0.1, "reasoning": "bad word used"}}
            """
            print(f"--- ОТПРАВЛЯЮ ЗАПРОС В GEMINI. Модель: {self.model} ---")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=150,
            )

            result_text = response.choices[0].message.content
            print(f"--- СЫРОЙ ОТВЕТ ОТ GEMINI: {result_text} ---")
            logger.info(f"AI Sentiment Analysis raw output: {result_text}")

            clean_json = self._extract_json(result_text)
            result = json.loads(clean_json)
            return result

        except Exception as e:
            print(f"!!! ОШИБКА ПРИ ВЫЗОВЕ GEMINI: {e} !!!")
            self._handle_api_error('Sentiment Analysis', e)
            return self._fallback_sentiment_analysis(text)

    def classify_request(self, text: str) -> dict:
        """Классифицирует тип запроса"""

        if not self.api_key or not self.client or AIService._api_disabled:
            if not self.api_key:
                logger.warning("OpenAI/Gemini API key not configured")
            return self._fallback_classification(text)

        try:
            prompt = f"""Determine the type of the following request. Use one of these categories: inquiry, feedback, collaboration, support, other.
            Request: {text}

            Respond in JSON format with keys: type, confidence (0-1), reasoning.
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=150,
            )

            result_text = response.choices[0].message.content
            logger.info(f"AI Classification raw output: {result_text}")

            clean_json = self._extract_json(result_text)
            result = json.loads(clean_json)
            return result

        except Exception as e:
            self._handle_api_error('Classification', e)
            return self._fallback_classification(text)

    def generate_response(self, name: str, comment: str) -> str:
        """Генерирует автоматический ответ на комментарий"""
        if not self.api_key or not self.client or AIService._api_disabled:
            if not self.api_key:
                logger.warning("OpenAI/Gemini API key not configured")
            return self._fallback_response(name)

        try:
            prompt = f"""Generate a professional and friendly response to the following customer inquiry.

            Customer Name: {name}
            Comment: {comment}

            The response should be warm, professional, and address their concern. Keep it to 2-3 sentences.
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=200
            )

            ai_response = response.choices[0].message.content
            logger.info(f"AI Generated Response: {ai_response}")
            return ai_response

        except Exception as e:
            self._handle_api_error('Response Generation', e)
            return self._fallback_response(name)

    def _fallback_sentiment_analysis(self, text: str) -> dict:
        """Fallback анализ тональности без AI"""
        positive_words = [
            'хорошо', 'отлично', 'замечательно', 'супер',
            'прекрасно', 'люблю', 'доволен', 'идеально',
            'спасибо', 'нравится'
        ]
        negative_words = [
            'плохо', 'ужасно', 'отвратительно', 'ненавижу',
            'ошибка', 'проблема', 'сломано', 'бесполезно',
            'недоволен', 'разочарован'
        ]

        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)

        if pos_count > neg_count:
            sentiment = 'positive'
            score = 0.8
        elif neg_count > pos_count:
            sentiment = 'negative'
            score = 0.2
        else:
            sentiment = 'neutral'
            score = 0.5

        return {
            'sentiment': sentiment,
            'score': score,
            'reasoning': 'Резервный анализ (ИИ недоступен)'
        }

    def _fallback_classification(self, text: str) -> dict:
        """Fallback классификация без AI"""
        keywords = {
            'inquiry': [
                'вопрос', 'подскажите', 'как',
                'что', 'можно', 'интересует'
            ],
            'feedback': [
                'отзыв', 'мнение', 'впечатление',
                'оценка', 'понравилось'
            ],
            'collaboration': [
                'сотрудничество', 'партнерство',
                'совместно', 'проект'
            ],
            'support': [
                'проблема', 'ошибка', 'не работает',
                'сломалось', 'помогите'
            ],
        }

        text_lower = text.lower()
        scores = {}

        for category, words in keywords.items():
            score = sum(1 for word in words if word in text_lower)
            scores[category] = score

        if not any(scores.values()):
            return {'type': 'other', 'confidence': 0.5,
                    'reasoning': 'Резервная классификация'}

        request_type = max(scores, key=scores.get)
        return {
            'type': request_type,
            'confidence': 0.6,
            'reasoning': 'Резервный анализ (ИИ недоступен)'
        }

    def _fallback_response(self, name: str) -> str:
        """Fallback ответ без AI"""
        return (
            f"Спасибо, {name}, за ваше обращение! "
            "Мы получили ваше сообщение и свяжемся с вами в ближайшее время."
        )