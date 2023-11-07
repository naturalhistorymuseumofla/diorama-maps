import svgwrite
import geopandas
from dotenv import dotenv_values

file_path = dotenv_values(".env")["FILE_PATH"]

gdf = geopandas.read_file(f'{file_path}/counties.geojson')
gdf.plot()

scale = 100
minx, miny, maxx, maxy = [x * scale for x in gdf.total_bounds]
width, height = maxx - minx, maxy - miny

dwg = svgwrite.Drawing(
    f'{file_path}/counties.svg',
    size=(width, height),
    viewBox=f'{minx} {0 - miny} {maxx - minx} {maxy - miny}'
)


def add_path(coordinates: list):
    path_data = "M" + " ".join([f"{x},{0 - y}" for x, y in coordinates]) + "Z"
    path = dwg.path(
        d=path_data,
        fill='none',
        stroke='black',
        style=f'stroke-width:{0.5 / scale}; stroke-linejoin:bevel',
    )
    path.scale(scale)
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

dwg.save()
