#!/usr/bin/env python3

import sys
import time
import json
from pathlib import Path
from typing import Dict

import yaml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from openai import OpenAI
from pypdf import PdfReader


WATCHFOLDER = Path("~/Desktop/Inbox").expanduser()
CATEGORY_PROMPT = Path("~/Desktop/Inbox/categories.yaml").expanduser()
FALLBACK_CATEGORY = "uncategorized"

DEBOUNCE_SECONDS = 1.0
LLM_BASE_URL = "http://127.0.0.1:1337/v1" # osaurus listens on a local port. You can change this to hit something online or a different local small model.
LLM_MODEL = "foundation"  # this example uses the local Apple intelligence foundation model
LLM_MAX_TOKENS = 80
MAX_INPUT_CHARS = 8_000
MAX_PDF_PAGES = 10

prompt_intro = ""

llm_client = OpenAI(
    base_url=LLM_BASE_URL,
    api_key="not-needed"
)

def load_category_config(config_path: Path):
    """
    Load a category configuration from a YAML file to be used in constructing the classification prompt.

    The configuration file is expected to contain a top-level key "categories"
    mapping to a dictionary of category names to dictionaries containing a "subject"
    key mapping to a string describing the category.

    For example:

    categories:
      category1:
        subject: "Category 1 description"
      category2:
        subject: "Category 2 description"
    """
    with config_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    toc = data["categories"]

    categories = {
        name: entry["subject"].strip()
        for name, entry in toc.items()
    }

    return categories

def extract_file_text(path: Path) -> str:
    """
    Extract text from a PDF file path.

    If the file is a PDF, it is read using PyPDF2 and the text from the first
    MAX_PDF_PAGES pages is extracted. If the PDF has more than MAX_PDF_PAGES pages,
    a message is printed indicating that only the first MAX_PDF_PAGES pages were
    read.
    """
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(path)
        text = []

        max_pages = min(len(reader.pages), MAX_PDF_PAGES)
        for i in range(max_pages):
            page_text = reader.pages[i].extract_text()
            if page_text:
                text.append(page_text)

        if len(reader.pages) > MAX_PDF_PAGES:
            print(
                f"[INFO] PDF {path.name}: "
                f"reading first {MAX_PDF_PAGES} of {len(reader.pages)} pages"
            )

        return "\n".join(text)

    return path.read_text(encoding="utf-8", errors="ignore")

def build_classification_prompt(filename: str, contents: str, categories: Dict[str, str]) -> str:
    """
    Build a classification prompt to be passed to the LLM.

    The prompt consists of a brief description of the task to be performed,
    a list of the pre-defined categories taken from the yaml file,
    additional rules to guide the decision,
    followed by the document text contents (truncated to MAX_INPUT_CHARS characters).

    The LLM is expected to respond with the name of the single best folder to classify the document into.
    """

    category_block = "\n".join(
        f"- {name}: {desc}"
        for name, desc in categories.items()
    )

    prompt_intro = f"""
You are classifying a document into ONE folder.

Choose the single best folder name from the list below of folder names and descriptions of the kind of content that should go into the folder.
Respond with ONLY the folder name.

Available folders:
{category_block}

Rules:
- Output ONLY a folder name
- No explanations
- No punctuation
- If uncertain, choose the closest match

Filename: {filename}

    """
    print(prompt_intro) # outputs the prompt so you can see what is being sent to the model
    return f"""
{prompt_intro}

Document contents:
{contents}
""".strip()


def classify_document(filename: str, contents: str, categories: Dict[str, str]) -> str:
    """
    Use the local llm to classify a document into a single category.

    filename: The name of the document (e.g. "example.txt")
    contents: The contents of the document as a string
    categories: A dictionary of category names to descriptions
    """
    response = llm_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": build_classification_prompt(filename, contents, categories)}],
        max_tokens=LLM_MAX_TOKENS,
        stream=True,
    )

    result = ""
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            result += chunk.choices[0].delta.content

    return result.strip()

class FileCreatedHandler(FileSystemEventHandler):
    def __init__(
        self,
        watch_folder: Path,
        categories: Dict[str, str],
    ):
        self.watch_folder = watch_folder
        self.categories = categories
        self.last_seen: Dict[Path, float] = {}

    def on_created(self, event):
        """
        Called when a file is created.

        Sebounce the event to prevent over-classification due to multiple file writes.
        Also skip directories and files without extractable text.
        """

        if event.is_directory:
            return

        src_path = Path(event.src_path)
        now = time.time()

        if src_path in self.last_seen and (now - self.last_seen[src_path]) < DEBOUNCE_SECONDS:
            return
        self.last_seen[src_path] = now

        try:
            contents = extract_file_text(src_path)
            if not contents.strip():
                raise ValueError("No extractable text found")
            if len(contents) > MAX_INPUT_CHARS:
              print(f"[INFO] Truncating input for {src_path.name} to {MAX_INPUT_CHARS} characters")
              contents = contents[:MAX_INPUT_CHARS]
        except Exception as e:
            print(f"[WARN] Could not extract text from {src_path.name}: {e}")
            folder = FALLBACK_CATEGORY
        else:
            try:
                folder = classify_document(src_path.name, contents, self.categories)
            except Exception as e:
                print(f"[ERROR] Classification failed: {e}")
                folder = FALLBACK_CATEGORY

        if folder not in self.categories:
            print(f"[WARN] Invalid category '{folder}', using '{FALLBACK_CATEGORY}'")
            folder = FALLBACK_CATEGORY

        print(f"File categorized as: {folder}")

def main(watch_folder: Path, config_file: Path):
    """
    A simple watchdog script that watches a folder for new files and classifies them
    """
    if not watch_folder.exists():
        print(f"Error: watch folder does not exist: {watch_folder}")
        sys.exit(1)

    categories = load_category_config(config_file)

    handler = FileCreatedHandler(
        watch_folder=watch_folder,
        categories=categories,
    )

    observer = Observer()
    observer.schedule(handler, str(watch_folder), recursive=False)
    observer.start()

    print(f"Watching inbox: {watch_folder}")

    print(f"Categories: {', '.join(categories.keys())}")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main(
        WATCHFOLDER,
        CATEGORY_PROMPT
    )
