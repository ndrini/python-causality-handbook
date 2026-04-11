#!/usr/bin/env python3
"""
TRASH

Notebook Translator - Translates English markdown cells to Italian using Claude API.
Reorganizes notebooks so each English markdown cell is followed by its Italian translation.


"""

import json
import os
import sys
from pathlib import Path
from anthropic import Anthropic

# Initialize Anthropic client
client = Anthropic()

# Conversation history for maintaining context across translations
conversation_history = []

def extract_markdown_cells(notebook_path):
    """Extract markdown cells and their indices from a notebook."""
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    markdown_cells = []
    for i, cell in enumerate(nb['cells']):
        if cell['cell_type'] == 'markdown':
            content = ''.join(cell['source'])
            # Skip cells that are too small (less than 100 chars) or empty
            if len(content.strip()) > 100:
                markdown_cells.append({
                    'index': i,
                    'content': content,
                    'cell': cell
                })

    return markdown_cells

def translate_text(text):
    """Translate text from English to Italian using Claude API with conversation history."""
    global conversation_history

    system_prompt = """You are an expert translator specializing in technical and academic content.
Your task is to translate English text to Italian while:
1. Preserving ALL mathematical formulas and equations exactly as they are (with $ delimiters)
2. Preserving markdown syntax (links, bold, italics, code blocks, etc.)
3. Preserving image references [img](...)
4. Maintaining technical terminology with proper Italian equivalents
5. Keeping the same structure and formatting
6. NOT translating code comments or variable names in code blocks
7. Translating only the actual descriptive text

Output ONLY the translated text, nothing else. No explanations, no preamble."""

    conversation_history.append({
        "role": "user",
        "content": f"Translate this text to Italian:\n\n{text}"
    })

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        system=system_prompt,
        messages=conversation_history
    )

    translated = response.content[0].text
    conversation_history.append({
        "role": "assistant",
        "content": translated
    })

    return translated

def process_notebook(notebook_path):
    """Process a single notebook: translate markdown cells and reorganize."""
    global conversation_history

    print(f"\n{'='*80}")
    print(f"Processing: {notebook_path.name}")
    print(f"{'='*80}")

    # Reset conversation history for each notebook for clarity
    conversation_history = []

    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    markdown_cells = extract_markdown_cells(notebook_path)

    if not markdown_cells:
        print(f"  ⓘ No significant markdown cells to translate")
        return 0

    print(f"  Found {len(markdown_cells)} markdown cells to translate")

    new_cells = []
    translated_count = 0

    for i, cell in enumerate(nb['cells']):
        # Check if this is a markdown cell we need to translate
        is_markdown_to_translate = any(mc['index'] == i for mc in markdown_cells)

        if is_markdown_to_translate:
            # Get the original markdown content
            markdown_cell = next(mc for mc in markdown_cells if mc['index'] == i)
            english_text = markdown_cell['content']

            print(f"  Translating cell {i}...", end=" ", flush=True)

            try:
                italian_text = translate_text(english_text)

                # Create English cell
                cell_en = json.loads(json.dumps(cell))  # Deep copy
                cell_en['source'] = [english_text.rstrip()]
                new_cells.append(cell_en)

                # Create Italian cell
                cell_it = json.loads(json.dumps(cell))  # Deep copy
                cell_it['source'] = [italian_text.lstrip()]
                new_cells.append(cell_it)

                translated_count += 1
                print("✓")
            except Exception as e:
                print(f"✗ Error: {e}")
                # Keep original cell on error
                new_cells.append(cell)
        else:
            # Keep non-markdown cells and small markdown cells as-is
            new_cells.append(cell)

    # Update notebook
    nb['cells'] = new_cells

    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)

    print(f"  ✓ Saved! ({len(nb['cells'])} total cells, {translated_count} translated)")
    return translated_count

def main():
    """Main function - process all notebooks 03-25."""
    notebooks_dir = Path('/mnt/condivisa/workspace/python-causality-handbook/causal-inference-for-the-brave-and-true')

    # Get notebooks 03-25
    notebooks = sorted([f for f in notebooks_dir.glob('*.ipynb')])
    notebooks_to_translate = [
        nb for nb in notebooks
        if any(nb.name.startswith(f'{i:02d}') for i in range(3, 26))
    ]

    print(f"\n🚀 Starting notebook translation")
    print(f"{'='*80}")
    print(f"Notebooks to process: {len(notebooks_to_translate)}")
    print(f"{'='*80}")

    total_translated = 0

    for nb_path in notebooks_to_translate:
        try:
            count = process_notebook(nb_path)
            total_translated += count
        except Exception as e:
            print(f"  ❌ Error processing {nb_path.name}: {e}")

    print(f"\n{'='*80}")
    print(f"✅ Translation complete!")
    print(f"{'='*80}")
    print(f"Total cells translated: {total_translated}")
    print(f"All notebooks have been reorganized with English → Italian pairs.")

if __name__ == '__main__':
    main()
