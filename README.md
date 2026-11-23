# FAQ Support Bot

A small customer-support bot for online stores. It answers from a FAQ file (`faq.json`).

- **Offline mode:** keyword matching, no API needed.
- **AI mode:** set `ANTHROPIC_API_KEY` and Claude writes answers using only your FAQ, falling back to offline mode on errors.

## Run
    python support_bot.py

## Customize
Edit `faq.json` with the client's questions and answers.

## Extend
Connect `answer()` to WhatsApp, a website chat widget, or Shopify via n8n/Make webhooks.
