LANGUAGES = ['de', 'en']
LANG_COLUMNS = [
    'name', 'short_description', 'description', 'resources', 'base_address', 'addresses', 'contact'
]
OTHER_COLUMNS = ['geo_coord', 'radar_group_id']
OTHER_COLUMNS_FULL = [*OTHER_COLUMNS, 'is_group', 'is_location', 'is_media', 'email', 'state', 'published', 'id']
OTHER_COLUMNS_FULL_WITHOUT_ID = OTHER_COLUMNS_FULL[0:-1]
