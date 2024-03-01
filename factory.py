from map import Map
from os import listdir
import geopandas
from os.path import isfile, join, basename

def map_factory(basepath: str, layers: list, mask: str, epsg):
    get_gdf = lambda filename: geopandas.read_file(join(basepath, filename)).to_crs(epsg)

    for file in listdir(join(basepath, 'range-data')):
        if not file.endswith('.geojson'): continue
        mask_gdf = get_gdf(mask).to_crs(epsg)
        range = get_gdf(join('range-data', file)).clip(mask_gdf)
        gdfs = [{**d, 'gdf': get_gdf(d['gdf'])} for d in layers]
        map = Map(
            name=file.split('.')[0],
            epsg=epsg,
            layers=[
                {
                    'name': 'range',
                    'gdf': range
                },
                *gdfs
            ]
        )
        map.save(join(basepath, 'maps', f"{basename(file).split('.')[0]}.svg"))