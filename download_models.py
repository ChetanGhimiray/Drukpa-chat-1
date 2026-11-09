"""Download and test-load the single translation model once, so the app starts
faster later and can run offline.   python download_models.py

Hugging Face caches it (Windows: %USERPROFILE%\\.cache\\huggingface). The model
is about 2.4 GB. It is loaded once for both translation directions.
"""
import gc
import logging

from dzongkha_bot.config import load_settings
from dzongkha_bot.hf_translator import BackendError
from dzongkha_bot.translation_service import build_translation_service

logging.basicConfig(level=logging.INFO, format="%(message)s")
s = load_settings()
service = build_translation_service(s)
if not service.backends:
    raise SystemExit("No Dzongkha translation models are configured.")

for b in service.backends:
    print(f"\n== {b.describe()} ==")
    try:
        b.load()
        print("OK, loaded.")
    except BackendError as e:
        print("FAILED:", e)
    b._model = b._tok = None  # free memory before the next one
    gc.collect()
print("\nDone. Set TRANSLATE_LOCAL_FILES_ONLY=true in .env if you want strictly offline use.")
