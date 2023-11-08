import svgwrite
import geopandas
from dotenv import dotenv_values
from os import listdir
from os.path import isfile, join


class Map:
    def __init__(self, continent:str):
        self.continent = continent
        self.basepath = dotenv_values(".env")["FILE_PATH"]
        self.scale = 1
        self.datapath = join(self.basepath, self.continent)
        self.gdfs = self.get_gdfs()
        self.minx, self.miny, self.maxx, self.maxy = self.get_bounds()
        self.dwg = self.init_drawing()

    def get_gdfs(self) -> list:
        print(self.datapath)
        gdfs = []
        for file in listdir(self.datapath):
            if file.endswith('.geojson'):
                gdf = geopandas.read_file(join(self.datapath, file))
                gdfs.append({
                    'name': file.split('.')[0],
                    'gdf': gdf.to_crs('epsg:2163')
                })
        return gdfs

    def get_bounds(self):
        minx = miny = maxx = maxy = 0
        for gdf in self.gdfs:
            _minx, _miny, _maxx, _maxy = [x * self.scale for x in gdf['gdf'].total_bounds]
            minx = _minx if _minx < minx else minx
            miny = _miny if _miny < miny else miny
            maxx = _maxx if _maxx > maxx else maxx
            maxy = _maxy if _maxy > maxy else maxy
        return [minx, miny, maxx, maxy]

    def get_viewbox(self):
        return f'0 {0 - (self.maxy - self.miny)} {self.maxx - self.minx} {self.maxy - self.miny}'

    def init_drawing(self):
        return svgwrite.Drawing(
            f'{self.basepath}/{self.continent}.svg',
            height='100%',
            width='100%',
            viewBox=self.get_viewbox(),
            id='map'
        )

    def trans(self, coord: float, type: str):
        if type == 'x':
            return (coord * self.scale) - self.minx
        if type == 'y':
            return (0 - (coord * self.scale - self.miny))

    def add_path(self, coords: list, lyr):
        path_data = "M" + " ".join([f"{self.trans(x, 'x')},{self.trans(y, 'y')}" for x, y in coords]) + "Z"
        path = self.dwg.path(
            d=path_data,
            fill='none',
        )
        path.scale(self.scale)
        lyr.add(path)


    def add_layer(self, gdf):
        lyr = svgwrite.container.Group(class_='path', id=gdf['name'])
        for feature in gdf['gdf'].iterrows():
            print(feature)
            geometry = feature[1]['geometry']
            if geometry.geom_type == 'Polygon':
                coordinates = geometry.exterior.coords
                self.add_path(coordinates, lyr)
            if geometry.geom_type == 'MultiPolygon':
                coordinates_list = [list(x.exterior.coords) for x in geometry.geoms]
                for coordinates in coordinates_list:
                    self.add_path(coordinates, lyr)
        self.dwg.add(lyr)

    def save(self):
        for gdf in self.gdfs:
            self.add_layer(gdf)
        self.dwg.add_stylesheet('map.css', title='styles')
        self.dwg.save()

map = Map('north-america')
map.save()
