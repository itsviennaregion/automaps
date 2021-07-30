from automaps.app import AutoMaps

app = AutoMaps(conf_path="./automapsconf.py")

# Aufruf mit python idee.py
# alternativ mit CLI: automaps idee.py (ev. mit Parametern)
# app startet frontend und server als sub processes
# conf wird von user geschrieben, kann aus mehreren py-Files bestehen
# conf beinhaltet alles aus conf_local, conf_server, conf und db.ini
# conf beinhaltet streamlit-Abteilung, Optionen werden an Streamlit weitergereicht

