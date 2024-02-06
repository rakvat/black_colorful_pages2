import dependencies # sets sys path for packages (has to be the first line)

import requests
import json
import osm_opening_hours_humanized as hoh
from typing import Any

from constants import LANGUAGES
from l10n.l import L


BASE_NODE_URL = "https://api.openstreetmap.org/api/0.6/node/"

def get_raw_osm_json(node_id: int) -> str | None:
    query = f"{BASE_NODE_URL}{node_id}.json"
    try:
        response = requests.get(query, timeout=10)
        if response.status_code != 200:
            return None
        elements = response.json()["elements"]
        if not elements or len(elements) != 1:
            return None
        return json.dumps(elements[0], ensure_ascii=False)
    except Exception as e:
        print("Failed", e)
        return None

def parse_osm_json(node_json: str) -> dict[str, str | None]:
    parsed_map = {}
    data = json.loads(node_json)
    tags = data["tags"]

    for lang in LANGUAGES:
        parsed = [
            _parse_opening_hours(tags, lang),
            _parse_wheelchair(tags, lang),
            _parse_toilets(tags, lang),
            _parse_phone(tags, lang),
        ]

        parsed_map[lang] = "<br/>".join([x for x in parsed if x])

    return parsed_map

def _parse_opening_hours(tags: Any, lang: str) -> str | None:
    field = tags.get("opening_hours")
    if not field:
        return None

    oh = hoh.OHParser(field, locale=lang)

    return f"<strong>{L[lang]['osm']['open']}</strong>: {' '.join(oh.description())}"

def _parse_wheelchair(tags: Any, lang: str) -> str | None:
    value = tags.get("wheelchair")
    if not value:
        return None

    l10n_key = f"wheelchair_access.{value}"
    text = f"<strong>{L[lang]['osm']['wheelchair_access']}</strong>: {L[lang]['osm'][l10n_key]}"

    description = tags.get(f"wheelchair:description:{lang}")
    if description:
        text = f"{text} ({description})"

    return text

def _parse_phone(tags: Any, lang: str) -> str | None:
    value = tags.get("contact:phone")
    if not value:
        return None

    return f"<strong>{L[lang]['osm']['phone']}</strong>: {value}"

def _parse_toilets(tags: Any, lang: str) -> str | None:
    value = tags.get("toilets")
    if not value or value == "no":
        return None

    text = f"<strong>{L[lang]['osm']['toilets']}</strong>: {L[lang]['osm']['yes']}"

    wheelchair_access = tags.get("toilets:wheelchair")
    if wheelchair_access and wheelchair_access == "yes":
        text = f"{text} ({L[lang]['osm']['wheelchair_access']})"

    return text
