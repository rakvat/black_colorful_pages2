from constants import LANGUAGES, LANG_COLUMNS, OTHER_COLUMNS, OTHER_COLUMNS_FULL, OTHER_COLUMNS_FULL_WITHOUT_ID
from model import Contact, ContactForOrganize, Filter
from typing import List, Optional

class DBContact:

    def __init__(self, mysql):
        self.mysql = mysql
        self.table_name = mysql.app.config["TABLE_NAME"]

    def contacts(self, filter: Filter, lang: str) -> List[Contact]:
        cursor = self.mysql.connection.cursor()
        cursor.execute(self._build_query(filter, lang))

        contacts = [Contact(*row) for row in cursor]

        cursor.close()
        return contacts

    def contacts_for_organize(self, filter: Filter) -> List[ContactForOrganize]:
        cursor = self.mysql.connection.cursor()
        cursor.execute(self._build_organize_query(filter))

        contacts = [ContactForOrganize.from_database_row(*row) for row in cursor]

        cursor.close()
        return contacts

    def _build_query(self, filter: Filter, lang: str) -> str:
        lang_colums_select = ", ".join([f"L{name}.{lang} AS {name}" for name in LANG_COLUMNS])
        other_colmuns_select = ", ".join(OTHER_COLUMNS)
        join = " ".join(
            [f"JOIN {self.table_name}_lang L{name} ON L{name}.id = {name}" for name in LANG_COLUMNS]
        )
        return (
            f"""SELECT {lang_colums_select}, {other_colmuns_select}
            FROM {self.table_name} Main {join}
            {self._get_filter_query(filter, lang, only_published=True)}
            ORDER BY name;"""
        )

    def _build_organize_query(self, filter: Filter) -> str:
        lang_colums_select = ", ".join([
            f"L{name}.{lang} AS {name}_{lang}" for lang in LANGUAGES for name in LANG_COLUMNS
        ])
        other_colmuns_select = ", ".join([f"Main.{column}" for column in OTHER_COLUMNS_FULL])
        join = " ".join(
            [f"JOIN {self.table_name}_lang L{name} ON L{name}.id = {name}" for name in LANG_COLUMNS]
        )
        return (
            f"""SELECT {lang_colums_select}, {other_colmuns_select}
            FROM {self.table_name} Main {join}
            {self._get_filter_query(filter, only_published=False)}
            ORDER BY name_en;"""
        )

    def _get_filter_query(self, filter: Filter, lang: Optional[str] = None, only_published: bool = True) -> str:
        filter_items = ["published=TRUE"] if only_published else []
        if filter.is_group:
            filter_items.append("is_group=TRUE")
        if filter.is_location:
            filter_items.append("is_location=TRUE")
        if filter.is_media:
            filter_items.append("is_media=TRUE")
        if filter.query:
            languages = [lang] if lang else LANGUAGES
            like_query = " OR ".join(
                [f"L{name}.{l} LIKE \"%{filter.query}%\"" for name in LANG_COLUMNS for l in languages]
            )
            filter_items.append(f"({like_query})")
        if not filter_items:
            return ""

        return f"WHERE {' AND '.join(filter_items)}"

    def create(self, contact: ContactForOrganize) -> None:
        cursor = self.mysql.connection.cursor()
        # insert language strings into lang table and get the ids
        lang_ids = {}
        for column in LANG_COLUMNS:
            columns = ",".join(LANGUAGES)
            values = ",".join([
                f"'{escape_for_sql(getattr(contact.texts[lang], column))}'" for lang in LANGUAGES
            ])
            insert_query = f"INSERT INTO {self.table_name}_lang({columns}) VALUES ({values});"
            cursor.execute(insert_query)
            cursor.execute("select last_insert_id();")
            self.mysql.connection.commit()
            lang_ids[column] = [row[0] for row in cursor][0]

        # insert into main table
        columns = ",".join([*LANG_COLUMNS, *OTHER_COLUMNS_FULL_WITHOUT_ID])
        raw_values = [lang_ids[column] for column in LANG_COLUMNS]
        raw_values.extend([
            f"'{escape_for_sql(contact.geo_coord)}'",
            f"'{escape_for_sql(contact.image)}'",
            as_sql_bool(contact.is_group),
            as_sql_bool(contact.is_location),
            as_sql_bool(contact.is_media),
            f"'{escape_for_sql(contact.email)}'",
            f"'{escape_for_sql(contact.state)}'",
            as_sql_bool(contact.published),
        ]);
        values = ",".join(map(str, raw_values))
        query = f"INSERT INTO {self.table_name}({columns}) VALUES ({values});"
        cursor.execute(query)
        self.mysql.connection.commit()


def as_sql_bool(value: bool) -> str:
    return "TRUE" if value else "FALSE"

def escape_for_sql(value: str) -> str:
    return value.replace("'", "\\'")
