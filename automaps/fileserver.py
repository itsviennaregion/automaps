import os
import pathlib
from pathlib import Path
from typing import Iterable, Iterator
import uuid
import re
import time

import streamlit as st

from automaps.confutils import has_config_option
import automapsconf


class DownloadPathJanitor:
    def __init__(
        self,
        download_path: str,
        max_seconds: int = 3600 * 8,
        file_extensions: Iterable[str] = ["PDF", "PNG", "SVG"],
    ):
        """Deletes old files in download path.

        Args:
            download_path (str): Path to search for old files. Normally:
                automapsconf.BASEPATH_FILESERVER
            max_seconds (int, optional): Only files which are older than this value
                (in seconds) get deleted. Defaults to 3600*8.
            file_extensions (Iterable[str], optional): Only files with one of these
                extensions get deleted. Defaults to ["PDF", "PNG", "SVG"].
        """
        self.path = Path(download_path)
        assert self.path.stem == "downloads"
        self.max_seconds = max_seconds
        self.file_extensions = ["." + x.upper() for x in file_extensions]

    def clean(self):
        """Searches for old files in download path and deletes them."""
        self._delete_files(self._find_old_files())

    def _find_all_files(self) -> Iterator[Path]:
        return (
            x for x in self.path.iterdir() if x.suffix.upper() in self.file_extensions
        )

    def _find_old_files(self) -> Iterator[Path]:
        now = time.time()
        return (
            x
            for x in self._find_all_files()
            if x.stat().st_mtime < now - self.max_seconds
        )

    @staticmethod
    def _delete_files(files: Iterable[Path]):
        for file in files:
            file.unlink()


def get_streamlit_download_path() -> Path:
    streamlit_static_path = pathlib.Path(st.__path__[0]) / "static"
    download_path = streamlit_static_path / "downloads"
    return download_path


def create_streamlit_download_path():
    download_path = get_streamlit_download_path()
    if not download_path.is_dir():
        download_path.mkdir()
        print(
            f"Download path '{download_path}' has been created. Maybe you need to "
            f"change the permissions (e.g. sudo chmod -R a+w {download_path})."
        )
    else:
        print(download_path)


def download_link(download_filepath, link_text):
    filename = os.path.basename(download_filepath)
    dl_link = f'<a href="downloads/{filename}" download>{link_text}</a><br></br>'
    return dl_link


def download_button(download_filepath, button_text):
    filename = os.path.basename(download_filepath)
    button_uuid = str(uuid.uuid4()).replace("-", "")
    button_id = re.sub(r"\d+", "", button_uuid)

    if has_config_option("DOWNLOAD_BUTTON_STYLE"):
        custom_css = automapsconf.DOWNLOAD_BUTTON_STYLE.format(button_id=button_id)
    else:
        custom_css = ""

    dl_link = (
        custom_css
        + '<div class="row-widget stButton">'
        + f'<a download="{filename}" id="{button_id}" '
        + f'href="downloads/{filename}">{button_text}</a><br></br>'
        + "</div>"
    )

    return dl_link
