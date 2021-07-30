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
* `ui_elements (Iterable[Union[MultiSelector, BaseSelector, Tuple[Callable, str]]])`: 
Iterable von UI-Elementen, wobei es sich entweder um `Selector`-Objekte oder Tupel aus 
`st.write` und einem String, z.B. `(st.write, "## Überschrift")` handeln kann. 
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
        ui_elements=[
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

__`BaseSelector`-Klassen__

Es stehen zwei von `selector.BaseSelector` abgeleitete Selector-Klassen zur Verfügung:

* `SelectorSimple`: Für Listen von Auswahlmöglichkeiten (z.B. "Bus" oder "Bahn"),
die direkt in `conf.py` definiert werden.
* `SelectorSQL`: Für Listen von Auswahlmöglichkeiten, die auf Basis einer
Datenbankabfrage gebildet werden.

Diese `Selector`-Klassen teilen die folgenden Parameter zur Initialisierung:
* `label (str)`: Bezeichnung des Selektors. Wird im UI angezeigt. Darüber hinaus
können mit Hilfe des Labels Abhängigkeiten zwischen den Selektoren eines `MapType`
definiert werden (siehe Parameter `depends_on_selectors`).
* `widget_method (Callable, optional)`: Eines der von streamlit bereitgestellten Widgets 
(z.B. st.radio oder st.selectbox). Wird kein Argument oder `None` übergeben, wird im
UI kein Widget zur Auswahl von Werten angezeigt. Die (z.B. durch eine SQL-Abfrage)
erstellte Liste von Optionen ist aber dennoch verfügbar und kann über das 
`self.data`-Attribut des zugehörigen `MapType` abgefragt werden. Mit diesem Mechanismus
lassen sich z.B. im Hintergrund SQL-Abfragen durchführen, deren Ergebnis zwar nicht
unmittelbar im UI sichtbar und auswählbar sein soll, das aber von nachfolgenden 
Selektoren genutzt werden kann.
* `widget_args (dict, optional)`: Dictionary von Argumenten, das zur Initialisierung
des widget-Objekts weitergegeben wird (z.B. `{"help"="Hilfetext"}`).
* `no_value_selected_text (str, optional)`: Auswahlmöglichkeit, die angezeigt wird,
bevor ein Wert ausgewählt wurde (z.B. "Räumliche Ebene auswählen ...").
* `depends_on_selectors (Union[List[str], Dict[str, Any]], optional)`: 
Damit können Bedingungen definiert werden, die erfüllt sein müssen, damit das Widget
angezeigt wird. Damit können Abhängigkeiten zwischen Selektoren festgelegt werden. 
Es kann entweder eine Liste oder ein Dictionary übergeben werden:

    * __Dictionary__: 
Als Keys müssen die Labels
von ebenfalls für denselben `MapType` definierten Selektoren verwendet werden, als
Values die Werte, die bei dem entsprechenden Selektor ausgewählt sein müssen. Wenn
z.B. beim Selektor mit dem Label "Räumliche Ebene" der Wert "Linie" ausgewählt sein
muss, dann ist `depends_on_selectors={"Räumliche Ebene": "Linie"}` zu setzen. Derzeit
kann nur auf Gleichheit geprüft werden. Wenn das Dictionary mehrere key/value-Paare
beinhaltet, muss nur eine der Bedingungen erfüllt sein (ODER-Verknüpfung).

    * __Liste__:
Eine Liste von Selektor-Labels von Selektoren desselben `MapType`. Wenn die 
entsprechenden Selektoren entweder `None` oder den Defaulttext 
(`no_value_selected_text`) als Wert annehmen, wird das Widget nicht angezeigt.
Beispielsweise kann ein Selektor für ÖV-Linien erst dann angezeigt werden, wenn zuvor
eine Gemeinde ausgewählt wurde (`depends_on_selectors=["Gemeinde"]`). Wenn die Liste
mehrere Selektor-Labels umfasst, wird das Widget angezeigt, sobald bei einem der
gelisteten Selektoren ein Wert ausgewählt wurde (ODER-Verknüpfung).
* `label_ui (str, optional)`: Alternative Bezeichnung des Widgets, die im UI angezeigt
werden soll.
* `optional (bool, optional, default False)`: Gibt an, ob das Widget optional ist, ob
also die Kartenerzeugung gestartet werden kann, obwohl das Widget den Defaultwert
(`no_value_selected_text`) oder eine leere Liste als Ergebnis übergibt. Hat Einfluss
auf das Setzen des flags `has init values` im zugehörigen `MapType`.
* `exclude_from_filename (bool, optional, default False)`: Wenn `True`, dann wird der
Wert / die Werte des Selektors nicht zur Erzeugung des Dateinamens herangezogen. 

Die `SelectorSimple`-Klasse wird darüber hinaus mit dem folgenden Parameter 
initialisiert:
* `options (Iterable[Any])`: Iterable von Auswahlmöglichkeiten.

Die `SelectorSQL`-Klasse verfügt zusätzlich über die folgenden 
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
* `provide_raw_options (Boolean, optional)`: Dem Data Dictionary des zugehörigen
`MapType` kann damit ein neuer Eintrag hinzugefügt werden. Dieser hat als Key den 
Namen des Selektors mit angehängtem `" OPTIONS"` und als Value alle zur Auswahl 
stehenden Optionen, unabhängig davon, welche im UI ausgewählt wurde. Default `False`. 

__`MultiSelector`-Klasse__

Zusätzlich zu den beiden von `BaseSelector` abgeleiteten Klassen steht der
`MultiSelector` zur Verfügung. Damit können mehrere Selektoren zusammengefasst werden.
Diese Selektoren sollten einander ausschließende Abhängigkeiten haben (definiert 
mit `depends_on_selectors`). Der erste über die `selectors`-Liste übergebene Selektor,
der einen Wert ungleich `None` zurückliefert, wird genutzt, um im `data`-Dictionary
einen Eintrag mit dem `label` des `MultiSelector` als Key anzulegen.

Die `MultiSelector`-Klasse wird mit den folgenden Parametern initialisiert:
* `label (str)`: Bezeichnung des Selektors. Wird im UI angezeigt. 
* `selectors (List[BaseSelector])`: Liste von `BaseSelector`-Objekten, siehe oben.
* `exclude_from_filename (bool, optional, default False)`: Wenn `True`, dann wird der
Wert / die Werte des Selektors nicht zur Erzeugung des Dateinamens herangezogen. 

Beispiel:

```python
MultiSelector(
    "Haltestellen",
    [
        SelectorSimple(
        "Haltestellen a",
        ["Alle", "Keine"],
        st.radio,
        depends_on_selectors={
            "Linien in der Gemeinde": [],
            "Linien im Bezirk": [],
            "Linien in Ausschreibungsregion": [],
            "Linien im Bundesland": [],
        },
        label_ui="Haltestellen",
    ),
    SelectorSimple(
        "Haltestellen b",
        ["Alle", "Bediente Haltestellen", "Keine"],
        st.radio,
        depends_on_selectors=[
            "Linien in der Gemeinde",
            "Linien im Bezirk",
            "Linien in Ausschreibungsregion",
            "Linien im Bundesland",
        ],
        label_ui="Haltestellen",
    ),
],
),
```

### `/conf_local.py`
Hier müssen die folgenden Variablen festgelegt werden:

Der Verzeichnispfad zum Speichern der erzeugten Karten (`BASEPATH_FILESERVER`), z.B.:

    BASEPATH_FILESERVER = "/usr/local/lib/python3.8/dist-packages/streamlit/static/downloads"

Der Verzeichnispfad zur QGIS-Installation (`QGIS_INSTALLATION_PATH`). Dieser kann im 
QGIS GUI in der Python Console mit folgendem Befehl eruiert werden:
`QgsApplication.prefixPath()`. Beispiel:

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

## Kartenlayer


### Steig Betriebszweig
```sql
-- drop view automaps_lin;
create or replace view automaps_lin as
select
    row_number () over (),
	lin.subnetwork,
    lin.opbranch,
    lin.fromstopid,
    lin.fromstopar,
    lin.fromstoppi,
    lin.tostopid,
    lin.tostopar,
    lin.tostoppi,
    lin.linediva,
    lin.lineefa,
    lin.project,
    lin.direction,
    lin.sequenceno,
    lin.geom::geometry(Linestring, 32633) as geom,
	bz.kurzbezeichnung kurz,
	case
		when bz.kode in (1, 4, 5, 6, 7, 9, 10)  then 'Bahn'
		when bz.kode in (21, 31)  then 'U-Bahn'
		when bz.kode in (11, 22, 32)  then 'Tram'
		when bz.kode in (23, 24, 33, 34, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 76, 77, 79, 81, 82, 86, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99)  then 'Bus'
		when bz.kode in (8, 25, 35, 73)  then 'Mikro V'
		else 'Unbekannt'
	end typ
from ptlinks_ptl_polyline lin
left join betriebszweige bz on bz.kode = lin.opbranch
;
```

### Steig Betriebszweig
```sql
-- drop view automaps_stg;
-- drop view automaps_hst;
-- drop view automaps_stg_class;
create or replace view automaps_stg_class as
select distinct
	stopid,
    stopareaid,
    stoppingpo,
	array_agg(lin_id) linien,
	array_agg(distinct kurz),
	case
		when array_agg(kode) && array[1, 4, 5, 6, 7, 9, 10]  then 'Bahn'
		when array_agg(kode) && array[21, 31]  then 'U-Bahn'
		when array_agg(kode) && array[11, 22, 32]  then 'Tram'
		when array_agg(kode) && array[23, 24, 33, 34, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 76, 77, 79, 81, 82, 86, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]  then 'Bus'
		when array_agg(kode) && array[8, 25, 35, 73]  then 'Mikro V'
		else 'Unbekannt'
	end typ
from (
select
	lin.fromstopid stopid,
	lin.fromstopar stopareaid,
	lin.fromstoppi stoppingpo,
	lin.lineefa lin_id,
	bz.kurzbezeichnung kurz,
	bz.kode
from ptlinks_ptl_polyline lin
left join betriebszweige bz on bz.kode = lin.opbranch
union
select
	lin.tostopid stopid,
	lin.tostopar stopareaid,
	lin.tostoppi stoppingpo,
	lin.lineefa lin_id,
	bz.kurzbezeichnung kurz,
	bz.kode
from ptlinks_ptl_polyline lin
left join betriebszweige bz on bz.kode = lin.opbranch
) unioned
group by
	stopid,
    stopareaid,
    stoppingpo
;
```

### Steig
```sql
-- drop view automaps_stg;
create or replace view automaps_stg as
select
    stg.subnetwork,
    stg.stopid,
    stg.stopareaid,
    stg.stoppingpo,
    stg.drawclass,
    stg.name1,
    stg.name2,
    stg.globalid,
    stg.servingsta,
    stg.geom::geometry(Point, 32633) as geom,
    hst.name1 as hst_name,
    st_x(hst.geom) as hst_x,
    st_y(hst.geom) as hst_y,
    cla.typ,
    cla.linien
from stoppingpoints_stp_point stg
left join stops_stp_point hst on stg.stopid = hst.stopid
left join automaps_stg_class cla on stg.stopid = cla.stopid 
    and stg.stopareaid = cla.stopareaid 
    and stg.stoppingpo = cla.stoppingpo
;
```

### Haltestelle
```sql
-- drop view automaps_hst;
create or replace view automaps_hst as
select
    hst.subnetwork,
    hst.stopid,
    hst.drawclass,
    hst.name1,
    hst.name2,
    hst.tarifzone,
    hst.attributes,
    hst.servinglin,
    hst.globalid,
    hst.servingsta,
    hst.name0,
    hst.geom::geometry(Point, 32633) as geom,
    case
        when array_agg(cla.typ) && array['Bahn']  then 'Bahn'
		when array_agg(cla.typ) && array['U-Bahn']  then 'U-Bahn'
		when array_agg(cla.typ) && array['Tram']  then 'Tram'
		when array_agg(cla.typ) && array['Bus']  then 'Bus'
		when array_agg(cla.typ) && array['Mikro V']  then 'Mikro V'
		else 'Unbekannt'
	end typ
from stops_stp_point hst
left join automaps_stg_class cla on hst.stopid = cla.stopid
group by
	hst.subnetwork,
    hst.stopid,
    hst.drawclass,
    hst.name1,
    hst.name2,
    hst.tarifzone,
    hst.attributes,
    hst.servinglin,
    hst.globalid,
    hst.servingsta,
    hst.name0,
    hst.geom
;
```
