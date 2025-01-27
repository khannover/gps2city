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
    ui.label("Germany Geocoordinates")

with ui.row().classes("w-full items-center"):
        m = ui.leaflet(center=(51.520, 10.405))
        m.set_zoom(6)
        m.classes("w-96 h-96 ms-[auto] me-[auto]")

#with open("output.json") as o:
#    geos = json.load(o)
#    for plz in geos.keys():
#        if plz.startswith(""):
#            tl = [geos[plz]["coords"][0][0],geos[plz]["coords"][0][1]]
#            tr = [geos[plz]["coords"][1][0],geos[plz]["coords"][1][1]]
#            br = [geos[plz]["coords"][2][0],geos[plz]["coords"][2][1]]
#            bl = [geos[plz]["coords"][3][0],geos[plz]["coords"][3][1]]
#            print([tl,tr,br,bl])
#            m.generic_layer(
#                name='polygon', 
#                args=[ 
#                    [tl,tr,br,bl], 
#                    {
#                        'color': string_to_hex_color(geos[plz]["name"]), 
#                        'radius': 0,
#                        'smoothFactor': 5.0,
#                        'stroke': False,
#                        'fillOpacity': 0.3,
#                    }
#                ]
#            )

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

def draw_radius(city_data, loc=(50.78, 6.05)):
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
                'radius': radius*1000
            }
        ]
    )


    # 3) Test-Koordinate (hier ein Beispiel)
    test_coordinate = loc  # (lat, lon)

    # 4) Entfernung berechnen
    dist = haversine_distance(city_center_lat, city_center_lon, 
                              test_coordinate[0], test_coordinate[1])

    # 5) Vergleich
    if dist <= radius:
        print("Die Koordinate liegt (approximativ) innerhalb der Stadtgrenzen von "+city_data["name"])
        print(f"Distanz zum Stadtzentrum: {dist:.2f} km")
        print(f"Berechneter Radius (Kreisapprox. aus Fläche): {radius:.2f} km")
        city_data["distance"] = dist
        return city_data
    else:
        return None

#with open("kreise_mittel.geojson") as o:
#    geos = json.load(o)
#    for feat in geos["features"]:
#        coords = []
#        for f in feat["geometry"]["coordinates"]:
#            for c in f:
#                coords.append([c[1], c[0]])
#        
#        name = feat["properties"]["NAME_3"]
#        color = string_to_hex_color(name)
#        m.generic_layer(
#                name='polygon', 
#                args=[ 
#                    coords, 
#                    {
#                        'fillColor': 'red',
#                        #color, 
#                        'color': 'black',
#                        'radius': 0,
#                        'smoothFactor': 2.0,
#                        'stroke': True,
#                        'fillOpacity': 0.4,
#                    }
#                ]
#            )


with open("german_cities.json") as o:
    cities = json.load(o)
    location_candidates = {}
    for city in cities:
        location_candidate = draw_radius(city, (52.411936, 9.676477))
        if location_candidate:
            location_candidates[str(location_candidate["name"])] = location_candidate["distance"]
    sorted_dict = dict(sorted(location_candidates.items(), reverse=True, key=lambda item: item[1])) 
    print(sorted_dict)
    lc = sorted_dict.popitem() if sorted_dict else [""]
    print("Die Geokoordinaten gehören zu " + lc[0])   
        

        
        




# with open("plz_geocoord.csv") as f:
#       for line in f:
#             plz = line.split(",")[0]
#             lat = line.split(",")[1][:6]
#             lng = line.split(",")[2][:6]
#             if plz.startswith("38"):
#                 m.marker(latlng=(lat, lng))

@ui.page("/init")
def init():
    with open("postalcode2city.json") as pc2city:
        #plz2stadt = {}
        #for entry in pc2city:
        #    p2c = json.loads(entry)
        #    plz2stadt[p2c["plz"]] = p2c["city"]
        #print(plz2stadt)
        
        #with open("plz-5stellig.geojson") as f:
        with open("kreise.geojson") as f:
            foo = json.load(f)
            output = {}
            for data in foo["features"]:
                #plz = data["properties"]["plz"]
                name = data["properties"]["NAME_3"].replace(" Städte", "")
                print(name)
                coords = data["geometry"]["coordinates"][0]
                lat1,lng1 = 0,0
                lat2,lng2 = 0,0

                count=0
                for c in coords:
                    if count == 0:
                        lat1,lng1= coords[0][1], coords[0][0] 
                        lat2,lng2 = coords[0][1], coords[0][0]
                    else:
                        if c[1] < lat1:
                            lat1 = c[1]
                        if c[1] > lat2:
                            lat2 = c[1]
                        if c[0] < lng1:
                            lng1 = c[0]
                        if c[0] > lng2:
                            lng2 = c[0]
                    count += 1
                output[name]={
                    "name": name, 
                    "coords": [[lat1,lng1],[lat2,lng1], [lat2,lng2], [lat1,lng2]],
                }
                if lat2 == 0:
                    break
            with open(f"output.json","w") as of:
                of.write(json.dumps(output))
                    
     
#    ui.label(str(first_coord[1]) + ", " + str(first_coord[0]))
#    ui.label(str(last_coord[1]) + ", " + str(last_coord[0]))

    #m.generic_layer(name='polygon', args=[ [[x1,y1],[x2,y1], [x2,y2], [x1,y2]], {'color': 'red', 'radius': 300}])



ui.run(
    port=1234,
    show=True,
    storage_secret="sdfjsf",
    uvicorn_logging_level="info",
)
