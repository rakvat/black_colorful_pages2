import dependencies # sets sys path for packages (has to be the first line)

from babel.dates import format_date, format_time
import requests
from datetime import datetime
from typing import Any, Dict, List, Optional

from constants import LANGUAGES
from l10n.l import L

class Radar:
    BASE_EVENTS_URL = "https://radar.squat.net/api/1.2/search/events.json"
    def __init__(self, group_id: int) -> None:
        self.group_id = group_id

    def get_events(self) -> Dict[str, Optional[str]]:
        events_map = {}
        for lang in LANGUAGES:
            events = self._request(lang)
            if not events:
                # assuming there are not events if we don't get any for the first language
                return {l: None for l in LANGUAGES}
            events_map[lang] = events

        return events_map

    def _query(self, lang:str) -> str:
        return f"{self.BASE_EVENTS_URL}?facets[group][]={self.group_id}&fields=title,date_time,event_status,url&limit=10&language={lang}"

    def _request(self, lang: str) -> Optional[str]:
        query = self._query(lang)
        try:
            response = requests.get(query, timeout=10)
            if response.status_code != 200:
                return None
            result = response.json()["result"]
            if not result:
                return None
            events = result.values()
            confirmed_events = sorted(
                [event for event in events if event["event_status"] == "confirmed"],
                key=lambda event: event["date_time"][0]["value"],
            )
            return self._format_events(lang, confirmed_events)
        except Exception as e:
            print("Failed", e)
            return None

    def _format_events(self, lang: str, events: List[Any]) -> Optional[str]:
        if not events:
            return None
        date_format = "EE, dd. MMM" if lang == 'de' else "EE, MMM dd"
        time_format = "H:mm" if lang == 'de' else "h:mm a"
        event_html = f"<h4>{L[lang]['list']['events_header']}</h4>";

        for event in events:
            event_html += "<p class='radar-event'>";
            start_date = datetime.fromisoformat(event["date_time"][0]["time_start"])
            if (event["date_time"][0]["time_start"] != event["date_time"][0]["time_end"]):
                end_date = datetime.fromisoformat(event["date_time"][0]["time_end"]);
            else:
                end_date = None;

            start_date_string = format_date(start_date, date_format, locale=lang)
            event_html += start_date_string + ' ' + format_time(start_date, time_format, locale=lang)
            if end_date:
                event_html += ' - ';
                end_date_string = format_date(end_date, date_format, locale=lang)
                if end_date_string != start_date_string:
                    event_html += end_date_string + ' ';
                event_html += format_time(end_date, time_format, locale=lang)
            event_html += f" <a href='{event['url']}' target='_blank'>{event['title']}</a>";
            event_html += "</p>";

        return event_html;
