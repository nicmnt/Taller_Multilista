import csv


class Node:
    """Nodo de la multilista: dato, siguiente y sublista (hijos)."""
    def __init__(self, data):
        self.data = data          # dict con la info del nodo
        self.next = None          # siguiente hermano
        self.sublist = None       # LinkedList con los hijos (o None)


class LinkedList:
    """Lista enlazada simple con cola para insertar en O(1)."""
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


class MultiList:
    """Multilista: Colombia -> Departamentos -> Municipios."""
    def __init__(self, nombre="Colombia"):
        self.root = LinkedList()
        self.root.append({"tipo": "País", "nombre": nombre})
        self.root.head.sublist = LinkedList()   # lista de departamentos

    @property
    def pais(self):
        return self.root.head

    def add_municipio(self, dep_cod, dep_nombre, mun):
        deps = self.pais.sublist
        dep = deps.find("codigo", dep_cod)
        if dep is None:
            dep = deps.append({"tipo": "Departamento", "codigo": dep_cod,
                               "nombre": dep_nombre})
            dep.sublist = LinkedList()          # lista de municipios
        dep.sublist.append(mun)

    @classmethod
    def from_csv(cls, path):
        ml = cls()
        with open(path, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                tipo_col = [k for k in r if k.startswith("Tipo")][0]
                ml.add_municipio(
                    r["Código Departamento"].strip(),
                    r["Nombre Departamento"].strip().title(),
                    {
                        "tipo": r[tipo_col].strip(),
                        "codigo": r["Código Municipio"].strip(),
                        "nombre": r["Nombre Municipio"].strip().title(),
                        "lon": float(r["longitud"].replace(",", ".")),
                        "lat": float(r["Latitud"].replace(",", ".")),
                    })
        return ml

    # ---------- salidas ----------
    def to_dict(self):
        def conv(node):
            d = dict(node.data)
            if node.sublist is not None:
                d["hijos"] = [conv(h) for h in node.sublist]
            return d
        return conv(self.pais)

    def print_tree(self, max_deps=3, max_muns=3):
        print(self.pais.data["nombre"])
        deps = list(self.pais.sublist)
        for i, dep in enumerate(deps[:max_deps]):
            last_dep = i == len(deps[:max_deps]) - 1
            print(("└── " if last_dep else "├── ") + f"Departamento: {dep.data['nombre']}")
            muns = list(dep.sublist)
            for j, m in enumerate(muns[:max_muns]):
                last = j == len(muns[:max_muns]) - 1
                pref = "    " if last_dep else "│   "
                print(f"{pref}{'└── ' if last else '├── '}Municipio: {m.data['nombre']}")


if __name__ == "__main__":
    ml = MultiList.from_csv("DIVIPOLA.csv")
    ml.print_tree()
    print("Departamentos:", ml.pais.sublist.size)
    print("Municipios:", sum(d.sublist.size for d in ml.pais.sublist))
