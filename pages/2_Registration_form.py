

#---------------------------------------------------------------------
import streamlit as st  # ✅ direct import
import numpy as np
import cv2
from streamlit_webrtc import webrtc_streamer
import av
from Home import face_rec

st.set_page_config(page_title='Registration Form', layout='centered')
st.subheader('Registration Form')

registration_form = face_rec.Registration_form()

person_name = st.text_input(label='Name', placeholder='Enter Full Name')
role = st.selectbox(label='Select Your Role', options=('Teacher', 'Student'))

def video_callback_func(frame):
    img = frame.to_ndarray(format="bgr24")
    reg_img, embedding = registration_form.get_embedding(img)

    if embedding is not None:
        with open("face_embedding.txt", mode='ab') as f:
            np.savetxt(f, embedding.reshape(1, -1))  # ✅ correct shape

    return av.VideoFrame.from_ndarray(reg_img, format="bgr24")

webrtc_streamer(key='registration', video_frame_callback=video_callback_func,
                rtc_configuration={
                            "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
                    }    
                )


if st.button("Submit"):
    return_val = registration_form.save_data_in_redis_db(person_name, role)

    if return_val == True:
        st.success(f"{person_name} registered successfully")
    elif return_val == "Not a valid Name and Role":
        st.error("Please enter a valid Name and Role")
    elif return_val == 'Not a valid File':
        st.error("face_embedding.txt not found — please capture face first")
    