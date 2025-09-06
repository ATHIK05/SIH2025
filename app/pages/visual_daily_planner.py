import streamlit as st

# Enhanced page configuration
st.set_page_config(
    page_title='Visual Daily Planner - Smart Attendance Suite',
    page_icon='📅',
    layout='wide'
)

# Custom CSS for premium visual planner UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }
    
    .planner-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .planner-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .input-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    .timetable-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        margin: 2rem 0;
        border-left: 5px solid #667eea;
    }
    
    .schedule-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        margin: 2rem 0;
        border-top: 4px solid #4CAF50;
    }
    
    .ai-suggestion-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3);
    }
    
    .progress-section {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        margin: 2rem 0;
        border-top: 4px solid #ff9800;
    }
    
    .attendance-card {
        background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(78, 205, 196, 0.3);
        margin: 2rem 0;
    }
    
    .legend-container {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
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
    
    .stTextInput > div > div > input,
    .stDateInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e1e5e9;
        padding: 0.75rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stDateInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stProgress > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    .stCheckbox > label {
        background: #f8f9fa;
        padding: 0.5rem;
        border-radius: 8px;
        border-left: 3px solid #667eea;
        margin: 0.25rem 0;
        transition: all 0.3s ease;
    }
    
    .stCheckbox > label:hover {
        background: #e9ecef;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

import pandas as pd
from datetime import datetime, time, timedelta
from firebase.firebase_admin_init import get_firestore_client
import plotly.figure_factory as ff
import requests
import json
import re

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

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_ACCESS_TOKEN = "7cPbyeLvLDTf7IS1eITUqcC5mDLxlzH2"
MISTRAL_MODEL = "mistral-large-latest"

def call_mistral_api(system_prompt, user_message, max_tokens=256):
    headers = {
        "Authorization": f"Bearer {MISTRAL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MISTRAL_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": max_tokens
    }
    response = requests.post(MISTRAL_API_URL, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        data = response.json()
        return data['choices'][0]['message']['content'].strip()
    else:
        return f"API Error: {response.text}"

def build_student_message(student_name, marks_data, interests, free_period_time=None):
    if marks_data:
        focus = min(marks_data, key=lambda m: m.get('marks', 100))
        subject = focus.get('subject', 'your subjects')
        mark = focus.get('marks', 'N/A')
        exam = focus.get('exam', '')
        mark_str = f"{subject} ({mark}%, {exam})"
    else:
        mark_str = "your subjects"
    interest_str = ', '.join(interests) if interests else "your interests"
    period_str = f" ({free_period_time})" if free_period_time else ""
    return (
        f"Hyy {student_name}! I have a free period{period_str} now. "
        f"My recent marks: {mark_str}. My interests: {interest_str}. "
        "What is a practical, encouraging, and specific study plan or suggestion for me to use this free time wisely?"
    )

system_prompt = (
    "You are a helpful, practical, and emotionally supportive student assistant. "
    "Always keep your answers short, actionable, and encouraging. "
    "Give specific, lively, and personalized study plans or suggestions for students based on their marks and interests. "
    "Start your response with a friendly greeting using the student's name."
)

# Helper to get day string from date
def get_day_str(date):
    return DAYS[date.weekday()] if date.weekday() < len(DAYS) else 'MON'

def boldify(text):
    return re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)

def show_visual_daily_planner():
    # Enhanced planner header
    st.markdown("""
    <div class="planner-header">
        <h1>📅 Visual Daily Planner</h1>
        <p style="font-size: 1.2rem; margin: 0; opacity: 0.9;">
            Plan your day with AI-powered suggestions and visual schedules
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if user is logged in and is a student
    if 'user' not in st.session_state or 'role' not in st.session_state:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%); 
                    color: white; padding: 2rem; border-radius: 15px; text-align: center; 
                    box-shadow: 0 10px 30px rgba(255, 107, 107, 0.3); margin: 2rem 0;">
            <h2>🚫 Authentication Required</h2>
            <p style="font-size: 1.1rem; margin: 0;">Please login to access this page.</p>
        </div>
        """, unsafe_allow_html=True)
        st.switch_page('pages/auth.py')
        return
    
    if st.session_state.get('role') != 'student':
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%); 
                    color: white; padding: 2rem; border-radius: 15px; text-align: center; 
                    box-shadow: 0 10px 30px rgba(255, 107, 107, 0.3); margin: 2rem 0;">
            <h2>🚫 Access Denied</h2>
            <p style="font-size: 1.1rem; margin: 0;">This feature is only for students.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%); 
                    color: white; padding: 1.5rem; border-radius: 12px; text-align: center; 
                    box-shadow: 0 4px 20px rgba(78, 205, 196, 0.3); margin: 1rem 0;">
            <p style="font-size: 1.1rem; margin: 0;">Faculty members should use the main dashboard.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button('Go to Main Dashboard'):
            st.switch_page('main_dashboard.py')
        st.stop()
    
    db = get_firestore_client()
    
    # Enhanced input section
    st.markdown("""
    <div class="input-container">
        <h3 style="color: #667eea; margin-bottom: 1rem;">📝 Enter Your Details</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        class_name = st.text_input(
            '📚 Class (e.g., 10A, 12B, etc.)', 
            max_chars=10, 
            key='planner_class_name',
            help="Enter your class identifier"
        )
    
    with col2:
        register_number = st.text_input(
            '🎓 Register Number (e.g., 22ISR026)', 
            max_chars=20, 
            key='planner_register_number',
            help="Enter your student registration number"
        )
    
    with col3:
        date = st.date_input(
            '📅 Select Date', 
            value=datetime.today(), 
            key='planner_date',
            help="Choose the date for planning"
        )
    
    student_data = None
    if register_number:
        student_ref = db.collection('students').document(register_number)
        doc = student_ref.get()
        if doc.exists:
            student_data = doc.to_dict()
    if class_name:
        schedule_ref = db.collection('schedules').document(class_name)
        schedule_doc = schedule_ref.get()
        week_timetable = {d: [{'subject': '', 'faculty': ''} for _ in PERIODS] for d in DAYS}
        if schedule_doc.exists:
            week_timetable.update(schedule_doc.to_dict().get('week_timetable', {}))
        # Build DataFrame for grid
        timetable_df = pd.DataFrame({
            day: [f"{cell['subject']} ({cell['faculty']})" if cell['subject'] else '' 
                  for cell in week_timetable[day]] 
            for day in DAYS
        }, index=[p['label'] for p in PERIODS])
        timetable_df.index.name = 'Period/Day'
        
        st.markdown("""
        <div class="timetable-card">
            <h3 style="color: #667eea; margin-bottom: 1.5rem;">📅 Weekly Class Timetable</h3>
        """, unsafe_allow_html=True)
        
        # For display, show subject (faculty) in each cell
        header_cols = st.columns([1] + [1]*len(DAYS))
        header_cols[0].markdown('**⏰ Period/Day**')
        for j, day in enumerate(DAYS):
            header_cols[j+1].markdown(f'**📅 {day}**')
        
        for i, period in enumerate(PERIODS):
            row_cols = st.columns([1] + [1]*len(DAYS))
            row_cols[0].markdown(f"**{period['label']}**")
            for j, day in enumerate(DAYS):
                cell = week_timetable[day][i]
                if cell.get('subject'):
                    val = f"📖 {cell.get('subject', '')}<br><small>👨‍🏫 {cell.get('faculty', '')}</small>"
                    row_cols[j+1].markdown(val, unsafe_allow_html=True)
                else:
                    row_cols[j+1].markdown("🆓 *Free*")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Show today's schedule, factoring in check-ins
        today_str = get_day_str(date)
        st.markdown(f"""
        <div class="schedule-card">
            <h3 style="color: #4CAF50; margin-bottom: 1.5rem;">🗓️ Today's Schedule - {today_str}</h3>
        """, unsafe_allow_html=True)
        
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
                
                is_free = False
            else:
                faculty_display = f"❌ {scheduled_faculty} (Not checked in)"
                is_free = not cell['subject']
            
            today_schedule.append({
                'period': scheduled_subject, 
                'faculty': faculty_display, 
                'start': start, 
                'end': end, 
                'free': is_free
            })
        
        if today_schedule:
            # Enhanced table display
            df = pd.DataFrame(today_schedule)
            st.dataframe(df, use_container_width=True)
            
            # Show legend
            st.markdown("""
            <div class="legend-container">
                <h4 style="margin-bottom: 0.5rem;">📋 Legend:</h4>
                <ul style="margin: 0;">
                    <li><strong>✅</strong> = Faculty checked in (scheduled)</li>
                    <li><strong>🔄</strong> = Substitution (different faculty checked in)</li>
                    <li><strong>❌</strong> = Faculty not checked in</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: #e3f2fd; color: #1976d2; padding: 2rem; border-radius: 12px; text-align: center;">
                <h4>📅 No Schedule Available</h4>
                <p style="margin: 0;">No timetable has been set for today.</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Gantt chart for today
        if today_schedule:
            st.markdown("""
            <div style="text-align: center; margin: 2rem 0;">
                <h3 style="color: #667eea;">📊 Visual Timeline</h3>
                <p style="color: #666;">Your day at a glance</p>
            </div>
            """, unsafe_allow_html=True)
            
            planner = []
            for s in today_schedule:
                planner.append({
                    'Task': s['period'] + (f" ({s['faculty']})" if s['faculty'] != '-' else ''),
                    'Start': datetime.combine(date, datetime.strptime(s['start'], '%I:%M %p').time()),
                    'Finish': datetime.combine(date, datetime.strptime(s['end'], '%I:%M %p').time()),
                    'Type': 'Free' if s['free'] else 'Class'
                })
            df = pd.DataFrame(planner)
            colors = {'Class': 'rgb(66, 135, 245)', 'Free': 'rgb(0, 204, 150)'}
            fig = ff.create_gantt(df, index_col='Type', show_colorbar=True, group_tasks=True, colors=colors, title='', bar_width=0.3, showgrid_x=True, showgrid_y=True)
            st.plotly_chart(fig, use_container_width=True)
        
        # Daily routine generator
        st.markdown("""
        <div class="ai-suggestion-card">
            <h2 style="margin-bottom: 1rem;">🤖 AI-Powered Daily Routine</h2>
            <p style="opacity: 0.9; margin: 0;">Personalized suggestions for your free periods</p>
        </div>
        """, unsafe_allow_html=True)
        
        if student_data and today_schedule:
            interests = student_data.get('interests', [])
            goals = student_data.get('goals', '')
            progress = student_data.get('progress', {})
            completed_tasks = student_data.get('completed_tasks', [])
            routine = []
            for s in today_schedule:
                if s['free']:
                    suggestions = []
                    
                    st.markdown(f"""
                    <div style="background: white; padding: 1.5rem; border-radius: 12px; margin: 1rem 0; border-left: 4px solid #4CAF50;">
                        <h4 style="color: #4CAF50; margin-bottom: 1rem;">🆓 Free Period: {s['start']} - {s['end']}</h4>
                    """, unsafe_allow_html=True)
                    
                    if student_data:
                        student_name = student_data.get('name', '')
                        marks_ref = db.collection('students').document(register_number).collection('marks').stream()
                        marks_data = [m.to_dict() for m in marks_ref]
                        user_message = build_student_message(student_name, marks_data, interests, free_period_time=f"{s['start']} - {s['end']}")
                        
                        with st.spinner("🤖 AI is analyzing your data and generating suggestions..."):
                            response = call_mistral_api(system_prompt, user_message, max_tokens=768)
                        
                        response = boldify(response)
                        st.markdown(
                            f'''
                            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                       padding: 2rem; border-radius: 12px; color: white; 
                                       box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3); 
                                       font-size: 1.1rem; margin: 1rem 0; max-height: 400px; overflow-y: auto;">
                                {response}
                            </div>
                            ''',
                            unsafe_allow_html=True
                        )
                        
                        # Extract tasks from response (bulleted or numbered points)
                        tasks = re.findall(r'\n\s*[-*•]\s+(.+)', response)
                        if not tasks:
                            tasks = re.findall(r'\n\s*\d+\.\s+(.+)', response)
                        
                        if tasks:
                            suggestions.extend(tasks)
                        else:
                            suggestions.append(response)
                    else:
                        st.warning('⚠️ No student data found.')
                    
                    # Task completion checkboxes
                    if suggestions and isinstance(suggestions[0], str):
                        st.markdown("#### ✅ Task Completion")
                        for idx, suggestion in enumerate(suggestions[:5]):  # Limit to 5 tasks
                            done = suggestion in completed_tasks
                            if done:
                                st.checkbox(f"✅ {suggestion}", value=True, disabled=True, key=f'daily_done_{s["start"]}_{idx}')
                            else:
                                if st.checkbox(f"📝 {suggestion}", value=False, key=f'daily_{s["start"]}_{idx}'):
                                    completed_tasks.append(suggestion)
                                    for interest in interests:
                                        if interest.lower() in suggestion.lower():
                                            progress[interest] = min(progress.get(interest, 0) + 20, 100)
                                    student_ref.update({'completed_tasks': completed_tasks, 'progress': progress})
                                    st.success(f'✅ Task completed: {suggestion}')
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    routine.append({
                        'start': s['start'],
                        'end': s['end'],
                        'suggestions': suggestions
                    })
            
            if not routine:
                st.markdown("""
                <div style="background: #e3f2fd; color: #1976d2; padding: 2rem; border-radius: 12px; text-align: center; margin: 2rem 0;">
                    <h4>📚 Fully Scheduled Day</h4>
                    <p style="margin: 0;">No free periods available today - all periods are scheduled!</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Progress Dashboard
            st.markdown("""
            <div class="progress-section">
                <h3 style="color: #ff9800; margin-bottom: 1.5rem;">📈 Your Progress Dashboard</h3>
            """, unsafe_allow_html=True)
            
            for interest in interests:
                pct = progress.get(interest, 0)
                st.markdown(f"**🎯 {interest.title()}**")
                st.progress(pct / 100.0 if pct > 1 else pct)
                st.markdown(f"<small style='color: #666;'>{pct}% Complete</small>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Completed Tasks History
            st.markdown("""
            <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); margin: 2rem 0; border-top: 4px solid #28a745;">
                <h3 style="color: #28a745; margin-bottom: 1.5rem;">✅ Completed Tasks History</h3>
            """, unsafe_allow_html=True)
            
            if completed_tasks:
                for task in completed_tasks:
                    st.markdown(f"""
                    <div style="background: #d4edda; color: #155724; padding: 1rem; border-radius: 8px; border-left: 4px solid #28a745; margin: 0.5rem 0;">
                        ✅ {task}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background: #e3f2fd; color: #1976d2; padding: 1.5rem; border-radius: 8px; text-align: center;">
                    <p style="margin: 0;">🚀 No tasks completed yet. Start with your first suggestion!</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
        else:
            st.markdown("""
            <div style="background: #fff3cd; color: #856404; padding: 2rem; border-radius: 12px; text-align: center; border-left: 4px solid #ffc107; margin: 2rem 0;">
                <h4>📝 Information Required</h4>
                <p style="margin: 0;">Enter your register number to see your personalized routine and progress.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Real-time attendance display
        st.markdown("""
        <div class="attendance-card">
            <h2 style="margin-bottom: 1rem;">🟢 Real-Time Attendance Status</h2>
            <p style="opacity: 0.9; margin: 0;">Live attendance data for your class</p>
        </div>
        """, unsafe_allow_html=True)
        
        attendance_ref = db.collection('attendance').document(f'{class_name}_{date}')
        attendance_doc = attendance_ref.get()
        if attendance_doc.exists:
            att_data = attendance_doc.to_dict()
            present = att_data.get('present', [])
            absent = att_data.get('absent', [])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); border-top: 4px solid #28a745; text-align: center;">
                    <h3 style="color: #28a745; margin-bottom: 1rem;">✅ Present Students</h3>
                    <h2 style="color: #28a745; margin: 0;">{len(present)}</h2>
                </div>
                """, unsafe_allow_html=True)
                
                if present:
                    st.markdown("**📋 Present List:**")
                    for student in present:
                        st.markdown(f"• {student}")
            
            with col2:
                st.markdown(f"""
                <div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); border-top: 4px solid #dc3545; text-align: center;">
                    <h3 style="color: #dc3545; margin-bottom: 1rem;">❌ Absent Students</h3>
                    <h2 style="color: #dc3545; margin: 0;">{len(absent)}</h2>
                </div>
                """, unsafe_allow_html=True)
                
                if absent:
                    st.markdown("**📋 Absent List:**")
                    for student in absent:
                        st.markdown(f"• {student}")
        else:
            st.markdown("""
            <div style="background: #e3f2fd; color: #1976d2; padding: 2rem; border-radius: 12px; text-align: center; margin: 2rem 0;">
                <h4>📊 No Attendance Data</h4>
                <p style="margin: 0;">No attendance records found for this class and date.</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%); 
                    color: white; padding: 3rem; border-radius: 15px; text-align: center; 
                    box-shadow: 0 10px 30px rgba(78, 205, 196, 0.3); margin: 2rem 0;">
            <h2>🚀 Get Started</h2>
            <p style="font-size: 1.2rem; margin: 1rem 0;">Enter your class name above to view your personalized daily planner!</p>
            <div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 8px; margin-top: 1.5rem;">
                <p style="margin: 0; font-size: 0.9rem;">💡 Tip: Make sure to enter both your class and register number for the best experience</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == '__main__':
    show_visual_daily_planner()
