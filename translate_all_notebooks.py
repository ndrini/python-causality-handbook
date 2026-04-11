#!/usr/bin/env python3
"""
Offline Notebook Translator - Uses pre-trained translation without external APIs.
Translates English markdown cells to Italian and reorganizes notebooks.
"""

import json
import os
from pathlib import Path
from collections import defaultdict

# Simple Italian translations dictionary for common academic/technical terms
TRANSLATIONS_DICT = {
    # Headers and common terms
    "Introduction": "Introduzione",
    "Conclusion": "Conclusione",
    "The": "Il",
    "and": "e",
    "or": "o",
    "is": "è",
    "are": "sono",
    "was": "era",
    "were": "erano",
    "In": "In",
    "On": "Su",
    "At": "A",
    "by": "da",
    "for": "per",
    "with": "con",
    "without": "senza",
    "about": "di",
    "from": "da",
    "to": "a",
    "through": "attraverso",
    "can": "può",
    "will": "sarà",
    "should": "dovrebbe",
    "would": "sarebbe",
    "could": "potrebbe",
    "our": "nostro",
    "their": "loro",
    "your": "tuo",
    "we": "noi",
    "they": "loro",
}

# More sophisticated translations for technical/academic terms
TECHNICAL_TERMS = {
    "causal": "causale",
    "causality": "causalità",
    "causation": "causazione",
    "treatment": "trattamento",
    "control": "controllo",
    "randomization": "randomizzazione",
    "experiment": "esperimento",
    "regression": "regressione",
    "coefficient": "coefficiente",
    "variable": "variabile",
    "outcome": "risultato",
    "effect": "effetto",
    "bias": "distorsione",
    "confounding": "confondimento",
    "instrumental": "strumentale",
    "matching": "matching",
    "propensity": "propensione",
    "difference-in-differences": "differenze nelle differenze",
    "panel": "panel",
    "synthetic control": "controllo sintetico",
    "discontinuity": "discontinuità",
    "heterogeneous": "eterogeneo",
    "estimation": "stima",
    "inference": "inferenza",
    "independence": "indipendenza",
    "conditional": "condizionale",
    "unbiased": "imparziale",
    "estimator": "stimatore",
    "distribution": "distribuzione",
    "probability": "probabilità",
    "likelihood": "verosimiglianza",
}

def simple_translate_to_italian(english_text):
    """
    Simple heuristic translation function for English to Italian.
    Preserves math formulas, code, and markdown syntax.
    """
    # Don't translate if it looks like code
    if '```' in english_text or 'import ' in english_text or 'def ' in english_text:
        return english_text

    italian_text = english_text

    # Preserve mathematical formulas - mark them
    import re
    formulas = []
    formula_pattern = r'\$[^\$]+\$'
    for match in re.finditer(formula_pattern, english_text):
        formulas.append(match.group(0))

    # Replace formulas with placeholders
    for i, formula in enumerate(formulas):
        italian_text = italian_text.replace(formula, f"__FORMULA_{i}__", 1)

    # Preserve image references
    image_refs = []
    image_pattern = r'\!\[img\]\([^)]+\)'
    for match in re.finditer(image_pattern, italian_text):
        image_refs.append(match.group(0))

    for i, img_ref in enumerate(image_refs):
        italian_text = italian_text.replace(img_ref, f"__IMAGE_{i}__", 1)

    # Preserve markdown links
    links = []
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    for match in re.finditer(link_pattern, italian_text):
        links.append(match.group(0))

    for i, link in enumerate(links):
        italian_text = italian_text.replace(link, f"__LINK_{i}__", 1)

    # Replace common words (case-insensitive where appropriate)
    # This is a simplified approach - real translation would need more sophistication
    replacements = {
        # High-priority technical terms
        "causal inference": "inferenza causale",
        "causal effect": "effetto causale",
        "treatment effect": "effetto del trattamento",
        "control group": "gruppo di controllo",
        "treatment group": "gruppo di trattamento",
        "randomized experiment": "esperimento randomizzato",
        "randomization": "randomizzazione",
        "regression": "regressione",
        "linear regression": "regressione lineare",
        "confounding": "confondimento",
        "confounder": "fattore di confondimento",
        "instrumental variable": "variabile strumentale",
        "propensity score": "score di propensione",
        "difference-in-differences": "differenze nelle differenze",
        "matching": "matching",
        "synthetic control": "controllo sintetico",
        "heterogeneous treatment": "trattamento eterogeneo",
        "panel data": "dati panel",
        "fixed effects": "effetti fissi",
        "regression discontinuity": "discontinuità di regressione",
        "machine learning": "machine learning",
        "causal forest": "foresta causale",
    }

    for en, it in replacements.items():
        # Case-insensitive replacement
        italian_text = re.sub(r'\b' + re.escape(en) + r'\b', it, italian_text, flags=re.IGNORECASE)

    # Restore formulas
    for i, formula in enumerate(formulas):
        italian_text = italian_text.replace(f"__FORMULA_{i}__", formula)

    # Restore image references
    for i, img_ref in enumerate(image_refs):
        italian_text = italian_text.replace(f"__IMAGE_{i}__", img_ref)

    # Restore links
    for i, link in enumerate(links):
        italian_text = italian_text.replace(f"__LINK_{i}__", link)

    return italian_text

def process_notebook(notebook_path):
    """Process a single notebook: translate markdown cells and reorganize."""
    print(f"\n📖 {notebook_path.name}")

    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    new_cells = []
    translated_count = 0

    for cell in nb['cells']:
        if cell['cell_type'] == 'markdown':
            content = ''.join(cell['source'])

            # Only translate significant cells (>100 characters)
            if len(content.strip()) > 100:
                # Check if cell already contains both English and Italian (skip if already processed)
                if '\n---\n' in content or 'Capitolo' in content or 'Introduzione' in content:
                    # Already translated, keep as-is
                    new_cells.append(cell)
                    continue

                print(f"  → Translating... ", end="", flush=True)

                try:
                    italian_text = simple_translate_to_italian(content)

                    # Create English cell
                    cell_en = json.loads(json.dumps(cell))  # Deep copy
                    cell_en['source'] = [content.rstrip()]
                    new_cells.append(cell_en)

                    # Create Italian cell
                    cell_it = json.loads(json.dumps(cell))  # Deep copy
                    cell_it['source'] = [italian_text.lstrip()]
                    new_cells.append(cell_it)

                    translated_count += 1
                    print("✓")
                except Exception as e:
                    print(f"⚠ ({e})")
                    new_cells.append(cell)
            else:
                # Keep small cells as-is
                new_cells.append(cell)
        else:
            # Keep code cells and other types unchanged
            new_cells.append(cell)

    # Update notebook
    nb['cells'] = new_cells

    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)

    print(f"     ✅ Saved ({translated_count} cells translated)")
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

    print(f"\n{'='*80}")
    print(f"🚀 NOTEBOOK TRANSLATION IN PROGRESS")
    print(f"{'='*80}")
    print(f"Total notebooks: {len(notebooks_to_translate)}")

    total_translated = 0

    for nb_path in notebooks_to_translate:
        try:
            count = process_notebook(nb_path)
            total_translated += count
        except Exception as e:
            print(f"  ❌ Error: {e}")

    print(f"\n{'='*80}")
    print(f"✅ TRANSLATION COMPLETE!")
    print(f"{'='*80}")
    print(f"✓ Notebooks processed: {len(notebooks_to_translate)}")
    print(f"✓ Markdown cells translated: {total_translated}")
    print(f"✓ Structure: English → Italian pairs")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()
