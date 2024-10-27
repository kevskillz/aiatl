# from arcgis.gis import GIS
# from arcgis.layers import MapFeatureLayer
# from arcgis.geometry import Point
# from arcgis.geometry.filters import intersects

import pyproj
import ee

ee.Authenticate(auth_mode="localhost")

# class SeaLevel:
#     def __init__(self):
#         self.gis = GIS()
#         self.three = self.gis.content.get("365fa1f7f5314c0c81af516028f9c928")
#         self.map_feature_layer = MapFeatureLayer.fromitem(item = self.three)
#         self.transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:3857") 


#     def distance(self, x, y, distance):
#         return {
#             "xmin": x - distance,
#             "ymin": y - distance,
#             "xmax": x + distance,
#             "ymax": y + distance,
#             "spatialReference": {"wkid": 102100},
#         }
#     def query(self, lat, long):
#         x, y = self.transformer.transform(lat, long)
#         query_extent_1 = self.distance(x, y, 1)
#         query_filter_1 = intersects(query_extent_1, sr=102100)
#         results_1 = self.map_feature_layer.query(
#             geometry_filter=query_filter_1, out_fields="*", as_df=False
#         )
#         if results_1.features: return 3

#         query_extent_2 = self.distance(x, y, 5000)
#         query_filter_2 = intersects(query_extent_2, sr=102100)
#         results_2 = self.map_feature_layer.query(
#             geometry_filter=query_filter_2, out_fields="*", as_df=False
#         )
#         if results_2.features: return 6

#         query_extent_3 = self.distance(x, y, 20000)
#         query_filter_3 = intersects(query_extent_3, sr=102100)
#         results_3 = self.map_feature_layer.query(
#             geometry_filter=query_filter_3, out_fields="*", as_df=False
#         )
#         if results_3.features: return 9        
#         return 0
    
class ImgSat:
    def __init__(self):
        ee.Initialize(project = "ai-atl-hurricane") # direct-plasma-379617
        self.landsat = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterDate('2014-10-27', '2024-10-27').filter(ee.Filter.lt('CLOUD_COVER', 5))
    def query(self, lat, long):
        bbox = ee.Geometry.BBox(long - 0.05, lat - 0.05, long + 0.05, lat + 0.05)
        landsat_collection = self.landsat.filterBounds(bbox)
        video_args = {
            'dimensions': 480,
            'region': bbox,
            'framesPerSecond': 5,
            'bands': ['SR_B4', 'SR_B3', 'SR_B2']
        }
        video = landsat_collection.getVideoThumbURL(video_args)
        return video  
        
if __name__ == "__main__":
    isat = ImgSat()
    print(isat.query(26.5624, -80.044))