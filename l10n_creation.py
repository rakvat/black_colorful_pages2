import json
from typing import Dict, Any, Optional


with open('l10n/source.json', 'r', encoding='utf-8') as f:
  data = json.load(f)


LANGUAGES = ["de", "en"]

L = { lang: {} for lang in LANGUAGES }

def build_l10n(d: Dict[str, Any], l_paths: Dict[str, Dict[str, Any]]) -> Optional[Dict[str, str]]:
    for key, value in d.items():
        if isinstance(value, str):
            # assuming all on this layer are of form "lang_code": "translation"
            return d
        else:
            for lang in LANGUAGES:
                l_paths[lang][key] = {}
            results = build_l10n(d[key], {lang: l_paths[lang][key] for lang in LANGUAGES})
            if results:
                for lang in LANGUAGES:
                    l_paths[lang][key] = results[lang]

build_l10n(data, L)

with open(f'l10n/l.py', 'w', encoding='utf-8') as f:
    f.write(f"L={L}")
