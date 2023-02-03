from dataclasses import dataclass
from typing import Dict

from constants import LANGUAGES, LANG_COLUMNS

BBOX_RADIUS = 0.002

@dataclass
class ContactTexts:
    name: str
    short_description: str
    description: str
    resources: str
    base_address: str
    addresses: str
    contact: str

@dataclass
class Contact(ContactTexts):
    geo_coord: str
    image: str

    def __init__(self,
        name: str,
        short_description: str,
        description: str,
        resources: str,
        base_address: str,
        addresses: str,
        contact: str,
        geo_coord: str,
        image: str,
    ) -> None:
        self.name = name
        self.short_description = short_description
        self.description = description
        self.resources = resources
        self.base_address = base_address
        self.addresses = addresses
        self.contact = contact
        self.geo_coord = geo_coord
        self.image = image
        self._prepare_for_html()

        if self.geo_coord:
            # set some fields needed for openstreetmap
            split = self.geo_coord.split(";")
            latitude, longitude = float(split[0]), float(split[1])
            self.geo_marker = f"{latitude:.5f},{longitude:.5f}"
            self.geo_bbox = f"{longitude - BBOX_RADIUS:.5f},{latitude - BBOX_RADIUS:.5f},{longitude + BBOX_RADIUS:.5f},{latitude + BBOX_RADIUS:.5f}"

    def _prepare_for_html(self) -> None:
        self.contact = self.contact.replace('@', '-at-')


@dataclass
class Filter:
    is_group: bool
    is_location: bool
    is_media: bool
    query: str

    @staticmethod
    def from_request(request) -> "Filter":
        return Filter(
            is_group = request.args.get('group') is not None,
            is_location = request.args.get('location') is not None,
            is_media = request.args.get('media') is not None,
            query = request.args.get('query') or "",
        )


@dataclass
class ContactForOrganize:
    texts: Dict[str, ContactTexts]
    """ mapping of language key to texts """
    geo_coord: str
    image: str
    is_group: bool
    is_location: bool
    is_media: bool
    email: str
    state: str
    published: bool
    id: int

    def __init__(self, *args) -> None:
        num_lang_columns = len(LANG_COLUMNS)
        self.texts = {}
        for index, lang in enumerate(LANGUAGES):
            contact_texts = ContactTexts(
                name = args[index * num_lang_columns + 0],
                short_description = args[index * num_lang_columns + 1],
                description = args[index * num_lang_columns + 2],
                resources = args[index * num_lang_columns + 3],
                base_address = args[index * num_lang_columns + 4],
                addresses = args[index * num_lang_columns + 5],
                contact = args[index * num_lang_columns + 6],
            )
            self.texts[lang] = contact_texts
        index_offset = num_lang_columns * len(LANGUAGES)

        self.geo_coord = args[index_offset + 0]
        self.image = args[index_offset + 1]
        self.is_group = args[index_offset + 2]
        self.is_location = args[index_offset + 3]
        self.is_media = args[index_offset + 4]
        self.email = args[index_offset + 5]
        self.state = args[index_offset + 6]
        self.published = args[index_offset + 7]
        self.id = args[index_offset + 8]
