"""Customer-support bot: answers from a FAQ file.

Modes:
  - Offline (default): keyword-overlap retrieval, no API needed.
  - AI: if ANTHROPIC_API_KEY is set, Claude writes the answer using only the FAQ as context.
Standard library only.
"""
import json
import os
import re
import urllib.request

FAQ_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "faq.json")
FALLBACK = "I'm not sure about that. Reply 'human' and a team member will help you."
STOP = {"the", "a", "an", "is", "are", "do", "i", "my", "your", "you", "what", "how",
        "can", "to", "of", "for", "and", "or", "it", "me", "we", "on", "in", "with"}


def load_faq(path=FAQ_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def tokens(text):
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP}


def best_match(question, faq, min_score=1):
    q = tokens(question)
    scored = [(len(q & tokens(item["q"] + " " + item["a"])), item) for item in faq]
    score, item = max(scored, key=lambda s: s[0])
    return item if score >= min_score else None


def ask_claude(question, faq, api_key, model=None):
    context = "\n".join(f"Q: {i['q']}\nA: {i['a']}" for i in faq)
    body = {
        "model": model or os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5"),
        "max_tokens": 300,
        "system": "You are a store support agent. Answer ONLY from the FAQ below, "
                  "briefly and politely. If the answer is not there, say you are "
                  "not sure and offer a human.\n\n" + context,
        "messages": [{"role": "user", "content": question}],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode(),
        headers={"x-api-key": api_key, "anthropic-version": "2023-06-01",
                 "content-type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["content"][0]["text"].strip()


def answer(question, faq=None):
    faq = faq or load_faq()
    if question.strip().lower() == "human":
        return "Connecting you with a team member. Please share your email."
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        try:
            return ask_claude(question, faq, key)
        except Exception:
            pass  # fall back to offline mode
    item = best_match(question, faq)
    return item["a"] if item else FALLBACK


if __name__ == "__main__":
    print("Support bot ready. Type 'quit' to exit.")
    while True:
        try:
            msg = input("You: ").strip()
        except EOFError:
            break
        if msg.lower() in {"quit", "exit"}:
            break
        if msg:
            print("Bot:", answer(msg))
