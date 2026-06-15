# PDF Reader + AI Summarizer

Streamlit app that reads PDF files, splits long content into chunks, and generates AI summaries with OpenAI. The app can detect whether a document is in French or English and keep the analysis and summaries in that same language.

## Features

- Upload PDF files from the browser
- Extract and clean PDF text
- Split large documents into token-aware chunks
- Generate `brief`, `detailed`, `bullet_points`, or `executive` summaries
- Analyze document structure
- Extract key quotes
- Export summaries as `.txt` and statistics as `.csv`
- Switch analysis/summary language automatically between French and English

## Requirements

- Python 3.9+
- An OpenAI API key

## Installation

```bash
git clone https://github.com/secksaloumdieng-pixel/PDF_Reader_AISummarizer.git
cd PDF_Reader_AISummarizer
python3 -m pip install -r requirements.txt
```

## Environment

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## Run the app

Use the same Python environment where the dependencies are installed:

```bash
python3 -m streamlit run app.py
```

## Project structure

- `app.py`: Streamlit UI and application flow
- `pdf_processor.py`: PDF extraction, cleaning, token counting, chunking
- `summarizer.py`: OpenAI-based summarization, analysis, and quote extraction
- `utils.py`: UI helpers, exports, API key validation

## Notes

- `.env` is ignored by Git and should never be committed.
- If `tiktoken` needs to download encoding files on first use, make sure your machine has internet access.
