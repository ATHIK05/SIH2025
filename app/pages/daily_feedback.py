import streamlit as st
from firebase.firebase_admin_init import get_firestore_client
from datetime import datetime

def show_daily_feedback_entry():
    st.title('Enter Daily Feedback for Student')
    db = get_firestore_client()
    if 'user' not in st.session_state or st.session_state.get('role') != 'faculty':
        st.error('Please login as faculty.')
        return
    faculty = st.session_state['user']
    class_name = st.text_input('Class (e.g., 10A, 12B, etc.)')
    students_ref = db.collection('students').where('class', '==', class_name)
    students = [(doc.id, doc.to_dict().get('name', '')) for doc in students_ref.stream()]
    student_choices = {f"{name} ({regno})": regno for regno, name in students}
    student_display = st.selectbox('Student', list(student_choices.keys())) if students else None
    date = st.date_input('Date', value=datetime.today())
    if student_display:
        regno = student_choices[student_display]
        feedback = st.text_area('Daily Feedback (optional)')
        if st.button('Submit Daily Feedback'):
            if not feedback:
                st.error('Feedback is required!')
            else:
                fb_ref = db.collection('students').document(regno).collection('daily_feedback').document(str(date))
                fb_ref.set({'faculty': faculty, 'feedback': feedback, 'date': str(date), 'timestamp': datetime.now().isoformat()})
                st.success('Daily feedback saved!')

if __name__ == '__main__':
    show_daily_feedback_entry()
