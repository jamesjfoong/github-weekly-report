from groq import Groq
from ..base import ReportGenerationClient

class GroqClient(ReportGenerationClient):
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)

    def generate_report(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant that generates insightful GitHub activity reports in HTML format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=5000
        )
        return response.choices[0].message.content