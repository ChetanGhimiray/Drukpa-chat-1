<<<<<<< HEAD
# Drukpa Chat

Drukpa Chat is a Dzongkha-first chatbot with a live Streamlit dashboard. It combines the first reference's short Qwen/Ollama chat setup and example prompts with the second reference's configurable chat providers, local translation pipeline, error handling, and setup checks. The dashboard adds a service status card, new-chat control, suggested questions, and transcript download.

The dashboard uses the Bhutan building photo and dragon logo supplied with the project. Its cards use solid backgrounds for readable text. Use the **Dark mode** toggle in the sidebar to switch themes.

## Start on Windows

Install Python 3.10 or newer, [Ollama](https://ollama.com/), and then run these commands in PowerShell from this folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
Copy-Item .env.example .env
ollama pull qwen2.5:3b
py download_models.py
py check_setup.py
py -m streamlit run app.py
```

Open the `Local URL` printed in the terminal (usually `http://localhost:8501`). On later starts, activate the environment and run `py -m streamlit run app.py`. `run.bat` is a shortcut after the environment and packages are installed.

The single Dzongkha-English translation checkpoint is about 2.4 GB and needs internet access on first download. It serves both directions. The first answer may take time while the model loads. Ollama runs locally. If it is offline or the configured chat model is missing, the dashboard shows a warning. Setup details are in `.env.example`.

## What is combined

- The Gradio reference used Qwen 2.5 3B through Ollama, local NLLB translation, and example prompts. Its useful low-friction setup and starter questions are represented in this app.
- The Streamlit reference provides a more capable configurable engine: text/script handling, provider fallback, and clear error states. This version replaces the multiple translator choices with one bidirectional Dzongkha-English NLLB checkpoint fine-tuned on a reported corpus of about 225,000 parallel sentences.
- The new dashboard uses a separate Drukpa Chat layout and includes a health indicator, conversation reset, message count, starter prompts, and conversation export.

The default translation pipeline converts Dzongkha to English with the selected [bilingual checkpoint](https://huggingface.co/kinleyrabgay/nllb-200-600M-dzo-eng-300k), asks the configured chat model, then translates back using the same checkpoint. If translation is unavailable or returns the wrong script, the app reports that instead of presenting untranslated text as a correct translation. The model card reports a Dzongkha-English training corpus of about 225,000 parallel sentences. This is a practical Dzongkha-focused choice, not an independent benchmark proving it is universally best. The model card lists a CC-BY-NC 4.0 license; check its terms before reuse.

## Checks

Run the offline unit and UI checks with:

```powershell
py -m pytest -q tests
```

The checks do not require live model calls. Real translation and chat quality still depend on downloading the models and running Ollama.

## Origin and responsible use

This project combines and adapts the two ZIP projects supplied as references. Their backend and translation ideas are acknowledged here; the dashboard, integration, and setup flow are adapted for Drukpa Chat. Get the original authors' permission where required, retain applicable licenses, and disclose your own and adapted contributions for coursework. Do not present another person's work as solely your own.
# Drukpa-chat-1
>>>>>>> a8654303f29fa9a4099c7958f04b56d32513d675
