from layers import get_layers, get_data, symbol
from svgmapper import Map
import os


marine_taxa = [
    'Phoca_vitulina',
    'Eumetopias_jubatus',
    'Ursus_maritimus',
    'Callorhinus_ursinus',
    'Odobenus_rosmarus',
]


def save_map(name:str, continent: str, level=0):
    layers = get_layers(
        name=name,
        continent=continent,
        level=level
     )
    if continent == 'africa':
        Map(
            name=name,
            mask=get_data('africa/africa-continent-bound.geojson'),
            epsg='esri:102022',
            size=(504, 504),
            css='/Users/dmarkbreiter/Code/diorama-maps/map.css',
            symbols=[symbol],
            layers=layers
        ).save(get_data(f'/africa/maps/{name}.svg'))

    if continent == 'north-america':
        mask = get_data(f'north-america/NorthAmericaBounds.geojson') if name not in marine_taxa else ''
        Map(
            name=name,
            mask=mask,
            epsg='epsg:2163',
            size=(504, 504),
            css='/Users/dmarkbreiter/Code/diorama-maps/map.css',
            symbols=[symbol],
            layers=layers
        ).save(get_data(f'north-america/level-{level}/maps/{name}.svg'))
    print(f'{name}.svg saved!')


def map_factory(continent:str, level=0):
    path = f'{continent}/range-data' if continent == 'africa' else f'{continent}/level-{level}/range-data'
    for layer in os.listdir(get_data(path)):
        if os.path.splitext(layer)[1] != '.geojson': continue
        name = layer.split('.')[0]
        if not os.path.exists(get_data(f'points/{layer}')):
            print(f'{name} does not have a corresponding point')
            continue
        save_map(name, continent, level)
