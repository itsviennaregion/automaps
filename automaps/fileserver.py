import base64
import os
import uuid
import re

import automapsconf


def download_link(download_filepath, link_text):
    filename = os.path.basename(download_filepath)
    dl_link = f'<a href="downloads/{filename}" download>{link_text}</a><br></br>'
    return dl_link


def download_button(download_filepath, button_text):
    filename = os.path.basename(download_filepath)
    button_uuid = str(uuid.uuid4()).replace("-", "")
    button_id = re.sub(r"\d+", "", button_uuid)

    if hasattr(automapsconf, "DOWNLOAD_BUTTON_STYLE") and automapsconf.DOWNLOAD_BUTTON_STYLE:
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
