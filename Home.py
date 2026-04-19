import streamlit as st


st.set_page_config(page_title="Attendance App",
                    page_icon="🧊",
                    layout="wide",
                    initial_sidebar_state="expanded",)


st.header('Attendance System using Face Recognition')

with st.spinner("Loading Models"):
    import face_rec


st.success("Models Loaded SuccessFully")
st.success("Redis connection : Success💯")

