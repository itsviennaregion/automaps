from pathlib import Path

from automaps.fileserver import (
    create_streamlit_download_path,
    get_streamlit_download_path,
)


def test_get_streamlit_download_path():
    p = get_streamlit_download_path()
    assert isinstance(p, Path)
    assert (p / "..").resolve().exists()


def test_create_streamlit_download_path():
    create_streamlit_download_path()
    p = get_streamlit_download_path()
    assert p.exists()
