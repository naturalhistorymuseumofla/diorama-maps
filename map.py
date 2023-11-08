import svgwrite
import geopandas
from dotenv import dotenv_values
from os import listdir
from os.path import isfile, join


class Map:
    def __init__(self, continent:str):
        self.basepath = dotenv_values(".env")["FILE_PATH"]
        self.datapath = f'{self.basepath}/{self.continent}'
        self.continent: continent
        self.gdfs = self.get_gdfs()
        self.minx, self.miny, self.maxx, self.miny = self.get_bounds()
        self.scale = 100
        self.dwg = self.init_drawing()

    def get_gdfs(self) -> list:
        files = [f for f in listdir(self.basepath) if isfile(join(self.basepath, f))]
        return [geopandas.read_file(f) for f in files]

    def get_bounds(self):
        minx, miny, maxx, maxy = 0
        for gdf in self.gdfs:
            _minx, _miny, _maxx, _maxy = gdf.total_bounds
            minx = _minx if _minx < minx else minx
            miny = _miny if _miny < miny else miny
            maxx = _maxx if _maxx > maxx else maxx
            maxy = _maxy if _maxy > maxy else maxy
        return [minx, miny, maxx, maxy]

    def get_viewbox(self):
        return f'{self.minx} {0 - self.miny} {self.maxx - self.minx} {self.maxy - self.miny}'

    def init_drawing(self):
        return svgwrite.Drawing(
            f'{self.basepath}/{self.continent}.svg',
            size=(self.maxx - self.minx, self.maxy - self.miny),
            viewBox=self.get_viewbox()
        )

    def add_path(self, coordinates: list):
        path_data = "M" + " ".join([f"{x},{0 - y}" for x, y in coordinates]) + "Z"
        path = map.path(
            d=path_data,
            fill='none'
        )
        path.scale(self.scale)
        self.dwg.add(path)

    def add_layer(self):


    def save(self):
        dwg = self.init_drawing()
