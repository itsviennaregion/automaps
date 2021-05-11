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

Das Frontend ist unter [http://localhost:8505/](http://localhost:8505/)
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
wird mit folgenden Argumenten initialisiert: 
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
        description="Hiermit kann man einen ÖV-Überblick erzeugen."
        "Das funktioniert so: ...",
        selectors=[
            SelectorSimple(
                "Räumliche Ebene",
                ["Linie", "Gemeinde"],
                st.selectbox,
                widget_args={"help":"Hilfetext"},
                no_value_selected_text="Räumliche Ebene auswählen ...",
            ),
            SelectorSQL(
                "Linie",
                "select distinct liniennummer from oev_strecken",
                st.selectbox,
                no_value_selected_text="Liniennummer auswählen ...",
                depends_on_selectors={"Räumliche Ebene": "Linie"},
            ),
        ],
        print_layout="test_layout",
    ),
}
```

Die Konfiguration der im UI angezeigten Auswahlmöglichkeiten erfolgt mit Hilfe von
`Selector`-Objekten.
Es stehen zwei von `selector.BaseSelector` abgeleitete Selector-Klassen zur Verfügung:

* `SelectorSimple`: Für Listen von Auswahlmöglichkeiten (z.B. "Bus" oder "Bahn"),
die direkt in `conf.py` definiert werden.
* `SelectorSQL`: Für Listen von Auswahlmöglichkeiten, die auf Basis von einer
Datenbankabfrage gebildet werden.

Diese `Selector`-Klassen teilen die folgenden Parameter zur Initialisierung:
* `label (str)`: Bezeichnung des Selektors. Wird im UI angezeigt. Darüber hinaus
können mit Hilfe des Labels Abhängigkeiten zwischen den Selektoren eines `MapType`
definiert werden (siehe Parameter `depends_on_selectors`).
* `widget_method (streamlit widget)`: Eines der von streamlit bereitgestellten Widgets 
(z.B. st.radio oder st.selectbox). 
* `widget_args (dict, optional)`: Dictionary von Argumenten, das zur Initialisierung
des widget-Objekts weitergegeben wird (z.B. `{"help"="Hilfetext"}`).
* `no_value_selected_text (str, optional)`: Auswahlmöglichkeit, die angezeigt wird,
bevor ein Wert ausgewählt wurde (z.B. "Räumliche Ebene auswählen ...").
* `depends_on_selectors (Dict[str, Any], optional)`: Dictionary, in dem Bedingungen
definiert werden können, die erfüllt sein müssen, damit das Widget angezeigt wird. Damit 
können Abhängigkeiten zwischen Selektoren festgelegt werden. Als Keys müssen die Labels
von ebenfalls für denselben `MapType` definierten Selektoren verwendet werden, als
Values die Werte, die bei dem entsprechenden Selektor ausgewählt sein müssen. Wenn
z.B. beim Selektor mit dem Label "Räumliche Ebene" der Wert "Linie" ausgewählt sein
muss, dann ist `depends_on_selectors={"Räumliche Ebene": "Linie"}` zu setzen. Derzeit
kann nur auf Gleichheit geprüft werden. Wenn das Dictionary mehrere key/value-Paare
beinhaltet, müssen alle Bedingungen erfüllt sein (UND-Verknüpfung).

Die `SelectorSimple`-Klasse wird darüber hinaus mit dem folgenden Parameter 
initialisiert:
* `options (Iterable[Any])`: Iterable von Auswahlmöglichkeiten.

Die `SelectorSQL`-Klasse wird darüber hinaus mit dem folgenden Parameter initialisiert:
* `sql (str)`: SQL-Statement, das an die in `db.ini` definierte Datenbank geschickt wird
und eine Liste an Auswahlmöglichkeiten liefern soll, z.B.: `"select distinct 
liniennummer from strecken"`.


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

Eine kleine Generatorklasse mit drei Schritten könnte z.B. so aussehen: 

```python
from collections import OrderedDict
import time

from automaps.generators.base import MapGenerator, Step


class MapGeneratorUeberblick(MapGenerator):
    name = "ÖV-Überblick"

    def _set_steps(self):
        self.steps = OrderedDict(
            {
                "Projekt laden": Step(self.load_project, 0.5),
                "Layer filtern": Step(self.filter_layers, 1),
                "Karte exportieren": Step(self.export_layout, 0.5),
            }
        )

    def load_project(self):
        self.step_data.project = self._get_project()
        self.step_data.layout = self._get_print_layout(project)
        self._set_project_variable(self.step_data.project, "data", str(self.data))

    def filter_layers(self):
        layer = self.step_data.project.mapLayersByName("gem")[0]
        layer.setSubsetString(f"gem_name = '{self.data['Gemeinde']}'")
        self._set_project_variable(
            self.step_data.project, "gemeinde_aktiv", self.data["Gemeinde"]
        )

    def export_layout(self):
        self._export_print_layout(self.step_data.layout)
```


