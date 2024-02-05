LANGUAGES = ['de', 'en']
LANG_COLUMNS = [
    'name', 'short_description', 'description', 'resources', 'base_address', 'addresses', 'contact', 'cached_events', 'osm_cached_info'
]
OTHER_COLUMNS = ['geo_coord', 'radar_group_id', 'osm_node_id']
OTHER_COLUMNS_FULL = [
    *OTHER_COLUMNS, 'is_group', 'is_location', 'is_media', 'email', 'state', 'published', 'events_cached_at', 'osm_cached_json', 'osm_cached_at'
]
