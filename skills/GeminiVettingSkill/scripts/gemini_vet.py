import os
import sys
from google import genai

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
)

def vet_query(prompt, model="gemini-2.5-flash"):
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "temperature": 0,
                "max_output_tokens": 1024,
                "tools": [{"google_search": {}}],
            },
        )
        return response.text
    except Exception as e:
        return f"Error: {str(e)}. Check API key."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gemini_vet.py 'your prompt here'")
        sys.exit(1)
    prompt = sys.argv[1]
    result = vet_query(prompt)
    print(result)
