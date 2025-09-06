import streamlit as st
from firebase.firebase_admin_init import get_firestore_client
from datetime import datetime

DAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
PERIODS = [
    {'label': '8:45 am - 9:40 am'},
    {'label': '9:40 am - 10:25 am'},
    {'label': '10:45 am - 11:30 am'},
    {'label': '11:30 am - 12:15 pm'},
    {'label': '1:15 pm - 2:00 pm'},
    {'label': '2:00 pm - 2:45 pm'},
    {'label': '3:00 pm - 3:45 pm'},
    {'label': '3:45 pm - 4:30 pm'},
]

def show_faculty_checkin():
    st.title('Faculty Period Check-in')
    db = get_firestore_client()
    if 'user' not in st.session_state or st.session_state.get('role') != 'faculty':
        st.error('Please login as faculty.')
        return
    faculty = st.session_state['user']
    class_name = st.text_input('Class (e.g., 10A, 12B, etc.)')
    date = st.date_input('Date', value=datetime.today())
    period_idx = st.selectbox('Period', list(range(len(PERIODS))), format_func=lambda i: PERIODS[i]['label'])
    if st.button('Check In'):
        checkin_ref = db.collection('checkins').document(f'{date}_{class_name}_{period_idx}')
        checkin_ref.set({'faculty': faculty, 'class': class_name, 'date': str(date), 'period_idx': period_idx, 'period_label': PERIODS[period_idx]['label'], 'timestamp': datetime.now().isoformat()})
        st.success(f'Checked in for {PERIODS[period_idx]["label"]} in {class_name}')

if __name__ == '__main__':
    show_faculty_checkin()
