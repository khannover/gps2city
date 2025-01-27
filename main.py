from nicegui import app, ui, run
import json
import random 
import colorsys


def string_to_hex_color(s):
    # Generate a hash from the string
    hash_code = abs(hash(s))
    # Get the last 6 characters of the hex representation of the hash
    hex_code = hex(hash_code)[-6:]
    # Ensure the hex code is 6 characters long
    hex_code = hex_code.zfill(6)
    # Return the hex color code
    return f"#{hex_code}"



with ui.header():
    ui.label("Germany Geocoordinates").classes("text-2xl")
    ui.space()
    ui.link(target="/docs", text="API Documentation").classes("text-white text-2xl")

with ui.row().classes("w-full "):
    label_city = ui.label()
    input_latitude = ui.input("Latitude", value=str(52.421936))
    input_longitude = ui.input("Longitude", value=str(9.696477))
    ui.button("Find City", on_click=process)


    m = ui.leaflet(center=(51.520, 10.405))
    m.set_zoom(6)
    m.classes("w-full h-[800px]")

import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Berechnet die Distanz zwischen zwei Koordinaten (lat, lon)
    auf einer (näherungsweise) kugelförmigen Erde mithilfe
    der Haversine-Formel. Ergebnis in Kilometern.
    """
    R = 6371.0  # Erdradius in km

    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    a = (math.sin(dLat / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin(dLon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def draw_radius(city_data, loc=None):
    if not loc:
        loc = (float(input_latitude.value), float(input_longitude.value))
    # 1) Daten parsen
    city_area = float(city_data.get("area",1))              
    # Stadtfläche in km²
    city_center_lat = float(city_data["coords"]["lat"])
    city_center_lon = float(city_data["coords"]["lon"])

    # 2) Radius aus der Fläche berechnen (Kreisfläche = π * r²)
    radius = math.sqrt(city_area / math.pi)
    color = string_to_hex_color(city_data.get("name"))
    m.generic_layer(
        name='circle', 
        args=[
            [city_center_lat, city_center_lon], 
            {
                'fillColor': color, 
                'color': 'red',
                'radius': radius*1000,
            }
        ]
    )

    # 3) Entfernung berechnen
    dist = haversine_distance(city_center_lat, city_center_lon, 
                              loc[0], loc[1])

    # 5) Vergleich
    if dist <= radius:
        print("Die Koordinate liegt (approximativ) innerhalb der Stadtgrenzen von "+city_data["name"])
        print(f"Distanz zum Stadtzentrum: {dist:.2f} km")
        print(f"Berechneter Radius (Kreisapprox. aus Fläche): {radius:.2f} km")
        city_data["distance"] = dist
        marker = m.marker(latlng=loc)
        return city_data
    else:
        return None

def process():
    with open("german_cities.json") as o:
        cities = json.load(o)
        location_candidates = {}
        for city in cities:
            location_candidate = draw_radius(city)
            if location_candidate:
                location_candidates[str(location_candidate["name"])] = location_candidate["distance"]

        # sort candidates by distance
        sorted_dict = dict(sorted(location_candidates.items(), reverse=True, key=lambda item: item[1]))
        lc = sorted_dict.popitem() if sorted_dict else ["Unbekannt"]
        label_city.text = "Die Geokoordinaten gehören zu " + lc[0]





@app.get("/api/gps2city/{lat}/{lon}")
def get_city(lat: float, lon: float):
    with open("german_cities.json") as o:
        cities = json.load(o)
        location_candidates = {}
        for city in cities:
            location_candidate = draw_radius(city, (lat, lon))
            if location_candidate:
                location_candidates[str(location_candidate["name"])] = location_candidate["distance"]
        sorted_dict = dict(sorted(location_candidates.items(), reverse=True, key=lambda item: item[0]))
        return sorted_dict

ui.run(
    port=1234,
    show=False,
    storage_secret="sdfjsf",
    uvicorn_logging_level="info",
    fastapi_docs=True,
)
