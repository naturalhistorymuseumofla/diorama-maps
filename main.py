from factory import map_factory

'''
map_factory(
    basepath='./data/north-america',
    epsg='epsg:2163',
    layers=[
        {
            'name': 'countries',
            'gdf':  'countries.geojson'
        },
        {
            'name': 'usa-states',
            'gdf': 'usa-states.geojson'
        },
        {
            'name': 'mx-states',
            'gdf': 'mexico-states.geojson'
        },
        {
            'name': 'ca-provinces',
            'gdf': 'canada-provinces.geojson'
        },
    ],
    mask='north-america.geojson',
)

map_factory(
    basepath='./data/africa',
    epsg='esri:102022',
    layers=[
        {
            'name': 'countries',
            'gdf': 'african-country-boundaries.geojson'
        }
    ],
    mask='africa-continent-boundary.geojson',
)
'''

map_factory(
    basepath='./data/africa',
    epsg='esri:102022',
    layers=[],
    mask='africa-continent-boundary.geojson',
)
