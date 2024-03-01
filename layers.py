from svgmapper import Symbol, Layer
import geopandas as gpd

get_data: str = lambda x: f'/Users/dmarkbreiter/Code/diorama-maps/data/{x}'
get_gdf : str = lambda x: gpd.read_file(get_data(x))


symbol = Symbol(
    id='scene',
    size=(35, 35),
    paths=[
        'm25.52,12.76c0,2-.46,3.9-1.29,5.58l-1.62,2.53-.03.03-9.82,15.31L2.92,20.88h0s-1.62-2.53-1.62-2.53C.46,16.66,0,14.77,0,12.76,0,5.71,5.72,0,12.76,0s12.75,5.71,12.75,12.76'
    ],
    stroke='black',
    stroke_width=2,
    fill='#e6b324'
)


def get_layers(name:str, continent: str, level=0):
    north_america_layers = [
        Layer(
            name='countries',
            path=get_data('north-america/countries.geojson')
        ),
        Layer(
            name='usa-states',
            path=get_data('north-america/usa-states.geojson')
        ),
        Layer(
            name='mx-states',
            path=get_data('north-america/mexico-states.geojson')
        ),
        Layer(
            name='ca-provinces',
            path=get_data('north-america/canada-provinces.geojson')
        ),
        Layer(
            name='great-lakes',
            path=get_data('north-america/great-lakes.geojson')
        )
    ]

    africa_layers = [
        Layer(
            name='africa',
            path=get_data('africa/african_continent_wo_islands.geojson')
        ),

        Layer(
            name='countries',
            path=get_data('africa/african_countries_wo_islands.geojson')
        ),
    ]

    if continent == 'africa':
        range = get_gdf(f'africa/range-data/{name}.geojson').to_crs('esri:102022')
        return [
            africa_layers[0],
            Layer(
                name='range',
                gdf=range.clip(get_gdf('africa/african_continent_wo_islands.geojson').to_crs('esri:102022'))
            ),
            africa_layers[1],
            Layer(
                name='diorama-locale',
                path=get_data(f'points/{name}.geojson'),
                symbol=symbol
            ),
        ]
    if continent == 'north-america':
        return [
            *north_america_layers[0:2],
            Layer(
               name='range',
               path=get_data(f'north-america/level-{level}/range-data/{name}.geojson')
            ),
            *north_america_layers[2:],
            Layer(
                name='diorama-locale',
                path=get_data(f'points/{name}.geojson'),
                symbol=symbol
            ),
        ]
