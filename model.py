from dataclasses import dataclass


@dataclass
class Contact:
    name: str
    short_description: str
    description: str
    resources: str
    base_address: str
    addresses: str
    contact: str
    email: str
    geo_coord: str
    image: str


@dataclass
class Filter:
    is_group: bool
    is_location: bool
    is_media: bool
    query: str | None = None

    @staticmethod
    def from_request(request) -> "Filter":
        return Filter(
            is_group = request.args.get('group') is not None,
            is_location = request.args.get('location') is not None,
            is_media = request.args.get('media') is not None,
            query = request.args.get('query')
        )
