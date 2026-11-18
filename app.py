import csv
import os
from flask import Flask, jsonify

# ---------------- MULTILISTA ----------------
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None
        self.sublist = None          # LinkedList de hijos


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def append(self, data):
        node = Node(data)
        if self.head is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.size += 1
        return node

    def find(self, key, value):
        cur = self.head
        while cur:
            if cur.data.get(key) == value:
                return cur
            cur = cur.next
        return None

    def __iter__(self):
        cur = self.head
        while cur:
            yield cur
            cur = cur.next


def construir_multilista(ruta_csv):
    pais = Node({"tipo": "País", "nombre": "Colombia"})
    pais.sublist = LinkedList()                      # departamentos

    # Lecutra del CSV 
    with open(ruta_csv, encoding="utf-8-sig", newline="") as f:
        for fila in csv.DictReader(f):
            cod_dep = fila["Código Departamento"].strip()
            dep = pais.sublist.find("codigo", cod_dep)
            if dep is None:
                dep = pais.sublist.append({
                    "tipo": "Departamento",
                    "codigo": cod_dep,
                    "nombre": fila["Nombre Departamento"].strip().title()})
                dep.sublist = LinkedList()           # municipios

            dep.sublist.append({
                "tipo": "Municipio",
                "codigo": fila["Código Municipio"].strip(),
                "nombre": fila["Nombre Municipio"].strip().title(),
                "lon": float(fila["longitud"].replace(",", ".")),
                "lat": float(fila["Latitud"].replace(",", "."))})
    return pais


def a_dict(nodo):
    d = dict(nodo.data)
    if nodo.sublist is not None:
        d["hijos"] = [a_dict(h) for h in nodo.sublist]
    return d


# ---------------- FLASK ----------------
CARPETA = os.path.dirname(os.path.abspath(__file__))
pais = construir_multilista(os.path.join(CARPETA, "DIVIPOLA.csv"))

app = Flask(__name__)

PAGINA = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><title>Multilista DIVIPOLA</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>html,body,#map{height:100%;margin:0}</style></head>
<body><div id="map"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const map = L.map('map').setView([4.57, -74.3], 6);
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
  {attribution: 'Tiles &copy; Esri', maxZoom: 19}).addTo(map);
fetch('/api/multilista').then(r => r.json()).then(pais => {
  pais.hijos.forEach(dep => dep.hijos.forEach(m =>
    L.circleMarker([m.lat, m.lon], {radius: 4})
     .bindPopup('<b>' + m.nombre + '</b><br>' + dep.nombre + '<br>' + m.codigo)
     .addTo(map)));
});
</script></body></html>"""


@app.route("/")
def index():
    return PAGINA


@app.route("/api/multilista")
def api():
    return jsonify(a_dict(pais))


if __name__ == "__main__":
    app.run(debug=True)
