# automaps

![](static/teaser.webm)

## Short description
__TODO__

## Architecture
__TODO__





## Start the Streamlit frontend + QGIS backend.
Execute from:

`./start_automaps.sh`. 

Possibly before:

`chmod +x start_automaps.sh`

The frontend is accessible at [http://localhost:8505/vormaps](http://localhost:8505/vormaps)
accessible. 

## Configuration
The following files and directories are relevant for the configuration:

    /conf.py
    /conf_local.py
    /conf_server.py
    /generators

### `/conf.py`
Here the configuration of the frontend and the map generation must be done in the variable
MAPTYPES_AVAIL` variable. This is a dictionary with the 
structure `Dict[str, MapType]`. 

As key of the dictionary a designation of the map type is to be assigned. This 
is displayed in the frontend for selection. 





### `/conf_local.py`
The following variables must be set here:

The directory path to store the generated maps (`BASEPATH_FILESERVER`), for example:

    BASEPATH_FILESERVER = `usr/local/lib/python3.8/dist-packages/streamlit/static/downloads`.

The directory path to the QGIS installation (`QGIS_INSTALLATION_PATH`). This can be set in the 
QGIS GUI in the Python Console with the following command:
`QgsApplication.prefixPath()`. Example:

    QGIS_INSTALLATION_PATH = "/usr".

The file path to the QGIS project file (`FILEPATH_QGIS_PROJECT`), for example:

    FILEPATH_QGIS_PROJECT = "/home/automaps/automaps_qgis/automaps_dev.qgz"

### `/conf_server.py`
The following variables must be set here:

The variable `GENERATORS` of type `Dict[str, MapGenerator]`. The keys to be used are those specified in 
`/conf.py` must be used as the `name` attributes of the `MapType` objects. As
values the corresponding map generators with the base class `MapGenerator`. 
(see below, `/generators`)

Example for `/conf_server.py`:

    from typing import Dict

    from automaps.generators import MapGeneratorOverview
    from automaps.generators.base import MapGenerator

    GENERATORS: Dict[str, MapGenerator] = {"public transport overview": MapGeneratorOverview}


### `/generators`
Here the individual map generators are created as a subclass of `MapGenerator` (to be found in 
in `/generators/base.py`).

For this purpose a new Python module is created in the package `generators`. This contains
the class definition of the generator. 



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
