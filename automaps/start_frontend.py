import sys
import time
from uuid import uuid1

conf_path, automaps_path = sys.argv[1:]
if conf_path not in sys.path:
    sys.path.insert(0, conf_path)
if automaps_path not in sys.path:
    sys.path.append(automaps_path)

import logging
import os
import pathlib
import traceback

import streamlit as st

from automaps.fileserver import (
    copy_static_content,
    download_button,
    DownloadPathJanitor,
    get_streamlit_download_path,
    create_streamlit_download_path,
)
from automaps.client.client import (
    ask_registry_for_idle_worker,
    ask_server_for_steps,
    send_job_cancellation_to_worker,
    send_job_finished_confirmation_to_server,
    send_task_to_server,
)
from automaps.confutils import get_config_value, get_default_args, has_config_option
import automaps.logutils as lu
import automapsconf
from automapsconf import MAPTYPES_AVAIL

PING_FOR_IDLE_WORKER_MAX_N_SECONDS_IN_TOTAL = 60
PING_FOR_IDLE_WORKER_EVERY_N_SECONDS = 0.5
MAX_PINGS = int(
    PING_FOR_IDLE_WORKER_MAX_N_SECONDS_IN_TOTAL / PING_FOR_IDLE_WORKER_EVERY_N_SECONDS
)


def _get_maptype_names():
    return [x.name for x in MAPTYPES_AVAIL]


def _get_maptype(name: str):
    for maptype in MAPTYPES_AVAIL:
        if name == maptype.name:
            return maptype


