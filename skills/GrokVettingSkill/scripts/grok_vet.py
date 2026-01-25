import os
import sys
from openai import OpenAI  # Grok API compatible

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),  # Set this env var
    base_url="https://api.x.ai/v1",  # xAI endpoint
)

def vet_query(prompt, model="grok-4-fast-reasoning-latest"):  # Using latest Grok-4 fast reasoning model
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}. Check API key."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python grok_vet.py 'your prompt here'")
        sys.exit(1)
    prompt = sys.argv[1]
    result = vet_query(prompt)
    print(result)
