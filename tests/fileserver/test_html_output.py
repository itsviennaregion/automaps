import os

from hypothesis import given, strategies as hst

from automaps.fileserver import download_button, download_link

import automapsconf


@given(download_filepath=hst.text(), link_text=hst.text())
def test_download_link(download_filepath, link_text):
    link = download_link(download_filepath, link_text)
    assert link[0] == "<"
    assert link[-1] == ">"
    assert "<a" in link
    assert "href=" in link
    assert f">{link_text}<" in link
    filename = os.path.basename(download_filepath)
    assert f"downloads/{filename}" in link


@given(download_filepath=hst.text(), button_text=hst.text())
def test_download_button(download_filepath, button_text):
    link = download_button(download_filepath, button_text)
    assert link[0] == "<"
    assert link[-1] == ">"
    assert "<a" in link
    assert "href=" in link
    assert f">{button_text}<" in link
    filename = os.path.basename(download_filepath)
    assert f"downloads/{filename}" in link
    assert "<style>" not in link


@given(download_filepath=hst.text(), button_text=hst.text())
def test_download_button_style(download_filepath, button_text):
    automapsconf.DOWNLOAD_BUTTON_STYLE = """
    <style>
        #{button_id} {{
            background-color: #99cc00;
            color: rgba(0,0,0,0.87);
            border: 0;
            padding: 0.35em 0.58em;
            position: relative;
            text-decoration: none;
            border-radius: 0.25rem;
        }}
        #{button_id}:hover {{
            background-color: #649b00;
        }}
        #{button_id}:active {{
            background-color: #99cc00;
            }}
        #{button_id}:focus:not(:active) {{
            background-color: #99cc00;
            }}
    </style> """
    link = download_button(download_filepath, button_text)
    assert "<style>" in link
