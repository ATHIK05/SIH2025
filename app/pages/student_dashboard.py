import streamlit as st

# Enhanced page configuration
st.set_page_config(
    page_title='Student Dashboard - Smart Attendance Suite',
    page_icon='🎓',
    layout='wide'
)

# Custom CSS for premium student dashboard UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }
    
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .dashboard-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .profile-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        border-left: 5px solid #667eea;
    }
    
    .info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border-top: 4px solid #667eea;
        transition: transform 0.3s ease;
    }
    
    .info-card:hover {
        transform: translateY(-5px);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.3);
        margin: 1rem 0;
    }
    
    .metric-card h3 {
        font-size: 2.5rem;
        margin: 0;
        font-weight: 700;
    }
    
    .metric-card p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1.1rem;
    }
    
    .timetable-container {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        margin: 2rem 0;
    }
    
    .legend-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }
    
    .suggestion-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3);
    }
    
    .progress-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .action-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 1rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        width: 100%;
        margin: 0.5rem 0;
    }
    
    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .stProgress > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Table Styling */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

from firebase.firebase_admin_init import get_firestore_client
from datetime import datetime
import pandas as pd
import base64
from io import BytesIO

def show_student_dashboard():
    # Enhanced dashboard header
    st.markdown("""
    <div class="dashboard-header">
        <h1>🎓 Student Dashboard</h1>
        <p style="font-size: 1.2rem; margin: 0; opacity: 0.9;">
            Welcome to your personalized learning hub
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    db = get_firestore_client()
    
    if 'user' not in st.session_state or st.session_state.get('role') != 'student':
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%); 
                    color: white; padding: 2rem; border-radius: 15px; text-align: center; 
                    box-shadow: 0 10px 30px rgba(255, 107, 107, 0.3); margin: 2rem 0;">
            <h2>🚫 Access Denied</h2>
            <p style="font-size: 1.1rem; margin: 0;">Please login as a student to access this dashboard.</p>
        </div>
        """, unsafe_allow_html=True)
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
    
    # Enhanced profile section
    col1, col2 = st.columns([1, 3])
    
    with col1:
        img_data = sdata.get('images', [None])[0]
        if img_data:
            try:
                # Remove any data URL prefix if present
                if isinstance(img_data, str) and img_data.startswith("data:image"):
                    img_data = img_data.split(",", 1)[1]
                if isinstance(img_data, str):
                    img_bytes = base64.b64decode(img_data)
                    st.image(
                        BytesIO(img_bytes), 
                        caption='Your Profile', 
                        width=200,
                        use_column_width=True
                    )
                else:
                    st.image(img_data, caption='Your Profile', width=200)
            except Exception as e:
                st.markdown("""
                <div style="background: #f8f9fa; padding: 2rem; border-radius: 10px; text-align: center; border: 2px dashed #dee2e6;">
                    <p style="color: #6c757d; margin: 0;">📷 Profile Image<br>Not Available</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: #f8f9fa; padding: 2rem; border-radius: 10px; text-align: center; border: 2px dashed #dee2e6;">
                <p style="color: #6c757d; margin: 0;">📷 Profile Image<br>Not Available</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="profile-card">
            <h2 style="color: #667eea; margin-bottom: 1rem;">👤 Profile Information</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                <div>
                    <h4 style="color: #333; margin-bottom: 0.5rem;">📝 Full Name</h4>
                    <p style="font-size: 1.1rem; color: #666; margin: 0;">{sdata.get('name', 'Not Available')}</p>
                </div>
                <div>
                    <h4 style="color: #333; margin-bottom: 0.5rem;">🎓 Register Number</h4>
                    <p style="font-size: 1.1rem; color: #666; margin: 0;">{regno}</p>
                </div>
                <div>
                    <h4 style="color: #333; margin-bottom: 0.5rem;">📚 Class</h4>
                    <p style="font-size: 1.1rem; color: #666; margin: 0;">{sdata.get('class', 'Not Available')}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Timetable for today
    st.markdown("""
    <div class="timetable-container">
        <h2 style="color: #667eea; margin-bottom: 1.5rem;">📅 Today's Schedule</h2>
    """, unsafe_allow_html=True)
    
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
        st.markdown("""
        <div style="background: #e3f2fd; color: #1976d2; padding: 2rem; border-radius: 12px; text-align: center; border-left: 4px solid #2196f3;">
            <h4>📅 No Schedule Available</h4>
            <p style="margin: 0;">No timetable has been set for today.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Attendance
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h2 style="color: #667eea;">📊 Academic Overview</h2>
    </div>
    """, unsafe_allow_html=True)
    
    attendance_ref = db.collection('attendance').where('class', '==', class_name)
    attendance_records = [doc.to_dict() for doc in attendance_ref.stream()]
    present_days = sum([regno in rec.get('present', []) for rec in attendance_records])
    total_days = len(attendance_records)
    
    attendance_percentage = (present_days/total_days*100) if total_days else 0
    
    # Enhanced metrics display
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{attendance_percentage:.1f}%</h3>
            <p>📈 Attendance Rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%); box-shadow: 0 8px 25px rgba(78, 205, 196, 0.3);">
            <h3>{present_days}</h3>
            <p>✅ Days Present</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); box-shadow: 0 8px 25px rgba(255, 152, 0, 0.3);">
            <h3>{total_days}</h3>
            <p>📅 Total Days</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Marks & Feedback
    st.markdown("""
    <div class="info-card">
        <h3 style="color: #667eea; margin-bottom: 1rem;">📝 Academic Performance</h3>
    """, unsafe_allow_html=True)
    
    marks_ref = student_ref.collection('marks').stream()
    marks_data = [m.to_dict() for m in marks_ref]
    if marks_data:
        # Create a more visually appealing table
        df = pd.DataFrame([{k: v for k, v in m.items() if k != 'timestamp'} for m in marks_data])
        st.dataframe(df, use_container_width=True)
        
        st.markdown("<h4 style='color: #667eea; margin-top: 1.5rem;'>💬 Faculty Feedback</h4>", unsafe_allow_html=True)
        for m in marks_data:
            if m.get('feedback'):
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #667eea; margin: 0.5rem 0;">
                    <strong>{m.get('exam', '')} - {m.get('subject', '')}</strong><br>
                    <em>"{m.get('feedback', '')}"</em><br>
                    <small style="color: #666;">- {m.get('faculty', '')}</small>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: #e3f2fd; color: #1976d2; padding: 1.5rem; border-radius: 8px; text-align: center;">
            <p style="margin: 0;">📊 No academic records available yet.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Daily Feedback
    st.markdown("""
    <div class="info-card">
        <h3 style="color: #667eea; margin-bottom: 1rem;">📅 Daily Feedback from Faculty</h3>
    """, unsafe_allow_html=True)
    
    fb_ref = student_ref.collection('daily_feedback').stream()
    feedback_found = False
    for fb in fb_ref:
        fbd = fb.to_dict()
        feedback_found = True
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #4CAF50; margin: 0.5rem 0;">
            <strong>📅 {fbd.get('date', '')}</strong><br>
            <p style="margin: 0.5rem 0;">{fbd.get('feedback', '')}</p>
            <small style="color: #666;">- {fbd.get('faculty', '')}</small>
        </div>
        """, unsafe_allow_html=True)
    
    if not feedback_found:
        st.markdown("""
        <div style="background: #e3f2fd; color: #1976d2; padding: 1.5rem; border-radius: 8px; text-align: center;">
            <p style="margin: 0;">💬 No daily feedback available yet.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Personalized Suggestions
    st.markdown("""
    <div class="suggestion-card">
        <h2 style="margin-bottom: 1rem;">🎯 Personalized Suggestions</h2>
        <p style="opacity: 0.9; margin: 0;">AI-powered recommendations based on your performance</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate attendance percentage
    
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
        st.markdown("""
        <div style="background: #fff3cd; color: #856404; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #ffc107; margin: 1rem 0;">
            <h4>📚 Academic Focus Needed!</h4>
        </div>
        """, unsafe_allow_html=True)
        
        for alert in academic_alerts:
            st.markdown(f"⚠️ {alert}")
        
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
            for interest in interests[:3]:  # Limit to top 3 interests
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
    st.markdown("""
    <div class="info-card">
        <h3 style="color: #667eea; margin-bottom: 1rem;">💡 Your Action Plan</h3>
    """, unsafe_allow_html=True)
    
    if suggestions:
        for i, suggestion in enumerate(suggestions[:8], 1):  # Limit to 8 suggestions
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #667eea; margin: 0.5rem 0;">
                <strong>{i}.</strong> {suggestion}
            </div>
            """, unsafe_allow_html=True)
        
        if len(suggestions) > 8:
            st.markdown(f"""
            <div style="background: #e3f2fd; color: #1976d2; padding: 1rem; border-radius: 8px; text-align: center; margin: 1rem 0;">
                <p style="margin: 0;">💡 <em>Showing top 8 suggestions. You have {len(suggestions)} total recommendations.</em></p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: #d4edda; color: #155724; padding: 1.5rem; border-radius: 8px; text-align: center;">
            <p style="margin: 0;">🎯 Keep up the great work! Continue with your current study routine.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Progress
    interests = sdata.get('interests', [])
    if interests:
        st.markdown("""
        <div class="progress-container">
            <h3 style="color: #667eea; margin-bottom: 1rem;">📈 Interest Progress Tracking</h3>
        """, unsafe_allow_html=True)
        
        progress = sdata.get('progress', {})
        for interest in interests:
            pct = progress.get(interest, 0)
            st.markdown(f"**{interest.title()}**")
            st.progress(pct / 100.0 if pct > 1 else pct)
            st.markdown(f"<small style='color: #666;'>{pct}% Complete</small>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Student-specific tools
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h2 style="color: #667eea;">🛠️ Student Tools</h2>
        <p style="color: #666;">Access your personalized learning tools</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button('📅 Visual Daily Planner', use_container_width=True):
            st.switch_page('pages/visual_daily_planner.py')
    
    with col2:
        if st.button('💡 AI Suggestion Engine', use_container_width=True):
            st.switch_page('pages/suggestion_engine.py')

if __name__ == '__main__':
    show_student_dashboard()
