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
        
        # Check for faculty check-in
        checkin_ref = db.collection('checkins').document(f'{date}_{class_name}_{i}')
        checkin_doc = checkin_ref.get()
        
        scheduled_subject = cell['subject'] if cell['subject'] else 'Free'
        scheduled_faculty = cell['faculty'] if cell['faculty'] else '-'
        
        if checkin_doc.exists:
            checkin_data = checkin_doc.to_dict()
            actual_faculty = checkin_data.get('faculty_name', 'Unknown')
            is_substitution = checkin_data.get('is_substitution', False)
            substitution_reason = checkin_data.get('substitution_reason', '')
            
            if is_substitution:
                faculty_display = f"🔄 {actual_faculty} (Sub for {scheduled_faculty})"
                if substitution_reason:
                    faculty_display += f" - {substitution_reason}"
            else:
                faculty_display = f"✅ {actual_faculty}"
        else:
            faculty_display = f"❌ {scheduled_faculty} (Not checked in)"
        
        today_schedule.append({
            'period': scheduled_subject, 
            'faculty': faculty_display, 
            'start': start, 
            'end': end
        })
    
    if today_schedule:
        st.table(pd.DataFrame(today_schedule))
        
        # Show legend
        st.info("""
        **Legend:**
        - ✅ = Faculty checked in (scheduled)
        - 🔄 = Substitution (different faculty checked in)
        - ❌ = Faculty not checked in
        """)
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
    # Personalized Suggestions
    st.write('---')
    st.subheader('🎯 Personalized Suggestions')
    
    # Calculate attendance percentage
    attendance_percentage = (present_days/total_days*100) if total_days else 0
    
    # Analyze academic performance
    academic_alerts = []
    weak_subjects = []
    strong_subjects = []
    subject_performance = {}
    
    for m in marks_data:
        subject = m.get('subject', '')
        marks = m.get('marks', 0)
        grade = m.get('grade', '').upper()
        
        if subject not in subject_performance:
            subject_performance[subject] = {'marks': [], 'grades': [], 'feedback': []}
        
        subject_performance[subject]['marks'].append(marks)
        subject_performance[subject]['grades'].append(grade)
        if m.get('feedback'):
            subject_performance[subject]['feedback'].append(m.get('feedback'))
    
    # Categorize subjects based on performance
    for subject, data in subject_performance.items():
        avg_marks = sum(data['marks']) / len(data['marks']) if data['marks'] else 0
        if avg_marks < 50 or any(g in ['C', 'D', 'E', 'F'] for g in data['grades']):
            weak_subjects.append(subject)
            academic_alerts.append(f"⚠️ **{subject}**: Average {avg_marks:.1f}% - Needs improvement")
        elif avg_marks >= 80:
            strong_subjects.append(subject)
    
    # Generate personalized suggestions based on data
    suggestions = []
    
    # 1. Attendance-based suggestions
    if attendance_percentage < 75:
        suggestions.append(f"📅 **Attendance Alert**: Your attendance is {attendance_percentage:.1f}%. Aim for 85%+ to maintain good academic standing.")
        suggestions.append("📚 **Action**: Attend all classes regularly and review missed topics from classmates.")
    elif attendance_percentage >= 90:
        suggestions.append(f"🎉 **Great Attendance**: {attendance_percentage:.1f}% - Keep up the excellent attendance!")
    
    # 2. Academic performance-based suggestions
    if weak_subjects:
        st.warning('📚 **Academic Focus Needed!**')
        for alert in academic_alerts:
            st.write(alert)
        
        for subject in weak_subjects:
            data = subject_performance[subject]
            avg_marks = sum(data['marks']) / len(data['marks'])
            
            # Subject-specific suggestions
            if 'math' in subject.lower() or 'mathematics' in subject.lower():
                suggestions.append(f"🔢 **{subject}**: Practice 10-15 problems daily. Focus on weak topics from your {avg_marks:.1f}% average.")
                suggestions.append(f"📖 **{subject}**: Review fundamental concepts and solve previous year papers.")
            elif 'science' in subject.lower() or 'physics' in subject.lower() or 'chemistry' in subject.lower():
                suggestions.append(f"🔬 **{subject}**: Conduct practical experiments and understand concepts. Current average: {avg_marks:.1f}%")
                suggestions.append(f"📚 **{subject}**: Watch educational videos and create concept maps.")
            elif 'english' in subject.lower() or 'language' in subject.lower():
                suggestions.append(f"📝 **{subject}**: Read daily for 30 minutes and practice writing. Improve from {avg_marks:.1f}%")
                suggestions.append(f"🗣️ **{subject}**: Practice speaking and vocabulary building exercises.")
            elif 'computer' in subject.lower() or 'programming' in subject.lower() or 'coding' in subject.lower():
                suggestions.append(f"💻 **{subject}**: Code for 1 hour daily. Practice on platforms like LeetCode, HackerRank.")
                suggestions.append(f"🛠️ **{subject}**: Build small projects to apply concepts practically.")
            else:
                suggestions.append(f"📖 **{subject}**: Dedicate 45 minutes daily for revision and practice. Target: Improve from {avg_marks:.1f}%")
            
            # Feedback-based suggestions
            for feedback in data['feedback']:
                if 'improve' in feedback.lower() or 'poor' in feedback.lower():
                    suggestions.append(f"💬 **{subject}**: Address faculty feedback: '{feedback[:50]}...'")
    
    # 3. Strong subjects encouragement
    if strong_subjects:
        suggestions.append(f"🌟 **Excellent Performance**: You're doing great in {', '.join(strong_subjects)}! Consider helping classmates.")
        for subject in strong_subjects:
            suggestions.append(f"🎯 **{subject}**: Challenge yourself with advanced topics and competitions.")
    
    # 4. Interest-based suggestions (only if no academic issues)
    if not weak_subjects and attendance_percentage >= 75:
        interests = sdata.get('interests', [])
        if interests:
            for interest in interests:
                if 'coding' in interest.lower() or 'programming' in interest.lower():
                    suggestions.append("💻 **Coding**: Join coding competitions, contribute to open-source projects, or learn a new programming language.")
                elif 'math' in interest.lower() or 'mathematics' in interest.lower():
                    suggestions.append("🔢 **Mathematics**: Participate in math olympiads, solve advanced problems, or explore mathematical concepts.")
                elif 'science' in interest.lower():
                    suggestions.append("🔬 **Science**: Conduct experiments, read scientific journals, or join science clubs.")
                elif 'art' in interest.lower() or 'design' in interest.lower():
                    suggestions.append("🎨 **Art**: Create a portfolio, learn new techniques, or participate in art exhibitions.")
                elif 'reading' in interest.lower() or 'literature' in interest.lower():
                    suggestions.append("📚 **Reading**: Join book clubs, write reviews, or explore different genres.")
        
        # General improvement suggestions
        suggestions.append("📈 **Growth**: Set weekly goals and track your progress in a journal.")
        suggestions.append("🌐 **Learning**: Explore online courses on Coursera, edX, or Khan Academy.")
        suggestions.append("🤝 **Leadership**: Consider mentoring junior students or leading study groups.")
    
    # 5. Time management suggestions
    if attendance_percentage < 85:
        suggestions.append("⏰ **Time Management**: Create a daily study schedule and stick to it.")
    
    # 6. Exam preparation suggestions
    suggestions.append("📝 **Exam Prep**: Create a revision timetable for upcoming exams.")
    suggestions.append("🧠 **Study Techniques**: Use active recall and spaced repetition for better retention.")
    
    # Display suggestions
    if suggestions:
        for i, suggestion in enumerate(suggestions[:8], 1):  # Limit to 8 suggestions
            st.write(f'👉 {suggestion}')
        
        if len(suggestions) > 8:
            st.info(f"💡 *Showing top 8 suggestions. You have {len(suggestions)} total recommendations.*")
    else:
        st.info("🎯 Keep up the great work! Continue with your current study routine.")
    # Progress
    st.write('---')
    st.subheader('Progress Dashboard')
    progress = sdata.get('progress', {})
    for interest in interests:
        pct = progress.get(interest, 0)
        st.write(f"**{interest.title()}**")
        st.progress(pct)
    
    # Student-specific tools
    st.write('---')
    st.subheader('Student Tools')
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button('📅 Visual Daily Planner'):
            st.switch_page('pages/visual_daily_planner.py')
    
    with col2:
        if st.button('💡 Suggestion Engine'):
            st.switch_page('pages/suggestion_engine.py')

if __name__ == '__main__':
    show_student_dashboard()
