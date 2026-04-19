
# import streamlit as st
# from Home import face_rec

# DATABASE_NAME_REDIS_LIST = 'attendance:logs'
# DATABASE_NAME = 'academy:register'

# st.set_page_config(page_title='Report', layout='centered')
# st.subheader("Reporting")

# def load_logs(name, end=-1):
#     log_list = face_rec.r.lrange(name, start=0, end=end)
#     return log_list

# tab1, tab2 = st.tabs(['Register Data', 'Logs'])

# with tab1:
#     if st.button("Show Data 📊"):
#         with st.spinner("Loading Data from Redis Database"):  # ✅ with not while
#             redis_db = face_rec.retrieve_data(DATABASE_NAME)
#         st.dataframe(redis_db[['Name', 'Role']])

# with tab2:
#     if st.button("Refresh 🔄️"):
#         logs = load_logs(name=DATABASE_NAME_REDIS_LIST)
#         decoded_logs = [log.decode('utf-8') for log in logs]  # ✅ decode bytes
#         st.write(decoded_logs)


import streamlit as st
from Home import face_rec
import pandas as pd

DATABASE_NAME_REDIS_LIST = 'attendance:logs'
DATABASE_NAME = 'academy:register'

st.set_page_config(page_title='Report', layout='centered')
st.subheader("Reporting")

def load_logs(name, end=-1):
    log_list = face_rec.r.lrange(name, start=0, end=end)
    return log_list

tab1, tab2= st.tabs(['Register Data','Show Logs'])

with tab1:
    if st.button("Show Data 📊"):
        with st.spinner("Loading Data from Redis Database"):
            redis_db = face_rec.retrieve_data(DATABASE_NAME)
        st.dataframe(redis_db[['Name', 'Role']])

with tab2:
    if st.button("Show Logs 📊"):
        logs = load_logs(name=DATABASE_NAME_REDIS_LIST)

        # ✅ Step 1: Check if logs exist
        if len(logs) == 0:
            st.warning("⚠️ No logs found in database")
        else:
            # ✅ Step 2: Decode bytes
            decoded_logs = [log.decode('utf-8') for log in logs]

            # ✅ Step 3: Parse into DataFrame
            # Each log = "Name-Role-Timestamp"
            parsed = []
            for log in decoded_logs:
                parts = log.split('-', 2)  # split max 2 times — timestamp has dashes too
                if len(parts) == 3:
                    parsed.append({
                        'Name': parts[0],
                        'Role': parts[1],
                        'Timestamp': parts[2]
                    })

            # ✅ Step 4: Show as DataFrame
            if parsed:
                log_df = pd.DataFrame(parsed)
                st.dataframe(log_df)
                st.success(f"✅ Total Records: {len(log_df)}")
            else:
                st.error("❌ Could not parse log data")

            # ✅ Optional: download button
            csv = log_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Logs as CSV 📥",
                data=csv,
                file_name='attendance_logs.csv',
                mime='text/csv'
            )


    if st.button("Refresh 🔄️"):
        logs = load_logs(name=DATABASE_NAME_REDIS_LIST)

        # ✅ Step 1: Check if logs exist
        if len(logs) == 0:
            st.warning("⚠️ No logs found in database")
        else:
            # ✅ Step 2: Decode bytes
            decoded_logs = [log.decode('utf-8') for log in logs]

            # ✅ Step 3: Parse into DataFrame
            # Each log = "Name-Role-Timestamp"
            parsed = []
            for log in decoded_logs:
                parts = log.split('-', 2)  # split max 2 times — timestamp has dashes too
                if len(parts) == 3:
                    parsed.append({
                        'Name': parts[0],
                        'Role': parts[1],
                        'Timestamp': parts[2]
                    })

            # ✅ Step 4: Show as DataFrame
            if parsed:
                log_df = pd.DataFrame(parsed)
                st.dataframe(log_df)
                st.success(f"✅ Total Records: {len(log_df)}")
            else:
                st.error("❌ Could not parse log data")

            # ✅ Optional: download button
            csv = log_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Logs as CSV 📥",
                data=csv,
                file_name='attendance_logs.csv',
                mime='text/csv'
            )