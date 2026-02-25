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

    system_prompt = """You are a research assistant.
You will be given a question and a set of numbered source passages retrieved from the web.
Your job is to write a clear, fluent answer using ONLY the information in those passages.
Cite sources using their number in brackets, like [1] or [2].
Do not add any information that is not present in the passages.
If the passages do not contain enough information to answer, say so clearly."""

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