from gdown.download import _get_session
from gdown.download_folder import _parse_google_drive_file
from gdown.parse_url import is_google_drive_url
import pandas as pd
import streamlit as st

@st.cache_data
def extract_files(folder_id):
    url = f"https://drive.google.com/drive/folders/{folder_id}"
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
    sess = _get_session(proxy=None, use_cookies=True, user_agent=user_agent)

    for _ in range(2):
        if is_google_drive_url(url):
            url += "&hl=en" if "?" in url else "?hl=en"

        res = sess.get(url, verify=True)
        if res.status_code != 200:
            st.error("Failed to access the Google Drive folder. Please check the folder permissions and try again.")
            st.stop()

        if is_google_drive_url(url) or not is_google_drive_url(res.url):
            break

        url = res.url

    gdrive_file, id_name_type_iter = _parse_google_drive_file(url=url, content=res.text)
    return gdrive_file.name, pd.DataFrame(id_name_type_iter, columns=['id', 'name', 'type'])