def start_frontend():
    _init()

    # Delete old files in download path
    if hasattr(automapsconf, "DOWNLOADS_RETAIN_TIME"):
        j = DownloadPathJanitor(
            get_streamlit_download_path(), automapsconf.DOWNLOADS_RETAIN_TIME
        )
    else:
        j = DownloadPathJanitor(get_streamlit_download_path())
    j.clean()

    # Add custom elements to UI
    _set_page_config()
    _copy_static_content()
    _show_logo()
    _show_project_title()
    _add_custom_html()

    # Show available map types and get selected value
    maptype_dict_key = st.sidebar.radio(
        get_config_value("MAPTYPE_TEXT", "Map type"), _get_maptype_names()
    )

    # Instantiate MapType object
    maptype = _get_maptype(maptype_dict_key)

    # Show information about the selected map type
    st.write(f"# {maptype.name}{maptype.html_beneath_name}", unsafe_allow_html=True)
    st.write(f"{maptype.description}", unsafe_allow_html=True)

    # Show widgets if conditions defined by Selector argument `depends_on_selectors`
    # are satisfied) and get selected values
    selector_values = maptype.selector_values

    # Create map TODO: Refactoring
    if st.button(get_config_value("CREATE_MAP_BUTTON_TEXT", "Create map")):

        # If there is an active job for this frontend, cancel it.
        # This prevents workers from keep hanging in states INITIALIZATION or PROCESSING.
        if st.session_state.get("active_job", None) is not None:
            send_job_cancellation_to_worker(
                st.session_state["active_job"], st.session_state["active_worker_port"]
            )

        # If there are required selections missing, inform user.
        if selector_values.get("has_init_values", False):
            st.info(
                get_config_value(
                    "MISSING_ATTRIBUTES_TEXT",
                    "Please define all required map attributes!",
                )
            )

        # Otherwise: Try to start processing
        else:
            job_uuid = ""
            worker_info = {}
            worker_port = None
            job_finished = False
            try:
                progress_bar = st.progress(0)
                progress = 0

                # Search for idle workers
                with st.spinner(
                    get_config_value(
                        "WAITING_FOR_SERVER_TEXT", "Waiting for map server ..."
                    )
                ):
                    worker_info = ask_registry_for_idle_worker(
                        st.session_state["frontend_uuid"]
                    )
                    worker_port = worker_info["idle_worker_port"]
                    i = 0
                    while worker_port is None and i < MAX_PINGS:
                        time.sleep(PING_FOR_IDLE_WORKER_EVERY_N_SECONDS)
                        worker_info = ask_registry_for_idle_worker(
                            st.session_state["frontend_uuid"]
                        )
                        worker_port = worker_info["idle_worker_port"]
                        i += 1

                    if worker_port is not None:
                        job_uuid = "J-" + str(uuid1())
                        st.session_state["active_job"] = job_uuid
                        st.session_state["active_worker_port"] = worker_port
                        logging.getLogger("frontend").info(
                            f"Frontend {lu.shorten_uuid(st.session_state['frontend_uuid'])}"
                            f" initialized job {lu.shorten_uuid(job_uuid)} for worker "
                            f"{lu.shorten_uuid(worker_info['idle_worker_uuid'])} on port "
                            f"{worker_port}"
                        )
                        steps = ask_server_for_steps(
                            maptype_dict_key, job_uuid, worker_port
                        )
                        logging.getLogger("frontend").info(
                            f"Worker {lu.shorten_uuid(worker_info['idle_worker_uuid'])} "
                            f"on port {worker_port} accepted job "
                            f"{lu.shorten_uuid(job_uuid)}"
                        )

                # Idle worker has been found
                if worker_port is not None:
                    for step in steps:
                        with st.spinner(
                            get_config_value(
                                "SPINNER_TEXT", "Creating map _{maptype_name}_ ({step})"
                            ).format(maptype_name=maptype.name, step=step)
                        ):
                            logging.getLogger("frontend").debug(
                                f"Frontend {lu.shorten_uuid(st.session_state['frontend_uuid'])} "
                                f"is requesting step '{step}' "
                                f"for job {lu.shorten_uuid(job_uuid)} from worker "
                                f"{lu.shorten_uuid(worker_info.get('idle_worker_uuid', None))} "
                                f"on port {worker_port}"
                            )
                            step_message = send_task_to_server(
                                maptype_dict_key,
                                selector_values,
                                maptype.print_layout,
                                step,
                                str(job_uuid),
                                worker_port,
                            )
                            progress += float(step_message["rel_weight"])
                            progress_bar.progress(progress)
                    progress_bar.progress(1.0)
                    st.success(
                        get_config_value(
                            "MAP_READY_TEXT", "Map _{maptype_name}_ ready"
                        ).format(maptype_name=maptype.name)
                    )
                    _show_download_button(step_message["filename"])
                    logging.getLogger("frontend").debug(
                        f"Frontend {lu.shorten_uuid(st.session_state['frontend_uuid'])} "
                        f"received results of finished job "
                        f"{lu.shorten_uuid(job_uuid)} from worker "
                        f"{lu.shorten_uuid(worker_info.get('idle_worker_uuid', None))} "
                        f"on port {worker_port}"
                    )
                    job_finished = True

                # No idle worker has been found
                else:
                    st.info(
                        get_config_value(
                            "NO_SERVER_AVAILABLE_TEXT",  # TODO: automapsconf.py
                            "Map server is busy, please retry later!",
                        )
                    )

            except Exception as e:
                _show_error_message(e)

            # All this is done, even if the browser window is closed
            finally:

                # If idle worker has been found and job is finished:
                # Send job finished confirmation
                if worker_port is not None and job_finished:
                    logging.getLogger("frontend").info(
                        f"Frontend {lu.shorten_uuid(st.session_state['frontend_uuid'])} "
                        f"is sending job finished confirmation for job "
                        f"{lu.shorten_uuid(job_uuid)} "
                        f"to worker "
                        f"{lu.shorten_uuid(worker_info.get('idle_worker_uuid', None))} "
                        f"on port {worker_port}"
                    )
                    send_job_finished_confirmation_to_server(job_uuid, worker_port)

                # If idle worker has been found, but job has not been finished
                # Send job cancellation to worker
                elif worker_port is not None and not job_finished:
                    logging.getLogger("frontend").info(
                        f"Frontend {lu.shorten_uuid(st.session_state['frontend_uuid'])} "
                        f"is sending job cancellation for job "
                        f"{lu.shorten_uuid(job_uuid)} "
                        f"to worker "
                        f"{lu.shorten_uuid(worker_info.get('idle_worker_uuid', None))} "
                        f"on port {worker_port}"
                    )
                    send_job_cancellation_to_worker(job_uuid, worker_port)

                # No idle worker has been found:
                # just do some logging
                else:
                    logging.getLogger("frontend").warning(
                        f"Frontend {lu.shorten_uuid(st.session_state['frontend_uuid'])} "
                        f"could not find idle worker. Job cancelled before "
                        f"initialization."
                    )

                st.session_state["active_job"] = None

    _show_debug_info(selector_values)


