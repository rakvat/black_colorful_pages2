from model import Contact, Filter
from typing import List

class DBContact:
    LANG_COLUMNS = [
        'name', 'short_description', 'description', 'resources', 'base_address', 'addresses', 'contact'
    ]
    OTHER_COLUMNS = ['geo_coord', 'image']


    def __init__(self, mysql, lang: str):
        self.mysql = mysql
        self.table_name = mysql.app.config["TABLE_NAME"]
        self.lang= lang

    def all_contacts(self, filter: Filter) -> List[Contact]:
        cursor = self.mysql.connection.cursor()
        cursor.execute(self._build_query(filter))

        contacts = [Contact(*row) for row in cursor]

        cursor.close()
        return contacts

    def _build_query(self, filter: Filter) -> str:
        lang_colums_select = ", ".join([f"L{name}.{self.lang} AS {name}" for name in self.LANG_COLUMNS])
        other_colmuns_select = ", ".join(self.OTHER_COLUMNS)
        join = " ".join(
            [f"JOIN {self.table_name}_lang L{name} ON L{name}.id = {name}" for name in self.LANG_COLUMNS]
        )
        return (
            f"""SELECT {lang_colums_select}, {other_colmuns_select}
            FROM {self.table_name} Main {join}
            {self._get_filter_query(filter)}
            ORDER BY name;"""
        )

    def _get_filter_query(self, filter: Filter) -> str:
        filter_query = "WHERE published=TRUE"
        if filter.is_group:
            filter_query = f"{filter_query} AND is_group=TRUE"
        if filter.is_location:
            filter_query = f"{filter_query} AND is_location=TRUE"
        if filter.is_media:
            filter_query = f"{filter_query} AND is_media=TRUE"
        if filter.query:
            like_query = " OR ".join(
                [f"L{name}.{self.lang} LIKE \"%{filter.query}%\"" for name in self.LANG_COLUMNS]
            )
            filter_query = f"{filter_query} AND ({like_query})"

        return filter_query
