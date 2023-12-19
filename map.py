import os.path
import shapely
import svgwrite
import geopandas


class Map:
    def __init__(self, name:str, layers:list, epsg: str, height: int = None, width: int = None):
        self.name = name
        self.layers = layers
        self.height = height
        self.width = width
        self.epsg = epsg
        self.gdfs = self.get_gdfs()
        self.minx, self.miny, self.maxx, self.maxy = self.get_bounds()
        self.dwg = self.init_drawing()
        self.name=''
        self.scale_x = 1
        self.scale_y = 1

    def get_gdfs(self) -> list:
        gdfs = [{**d, 'gdf': d['gdf'].to_crs(self.epsg)} for d in self.layers]
        '''
        gdfs = []
        for file in self.layers:
            gdfs.append({
                'name': 'name',
                'gdf': file.to_crs(f'epsg:{self.epsg}')
            })
        '''
        return gdfs

    def clip(self, mask):
        self.gdfs = [{**d, 'gdf': d['gdf'].clip(mask=mask)} for d in self.gdfs]
        self.minx, self.miny, self.maxx, self.maxy = self.get_bounds()

    def get_bounds(self):
        minx = miny = maxx = maxy = 0
        for gdf in self.gdfs:
            _minx, _miny, _maxx, _maxy = [x for x in gdf['gdf'].total_bounds]
            minx = _minx if _minx < minx else minx
            miny = _miny if _miny < miny else miny
            maxx = _maxx if _maxx > maxx else maxx
            maxy = _maxy if _maxy > maxy else maxy
        return [minx, miny, maxx, maxy]

    def get_viewbox(self):
        if self.width and self.height:
            self.scale_x = self.width / (self.maxx - self.minx)
            self.scale_y = self.height / self.maxy - self.miny
            return f'0 {0 - (self.maxy - self.miny)} {self.width} {self.height}'
        else:
            return f'0 {0 - (self.maxy - self.miny)} {self.maxx - self.minx} {self.maxy - self.miny}'

    def init_drawing(self):
        return svgwrite.Drawing(
            f'file.svg',
            height='100%',
            width='100%',
            viewBox=self.get_viewbox(),
            id='map'
        )

    def trans(self, coord: float, type: str):
        if type == 'x':
            m = (coord) - self.minx
        if type == 'y':
            m = 0 - (coord - self.miny)
        return round(m, 4)

    def simplify(self, polygon:shapely.Polygon):
        coord_num = len(polygon.exterior.coords)
        if coord_num < 30000:
            return polygon
        geometry = polygon
        tolerance = 0
        while coord_num > 30000:
            tolerance += 100
            geometry = geometry.simplify(tolerance)
            coord_num = len(geometry.exterior.coords)
        return geometry

    def add_path(self, polygon: shapely.Polygon, lyr):
        simplified_polygon = self.simplify(polygon)
        coordinates = simplified_polygon.exterior.coords
        data = [f"{(self.trans(x, 'x'))} {self.trans(y, 'y')}" for x, y in coordinates]
        path_data = "M " + " ".join(data) + " Z"
        path = self.dwg.path(
            d=path_data,
            class_=self.name,
            stroke_width='1',
        )
        lyr.add(path)

    def add_layer(self, gdf):
        lyr = svgwrite.container.Group(class_=gdf['name'], id=gdf['name'])
        self.name = gdf['name']
        for feature in gdf['gdf'].iterrows():
            if 'name' in feature[1]:
                name = 'feature' if 'name' not in feature[1] else feature[1]['name']
                group = svgwrite.container.Group(id=name.replace(' ', '-'))
            else:
                group = svgwrite.container.Group()
            print(feature)
            geometry = feature[1]['geometry']
            if geometry.geom_type == 'Polygon':
                self.add_path(geometry, group)
            if geometry.geom_type == 'MultiPolygon':
                for geom in geometry.geoms:
                    self.add_path(geom, group)
            lyr.add(group)
        self.dwg.add(lyr)

    def save(self, filename: str):
        with open('map.css') as f:
            css = f.read()
        for gdf in self.gdfs:
            self.add_layer(gdf)
        self.dwg.embed_stylesheet(css)
        self.dwg.saveas(filename=filename)
