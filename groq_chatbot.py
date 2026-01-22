from groq import Groq

class GroqChatbot:
    def __init__(self, api_key, model="llama-3.1-8b-instant"):
        self.client = Groq(api_key=api_key)
        self.model = model

    def get_response(self, prompt: str):
        chat = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}], 
            temperature=0.7
        )
        return chat.choices[0].message.content

