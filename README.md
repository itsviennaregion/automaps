# Automatische Karten

## Installation
* Python-Environment erstellen und pip install `requirements.txt`. Für
  die Erzeugung von Karten muss `PyQGIS` installiert und konfiguriert
  sein.
* Datenbankkonfiguration als File `db.ini` im Stammverzeichnis des Repos hinterlegen:

```ini
    [db]
    drivername=postgresql
    database=postgis
    username=
    password=
    host=VOR-GISDB01-PR
    port=5432
```

## Start des Frontends
`start_frontend.sh` oder `start_frontend.bat` ausführen.

Das Frontend ist unter [http://localhost:8501/](http://localhost:8501/)
erreichbar. 

## Konfiguration
Die folgenden Files und Verzeichnisse sind für die Konfiguration relevant:

    /conf.py
    /generators

### `/conf.py`
Hier müssen zwei Variablen festgelegt werden:

Der Pfad zum Speichern der erzeugten Karten (`BASEPATH_FILESERVER`), z.B.:

    BASEPATH_FILESERVER = r"D:\temp\automap"

Die Konfiguration des Frontends und der Kartenerstellung (`MAPTYPES_AVAIL`). Dabei 
handelt es sich um ein Dictionary mit der Struktur `Dict[str, MapType]`. `MapType`
wird mit folgenden Argumenten initialisiert:
* `name (str)`: Name des Kartentyps
* `description (str)`: Beschreibung des Kartentyps
* `selectors (Iterable[Selector])`: Iterable von `Selector`-Objekten. Damit werden die
  Auswahlmöglichkeiten, die im UI angezeigt werden, definiert. Die Auswahl wird beim 
  Start der Verarbeitung als `self.data`-Attribut übergeben.
* `generator (Type[MapGenerator])`: Subklasse von `MapGenerator`. Diese Klassen 
  legen die Schritte der Kartenerstellung fest und werden als Files im Verzeichnis 
  `/generators` definiert

Beispiel:
```python
MAPTYPES_AVAIL: Dict[str, MapType] = {
    "ÖV-Überblick": MapType(
        "ÖV-Überblick",
        "Hiermit kann man einen ÖV-Überblick erzeugen. Das funktioniert so: ...",
        [
            SelectorSimple("Layout", ["A", "B"], st.radio),
            SelectorSimple("Linie", ["1", "2", "3"], st.selectbox),
        ],
        MapGeneratorUeberblick,
    ),
}
```

### `/generators`
Hier werden die einzelnen Kartengeneratoren als Subklasse von `MapGenerator` (zu 
finden in `/generators/base.py`) definiert.

Dafür wird jeweils ein neues Pythonmodul im Package `generators` erzeugt. Dieses enthält
die Klassendefinition des Generators. 

Jede Generatorklasse benötigt ein Klassenattribut `name`, eine Methode `_set_steps()`
und frei definierbare Methoden zur Kartenerstellung. Eine Minimale Generatorklasse mit
nur einem Schritt könnte z.B. so aussehen:

```python
class MapGeneratorPendler(MapGenerator):
    name = "Pendler"

    def _set_steps(self):
        self.steps = [
            Step("Schritt A", self.schritt_A, 1),
        ]

    def schritt_A(self):
        time.sleep(1)
```

Die Methode `_set_steps()` muss das Attribut `self.steps` vom Typ `List[Step]` setzen.
`Step` ist ein NamedTuple mit den Attributen `name`, `func` und `weight`. 
* `name (str)` bezeichnet den Schritt.
* `func (Callable)` ist die in der Klasse definierte Methode, die den Schritt ausführt.
* `weight (float)` ist das relative Gewicht des Schritts bezüglich der voraussichtlichen
  Verarbeitungszeit (relativ zu den anderen Schritten eines Kartengenerators). Dies
  dient der Anzeige des Progressbars im UI.
