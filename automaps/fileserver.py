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
                background-color: #99cc00;
                color: rgba(0,0,0,0.87);
                border: 0;
                padding: 0.25em 0.38em;
                position: relative;
                text-decoration: none;
                border-radius: 0.25rem;
            }}
            #{button_id}:hover {{
                background-color: #649b00;
                color: rgba(0,0,0,0.87);
                border: 0;
                border-radius: 0.25rem;
            }}
            #{button_id}:active {{
                background-color: #99cc00;
                color: rgba(0,0,0,0.87);
                border: 0;
                border-radius: 0.25rem;
                }}
            #{button_id}:focus:not(:active) {{
                background-color: #99cc00;
                color: rgba(0,0,0,0.87);
                border: 0;
                border-radius: 0.25rem;
                }}
        </style> """

    dl_link = (
        custom_css
        + '<div class="row-widget stButton">'
        + f'<a download="{filename}" id="{button_id}" '
        + f'href="downloads/{filename}">{button_text}</a><br></br>'
        + "</div>"
    )

    return dl_link
