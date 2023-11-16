import svgwrite
import geopandas
from dotenv import dotenv_values
from os import listdir
from os.path import isfile, join


style = '''
    g {
      stroke-linejoin: bevel;
      fill: none;
    }
    
    path { 
      stroke: #000000;
      stroke-width: 1000px; 
    }
    
    .example-ranges {
      fill: #43AF6E;
    }
    
    .latin-american-boundaries { 
       stroke-width: 2000px
     }
     
     
'''


class Map:
    def __init__(self, name:str, scale:int=1, epsg:str='2163'):
        self.name = name
        self.base_path = dotenv_values(".env")["FILE_PATH"]
        self.scale = scale
        self.epsg = epsg
        self.data_path = join(self.base_path, self.name)
        self.gdfs = self.get_gdfs()
        self.minx, self.miny, self.maxx, self.maxy = self.get_bounds()
        self.dwg = self.init_drawing()

    def get_gdfs(self) -> list:
        print(self.data_path)
        gdfs = []
        for file in listdir(self.data_path):
            if file.endswith('.geojson'):
                gdf = geopandas.read_file(join(self.data_path, file))
                gdfs.append({
                    'name': file.split('.')[0],
                    'gdf': gdf.to_crs(f'epsg:{self.epsg}')
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
            f'{self.base_path}/{self.name}.svg',
            height='100%',
            width='100%',
            viewBox=self.get_viewbox(),
            id='map'
        )

    def trans(self, coord: float, type: str):
        if type == 'x':
            m = (coord * self.scale) - self.minx
        if type == 'y':
            m = 0 - (coord * self.scale - self.miny)
        return round(m, 4)


    def add_path(self, coords: list, lyr):
        data = [f"{(self.trans(x, 'x'))} {self.trans(y, 'y')}" for x, y in coords]
        path_data = "M " + " ".join(data) + " Z"
        path = self.dwg.path(
            d=path_data,
        )
        path.scale(self.scale)
        lyr.add(path)

    def add_layer(self, gdf):
        lyr = svgwrite.container.Group(class_=gdf['name'], id=gdf['name'])
        for feature in gdf['gdf'].iterrows():
            if 'name' in feature[1]:
                group = svgwrite.container.Group(id=name.replace(' ', '-'))
            else:
                group = svgwrite.container.Group()
            name = 'feature' if 'name' not in feature[1] else feature[1]['name']
            print(feature)
            geometry = feature[1]['geometry']
            if geometry.geom_type == 'Polygon':
                coordinates = geometry.exterior.coords
                self.add_path(coordinates, group)
            if geometry.geom_type == 'MultiPolygon':
                coordinates_list = [list(x.exterior.coords) for x in geometry.geoms]
                for coordinates in coordinates_list:
                    self.add_path(coordinates, group)
            lyr.add(group)
        self.dwg.add(lyr)

    def save(self):
        for gdf in self.gdfs:
            self.add_layer(gdf)
        self.dwg.embed_stylesheet(style)
        self.dwg.save()

#map = Map('africa', epsg='esri:102022')
map = Map('north-america')
map.save()
