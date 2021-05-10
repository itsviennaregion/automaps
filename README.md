# Automatische Karten

## Kurzbeschreibung
__TODO__

## Architektur
__TODO__

## Installation
* QGIS installieren
* Installation der benötigten Packages (__im von QGIS genutzten Python-Interpreter!__): 

    `pip install -r requirements.txt`

    oder

    `python3 -m pip install -r requirements.txt`


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
* Lokale Konfiguration als File `conf_local.py` im Stammverzeichnise des Repos hinterlegen (zum Inhalt der Datei siehe unten).

## Start des Streamlit Frontends + QGIS Backend
Ausführen von:

`./start_automaps.sh` 

Eventuell vorher:

`chmod +x start_automaps.sh`

Das Frontend ist unter [http://localhost:8501/](http://localhost:8501/)
erreichbar. 

## Konfiguration
Die folgenden Files und Verzeichnisse sind für die Konfiguration relevant:

    /conf.py
    /conf_local.py
    /conf_server.py
    /generators

### `/conf.py`
Hier muss die Konfiguration des Frontends und der Kartenerstellung in der Variable
`MAPTYPES_AVAIL` erfolgen. Dabei handelt es sich um ein Dictionary mit der 
Struktur `Dict[str, MapType]`. 

Als Key des Dictionaries soll eine Bezeichnung des Kartentyps vergeben werden. Diese 
wird im Frontend zur Auswahl angezeigt. 

`MapType`
wird mit folgenden Argumenten initialisiert: __TODO: aktualisieren__
* `name (str)`: Name des Kartentyps. Dieser muss als Key in der Variable `GENERATORS` 
in `/conf_server.py` vorkommen (siehe unten).
* `description (str)`: Beschreibung des Kartentyps. Wird im Frontend angezeigt.
* `selectors (Iterable[Selector])`: Iterable von `Selector`-Objekten. Damit werden die
  Auswahlmöglichkeiten, die im UI angezeigt werden, definiert. Die Auswahl wird beim 
  Start der Verarbeitung als `self.data`-Attribut übergeben.
* `print_layout (str)`: Name des im QGIS-Projektfile (siehe `/conf_local.py`)
verwendeten Print-Layouts

Beispiel:
```python
MAPTYPES_AVAIL: Dict[str, MapType] = {
    "ÖV-Überblick": MapType(
        name="ÖV-Überblick",
        description="Hiermit kann man einen ÖV-Überblick erzeugen. "
        "Das funktioniert so: ...",
        selectors=[
            SelectorSimple("Layout", ["A", "B"], st.radio),
            SelectorSimple("Linie", ["1", "2", "3"], st.selectbox),
            SelectorSQL(
                "Gemeinde", "select distinct von_gemeinde from pendlergem", st.selectbox
            ),
        ],
        print_layout="test_layout",
    ),
}
```

### `/conf_local.py`
Hier müssen die folgenden Variablen festgelegt werden:

Der Verzeichnispfad zum Speichern der erzeugten Karten (`BASEPATH_FILESERVER`), z.B.:

    BASEPATH_FILESERVER = "/home/automaps/automaps_files"

Der Verzeichnispfad zur QGIS-Installation (`QGIS_INSTALLATION_PATH`), z.B.:

    QGIS_INSTALLATION_PATH = "/usr"

Der Dateipfad zum QGIS-Projektfile (`FILEPATH_QGIS_PROJECT`), z.B.:

    FILEPATH_QGIS_PROJECT = "/home/automaps/automaps_qgis/automaps_dev.qgz"

### `/conf_server.py`
Hier müssen die folgenden Variablen festgelegt werden:

Die Variable `GENERATORS` vom Typ `Dict[str, MapGenerator]`. Als Keys müssen die in 
`/conf.py` festgelegten `name`-Attribute der `MapType`-Objekte verwendet werden. Als
Values die dazugehörigen Kartengeneratoren mit der Basisklasse `MapGenerator` 
(siehe unten, `/generators`)

Beispiel für `/conf_server.py`:

    from typing import Dict

    from automaps.generators import MapGeneratorUeberblick
    from automaps.generators.base import MapGenerator

    GENERATORS: Dict[str, MapGenerator] = {"ÖV-Überblick": MapGeneratorUeberblick}


### `/generators`
Hier werden die einzelnen Kartengeneratoren als Subklasse von `MapGenerator` (zu 
finden in `/generators/base.py`) definiert.

Dafür wird jeweils ein neues Pythonmodul im Package `generators` erzeugt. Dieses enthält
die Klassendefinition des Generators. 

Jede Generatorklasse benötigt ein Klassenattribut `name`, eine Methode `_set_steps()`
und frei definierbare Methoden zur Kartenerstellung. 

Die Methode `_set_steps()` muss das Attribut `self.steps` vom Typ 
`OrderedDict[str, Step]` setzen. Als Keys sollten sprechende Namen des 
Verarbeitungsschrittes vergeben werden. Diese werden auch so im Frontend zur Information
über den Verarbeitungsfortschritt angezeigt. Die Verarbeitung erfolgt in der im 
`OrderedDict` festgelegten Reihenfolge.

Als Values werden NamedTuple vom Typ `Step` erwartet, mit folgenden Attributen:
* `func (Callable)` ist die in der Klasse definierte Methode, die den Schritt ausführt.
* `weight (float)` ist das relative Gewicht des Schritts bezüglich der voraussichtlichen
  Verarbeitungszeit (relativ zu den anderen Schritten eines Kartengenerators). Dies
  dient der Anzeige des Progressbars im Frontend.

__Achtung!__: Für jede Ausführung eines Schrittes wird eine neue Instanz des
`MapGenerator` erzeugt! Das Attribut `self` kann deshalb nicht zur Weitergabe von Daten 
zwischen den Schritten genutzt werden. Stattdessen kann das Attribut `step_data` 
vom Typ `StepData` genutzt werden, wie im Beispiel ersichtlich wird. Dafür können dem
Objekt beliebige Attribute hinzugefügt werden.

Eine kleine Generatorklasse mit vier Schritten könnte z.B. so aussehen: __TODO: aktualisieren__

```python
import time

from collections import OrderedDict

from automaps.generators.base import MapGenerator, Step


class MapGeneratorUeberblick(MapGenerator):
    name = "ÖV-Überblick"

    def _set_steps(self):
        self.steps = OrderedDict(
            {
                "Projekt laden": Step(self.load_project, 0.5),
                "Layer filtern": Step(self.filter_layers, 1),
                "Kartenausschnitt festlegen": Step(self.set_extent, 1),
                "Karte exportieren": Step(self.export_layout, 0.5),
            }
        )

    def load_project(self):
        project = self._get_project()
        layout = self._get_print_layout(project)
        self.step_data.project = project
        self.step_data.layout = layout

    def filter_layers(self):
        time.sleep(0.5)

    def set_extent(self):
        time.sleep(0.5)

    def export_layout(self):
        self._export_print_layout(self.step_data.layout)
```


