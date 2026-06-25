from google import genai
from google.genai import types
import json
from config import GEMINI_API_KEY

class GeminiLanguageService:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    async def check_essay(self, essay_text: str, topic: str) -> dict:
        prompt = f"""
        You are an expert IELTS and CEFR examiner. Analyze the following essay based on the topic provided.
        Topic: "{topic}"
        Essay: "{essay_text}"
        
        Provide the analysis strictly in JSON format with the following keys. Do not include markdown code block formatting like ```json.
        {{
            "band_score": "Overall IELTS Band score (e.g., 6.5)",
            "grammar_errors": ["List of 3-4 major grammar mistakes found and their corrections"],
            "vocabulary_feedback": "Short feedback on vocabulary usage and suggestions for higher-level synonyms",
            "detailed_feedback": "General feedback on Task Achievement and Coherence"
        }}
        """
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application_json"
                )
            )
            return json.loads(response.text.strip())
        except Exception as e:
            return {
                "band_score": "Nomalum",
                "grammar_errors": [f"Xatolik yuz berdi: {str(e)}"],
                "vocabulary_feedback": "Qayta urining",
                "detailed_feedback": "Xato"
            }