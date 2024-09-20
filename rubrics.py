import pandas as pd
import streamlit as st

def manage_rubrics(st):
    st.title("Manage Rubrics")

    # Custom CSS to align the delete button
    st.markdown("""
    <style>
    .stButton > button {
        margin-top: 1.7rem;
    }
    </style>
    """, unsafe_allow_html=True)

    csv_path = f"marks/{st.session_state.folder_id}.csv"
    df = pd.read_csv(csv_path)
    
    st.session_state.rubrics = df.columns[2:].tolist()
    
    for i, rubric in enumerate(st.session_state.rubrics):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            new_name = st.text_input(f"Rubric {i+1} Name", value=rubric, key=f"rubric_name_{i}")
        with col2:
            default_marks = int(df.loc[df['file_name'] == 'Marks', rubric].values[0])
            new_marks = st.number_input(f"Marks", value=default_marks, min_value=1, key=f"rubric_marks_{i}")
        with col3:
            if st.button("Delete", key=f"delete_rubric_{i}"):
                st.session_state.rubrics.pop(i)
                if rubric in df.columns:
                    df = df.drop(columns=[rubric])
                    df.to_csv(csv_path, index=False)
                    st.rerun()

        if new_name != rubric:
            if rubric in df.columns:
                df = df.rename(columns={rubric: new_name})
            st.session_state.rubrics[i] = new_name
            df.to_csv(csv_path, index=False)
            st.rerun()
            
        df.loc[df['file_name'] == 'Marks', new_name] = new_marks
        df.to_csv(csv_path, index=False)

    st.markdown("<br>", unsafe_allow_html=True)  # Add some space before the "Add Rubric" button

    if st.button("Add Rubric", key="add_rubric"):
        new_rubric = f"New Rubric {len(st.session_state.rubrics) + 1}"
        st.session_state.rubrics.append(new_rubric)
        df[new_rubric] = False
        df.loc[df['file_name'] == 'Marks', new_rubric] = 1
        df.to_csv(csv_path, index=False)
        st.rerun()
  
    st.markdown("<br>", unsafe_allow_html=True)  # Add some space before the "Go to Marking" button

    if st.button("Go to Marking", key="go_to_marking"):
        st.session_state.page = 'marking'
        df.to_csv(csv_path, index=False)
        st.rerun()