import pandas as pd
import os

def mark_assignments(st):
    csv_path = f"marks/{st.session_state.folder_id}.csv"
    df = pd.read_csv(csv_path)
    
    pdf_files = df['file_name'].tolist()[1:]  # Start from index 1
    file_ids = df['file_id'].tolist()[1:]  # Start from index 1
    
    main_col, sidebar_col = st.columns([0.7, 0.3])
    
    with main_col:
        if 1 <= st.session_state.current_file_index < len(df):
            current_file = pdf_files[st.session_state.current_file_index - 1]
            current_file_id = file_ids[st.session_state.current_file_index - 1]
            st.header(current_file)
            
            pdf_url = f"https://drive.google.com/file/d/{current_file_id}/preview"
            st.components.v1.iframe(pdf_url, width=None, height=600)
        else:
            st.warning("No file to display. Please check if there are any files in the folder.")
    
    with sidebar_col:
        st.sidebar.header("Rubrics")
        rubrics = df.columns[2:].tolist()
        
        checkbox_states = {}
        
        if 1 <= st.session_state.current_file_index < len(df):
            for rubric in rubrics:
                current_value = df.at[st.session_state.current_file_index, rubric] == 'True'
                checkbox_key = f"{file_ids[st.session_state.current_file_index - 1]}_{rubric}"
                checkbox_states[rubric] = st.sidebar.checkbox(rubric, value=current_value, key=checkbox_key)
        
        st.sidebar.markdown("---")
        col1, col2 = st.sidebar.columns([1, 1])
        with col1:
            if st.button("◀ Previous", use_container_width=True):
                update_marks(st, df, checkbox_states, csv_path)
                st.session_state.current_file_index = max(1, st.session_state.current_file_index - 1)
                st.rerun()
        
        with col2:
            if st.button("Next ▶", use_container_width=True):
                update_marks(st, df, checkbox_states, csv_path)
                st.session_state.current_file_index = min(len(df) - 1, st.session_state.current_file_index + 1)
                st.rerun()
        
        st.sidebar.markdown("<br>" * 5, unsafe_allow_html=True)
        
        if st.sidebar.button("Edit Rubrics", use_container_width=True):
            st.session_state.page = 'rubrics'
            st.rerun()
        
        weightage = df.iloc[0, 2:].astype(float)  
        attestments = df.iloc[1:, 2:].applymap(lambda x: (type(x) == bool and x) or (type(x) == str and x.lower() == 'true'))

        df_save = df.copy()
        df_save['aggregate_marks'] = attestments.apply(lambda row: (row * weightage).sum(), axis=1)

        # Display the resulting DataFrame
        st.sidebar.download_button(
            label="Download Marks",
            data=df_save.to_csv(index=False),
            file_name=f"{df.iloc[0]['file_id']}.csv",
            mime="text/csv",
            use_container_width=True
        )

def update_marks(st, df, checkbox_states, csv_path):
    if 1 <= st.session_state.current_file_index < len(df):
        for rubric, state in checkbox_states.items():
            df.at[st.session_state.current_file_index, rubric] = state
        df.to_csv(csv_path, index=False)
    else:
        st.warning("Unable to update marks. Invalid file index.")

