from dataclasses import dataclass

BBOX_RADIUS = 0.002

@dataclass
class Contact:
    name: str
    short_description: str
    description: str
    resources: str
    base_address: str
    addresses: str
    contact: str
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
        self.description: str = description
        self.resources: str = resources
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