def _init():
    if "frontend_uuid" not in st.session_state:
        st.session_state["frontend_uuid"] = "F-" + str(uuid1())
        logging.getLogger("frontend").info(
            "Frontend initalized with uuid "
            f"{lu.shorten_uuid(st.session_state['frontend_uuid'])}"
        )
    if not hasattr(automapsconf, "init_done"):
        create_streamlit_download_path()
        # _copy_static_content()
        logging.getLogger("frontend").setLevel(
            get_config_value("LOG_LEVEL_SERVER", logging.INFO)
        )
        lu.add_file_handler(logging.getLogger("frontend"))
        logging.getLogger("frontend").info("Automaps initialized!")
        logging.getLogger("frontend").info(
            f"Download path: {get_streamlit_download_path()}"
        )
        max_seconds = (
            automapsconf.DOWNLOADS_RETAIN_TIME
            if hasattr(automapsconf, "DOWNLOADS_RETAIN_TIME")
            else get_default_args(DownloadPathJanitor.__init__)["max_seconds"]
        )
        logging.getLogger("frontend").info(
            f"Downloads are retained for {max_seconds} seconds "
            f"({max_seconds / 3600:.1f} hours)."
        )

        automapsconf.init_done = True


@st.cache
def _copy_static_content():
    if get_config_value("STATIC_PATH"):
        project_static_path, streamlit_static_path = copy_static_content()
        logging.getLogger("frontend").info(
            f"Static content copied from {project_static_path} to "
            f"frontend static content path {streamlit_static_path}"
        )


def _show_download_button(filename: str):
    download_button_str = download_button(
        os.path.basename(filename),
        "Download",
        filename_for_user="_".join(os.path.basename(filename).split("_")[1:]),
    )
    st.markdown(download_button_str, unsafe_allow_html=True)


def _show_error_message(exception: Exception):
    st.error(f"Sorry, there has been an error: {exception}")
    tb = traceback.format_exc()
    st.error(tb)


def _show_logo():
    if has_config_option("LOGO_PATH"):
        st.sidebar.write(
            f"""
        <a href="./">
            <img src="{automapsconf.LOGO_PATH}" alt="Logo" style="margin-bottom: 3rem;">
        </a>
        """,
            unsafe_allow_html=True,
        )


def _set_page_config():
    favicon_path = get_config_value("FAVICON_PATH", None)
    page_title = get_config_value("PAGE_TITLE", None)
    st.set_page_config(page_title=page_title, page_icon=favicon_path)


def _show_project_title():
    if has_config_option("PROJECT_TITLE"):
        st.sidebar.markdown(f"# {automapsconf.PROJECT_TITLE}")
        st.sidebar.markdown("#")


def _add_custom_html():
    if has_config_option("CUSTOM_HTML"):
        st.markdown(automapsconf.CUSTOM_HTML, unsafe_allow_html=True)


def _show_debug_info(selector_values):
    if get_config_value("SHOW_DEBUG_INFO"):
        # Show selected values for all widgets (for debugging)
        if st.checkbox("Debug"):
            st.write("## Debug Info")
            st.write(f"Frontend UUID: `{st.session_state['frontend_uuid']}`")
            for k, v in selector_values.items():
                st.write(f"{k}: __{v}__")


if __name__ == "__main__":
    start_frontend()
