#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : C.py
# @Author: huifer
# @Date  : 2018/5/22 0022
import gdal
import osr
import ogr

a = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [
                            3753081.9140625,
                            66.79190947341796
                        ],
                        [
                            3753078.3984375,
                            47.040182144806664
                        ],
                        [
                            3753120.9375,
                            63.54855223203644
                        ],
                        [
                            3753086.8359375,
                            71.85622888185527
                        ],
                        [
                            3753093.515625,
                            64.62387720204688
                        ],
                        [
                            3753081.9140625,
                            66.79190947341796
                        ]
                    ]
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [
                        3753069.43359375,
                        71.18775391813158
                    ],
                    [
                        3753100.546875,
                        43.45291889355465
                    ]
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [
                        3753112.32421875,
                        53.54030739150022
                    ],
                    [
                        3753109.5117187495,
                        70.55417853776078
                    ],
                    [
                        3753080.68359375,
                        68.52823492039876
                    ]
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Point",
                "coordinates": [
                    3753069.08203125,
                    62.59334083012024
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Point",
                "coordinates": [
                    3753102.12890625,
                    55.57834467218206
                ]
            }
        }
    ]
}


def create_polygon(coords):
    ring = ogr.Geometry(ogr.wkbLinearRing)
    for coord in coords:
        for xy in coord:
            ring.AddPoint(xy[0], xy[1])

            poly = ogr.Geometry(ogr.wkbPolygon)
            poly.AddGeometry(ring)
    return poly.ExportToWkt()


def create_shp_with_geoJson(a):
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
    gdal.SetConfigOption("SHAPE_ENCODING", "GBK")
    driver = ogr.GetDriverByName("ESRI Shapefile")
    # Polygon
    polygon_data_source = driver.CreateDataSource("testPolygon.shp")
    polygon_layer = polygon_data_source.CreateLayer("testPolygon", geom_type=ogr.wkbPolygon)
    field_testfield = ogr.FieldDefn("polygon", ogr.OFTString)
    field_testfield.SetWidth(254)
    polygon_layer.CreateField(field_testfield)

    # Point
    point_data_source = driver.CreateDataSource("testPoint.shp")
    point_layer = polygon_data_source.CreateLayer("testPoint", geom_type=ogr.wkbPoint)
    field_testfield = ogr.FieldDefn("point", ogr.OFTString)
    field_testfield.SetWidth(254)
    point_layer.CreateField(field_testfield)

    # line
    polyline_data_source = driver.CreateDataSource("testLine.shp")
    polyline_layer = polygon_data_source.CreateLayer("testLine", geom_type=ogr.wkbLineString)

    field_testfield = ogr.FieldDefn("polyline", ogr.OFTString)
    field_testfield.SetWidth(254)
    polyline_layer.CreateField(field_testfield)

    for i in a['features']:
        geo = i.get("geometry")
        geo_type = geo.get('type')

        if geo_type == 'Polygon':
            polygonCOOR = geo.get('coordinates')
            poly = create_polygon(polygonCOOR)
            if poly:
                feature = ogr.Feature(polygon_layer.GetLayerDefn())
                feature.SetField('polygon', 'test')
                area = ogr.CreateGeometryFromWkt(poly)
                feature.SetGeometry(area)
                polygon_layer.CreateFeature(feature)
                feature = None
        elif geo_type == "MultiPolygon":
            # 简单操作
            feature = ogr.Feature(polygon_layer.GetLayerDefn())
            feature.SetField('polygon', "test")

            gjson = ogr.CreateGeometryFromJson(str(geo))
            if gjson:
                feature.SetGeometry(gjson)
                polygon_layer.CreateFeature(feature)
                feature = None
        elif geo_type == "Point":
            feature = ogr.Feature(point_layer.GetLayerDefn())
            feature.SetField('point', "point")

            point_geo = ogr.CreateGeometryFromJson(str(geo))
            if point_geo:
                feature.SetGeometry(point_geo)
                point_layer.CreateFeature(feature)
                feature = None

            pass
        elif geo_type == "LineString":
            feature = ogr.Feature(polyline_layer.GetLayerDefn())
            feature.SetField('polyline', "point")

            line_geo = ogr.CreateGeometryFromJson(str(geo))
            if line_geo:
                feature.SetGeometry(line_geo)
                polyline_layer.CreateFeature(feature)
                feature = None
            pass
        else:
            print('Could not discern geometry')


if __name__ == '__main__':
    create_shp_with_geoJson(a)