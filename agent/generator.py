# agent/generator.py

import ollama
from config import OLLAMA_MODEL


def build_context(top_passages):
    """
    Format the retrieved passages into a numbered list for the LLM prompt.
    Each entry includes its source URL so the model can cite it.
    """
    lines = []
    for i, p in enumerate(top_passages, 1):
        lines.append(f"[{i}] (Source: {p['url']})\n{p['passage']}")
    return "\n\n".join(lines)


def generate_answer(query, top_passages):
    """
    Send the query and retrieved passages to Ollama.
    The system prompt instructs the model to:
      - Only use information from the provided passages
      - Cite sources using their [number]
      - Be concise but complete
      - Admit when the passages don't contain enough information
    """
    context = build_context(top_passages)

    system_prompt = """You are an expert research assistant. Your job is to answer questions accurately using only the provided source passages.

Rules you must follow:
- Base your answer ONLY on the passages provided. Never add outside knowledge.
- Always cite your sources using [1], [2], etc. after each claim.
- If multiple passages support the same point, cite all of them like [1][3].
- Structure your answer with a direct response first, then supporting details.
- If the passages contradict each other, mention both perspectives.
- If the passages don't contain enough information, say exactly what is missing.
- Keep your answer between 3 and 6 sentences unless the question requires more detail.
"""
    user_prompt = f"""Question: {query}

Retrieved passages:
{context}

Write a well-structured answer based only on the passages above."""

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}
        ]
    )

    return response["message"]["content"]