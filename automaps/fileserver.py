import base64
import os
import uuid
import re


def download_link(download_filepath, link_text):
    filename = os.path.basename(download_filepath)
    dl_link = f'<a href="downloads/{filename}" download>{link_text}</a><br></br>'
    return dl_link


def download_button(download_filepath, button_text):
    filename = os.path.basename(download_filepath)
    button_uuid = str(uuid.uuid4()).replace("-", "")
    button_id = re.sub(r"\d+", "", button_uuid)

    custom_css = f"""
        <style>
            #{button_id} {{
                background-color: rgb(230, 230, 230);
                color: rgb(38, 39, 48);
                padding: 0.25em 0.38em;
                position: relative;
                text-decoration: none;
                border-radius: 4px;
                border-width: 1px;
                border-style: solid;
                border-color: rgb(230, 234, 241);
                border-image: initial;
            }}
            #{button_id}:hover {{
                border-color: rgb(246, 51, 102);
                color: rgb(246, 51, 102);
            }}
            #{button_id}:active {{
                box-shadow: none;
                background-color: rgb(246, 51, 102);
                color: white;
                }}
        </style> """

    dl_link = (
        custom_css
        + f'<a download="{filename}" id="{button_id}" '
        + f'href="downloads/{filename}">{button_text}</a><br></br>'
    )

    return dl_link
