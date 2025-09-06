import streamlit as st
from firebase.firebase_admin_init import get_firestore_client
from datetime import datetime
import pandas as pd
import base64
from io import BytesIO

def show_student_dashboard():
    st.title('🎓 Student Dashboard')
    db = get_firestore_client()
    if 'user' not in st.session_state or st.session_state.get('role') != 'student':
        st.error('Please login as a student.')
        return
    username = st.session_state['user']
    user_doc = db.collection('users').document(username).get()
    if not user_doc.exists:
        st.error('Student record not found!')
        return
    user_data = user_doc.to_dict()
    regno = user_data.get('register_number', username)
    student_ref = db.collection('students').document(regno)
    student_doc = student_ref.get()
    if not student_doc.exists:
        st.error('Student record not found!')
        return
    sdata = student_doc.to_dict()
    img_data = sdata.get('images', [None])[0]
    if img_data:
        try:
            # Remove any data URL prefix if present
            if isinstance(img_data, str) and img_data.startswith("data:image"):
                img_data = img_data.split(",", 1)[1]
            if isinstance(img_data, str):
                img_bytes = base64.b64decode(img_data)
                st.image(BytesIO(img_bytes), caption='Student Image', width=150)
            else:
                st.image(img_data, caption='Student Image', width=150)
        except Exception as e:
            st.warning(f"Could not display image: {e}")
    else:
        st.info("No student image available.")
    st.write(f"**Name:** {sdata.get('name', '')}")
    st.write(f"**Register Number:** {regno}")
    st.write(f"**Class:** {sdata.get('class', '')}")
    # Timetable for today
    st.write('---')
    st.subheader('Today\'s Timetable')
    class_name = sdata.get('class', '')
    date = datetime.today().date()
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
    def get_day_str(date):
        return DAYS[date.weekday()] if date.weekday() < len(DAYS) else 'MON'
    schedule_ref = db.collection('schedules').document(class_name)
    schedule_doc = schedule_ref.get()
    week_timetable = {d: [{'subject': '', 'faculty': ''} for _ in PERIODS] for d in DAYS}
    if schedule_doc.exists:
        week_timetable.update(schedule_doc.to_dict().get('week_timetable', {}))
    today_str = get_day_str(date)
    today_periods = week_timetable.get(today_str, [{'subject': '', 'faculty': ''} for _ in PERIODS])
    today_schedule = []
    for i, cell in enumerate(today_periods):
        start, end = PERIODS[i]['label'].split(' - ')
        today_schedule.append({'period': cell['subject'] if cell['subject'] else 'Free', 'faculty': cell['faculty'] if cell['faculty'] else '-', 'start': start, 'end': end})
    if today_schedule:
        st.table(pd.DataFrame(today_schedule))
    else:
        st.info('No schedule set for today!')
    # Attendance
    st.write('---')
    st.subheader('Attendance Report')
    attendance_ref = db.collection('attendance').where('class', '==', class_name)
    attendance_records = [doc.to_dict() for doc in attendance_ref.stream()]
    present_days = sum([regno in rec.get('present', []) for rec in attendance_records])
    total_days = len(attendance_records)
    st.metric('Attendance %', f"{(present_days/total_days*100) if total_days else 0:.1f}%")
    st.write(f"Present: {present_days} / {total_days}")
    # Marks & Feedback
    st.write('---')
    st.subheader('Marks, Grades & Faculty Feedback')
    marks_ref = student_ref.collection('marks').stream()
    marks_data = [m.to_dict() for m in marks_ref]
    if marks_data:
        st.table([{k: v for k, v in m.items() if k != 'timestamp'} for m in marks_data])
        for m in marks_data:
            st.write(f"**{m.get('exam', '')} - {m.get('subject', '')}:** {m.get('feedback', '')} (by {m.get('faculty', '')})")
    else:
        st.info('No marks/grades found.')
    # Daily Feedback
    st.write('---')
    st.subheader('Daily Feedback from Faculty')
    fb_ref = student_ref.collection('daily_feedback').stream()
    for fb in fb_ref:
        fbd = fb.to_dict()
        st.write(f"{fbd.get('date', '')}: {fbd.get('feedback', '')} (by {fbd.get('faculty', '')})")
    # Suggestions
    st.write('---')
    st.subheader('Personalized Suggestions')
    # Academic-first suggestions if needed
    academic_alerts = []
    for m in marks_data:
        if m.get('marks', 100) < 50 or m.get('grade', '').upper() in ['C', 'D', 'E', 'F']:
            academic_alerts.append(f"Low performance in {m.get('subject', '')} ({m.get('exam', '')}): {m.get('marks', '')} ({m.get('grade', '')})")
        if 'feedback' in m and m['feedback'] and ('improve' in m['feedback'].lower() or 'poor' in m['feedback'].lower()):
            academic_alerts.append(f"Faculty feedback for {m.get('subject', '')}: {m['feedback']}")
    if academic_alerts:
        st.warning('Academic Focus Needed!')
        for alert in academic_alerts:
            st.write(f'⚠️ {alert}')
    interests = sdata.get('interests', [])
    suggestions = []
    if academic_alerts:
        for m in marks_data:
            if m.get('marks', 100) < 50 or m.get('grade', '').upper() in ['C', 'D', 'E', 'F']:
                suggestions.append(f'Review {m.get("subject", "")} notes and practice more problems (Exam: {m.get("exam", "")})')
            if 'feedback' in m and m['feedback'] and ('improve' in m['feedback'].lower() or 'poor' in m['feedback'].lower()):
                suggestions.append(f'Follow up on faculty feedback for {m.get("subject", "")} (Exam: {m.get("exam", "")})')
    else:
        for interest in interests:
            if 'coding' in interest.lower():
                suggestions.append(f'Practice coding on LeetCode or HackerRank')
            if 'math' in interest.lower():
                suggestions.append(f'Solve math puzzles or Olympiad problems')
            if 'reading' in interest.lower():
                suggestions.append(f'Read a book or article related to your goal')
            if 'science' in interest.lower():
                suggestions.append(f'Watch a science documentary or experiment video')
            if 'art' in interest.lower():
                suggestions.append(f'Work on a drawing or digital art project')
        suggestions.append('Review your class notes or prepare for upcoming exams')
        suggestions.append('Explore online courses related to your interests (Coursera, edX, etc.)')
    for suggestion in suggestions:
        st.write(f'👉 {suggestion}')
    # Progress
    st.write('---')
    st.subheader('Progress Dashboard')
    progress = sdata.get('progress', {})
    for interest in interests:
        pct = progress.get(interest, 0)
        st.write(f"**{interest.title()}**")
        st.progress(pct)

if __name__ == '__main__':
    show_student_dashboard()
