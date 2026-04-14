#!/usr/bin/env python3
"""
Script per tradurre notebook da inglese a italiano mantenendo la struttura.
Ogni cella markdown in inglese sarà seguita dalla sua traduzione italiana.
"""

import json
import os
import sys
import copy
from pathlib import Path
import textwrap

try:
    from anthropic import Anthropic
except ImportError:
    print("Errore: libreria anthropic non trovata")
    sys.exit(1)

# Inizializza il client
client = Anthropic()

def extract_markdown_text(cell):
    """Estrae il testo markdown da una cella"""
    if cell['cell_type'] != 'markdown':
        return None
    return ''.join(cell['source'])

def translate_text(text, conversation_history=None):
    """
    Traduce il testo da inglese a italiano usando Claude.
    Mantiene formule matematiche, codice, immagini, link markdown.
    """
    if conversation_history is None:
        conversation_history = []

    system_prompt = """You are an expert translator specializing in technical and academic content.
Your task is to translate English text to Italian while:
1. Preserving ALL mathematical formulas and equations exactly as they are (with $ delimiters)
2. Preserving markdown syntax (links, bold, italics, code blocks, etc.)
3. Preserving image references [img](...)
4. Maintaining technical terminology with proper Italian equivalents
5. Keeping the same structure and formatting
6. NOT translating code comments or variable names in code blocks
7. Translating only the actual descriptive text

Output ONLY the translated text, nothing else."""

    conversation_history.append({
        "role": "user",
        "content": f"Please translate this text to Italian:\n\n{text}"
    })

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4096,
            system=system_prompt,
            messages=conversation_history
        )

        translated = response.content[0].text
        conversation_history.append({
            "role": "assistant",
            "content": translated
        })

        return translated, conversation_history

    except Exception as e:
        print(f"❌ Errore traduzione: {e}")
        return None, conversation_history

def split_markdown_cell(cell, english_text, italian_text):
    """Crea due celle: una con testo inglese, una con italiano"""
    cell1 = copy.deepcopy(cell)
    cell2 = copy.deepcopy(cell)

    cell1['source'] = [english_text.rstrip()]
    cell2['source'] = [italian_text.lstrip()]

    return cell1, cell2

def process_notebook(nb_path, dry_run=False):
    """Processa un notebook e aggiunge le traduzioni"""
    print(f"\n📖 Elaborando: {os.path.basename(nb_path)}")

    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    new_cells = []
    conversation_history = []
    translated_count = 0

    for i, cell in enumerate(nb['cells']):
        if cell['cell_type'] == 'markdown':
            english_text = extract_markdown_text(cell)

            # Evita di ri-tradurre celle già tradotte o troppo corte
            if english_text and len(english_text.strip()) > 50 and "---" not in english_text:
                print(f"  Cella {i}: traduzione in corso...", end=" ", flush=True)

                italian_text, conversation_history = translate_text(
                    english_text,
                    conversation_history
                )

                if italian_text:
                    # Crea due celle: inglese e italiano
                    cell_en, cell_it = split_markdown_cell(cell, english_text, italian_text)
                    new_cells.append(cell_en)
                    new_cells.append(cell_it)
                    translated_count += 1
                    print("✓")
                else:
                    # Se la traduzione fallisce, mantieni la cella originale
                    new_cells.append(cell)
                    print("⚠️ SKIP")
            else:
                # Cella troppo piccola o vuota, mantienila
                new_cells.append(cell)
        else:
            # Code cell o altro, mantieni come è
            new_cells.append(cell)

    if not dry_run:
        nb['cells'] = new_cells
        with open(nb_path, 'w', encoding='utf-8') as f:
            json.dump(nb, f, ensure_ascii=False, indent=2)
        print(f"  ✓ Salvato! ({len(nb['cells'])} celle totali, {translated_count} tradotte)")
    else:
        print(f"  [DRY RUN] Sarebbero {translated_count} celle tradotte")

    return translated_count

def main():
    # Usa percorsi relativi basati sulla posizione dello script per maggiore portabilità
    script_dir = Path(__file__).parent
    notebooks_dir = script_dir / 'causal-inference-for-the-brave-and-true'

    # Notebook da tradurre (03-25)
    notebooks = sorted([f for f in notebooks_dir.glob('*.ipynb')])
    notebooks_to_translate = [
        nb for nb in notebooks
        if any(nb.name.startswith(f'{i:02d}') for i in range(3, 26))
    ]

    print(f"🚀 Avvio traduzione di {len(notebooks_to_translate)} notebook")
    print(f"{'='*80}")

    total_translated = 0

    for nb_path in notebooks_to_translate:
        try:
            count = process_notebook(nb_path)
            total_translated += count
        except Exception as e:
            print(f"  ❌ Errore: {e}")

    print(f"\n{'='*80}")
    print(f"✅ Completato! Tradotte {total_translated} celle markdown")

if __name__ == '__main__':
    main()
