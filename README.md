# Tempo

Tempo is a local-first web app for turning a technical-paper PDF into an evidence-grounded replication brief. This initial implementation delivers the first vertical slice: upload, asynchronous validation and positioned native-text extraction, original-PDF viewing, one deterministic validated highlight, a small replication brief, and Markdown/JSON exports.

## Run locally

1. Copy `.env.example` to `.env` and adjust the local data directory if needed. No OpenAI key is required for this slice.
2. Start the API:

   ```sh
   cd apps/api
   python -m venv .venv
   .venv/bin/pip install -e '.[dev]'
   .venv/bin/uvicorn tempo.main:app --reload --port 8000
   ```

3. In another terminal, start the web app:

   ```sh
   cd apps/web
   npm install
   npm run dev
   ```

Open http://localhost:3000 and upload a native-text PDF.

For scanned or image-only pages, install the local Tesseract executable before starting the API. On macOS with Homebrew:

```sh
brew install tesseract
```

If OCR is required but Tesseract is unavailable, Tempo reports a safe processing error rather than returning ungrounded text.

## Plan review and intentional scope

The implementation follows Milestone 1 of `IMPLEMENTATION_PLAN.md`, which explicitly calls for the smallest complete vertical slice before OCR, segmentation, real model calls, synthesis, and optional GitHub enrichment. Its deterministic stub derives an evidence quote only from a stored extracted block and renders geometry only produced by the extractor; it never presents model-generated coordinates as evidence.

The plan’s `gpt-6-luna` default is retained in `.env.example`; it is currently supported by the Responses API, including structured outputs. A later real-analysis milestone should add the specified structured-output provider, usage caps, OCR and alignment tests.
