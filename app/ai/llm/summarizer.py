import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def summarize_article(article):
    text = (article.get("title") or "") + ". " + (article.get("description") or "")
    prompt = f"Summarize in 3 lines this news on financial market:\n\n{text}\n\nSummary:"
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0.7
    )

    return response['choices'][0]['message']['content'].strip()
