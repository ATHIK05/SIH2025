import streamlit as st
from firebase.firebase_admin_init import get_firestore_client
from datetime import datetime

def show_marks_feedback_entry():
    st.subheader('📝 Enter Marks/Grades & Feedback')
    db = get_firestore_client()
    if 'user' not in st.session_state or st.session_state.get('role') != 'faculty':
        st.error('Please login as faculty.')
        return
    faculty = st.session_state['user']
    class_name = st.text_input('Class (e.g., 10A, 12B, etc.)', key='marks_class_name')
    subject = st.text_input('Subject', key='marks_subject')
    exam_name = st.text_input('Exam/Test Name', key='marks_exam_name')
    students_ref = db.collection('students').where('class', '==', class_name)
    students = [(doc.id, doc.to_dict().get('name', '')) for doc in students_ref.stream()]
    student_choices = {f"{name} ({regno})": regno for regno, name in students}
    student_display = st.selectbox('Student', list(student_choices.keys()), key='marks_student_select') if students else None
    if student_display:
        regno = student_choices[student_display]
        marks = st.number_input('Marks', min_value=0, max_value=100, key='marks_marks_input')
        grade = st.text_input('Grade (e.g., A, B, C)', key='marks_grade')
        feedback = st.text_area('Faculty Feedback (required)', key='marks_feedback')
        if st.button('Submit Marks & Feedback', key='marks_submit_btn'):
            if not feedback:
                st.error('Feedback is required!')
            else:
                mark_ref = db.collection('students').document(regno).collection('marks').document(f'{exam_name}_{subject}')
                mark_ref.set({'marks': marks, 'grade': grade, 'faculty': faculty, 'subject': subject, 'exam': exam_name, 'feedback': feedback, 'timestamp': datetime.now().isoformat()})
                st.success('Marks, grade, and feedback saved!')

if __name__ == '__main__':
    show_marks_feedback_entry()
