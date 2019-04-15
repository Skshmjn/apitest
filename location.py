from math import radians, sin, sqrt, asin, cos

import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

CORS(app)


@app.route('/')
def home():
    return "hello world"


@app.route('/get_location', methods=['GET'])
def get_location():
    conn = psycopg2.connect(host="localhost", database="Test", user="postgres", password="15021997")
    key = input("Enter pin code here ")

    cur = conn.cursor()
    cur.execute("SELECT * from location WHERE Key='{}';".format(key))
    row = cur.fetchone()

    response = {
        'message': str(row),

    }

    cur.close()
    conn.commit()
    conn.close()
    return jsonify(response), 200


@app.route('/post_location', methods=['POST'])
def post_location():
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data found'
        }
        return jsonify(response), 400
    if 'key' not in values:
        response = {
            'message': 'some data not found'
        }
        return jsonify(response), 400

    conn = psycopg2.connect(host="localhost", database="Test", user="postgres", password="15021997")
    cur = conn.cursor()
    cur.execute("INSERT INTO location(key,place_name, admin_name, latitude,"
                " longitude, accuracy) VALUES ('{}','{}','{}',{},{},{});".format(values["key"], values["place_name"],
                                                                                 values["admin_name"],
                                                                                 float(values["latitude"]),
                                                                                 float(values["longitude"]),
                                                                                 int(values["accuracy"])))

    cur.close()
    conn.commit()
    conn.close()
    response = {
        'message': 'Value is inserted',

    }
    return jsonify(response), 201


@app.route('/get_using_postgres', methods=['GET'])
def get_using_postgres():
    conn = psycopg2.connect(host="localhost", database="Test", user="postgres", password="15021997")
    cur = conn.cursor()
    lat = input('input latitude:')
    lng = input('input longitude:')
    distance = int(input('input distance in KM:')) * 1000
    cur.execute("CREATE EXTENSION IF NOT EXISTS cube")
    cur.execute("CREATE EXTENSION IF NOT EXISTS earthdistance")
    cur.execute(
        ' SELECT * FROM location WHERE earth_box(ll_to_earth({}, {})'
        ', {}) @> ll_to_earth(latitude, longitude);'.format(lat, lng, distance))

    row = cur.fetchone()
    message = []
    while row is not None:
        message.append(row)
        row = cur.fetchone()

    response = {
        'message': message,

    }
    cur.close()
    conn.commit()
    conn.close()
    return jsonify(response), 200


@app.route('/get_using_self', methods=['GET'])
def get_using_self():
    conn = psycopg2.connect(host="localhost", database="Test", user="postgres", password="15021997")
    cur = conn.cursor()
    lat = input('input latitude:')
    lng = input('input longitude:')
    distance = input('input distance in KM:')

    cur.execute(
        ' SELECT * FROM location ;')
    message = []
    row = cur.fetchone()
    while row is not None:
        if row[3] is not None and row[4] is not None:
            if distances(float(lat), float(row[3]), float(lng), float(row[4])) <= float(distance):
                message.append(row)
        row = cur.fetchone()

    cur.close()
    conn.commit()
    conn.close()
    response = {
        'message': message,

    }
    return jsonify(response), 200


@app.route('/check_coordinate_geojson', methods=['GET'])
def check_coordinate_geojson():
    conn = psycopg2.connect(host="localhost", database="Test", user="postgres", password="15021997")
    lat = float(input('input latitude:'))
    lng = float(input('input longitude:'))

    cur = conn.cursor()
    cur.execute("SELECT * from geojson;")
    row = cur.fetchone()
    response = {
        'message': '',

    }

    while row is not None:
        p = [float(i) for i in row[0].split(',')]
        latitudes = p[1::2]
        longitudes = p[::2]
        coordinates = list(zip(latitudes, longitudes))

        if point_in_poly(lat, lng, coordinates):
            response = {
                'message': row[1],

            }
        row = cur.fetchone()

    cur.close()
    conn.commit()
    conn.close()
    return jsonify(response), 200


def distances(lat1, lat2, lon1, lon2):
    # The math module contains a function named
    # radians which converts from degrees to radians.
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2

    c = 2 * asin(sqrt(a))

    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371

    # calculate the result
    return (c * r)


def point_in_poly(x, y, poly):
    n = len(poly)
    inside = False

    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


if __name__ == '__main__':
    app.debug = True
    app.run(port=5000)
