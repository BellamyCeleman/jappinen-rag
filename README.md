# Jäppinen RAG — AI Assistant for Field Mechanics

A command-line proof-of-concept that lets field mechanics ask questions about product documentation. Uses Retrieval-Augmented Generation (RAG): relevant passages are retrieved from technical manuals and passed to GPT-4o-mini to generate accurate answers.

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your OpenAI API key

Create a file called `dev.env` in the project root:

```
OPENAI_API_KEY=your-api-key-here
```

### 3. Add the PDF manuals

Place the following PDF files in the `manuals/` directory:

```
manuals/
  LAD-Front-Loading-Service-Manual-L11.pdf
  technical-manual-w11663204-revb.pdf
```

## Usage

Run from the project root:

```bash
python src/main.py
```

On the first run the PDFs are converted to text and indexed into ChromaDB. This may take a moment. On subsequent runs the indexing is skipped automatically.

Then ask questions in the prompt:

```
Ask a question (or 'quit' to exit): How do I replace the door seal?

Answer: ...
```

Type `quit` to exit.

## How it works

1. PDFs are parsed with `pdfplumber`, extracting both plain text and tables
2. Text is split into chunks by page and stored in a local ChromaDB vector database
3. When a question is asked, the most relevant chunks are retrieved and sent as context to GPT-4o-mini
4. The model answers strictly based on the provided documentation
