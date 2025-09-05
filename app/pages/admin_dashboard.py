import streamlit as st
import pandas as pd
from firebase.firebase_admin_init import get_firestore_client
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date

def show_admin_dashboard():
    st.title('Admin/Faculty Attendance Dashboard')
    class_name = st.text_input('Class (e.g., 10A, 12B, etc.)', max_chars=10, key='admin_class_name')
    start_date = st.date_input('Start Date', value=date.today(), key='admin_start_date')
    end_date = st.date_input('End Date', value=date.today(), key='admin_end_date')
    db = get_firestore_client()
    if class_name and start_date and end_date:
        attendance_ref = db.collection('attendance').where('class', '==', class_name)
        records = []
        # Build a register_number -> name map for this class
        students_ref = db.collection('students').where('class', '==', class_name)
        regno_to_name = {doc.to_dict()['register_number']: doc.to_dict()['name'] for doc in students_ref.stream()}
        for doc in attendance_ref.stream():
            data = doc.to_dict()
            att_date = pd.to_datetime(data['date']).date()
            if start_date <= att_date <= end_date:
                present = [f"{regno} - {regno_to_name.get(regno, '')}" for regno in data.get('present', [])]
                absent = [f"{regno} - {regno_to_name.get(regno, '')}" for regno in data.get('absent', [])]
                records.append({
                    'date': att_date,
                    'present': len(present),
                    'absent': len(absent),
                    'present_list': present,
                    'absent_list': absent
                })
        if records:
            df = pd.DataFrame(records)
            st.write('### Attendance Summary')
            st.dataframe(df[['date', 'present', 'absent']])
            # Plot trends
            fig, ax = plt.subplots()
            sns.lineplot(data=df, x='date', y='present', label='Present', ax=ax)
            sns.lineplot(data=df, x='date', y='absent', label='Absent', ax=ax)
            ax.set_ylabel('Count')
            ax.set_title('Attendance Trend')
            st.pyplot(fig)
            # Download logs
            csv = df.to_csv(index=False)
            st.download_button('Download Attendance Log as CSV', csv, file_name=f'{class_name}_attendance.csv', key='admin_download_btn')
            # Show detailed lists
            st.write('---')
            st.write('### Detailed Attendance Lists')
            for i, row in df.iterrows():
                st.write(f"**{row['date']}**")
                st.write(f"Present: {row['present_list']}")
                st.write(f"Absent: {row['absent_list']}")
        else:
            st.info('No attendance records found for this class and date range.')
    else:
        st.info('Enter class and date range to view analytics.')

if __name__ == '__main__':
    show_admin_dashboard()
