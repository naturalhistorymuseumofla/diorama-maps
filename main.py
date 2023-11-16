import svgwrite
import geopandas
from dotenv import dotenv_values

file_path = dotenv_values(".env")["FILE_PATH"]

gdf = geopandas.read_file(f'{file_path}/north-america/north-america.json')
gdf.to_crs(gdf.crs, '9820').plot()
gdf.plot()

scale = 100
minx, miny, maxx, maxy = [x * scale for x in gdf.total_bounds]
width, height = maxx - minx, maxy - miny

dwg = svgwrite.Drawing(
    f'{file_path}/north-america/states.svg',
    #size=(width, height),
    height='100%',
    width='100%',
    viewBox=f'0 {0 - (maxy-miny)} {maxx - minx} {maxy - miny}'
)

def translate(coord: float, type: str):
    if type == 'x':
        return (coord * scale) - minx
    if type == 'y':
        return (0-(coord * scale - miny))



def add_path(coordinates: list):
    path_data = "M" + " ".join([f"{translate(x, 'x')},{translate(y, 'y')}" for x, y in coordinates]) + "Z"
    path = dwg.path(
        d=path_data,
        fill='none',
        stroke='black',
        class_='path'
    )
    #path.scale(scale)
    # path.scale(1,-1)
    dwg.add(path)


for feature in gdf.iterrows():
    geometry = feature[1]['geometry']
    if geometry.geom_type == 'Polygon':
        coordinates = geometry.exterior.coords
        add_path(coordinates)

    if geometry.geom_type == 'MultiPolygon':
        coordinates_list = [list(x.exterior.coords) for x in geometry.geoms]
        for coordinates in coordinates_list:
            add_path(coordinates)

dwg.add_stylesheet('map.css', title='styles')
dwg.save()
