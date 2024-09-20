import pandas as pd
import streamlit as st

def mark_assignments(st):
    csv_path = f"marks/{st.session_state.folder_id}.csv"
    df = pd.read_csv(csv_path)
    
    pdf_files = df['file_name'].tolist()
    file_ids = df['file_id'].tolist()
    
    main_col, sidebar_col = st.columns([0.7, 0.3])
    
    with main_col:
        current_file = pdf_files[st.session_state.current_file_index]
        current_file_id = file_ids[st.session_state.current_file_index]
        st.header(current_file)
        
        pdf_url = f"https://drive.google.com/file/d/{current_file_id}/preview"
        st.components.v1.iframe(pdf_url, width=None, height=600)
    
    with sidebar_col:
        st.sidebar.header("Rubrics")
        rubrics = df.columns[2:].tolist()
        
        checkbox_states = {}
        
        for rubric in rubrics:
            current_value = df.at[st.session_state.current_file_index, rubric] == 'True'
            checkbox_key = f"{current_file_id}_{rubric}"
            checkbox_states[rubric] = st.sidebar.checkbox(rubric, value=current_value, key=checkbox_key)
        
        st.sidebar.markdown("---")
        col1, col2 = st.sidebar.columns([1, 1])
        with col1:
            if st.button("◀ Previous", use_container_width=True):
                update_marks(df, checkbox_states, csv_path)
                st.session_state.current_file_index = max(1, st.session_state.current_file_index - 1)
                st.rerun()
        
        with col2:
            if st.button("Next ▶", use_container_width=True):
                update_marks(df, checkbox_states, csv_path)
                st.session_state.current_file_index = min(len(pdf_files) - 1, st.session_state.current_file_index + 1)
                st.rerun()
        
        st.sidebar.markdown("<br>" * 5, unsafe_allow_html=True)
        
        if st.sidebar.button("Edit Rubrics", use_container_width=True):
            st.session_state.page = 'rubrics'
            st.rerun()
        
        st.sidebar.download_button(
            label="Download Marks",
            data=df.to_csv(index=False),
            file_name=f"{df.iloc[0]['file_id']}.csv",
            mime="text/csv",
            use_container_width=True
        )

def update_marks(df, checkbox_states, csv_path):
    for rubric, state in checkbox_states.items():
        df.at[st.session_state.current_file_index, rubric] = state
    df.to_csv(csv_path, index=False)

if __name__ == "__main__":
    mark_assignments(st)