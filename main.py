import streamlit as st
import pandas as pd
import os
import re
from rubrics import manage_rubrics
from markings import mark_assignments
from drive import extract_files

def extract_folder_id(link):
    pattern = r'(?:https?:\/\/)?(?:www\.)?drive\.google\.com\/(?:drive\/folders\/|folderview\?id=)([a-zA-Z0-9_-]+)'
    return re.search(pattern, link).group(1) if re.search(pattern, link) else None

def manage_csv_file(folder_id):
    csv_path = f"marks/{folder_id}.csv"
    folder_name, files = extract_files(folder_id)
    files = files[files['type'] == 'application/pdf'].drop(columns=['type'])
    
    if not os.path.exists(csv_path):
        df = pd.DataFrame({'file_id': [folder_name], 'file_name': ['Marks']})
        df.to_csv(csv_path, index=False)
    else:
        df = pd.read_csv(csv_path)
    
    first_row = df.iloc[0]
    df = df.iloc[1:].reset_index(drop=True)
    
    df = pd.merge(df, files, how='left', left_on='file_id', right_on='id', suffixes=('', '_new'))
    df['file_name'] = df['name'].combine_first(df['file_name'])
    df = df.drop(columns=['id', 'name'])
    
    new_files = files[~files['id'].isin(df['file_id'])].rename(columns={'id': 'file_id', 'name': 'file_name'})
    df = pd.concat([df, new_files], ignore_index=True)
    df = df[df['file_id'].isin(files['id'])]
    df = pd.concat([pd.DataFrame([first_row]), df], ignore_index=True)
    
    df.to_csv(csv_path, index=False)
    return df

def main():
    st.set_page_config(page_title="Assignment Marker", layout="wide")
    
    if not os.path.exists("marks"):
        os.mkdir("marks")

    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    if 'current_file_index' not in st.session_state:
        st.session_state.current_file_index = 1
    if 'folder_id' not in st.session_state:
        st.session_state.folder_id = None

    st.sidebar.title("Assignment Marker")
    
    if st.session_state.page == 'home':
        st.title("Welcome to Assignment Marker")
        st.write("Enter the Google Drive folder link containing the assignments:")
        folder_link = st.text_input("Folder Link", key="folder_link")
        if st.button("Start Marking", key="start_marking"):
            folder_id = extract_folder_id(folder_link)
            if folder_id:
                st.session_state.folder_id = folder_id
                df = manage_csv_file(folder_id)
                st.session_state.page = 'rubrics' if len(df.columns) <= 2 else 'marking'
                st.rerun()
            else:
                st.error("Invalid Google Drive folder link. Please check the URL and try again.")

    elif st.session_state.page == 'rubrics':
        manage_rubrics(st)

    elif st.session_state.page == 'marking':
        mark_assignments(st)

if __name__ == "__main__":
    main()