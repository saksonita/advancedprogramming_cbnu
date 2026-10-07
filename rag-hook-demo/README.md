# Why RAG? A hook demo

A tiny web app that asks an LLM the same question twice: once on its own, and once with the cafe's information pasted into the prompt. It shows the core idea of RAG before any chunking, embeddings or vector databases.

## Run it

```bash
pip install -r requirements.txt
cp .env.example .env      # then put your API key in .env
python app.py
```

Open http://127.0.0.1:5000

The app works with any OpenAI-compatible API. `.env.example` has settings for xAI Grok and Groq.

## How to run the demo in class

1. **Model alone.** Ask "Tumbler discount on Friday?" with *Ask model alone*. The model has never seen Bean Bridge Cafe's rules, so it guesses or says it doesn't know. Ask the class: is this answer correct? How would you know?
2. **Model + cafe info.** Ask the same question with *Ask with cafe info*. Now it answers correctly (the discount is Tuesdays only). Open *Show the prompt sent* and point out that nothing about the model changed. We only pasted the right text into the prompt. That is RAG; the rest of the class is about automating this step.
3. **Not in the file.** Ask "Free Wi-Fi?". A grounded answer should say the information doesn't cover it.
4. **Edit live.** Change a rule on the receipt (for example, make the tumbler discount 1,000 won on Fridays) and ask again. The answer follows the text, not the model's memory.
5. **Bridge question.** "This file is five lines. What if the cafe chain has a 300-page manual?" This leads into chunking and retrieval.

## Files

| File | What it does |
|---|---|
| `app.py` | Flask server. `build_messages()` is the one function students should read: it shows the plain prompt vs the augmented prompt. |
| `templates/index.html` | The demo page. |
| `cafe_info.txt` | The cafe's private information (made up, so no model can know it). |
