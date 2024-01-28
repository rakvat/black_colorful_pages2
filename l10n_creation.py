import json
from typing import Any


with open('l10n/source.json', 'r', encoding='utf-8') as f:
  data = json.load(f)


LANGUAGES = ["de", "en"]

L = { lang: {} for lang in LANGUAGES }

def build_l10n(d: dict[str, Any], l_paths: dict[str, dict[str, Any]]) -> dict[str, str] | None:
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
