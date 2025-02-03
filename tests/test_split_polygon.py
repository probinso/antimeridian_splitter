import shapely.geometry
from antimeridian_splitter.split_polygon import split_polygon
from antimeridian_splitter.geopolygon_utils import OutputFormat
import json
from functools import reduce
from shapely.geometry.base import BaseGeometry
from shapely.geometry.collection import GeometryCollection
from shapely.geometry import (
    Polygon, MultiPolygon, LineString, Point, MultiLineString, GeometryCollection
)
import pytest
from shapely.geometry import shape
from shapely import wkt
import shapely


example_polygon1 = """
{
    "type": "Polygon",
    "coordinates": [
        [
        [179.0, 0.0], [-179.0, 0.0], [-179.0, 1.0],
        [179.0, 1.0], [179.0, 0.0]
        ]
    ]
}"""

def test_split_polygon_to_geometrycollection():
    poly: dict = json.loads(example_polygon1)
    dst: GeometryCollection  = split_polygon(poly, OutputFormat.GeometryCollection)
    cmp = wkt.loads('GEOMETRYCOLLECTION (POLYGON ((180 0, 179 0, 179 1, 180 1, 180 0)), POLYGON ((-180 1, -179 1, -179 0, -180 0, -180 1)))')
    assert dst.difference(cmp).is_empty

def test_split_polygon_to_geojson():
    poly: dict = json.loads(example_polygon1)
    res = split_polygon(poly, OutputFormat.Geojson)
    assert str(res) == """['{"type": "Polygon", "coordinates": [[[180.0, 0.0], [179.0, 0.0], [179.0, 1.0], [180.0, 1.0], [180.0, 0.0]]]}', '{"type": "Polygon", "coordinates": [[[-180.0, 1.0], [-179.0, 1.0], [-179.0, 0.0], [-180.0, 0.0], [-180.0, 1.0]]]}']"""
    assert len(res) == 2

def test_split_polygon_to_polygons():
    poly: dict = json.loads(example_polygon1)
    res: GeometryCollection = split_polygon(poly, OutputFormat.GeometryCollection)
    assert len(res.geoms) == 2
    string_repr = str([str(poly) for poly in res.geoms])
    expect = """['POLYGON ((180 0, 179 0, 179 1, 180 1, 180 0))', 'POLYGON ((-180 1, -179 1, -179 0, -180 0, -180 1))']"""
    assert expect == string_repr


example_multipolygon = {
    'type': 'MultiPolygon',
    'coordinates': [
        [
            [
                [179.0, 55.0],
                [179.0, 56.0],
                [179.0, 56.0],
                [179.0, 57.0],
                [179.0, 57.0],
                [180.0, 58.0],
                [180.0, 55.0],
                [179.0, 55.0]
            ],
        ],
        [
            [
                [-180.0, 58.0],
                [-179.0, 58.0],
                [-175.0, 57.0],
                [-175.0, 57.0],
                [-175.0, 56.0],
                [-176.0, 56.0],
                [-176.0, 55.0],
                [-176.0, 55.0],
                [-180.0, 55.0],
                [-180.0, 58.0]
            ],
        ]
    ]
}

def test_split_multipolygons():
    geom = shapely.geometry.shape(example_multipolygon)
    split_geom_along_antimeridian(geom)


    # polygon_collection = split_polygon(example_multipolygon, OutputFormat.Polygons)
    # target_multipolygon = reduce(BaseGeometry.union, polygon_collection)
    # assert json.dumps(example_multipolygon)


from shapely.geometry.base import BaseGeometry
from shapely.ops import split, transform





from pathlib import Path

@pytest.fixture
def setup_image_directory(tmp_path):
    """Setup a temporary directory."""
    return Path(__file__).parent


@pytest.mark.parametrize("geom, expected_length", [
    (Polygon([(-190, 10), (-170, 10), (-170, -10), (-190, -10), (-190, 10)]), 2),
    (MultiPolygon([Polygon([(-190, 10), (-170, 10), (-170, -10), (-190, -10), (-190, 10)])]), 2),
    (Polygon([(-179, -89), (-179, 89), (179, 89), (179, -89), (-179, -89)]), 1),
    (Point(170, 0), 1),
    (LineString([(170, 0), (190, 0)]), 2),
    (Polygon([(170, 10), (190, 10), (190, -10), (170, -10), (170, 10)]), 2),
    (Polygon([(170, 10), (175, 10), (175, -10), (170, -10), (170, 10)]), 1),
    (Polygon([(179, -10), (181, -10), (181, 10), (179, 10), (179, -10)]), 2),
    (MultiPolygon([Polygon([(170, 10), (190, 10), (190, -10), (170, -10), (170, 10)])]), 2),
    (MultiPolygon([Polygon([(170, 10), (175, 10), (175, -10), (170, -10), (170, 10)])]), 1),
    (MultiLineString([LineString([(170, 0), (190, 0)])]), 2),
    (MultiLineString([LineString([(170, 0), (175, 0)])]), 1),
    (GeometryCollection([Point(170, 0), LineString([(170, 0), (190, 0)])]), 3),
    (GeometryCollection([Polygon([(170, 10), (190, 10), (190, -10), (170, -10), (170, 10)]), Point(170, 0)]), 3),
    (Polygon([(170, 10), (-190, 10), (-190, -10), (170, -10), (170, 10)]), 2),
    (Polygon([(170, 10), (200, 10), (200, -10), (170, -10), (170, 10)]), 2),
    (Polygon([(170, 10), (180, 10), (180, -10), (170, -10), (170, 10)]), 1),
    (Polygon([(170, 10), (190, 10), (190, 5), (170, 5), (170, 10)]), 2),
    (Polygon([(170, 10), (170, -10), (190, -10), (190, 10), (170, 10)]), 2),
    (MultiPolygon([Polygon([(170, 10), (190, 10), (190, -10), (170, -10), (170, 10)]), Polygon([(170, 20), (190, 20), (190, 15), (170, 15), (170, 20)])]), 4),
    (MultiPolygon([Polygon([(170, 10), (190, 10), (190, -10), (170, -10), (170, 10)]), Polygon([(170, 20), (175, 20), (175, 15), (170, 15), (170, 20)])]), 3),
    (GeometryCollection([Polygon([(170, 10), (190, 10), (190, -10), (170, -10), (170, 10)]), MultiPolygon([Polygon([(170, 20), (190, 20), (190, 15), (170, 15), (170, 20)])])]), 4),
    (Polygon([(170, 10), (190, 10), (190, -10), (170, -10), (170, 10)], holes=[((172, 5), (175, 5), (175, -5), (172, -5), (172, 5))]), 2),
    (Polygon([(170, 10), (200, 10), (200, -10), (170, -10), (170, 10)], holes=[((172, 5), (175, 5), (175, -5), (172, -5), (172, 5))]), 2),
    (Polygon([(170, 10), (190, 10), (190, -10), (170, -10), (170, 10)], holes=[((180, 5), (190, 5), (190, -5), (180, -5), (180, 5))]), 3),
    (Polygon([(170, 10), (180, 10), (180, -10), (170, -10), (170, 10)], holes=[((172, 5), (175, 5), (175, -5), (172, -5), (172, 5))]), 1),
])
def test_split_geom_along_antimeridian(geom, expected_length):
    result = split_geom_along_antimeridian(geom)
    assert len(result.geoms) == expected_length

    