import dependencies # sets sys path for packages (has to be the first line)

import requests
import json

from constants import LANGUAGES


class OSM:
    BASE_NODE_URL = "https://api.openstreetmap.org/api/0.6/node/"

    @staticmethod
    def get_raw_json(node_id: int) -> str | None:
        query = f"{OSM.BASE_NODE_URL}{node_id}.json"
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

    @staticmethod
    def parse(node_json: str) -> dict[str, str | None]:
        parsed_map = {}
        data = json.loads(node_json)
        tags = data["tags"]

        for lang in LANGUAGES:
            parsed = [
                tags.get("opening_hours"),
                tags.get("wheelchair"),
                tags.get(f"wheelchair:description:{lang}")
            ]

            parsed_map[lang] = ". ".join([x for x in parsed if x])

        return parsed_map
