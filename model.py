from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Any, Optional

from constants import LANGUAGES, LANG_COLUMNS

BBOX_RADIUS = 0.002

@dataclass
class ContactTexts:
    name: str
    short_description: Optional[str]
    description: Optional[str]
    resources: Optional[str]
    base_address: Optional[str]
    addresses: Optional[str]
    contact: Optional[str]
    cached_events: Optional[str]

@dataclass
class Contact(ContactTexts):
    geo_coord: str
    radar_group_id: Optional[int] = None
    id: Optional[int] = None

    def __init__(self,
        id: int,
        name: str,
        short_description: Optional[str],
        description: Optional[str],
        resources: Optional[str],
        base_address: Optional[str],
        addresses: Optional[str],
        contact: Optional[str],
        cached_events: Optional[str],
        geo_coord: Optional[str],
        radar_group_id: Optional[int],
    ) -> None:
        self.id = id
        self.name = name
        self.short_description = short_description or ''
        self.description = description or ''
        self.resources = resources or ''
        self.base_address = base_address or ''
        self.addresses = addresses or ''
        self.contact = contact or ''
        self.cached_events = cached_events or ''
        self.geo_coord = geo_coord or ''
        self.radar_group_id = radar_group_id

        if self.geo_coord:
            # set some fields needed for openstreetmap
            split = self.geo_coord.split(";")
            latitude, longitude = float(split[0]), float(split[1])
            self.geo_marker = f"{latitude:.5f},{longitude:.5f}"
            self.geo_bbox = f"{longitude - BBOX_RADIUS:.5f},{latitude - BBOX_RADIUS:.5f},{longitude + BBOX_RADIUS:.5f},{latitude + BBOX_RADIUS:.5f}"


@dataclass
class Filter:
    is_group: bool = False
    is_location: bool = False
    is_media: bool = False
    query: str = ""
    id: Optional[int] = None

    @staticmethod
    def from_request(request) -> "Filter":
        return Filter(
            is_group = request.args.get('group', False),
            is_location = request.args.get('location', False),
            is_media = request.args.get('media', False),
            query = request.args.get('query', ''),
        )

    @staticmethod
    def for_id(id: int) -> "Filter":
        return Filter(id = id)


@dataclass
class ContactForOrganize:
    texts: Dict[str, ContactTexts]
    """ mapping of language key to texts """

    geo_coord: str
    is_group: bool
    is_location: bool
    is_media: bool
    email: str
    state: str
    published: bool
    radar_group_id: Optional[int] = None
    events_cached_at: Optional[datetime] = None
    id: Optional[int] = None

    @staticmethod
    def from_database_row(*args) -> "ContactForOrganize":
        num_lang_columns = len(LANG_COLUMNS)
        texts = {}
        id = args[0]
        for index, lang in enumerate(LANGUAGES):
            contact_texts = ContactTexts(
                name = args[index * num_lang_columns + 1],
                short_description = args[index * num_lang_columns + 2] or '',
                description = args[index * num_lang_columns + 3] or '',
                resources = args[index * num_lang_columns + 4] or '',
                base_address = args[index * num_lang_columns + 5] or '',
                addresses = args[index * num_lang_columns + 6] or '',
                contact = args[index * num_lang_columns + 7] or '',
                cached_events = args[index * num_lang_columns + 8] or '',
            )
            texts[lang] = contact_texts
        index_offset = 1 + num_lang_columns * len(LANGUAGES)

        return ContactForOrganize(
            id = id,
            texts = texts,
            geo_coord = args[index_offset + 0],
            radar_group_id = args[index_offset + 1],
            is_group = args[index_offset + 2],
            is_location = args[index_offset + 3],
            is_media = args[index_offset + 4],
            email = args[index_offset + 5],
            state = args[index_offset + 6],
            published = args[index_offset + 7],
            events_cached_at = args[index_offset + 8],
        )

    @staticmethod
    def from_form_data(data: Dict[str, Any]) -> "ContactForOrganize":
        texts = {}
        for lang in LANGUAGES:
            contact_texts = ContactTexts(
                name = data.get(f"{lang}_name", ""),
                short_description = data.get(f"{lang}_short_description", ""),
                description = data.get(f"{lang}_description", ""),
                resources = data.get(f"{lang}_resources", ""),
                base_address = data.get(f"{lang}_base_address", ""),
                addresses = data.get(f"{lang}_addresses", ""),
                contact = data.get(f"{lang}_contact", ""),
                cached_events = "",
            )
            texts[lang] = contact_texts

        return ContactForOrganize(
            texts = texts,
            geo_coord = data.get("geo_coord", ""),
            is_group = data.get("is_group", False),
            is_location = data.get("is_location", False),
            is_media = data.get("is_media", False),
            email = data.get("email", ""),
            state = data.get("state", ""),
            published = data.get("published", False),
            radar_group_id = data.get("radar_group_id"),
        )

    @staticmethod
    def empty() -> "ContactForOrganize":
        texts = {}
        for lang in LANGUAGES:
            contact_texts = ContactTexts(
                name = "",
                short_description = "",
                description = "",
                resources = "",
                base_address = "",
                addresses = "",
                contact = "",
                cached_events = "",
            )
            texts[lang] = contact_texts

        return ContactForOrganize(
            texts = texts,
            geo_coord = "",
            is_group = False,
            is_location = False,
            is_media = False,
            email = "",
            state = "",
            published = False,
        )
