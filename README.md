# Source code for Schwarz-Bunte-Seiten-Berlin

This is the source code of https://schwarz-bunte-seiten-berlin.org.

A super simple flask app using mysql.


## Requirements

Python 3.11

```
pip install -r requirements.in
```

## Run

```
flask --app app --debug run
```

## Config File

Create file `config.json` with the following content:

```
{
    "MYSQL_HOST": "...",
    "MYSQL_USER": "...",
    "MYSQL_PASSWORD": "...",
    "MYSQL_DB": "...",
    "TABLE_NAME": "e.g. contacts_berlin",
    "DEFAULT_LANG": "e.g. de",
    "ORGANIZE_LOGIN": "e.g. admin",
    "ORGANIZE_PASSWORD": "hashed password"
}
```

Create the hashed password with
`bcrypt.hashpw("your password here".encode('utf-8'), bcrypt.gensalt(10)).decode('utf-8')`

## MySQL Setup

Administration e.g. with `mysql --host=localhost --user=myname --password=password mydb`.
The access can be configured with config.json.

Two tables are needed:

```
mysql> describe contacts_berlin;
+-------------------+-------------+------+-----+---------+----------------+
| Field             | Type        | Null | Key | Default | Extra          |
+-------------------+-------------+------+-----+---------+----------------+
| id                | int         | NO   | PRI | NULL    | auto_increment |
| name              | smallint    | NO   |     | NULL    |                |
| short_description | smallint    | YES  |     | NULL    |                |
| description       | smallint    | YES  |     | NULL    |                |
| resources         | smallint    | YES  |     | NULL    |                |
| base_address      | smallint    | YES  |     | NULL    |                |
| addresses         | smallint    | YES  |     | NULL    |                |
| contact           | smallint    | YES  |     | NULL    |                |
| is_group          | tinyint(1)  | YES  |     | NULL    |                |
| is_location       | tinyint(1)  | YES  |     | NULL    |                |
| is_media          | tinyint(1)  | YES  |     | NULL    |                |
| email             | text        | YES  |     | NULL    |                |
| geo_coord         | varchar(16) | YES  |     | NULL    |                |
| state             | text        | NO   |     | NULL    |                |
| published         | tinyint(1)  | NO   |     | 0       |                |
| radar_group_id    | int         | YES  |     | NULL    |                |
| cached_events     | smallint    | YES  |     | NULL    |                |
| events_cached_at  | timestamp   | YES  |     | NULL    |                |
| osm_node_id       | int         | YES  |     | NULL    |                |
| osm_cached_json   | text        | YES  |     | NULL    |                |
| osm_cached_info   | smallint    | YES  |     | NULL    |                |
| osm_cached_at     | timestamp   | YES  |     | NULL    |                |
+-------------------+-------------+------+-----+---------+----------------+

mysql> describe contacts_berlin_lang;
+-------+------+------+-----+---------+----------------+
| Field | Type | Null | Key | Default | Extra          |
+-------+------+------+-----+---------+----------------+
| id    | int  | NO   | PRI | NULL    | auto_increment |
| de    | text | NO   |     | NULL    |                |
| en    | text | NO   |     | NULL    |                |
+-------+------+------+-----+---------+----------------+
```

## L10n

* Edit `l10n/source.json`
* run `python l10n_creation.py`
* `l10n/l.py` gets updated which is imported in the code

## Admin Interface

* Can be accessed at `/organize`
* The password is set in `config.json`

## Customization

Feel free to use the code for similar projects in your cities or regions.

While some texts in .html files are Berlin specific and need to be adapted, the code itself is generic.

You will also have to add custom images like `static/header.png`.
