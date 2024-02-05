from datetime import datetime, timedelta
from constants import LANGUAGES, LANG_COLUMNS, OTHER_COLUMNS, OTHER_COLUMNS_FULL
from model import Contact, ContactForOrganize, Filter
from typing import Any

class DBContact:

    def __init__(self, mysql):
        self.mysql = mysql
        self.table_name = mysql.app.config["TABLE_NAME"]

    def contacts(self, filter: Filter, lang: str) -> list[Contact]:
        cursor = self.mysql.connection.cursor()
        cursor.execute(self._build_query(filter, lang))

        contacts = [Contact(*row) for row in cursor]

        cursor.close()
        return contacts

    def contacts_for_organize(self, filter: Filter) -> list[ContactForOrganize]:
        cursor = self.mysql.connection.cursor()
        cursor.execute(self._build_organize_query(filter))

        contacts = [ContactForOrganize.from_database_row(*row) for row in cursor]

        cursor.close()
        return contacts

    def _build_query(self, filter: Filter, lang: str) -> str:
        lang_columns_select = ", ".join([f"L{name}.{lang} AS {name}" for name in LANG_COLUMNS])
        other_colmuns_select = ", ".join(OTHER_COLUMNS)
        join = " ".join(
            [f"LEFT JOIN {self.table_name}_lang L{name} ON L{name}.id = {name}" for name in LANG_COLUMNS]
        )
        return (
            f"""SELECT Main.id, {lang_columns_select}, {other_colmuns_select}
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
            [f"LEFT JOIN {self.table_name}_lang L{name} ON L{name}.id = {name}" for name in LANG_COLUMNS]
        )
        return (
            f"""SELECT Main.id, {lang_colums_select}, {other_colmuns_select}
            FROM {self.table_name} Main {join}
            {self._get_filter_query(filter, only_published=False)}
            ORDER BY name_en;"""
        )

    def _get_filter_query(self, filter: Filter, lang: str | None = None, only_published: bool = True) -> str:
        if filter.id:
            return f"WHERE Main.id={filter.id}"

        filter_items = ["published=TRUE"] if only_published else []
        if filter.is_group:
            filter_items.append("is_group=TRUE")
        if filter.is_location:
            filter_items.append("is_location=TRUE")
        if filter.is_media:
            filter_items.append("is_media=TRUE")
        if filter.only_with_events:
            filter_items.append("cached_events IS NOT NULL")
        if filter.query:
            languages = [lang] if lang else LANGUAGES
            query = filter.query.replace('"', '\\"')
            like_query = " OR ".join(
                [f"L{name}.{l} LIKE \"%{query}%\"" for name in LANG_COLUMNS for l in languages]
            )
            filter_items.append(f"({like_query})")
        if not filter_items:
            return ""

        return f"WHERE {' AND '.join(filter_items)}"

    def _insert_lang_row(self, cursor: Any, contact: ContactForOrganize, column: str, languages: str) -> int | None:
        values = [getattr(contact.texts[lang], column) or '' for lang in LANGUAGES]
        if all(v == '' for v in values): # don't insert lang fields if all values are empty
            return None
        escaped_values = ",".join([
            f"'{escape_for_sql(value)}'" for value in values
        ])
        cursor.execute(f"INSERT INTO {self.table_name}_lang({languages}) VALUES ({escaped_values});")
        cursor.execute("select last_insert_id();")
        self.mysql.connection.commit()
        return [row[0] for row in cursor][0]

    def create(self, contact: ContactForOrganize) -> None:
        cursor = self.mysql.connection.cursor()
        # insert language strings into lang table and get the ids
        languages = ",".join(LANGUAGES)
        lang_ids = {column: self._insert_lang_row(cursor, contact, column, languages) for column in LANG_COLUMNS}

        # insert into main table
        columns = ",".join([*LANG_COLUMNS, *OTHER_COLUMNS_FULL])
        raw_values: list[str | int | None] = [lang_ids[column] or 'NULL' for column in LANG_COLUMNS]
        raw_values.extend([
            f"'{escape_for_sql(contact.geo_coord)}'",
            f"'{contact.radar_group_id}'"  if contact.radar_group_id else 'NULL',
            f"'{contact.osm_node_id}'"  if contact.osm_node_id else 'NULL',
            as_sql_bool(contact.is_group),
            as_sql_bool(contact.is_location),
            as_sql_bool(contact.is_media),
            f"'{escape_for_sql(contact.email)}'",
            f"'{escape_for_sql(contact.state)}'",
            as_sql_bool(contact.published),
            'NULL',  # events_cached_at
            'NULL',  # osm_cached_json
            'NULL',  # osm_cached_at
        ]);
        values = ",".join(map(str, raw_values))
        cursor.execute(f"INSERT INTO {self.table_name}({columns}) VALUES ({values});")
        self.mysql.connection.commit()
        cursor.close()

    def update(self, id: int, contact: ContactForOrganize) -> None:
        cursor = self.mysql.connection.cursor()
        lang_columns = ",".join(LANG_COLUMNS)
        languages = ",".join(LANGUAGES)
        cursor.execute(f"SELECT {lang_columns} FROM {self.table_name} WHERE id={id};")
        contact_db_row = [row for row in cursor][0]

        # update language strings in lang table
        for index, column in enumerate(LANG_COLUMNS):
            lang_id = contact_db_row[index]
            if not lang_id:
                lang_id = self._insert_lang_row(cursor, contact, column, languages)
                if lang_id is not None:
                    cursor.execute(f"UPDATE {self.table_name} SET {column}={lang_id} WHERE id={id};")
                    self.mysql.connection.commit()
            else:
                values = ",".join([
                    f"{lang}='{escape_for_sql(getattr(contact.texts[lang], column) or '')}'" for lang in LANGUAGES
                ])
                cursor.execute(f"UPDATE {self.table_name}_lang SET {values} WHERE id={lang_id};")

        self.mysql.connection.commit()

        # update main table
        lang_columns = ",".join([*LANG_COLUMNS, *OTHER_COLUMNS_FULL])
        values = ",".join([
            f"geo_coord='{escape_for_sql(contact.geo_coord)}'",
            f"radar_group_id={contact.radar_group_id}" if contact.radar_group_id else "radar_group_id=NULL",
            f"osm_node_id={contact.osm_node_id}" if contact.osm_node_id else "osm_node_id=NULL",
            f"is_group={as_sql_bool(contact.is_group)}",
            f"is_location={as_sql_bool(contact.is_location)}",
            f"is_media={as_sql_bool(contact.is_media)}",
            f"email='{escape_for_sql(contact.email)}'",
            f"state='{escape_for_sql(contact.state)}'",
            f"published={as_sql_bool(contact.published)}",
            f"events_cached_at='{contact.events_cached_at.isoformat()}'" if contact.events_cached_at else "events_cached_at=NULL",
            f"osm_cached_json='{escape_for_sql(contact.osm_cached_json)}'" if contact.osm_cached_json else "osm_cached_json=NULL",
            f"osm_cached_at='{contact.osm_cached_at.isoformat()}'" if contact.osm_cached_at else "osm_cached_at=NULL",
        ]);
        cursor.execute(f"UPDATE {self.table_name} SET {values} WHERE id={id};")
        self.mysql.connection.commit()
        cursor.close()

    def delete(self, id: int) -> None:
        cursor = self.mysql.connection.cursor()
        columns = ",".join(LANG_COLUMNS)
        cursor.execute(f"SELECT {columns} FROM {self.table_name} WHERE id={id};")
        lang_ids = ",".join([str(lang_id) for lang_id in [row for row in cursor][0] if lang_id is not None])
        cursor.execute(f"DELETE FROM {self.table_name}_lang WHERE id IN ({lang_ids});")
        cursor.execute(f"DELETE FROM {self.table_name} WHERE id={id};")
        self.mysql.connection.commit()
        cursor.close()

    def contact_to_event_cache(self, count: int) -> list[tuple[int, int]]:
        # returns the contact id and its radar_group_id of count contacts for which the events where never cached or > 5 hours ago
        five_hours_ago = (datetime.now() - timedelta(hours=5)).isoformat()
        cursor = self.mysql.connection.cursor()
        cursor.execute(
            f"SELECT id, radar_group_id FROM {self.table_name} "
            f"WHERE radar_group_id IS NOT NULL AND (events_cached_at IS NULL OR events_cached_at < '{five_hours_ago}') "
            f"LIMIT {count}"
        )

        if cursor.rowcount == 0:
            return []
        ids = [(contact_id, radar_group_id) for contact_id, radar_group_id in cursor]

        cursor.close()
        return ids

    def update_events_cache(self, contact_id: int, events_map: dict[str, str | None]) -> None:
        contact = self.contacts_for_organize(Filter.for_id(contact_id))[0]
        for lang in LANGUAGES:
            contact.texts[lang].cached_events = events_map[lang]
        contact.events_cached_at = datetime.now()
        self.update(contact_id, contact)


def as_sql_bool(value: bool) -> str:
    return "TRUE" if value else "FALSE"

def escape_for_sql(value: str) -> str:
    return value.replace("'", "\\'")
