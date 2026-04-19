from dotenv import load_dotenv
load_dotenv()  # loads .env variables into os.environ
import pandas as pd
import numpy as np
import cv2
import time
from datetime import datetime
import os

import redis

# Insightface
from insightface.app import FaceAnalysis
from sklearn.metrics import pairwise

# ✅ Redis Connection via Environment Variables (safe for deployment)
hostname = os.environ.get("REDIS_HOST", "redis-13725.c14.us-east-1-3.ec2.cloud.redislabs.com")
port = int(os.environ.get("REDIS_PORT", 13725))
password = os.environ.get("REDIS_PASSWORD", "")

r = redis.StrictRedis(
    host=hostname,
    port=port,
    password=password
)

# Retrieve Data From database
def retrieve_data(name):
    retrieve_dict = r.hgetall(name)
    retrieve_series = pd.Series(retrieve_dict)
    retrieve_series = retrieve_series.apply(lambda x: np.frombuffer(x, dtype=np.float32))
    index = retrieve_series.index
    index = list(map(lambda x: x.decode(), index))
    retrieve_series.index = index
    retrieve_df = retrieve_series.to_frame().reset_index()
    retrieve_df.columns = ['name_role', 'facial_features']
    retrieve_df[['Name', 'Role']] = retrieve_df['name_role'].apply(lambda x: x.split('@')).apply(pd.Series)
    return retrieve_df[['Name', 'Role', 'facial_features']]


# ✅ Use buffalo_l model (higher accuracy)
faceapp = FaceAnalysis(
    name="buffalo_sc",
    root='insightFace',
    providers=['CPUExecutionProvider']
)

faceapp.prepare(ctx_id=0, det_size=(640, 640), det_thresh=0.5)


# ML Search Algorithm
def ml_search_algorithm(dataframe, features_column, test_vector, name_role=['Name', 'Role'], thresh=0.5):
    """
    Cosine similarity based search algorithm
    """
    dataframe = dataframe.copy()
    X_list = dataframe[features_column].tolist()
    x = np.array(X_list)

    similar = pairwise.cosine_similarity(x, test_vector.reshape(1, -1))
    similar_arr = np.array(similar).flatten()
    dataframe['cosine'] = similar_arr

    data_filter = dataframe.query(f'cosine >= {thresh}')
    if len(data_filter) > 0:
        data_filter = data_filter.reset_index(drop=True)
        argmax = data_filter['cosine'].argmax()
        Name, Role = data_filter.loc[argmax][name_role]
    else:
        Name = 'Unknown'
        Role = 'Unknown'
    return Name, Role


class RealTimePred:
    def __init__(self):
        self.logs = dict(name=[], role=[], current_time=[])

    def reset_dict(self):
        self.logs = dict(name=[], role=[], current_time=[])

    def saveLogs_redis(self):
        dataframe = pd.DataFrame(self.logs)
        dataframe = dataframe.drop_duplicates('name')

        name_list = dataframe['name'].tolist()
        role_list = dataframe['role'].tolist()
        current_time = dataframe['current_time'].tolist()
        encode_data = []

        for name, role, cur in zip(name_list, role_list, current_time):
            if name != 'Unknown':
                encode_data.append(f"{name}-{role}-{cur}")

        if len(encode_data) > 0:
            r.lpush('attendance:logs', *encode_data)

        self.reset_dict()

    def face_prediction(self, test_image, dataframe, features_column, name_role=['Name', 'Role'], thresh=0.5):
        result = faceapp.get(test_image)
        test_copy = test_image.copy()
        current_time = str(datetime.now())

        for res in result:
            x1, y1, x2, y2 = res['bbox'].astype(int)
            embedding = res['embedding']
            Name, Role = ml_search_algorithm(
                dataframe, features_column,
                test_vector=embedding,
                name_role=name_role,
                thresh=thresh
            )
            color = (0, 0, 255) if Name == 'Unknown' else (0, 255, 0)
            cv2.putText(test_copy, Name, (x1, y1), cv2.FONT_HERSHEY_DUPLEX, 0.5, color, 2)
            cv2.putText(test_copy, current_time, (x1, y2 + 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, color, 2)

            self.logs['name'].append(Name)
            self.logs['role'].append(Role)
            self.logs['current_time'].append(current_time)

        return test_copy


class Registration_form:
    def __init__(self):
        self.sample = 0

    def reset(self):
        self.sample = 0

    def get_embedding(self, frame):
        result = faceapp.get(frame, max_num=1)
        embedding = None
        for res in result:
            self.sample += 1
            x1, y1, x2, y2 = res['bbox'].astype(int)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
            text = f"samples = {self.sample}"
            cv2.putText(frame, text, (x1, y1), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 0), 2)
            embedding = res['embedding']
        return frame, embedding

    def save_data_in_redis_db(self, name, role):
        if name is not None:
            if name.strip() != '':
                key = f'{name}@{role}'
            else:
                return "Not a valid Name and Role"
        else:
            return "Not a valid Name and Role"

        if 'face_embedding.txt' not in os.listdir():
            return 'Not a valid File'

        x_array = np.loadtxt('face_embedding.txt', dtype=np.float32)
        received_samples = int(x_array.size / 512)
        x_array = x_array.reshape(received_samples, 512)
        x_array = np.asarray(x_array)
        x_mean = x_array.mean(axis=0)
        x_mean = x_mean.astype(np.float32)
        x_mean_bytes = x_mean.tobytes()

        r.hset(name='academy:register', key=key, value=x_mean_bytes)
        os.remove('face_embedding.txt')
        self.reset()
        return True
