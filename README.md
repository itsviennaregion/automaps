# Automatische Karten

![](static/teaser.webm)

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

Das Frontend ist unter [http://localhost:8505/vormaps](http://localhost:8505/vormaps)
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
* `ui_elements (Iterable[Union[BaseSelector, Tuple[Callable, str]]])`: Iterable von 
UI-Elementen, wobei es sich entweder um `Selector`-Objekte oder Tupel aus `st.write` und
einem String, z.B. `(st.write, "## Überschrift")` handeln kann. 
    * Mit `Selector`-Objekten werden die Auswahlmöglichkeiten, die im UI angezeigt 
    werden, definiert. Die Auswahl wird beim Start der Verarbeitung als 
    `self.data`-Attribut übergeben.
    * Mit Tupeln von der Art `(st.write, str)` können Texte im UI angezeigt werden,
    z.B. um Überschriften oder weitere Erklärungen darzustellen. Künftig werden
    eventuell auch andere streamlit-Methoden unterstützt.
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
            (st.write, "## Grundeinstellungen"),
            SelectorSimple(
                "Räumliche Ebene",
                ["Linie", "Gemeinde"],
                st.selectbox,
                widget_args={"help":"Hilfetext"},
                no_value_selected_text="Räumliche Ebene auswählen ...",
            ),
            SelectorSQL(
                "Gemeinde",
                "select distinct pg from bev_gemeinden",
                st.selectbox,
                no_value_selected_text="Gemeinde auswählen ...",
                depends_on_selectors={"Räumliche Ebene": "Gemeinde"},
            ),
            (st.write, "## Kartenelemente"),
            SelectorSQL(
                "Linien",
                """
                select distinct line_name
                from
                    pt_links l,
                    gemeinden g
                where
                    g.name = '{{ data["Gemeinde"] }}'
                    and ST_Intersects(l.geom, g.geom)
                """,
                st.multiselect,
                additional_values=["ALLE"],
                depends_on_selectors={"Räumliche Ebene": "Gemeinde"},
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
* `SelectorSQL`: Für Listen von Auswahlmöglichkeiten, die auf Basis einer
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

Die `SelectorSQL`-Klasse verfügt darüber zusätzlich über die folgenden 
Initialisierungsparameter:
* `sql (str)`: SQL-Statement, das an die in `db.ini` definierte Datenbank geschickt wird
und eine Liste an Auswahlmöglichkeiten liefern soll, z.B.: `"select distinct 
liniennummer from strecken"`. Der String kann 
[Jinja2](https://pypi.org/project/Jinja2/)-Ausdrücke zum Auslesen des 
`data`-Dictionaries mit den auswähltenden UI-Optionen beinhalten. 
Damit können die ausgewählten Werte eines im `MapType` als `ui_element` 
definierten Selektors in der SQL-Abfrage eines anderen Selektors verwendet werden. Auf 
diese Weise kann zum Beispiel die Auswahl von Buslinien auf jene Linien eingeschränkt 
werden, welche die ausgewählte Gemeinde schneiden. Für ein Beispiel siehe oben bei 
`MapType`. 
* `additional_values (Iterable[Any], optional)`: Iterable von zusätzlichen 
Auswahlmöglichkeiten, die den per SQL gewonnenen Werten vorangestellt werden,
z.B. `["ALLE"]`.


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

Bei der Initialisierung werden das zugehörige QGIS-Projekt (definiert in 
`/conf_local.py`) und das Druck-Layout (definiert mit dem Argument `print_layout`
in der Konfiguration des zugehörigen `MapType` in `/conf.py`) geladen. Die zwei 
geladenen Objekte werden in `self.step_data.project` und `self.step_data.layout` 
abgelegt und sind dort für alle Bearbeitungsschritte verfügbar.

Eine kleine Generatorklasse mit drei Schritten könnte z.B. so aussehen: 

```python
from collections import OrderedDict

from automaps.generators.base import MapGenerator, Step


class MapGeneratorUeberblick(MapGenerator):
    name = "ÖV-Überblick"

    def _set_steps(self):
        self.steps = OrderedDict(
            {
                "Projektvariablen setzen": Step(self.set_variables, 1),
                "Layer filtern": Step(self.filter_layers, 1),
                "Kartenausschnitt festlegen": Step(self.set_extent, 1),
                "Karte exportieren": Step(self.export_layout, 3),
            }
        )

    def set_variables(self):
        self._set_project_variable("gemeinde_aktiv", self.data["Gemeinde"])

    def filter_layers(self):
        self._set_map_layer_filter_expression(
                "bev_gemeinden", f"pg = '{self.data['Gemeinde']}'"
            )
    
    def set_extent(self):
        self._zoom_map_to_layer_extent(
            "Hauptkarte", self._get_map_layer("bev_gemeinden")
        )

    def export_layout(self):
        self._export_print_layout(self.step_data.layout)
```


