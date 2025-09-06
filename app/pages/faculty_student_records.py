import streamlit as st
from firebase.firebase_admin_init import get_firestore_client
import base64
from io import BytesIO
from PIL import Image

def show_faculty_student_records():
    st.subheader('👥 Student Records (Faculty View)')
    db = get_firestore_client()
    if 'user' not in st.session_state or st.session_state.get('role') != 'faculty':
        st.error('Please login as faculty.')
        return
    faculty = st.session_state['user']
    # Get faculty subjects and classes
    user_doc = db.collection('users').document(faculty).get()
    if not user_doc.exists:
        st.error('Faculty record not found!')
        return
    user_data = user_doc.to_dict()
    subjects = [s.strip() for s in user_data.get('subjects', '').split(',')]
    # List all students in classes handled by this faculty
    students_ref = db.collection('students').stream()
    students = []
    for doc in students_ref:
        sdata = doc.to_dict()
        students.append((doc.id, sdata))
    student_choices = {f"{s['name']} ({regno})": regno for regno, s in students}
    student_display = st.selectbox('Student', list(student_choices.keys()), key='records_student_select') if students else None
    if student_display:
        regno = student_choices[student_display]
        sdata = next(s for r, s in students if r == regno)
        # Fix: decode base64 image
        if sdata.get('images'):
            try:
                img_b64 = sdata['images'][0]
                img_bytes = base64.b64decode(img_b64)
                img = Image.open(BytesIO(img_bytes))
                st.image(img, caption='Student Image', width=150)
            except Exception:
                st.info('Could not display student image.')
        st.write(f"**Name:** {sdata.get('name', '')}")
        st.write(f"**Register Number:** {regno}")
        st.write(f"**Class:** {sdata.get('class', '')}")
        # Marks/grades
        st.write('---')
        st.subheader('Marks & Grades')
        marks_ref = db.collection('students').document(regno).collection('marks').stream()
        marks_data = [m.to_dict() for m in marks_ref]
        if marks_data:
            st.table([{k: v for k, v in m.items() if k != 'timestamp'} for m in marks_data])
        else:
            st.info('No marks/grades found.')
        # Feedback
        st.write('---')
        st.subheader('Faculty Feedback (All Exams)')
        for m in marks_data:
            st.write(f"**{m.get('exam', '')} - {m.get('subject', '')}:** {m.get('feedback', '')} (by {m.get('faculty', '')})")
        # Daily feedback
        st.write('---')
        st.subheader('Daily Feedback')
        fb_ref = db.collection('students').document(regno).collection('daily_feedback').stream()
        for fb in fb_ref:
            fbd = fb.to_dict()
            st.write(f"{fbd.get('date', '')}: {fbd.get('feedback', '')} (by {fbd.get('faculty', '')})")
        # Suggestions from other faculty (feedbacks)
        st.write('---')
        st.subheader('Suggestions/Feedback from Other Faculty')
        for m in marks_data:
            if m.get('faculty', '') != faculty:
                st.write(f"**{m.get('exam', '')} - {m.get('subject', '')}:** {m.get('feedback', '')} (by {m.get('faculty', '')})")
        # Exam history
        st.write('---')
        st.subheader('Exam/Test History')
        for m in marks_data:
            st.write(f"{m.get('exam', '')} - {m.get('subject', '')}: {m.get('marks', '')} ({m.get('grade', '')})")

if __name__ == '__main__':
    show_faculty_student_records()
