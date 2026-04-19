

#  _____________________________
import streamlit as st
import pandas as pd
import numpy as np
from Home import face_rec
from streamlit_webrtc import webrtc_streamer
import av
import time
import threading

DATABASE_NAME = 'academy:register'
WAIT_TIME = 30

st.set_page_config(page_title='Real Time Prediction', layout='centered')
st.subheader('Real Time Prediction')

if 'redis_face_db' not in st.session_state:
    with st.spinner("Retrieving Data from Database..."):
        st.session_state['redis_face_db'] = face_rec.retrieve_data(DATABASE_NAME)

st.dataframe(st.session_state['redis_face_db'])
st.success('Data Retrieved Successfully')

# ✅ Plain module-level variables — NOT session_state inside callback
realtimepred = face_rec.RealTimePred()
redis_face_db = st.session_state['redis_face_db']
set_time = time.time()
frame_count = 0
last_frame = None
lock = threading.Lock()

def save_logs_background():
    try:
        realtimepred.saveLogs_redis()
        print("✅ Logs saved to Redis")
    except Exception as e:
        print(f"❌ Redis save error: {e}")

def video_frame_callback(frame):
    global set_time, frame_count, last_frame

    img = frame.to_ndarray(format="bgr24")
    frame_count += 1

    if frame_count % 3 == 0:
        with lock:
            pred_img = realtimepred.face_prediction(
                img, redis_face_db,
                'facial_features',
                ['Name', 'Role'],
                thresh=0.5
            )
            last_frame = pred_img
    else:
        with lock:
            pred_img = last_frame if last_frame is not None else img

    timenow = time.time()
    if timenow - set_time >= WAIT_TIME:
        thread = threading.Thread(target=save_logs_background)
        thread.daemon = True
        thread.start()
        set_time = time.time()

    return av.VideoFrame.from_ndarray(pred_img, format="bgr24")

webrtc_streamer(
    key="realtimePrediction",
    video_frame_callback=video_frame_callback,
    media_stream_constraints={"video": True, "audio": False},
     rtc_configuration={
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    }
) 