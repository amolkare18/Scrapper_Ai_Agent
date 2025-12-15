from huggingface_hub import InferenceClient
from helpers.config import HF_API_KEY

client = InferenceClient(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    token=HF_API_KEY
)

def ask_llm(prompt: str, temperature=0.7):
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an expert in Amazon products.explain more why this is a best product value-for-money,and if product price is 0 dont consider it ,tell user that this is not actual value but still give an best suggestion"},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=512
    )
    return response.choices[0].message.content
