import streamlit as st

# Enhanced page configuration
st.set_page_config(
    page_title='AI Suggestion Engine - Smart Attendance Suite',
    page_icon='💡',
    layout='wide'
)

# Custom CSS for premium suggestion engine UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }
    
    .suggestion-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .suggestion-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .input-section {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        border-left: 5px solid #667eea;
    }
    
    .profile-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        margin: 2rem 0;
        border-top: 4px solid #4CAF50;
    }
    
    .academic-alert {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(255, 152, 0, 0.3);
    }
    
    .interests-card {
        background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(78, 205, 196, 0.3);
    }
    
    .progress-section {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        margin: 2rem 0;
        border-top: 4px solid #ff9800;
    }
    
    .ai-response-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        max-height: 500px;
        overflow-y: auto;
    }
    
    .dynamic-suggestions {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        margin: 2rem 0;
        border-left: 5px solid #ff6b6b;
    }
    
    .completed-tasks {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        margin: 2rem 0;
        border-top: 4px solid #28a745;
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
    
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e1e5e9;
        padding: 0.75rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stProgress > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    .stCheckbox > label {
        background: #f8f9fa;
        padding: 0.75rem;
        border-radius: 8px;
        border-left: 3px solid #667eea;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .stCheckbox > label:hover {
        background: #e9ecef;
        transform: translateX(5px);
    }
    
    .suggestion-item {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .suggestion-item:hover {
        background: #e9ecef;
        transform: translateX(5px);
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

from firebase.firebase_admin_init import get_firestore_client
import requests
import json
import re

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

def show_suggestion_engine():
    # Enhanced suggestion engine header
    st.markdown("""
    <div class="suggestion-header">
        <h1>💡 AI Suggestion Engine</h1>
        <p style="font-size: 1.2rem; margin: 0; opacity: 0.9;">
            Get personalized learning recommendations powered by artificial intelligence
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
    
    # Enhanced input section
    st.markdown("""
    <div class="input-section">
        <h3 style="color: #667eea; margin-bottom: 1rem;">📝 Enter Your Details</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        class_name = st.text_input(
            '📚 Class (e.g., 10A, 12B, etc.)', 
            max_chars=10, 
            key='suggestion_class_name',
            help="Enter your class identifier"
        )
    
    with col2:
        register_number = st.text_input(
            '🎓 Register Number (e.g., 22ISR026)', 
            max_chars=20, 
            key='suggestion_register_number',
            help="Enter your student registration number"
        )
    
    db = get_firestore_client()
    
    if class_name and register_number:
        student_ref = db.collection('students').document(register_number)
        doc = student_ref.get()
        if doc.exists and doc.to_dict().get('class') == class_name:
            data = doc.to_dict()
            student_name = data.get('name', '')
            interests = data.get('interests', [])
            goals = data.get('goals', '')
            progress = data.get('progress', {})
            completed_tasks = data.get('completed_tasks', [])
            
            # Enhanced student profile display
            st.markdown(f"""
            <div class="profile-card">
                <h3 style="color: #4CAF50; margin-bottom: 1rem;">👤 Student Profile</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                    <div>
                        <h4 style="color: #333; margin-bottom: 0.5rem;">📝 Name</h4>
                        <p style="font-size: 1.1rem; color: #666; margin: 0;">{student_name}</p>
                    </div>
                    <div>
                        <h4 style="color: #333; margin-bottom: 0.5rem;">🎓 Register Number</h4>
                        <p style="font-size: 1.1rem; color: #666; margin: 0;">{register_number}</p>
                    </div>
                    <div>
                        <h4 style="color: #333; margin-bottom: 0.5rem;">📚 Class</h4>
                        <p style="font-size: 1.1rem; color: #666; margin: 0;">{class_name}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Fetch academic data
            marks_ref = student_ref.collection('marks').stream()
            marks_data = [m.to_dict() for m in marks_ref]
            academic_alerts = []
            for m in marks_data:
                if m.get('marks', 100) < 50 or m.get('grade', '').upper() in ['C', 'D', 'E', 'F']:
                    academic_alerts.append(f"Low performance in {m.get('subject', '')} ({m.get('exam', '')}): {m.get('marks', '')} ({m.get('grade', '')})")
                if 'feedback' in m and m['feedback'] and ('improve' in m['feedback'].lower() or 'poor' in m['feedback'].lower()):
                    academic_alerts.append(f"Faculty feedback for {m.get('subject', '')}: {m['feedback']}")
            
            if academic_alerts:
                st.markdown("""
                <div class="academic-alert">
                    <h3 style="margin-bottom: 1rem;">⚠️ Academic Focus Needed!</h3>
                    <p style="opacity: 0.9; margin: 0;">Areas requiring immediate attention</p>
                </div>
                """, unsafe_allow_html=True)
                
                for alert in academic_alerts:
                    st.markdown(f"""
                    <div style="background: #fff3cd; color: #856404; padding: 1rem; border-radius: 8px; border-left: 4px solid #ffc107; margin: 0.5rem 0;">
                        ⚠️ {alert}
                    </div>
                    """, unsafe_allow_html=True)
            
            if not interests:
                st.markdown("""
                <div style="background: #e3f2fd; color: #1976d2; padding: 2rem; border-radius: 12px; text-align: center; margin: 2rem 0;">
                    <h4>🎯 Set Your Interests</h4>
                    <p style="margin: 0;">No interests found. Please enter your interests to get personalized suggestions.</p>
                </div>
                """, unsafe_allow_html=True)
                
                new_interests = st.text_input(
                    '🎯 Enter Your Interests (comma separated)', 
                    key='suggestion_new_interests',
                    placeholder="e.g., coding, mathematics, science, art, music",
                    help="Enter your interests separated by commas"
                )
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button('💾 Save Interests', key='suggestion_save_interests', use_container_width=True) and new_interests:
                    student_ref.update({'interests': [i.strip() for i in new_interests.split(',')]})
                        st.markdown("""
                        <div style="background: #d4edda; color: #155724; padding: 1.5rem; border-radius: 8px; text-align: center; margin: 1rem 0;">
                            <h4>✅ Success!</h4>
                            <p style="margin: 0;">Interests saved! Please reload to see personalized suggestions.</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                # Enhanced interests display
                st.markdown(f"""
                <div class="interests-card">
                    <h3 style="margin-bottom: 1rem;">🎯 Your Learning Profile</h3>
                    <div style="margin-bottom: 1rem;">
                        <h4 style="opacity: 0.9;">Interests:</h4>
                        <p style="font-size: 1.1rem; margin: 0;">{', '.join(interests)}</p>
                    </div>
                    <div>
                        <h4 style="opacity: 0.9;">Goal:</h4>
                        <p style="font-size: 1.1rem; margin: 0;">{goals if goals else 'Not set yet'}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Update interests/goals section
                with st.expander("✏️ Update Your Profile", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        new_interests = st.text_input(
                            'Update Interests', 
                            value=','.join(interests), 
                            key='suggestion_update_interests',
                            help="Modify your interests (comma separated)"
                        )
                    with col2:
                        new_goals = st.text_input(
                            'Update Goal', 
                            value=goals, 
                            key='suggestion_update_goals',
                            help="Set or update your learning goal"
                        )
                    
                    if st.button('💾 Save Updates', key='suggestion_save_updates', use_container_width=True):
                        student_ref.update({'interests': [i.strip() for i in new_interests.split(',')], 'goals': new_goals})
                        st.success('✅ Profile updated! Please reload to see new suggestions.')
                
                # Progress Overview
                st.markdown("""
                <div class="progress-section">
                    <h3 style="color: #ff9800; margin-bottom: 1.5rem;">📈 Progress Overview</h3>
                """, unsafe_allow_html=True)
                
                for interest in interests:
                    pct = progress.get(interest, 0)
                    st.markdown(f"**🎯 {interest.title()}**")
                    st.progress(pct / 100.0 if pct > 1 else pct)
                    st.markdown(f"<small style='color: #666;'>{pct}% Complete</small>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Main suggestions section
                st.markdown("""
                <div style="text-align: center; margin: 2rem 0;">
                    <h2 style="color: #667eea;">🎯 Your Personalized Learning Plan</h2>
                    <p style="color: #666; font-size: 1.1rem;">AI-powered recommendations tailored just for you</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Generate dynamic suggestions based on student data
                dynamic_suggestions = generate_dynamic_suggestions(student_name, marks_data, interests, progress, completed_tasks)
                
                # Display dynamic suggestions first
                st.markdown("""
                <div class="dynamic-suggestions">
                    <h3 style="color: #ff6b6b; margin-bottom: 1.5rem;">📊 Data-Driven Recommendations</h3>
                    <p style="color: #666; margin-bottom: 1rem;">Based on your academic performance and progress</p>
                """, unsafe_allow_html=True)
                
                for suggestion in dynamic_suggestions[:5]:  # Show top 5 dynamic suggestions
                    st.markdown(f"""
                    <div class="suggestion-item">
                        👉 {suggestion}
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # AI-powered suggestions
                st.markdown("""
                <div style="text-align: center; margin: 2rem 0;">
                    <h3 style="color: #667eea;">🤖 AI-Powered Personalized Suggestions</h3>
                    <p style="color: #666;">Advanced AI analysis of your learning patterns</p>
                </div>
                """, unsafe_allow_html=True)
                
                user_message = build_student_message(student_name, marks_data, interests)
                
                with st.spinner("🤖 AI is analyzing your data and generating personalized suggestions..."):
                    response = call_mistral_api(system_prompt, user_message, max_tokens=768)
                
                response = boldify(response)
                
                st.markdown(f"""
                <div class="ai-response-card">
                    {response}
                </div>
                """, unsafe_allow_html=True)
                
                # Extract tasks from response (bulleted or numbered points)
                tasks = re.findall(r'\n\s*[-*•]\s+(.+)', response)
                if not tasks:
                    tasks = re.findall(r'\n\s*\d+\.\s+(.+)', response)
                
                # Task completion section
                if tasks:
                    st.markdown("""
                    <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); margin: 2rem 0; border-left: 5px solid #4CAF50;">
                        <h3 style="color: #4CAF50; margin-bottom: 1.5rem;">✅ Task Completion Tracker</h3>
                        <p style="color: #666; margin-bottom: 1rem;">Check off tasks as you complete them to track your progress</p>
                    """, unsafe_allow_html=True)
                    
                    for idx, task in enumerate(tasks):
                        done = task in completed_tasks
                        if done:
                            st.checkbox(f"✅ {task}", value=True, disabled=True, key=f'sugg_done_{idx}')
                        else:
                            if st.checkbox(f"📝 {task}", value=False, key=f'sugg_{idx}'):
                                completed_tasks.append(task)
                                for interest in interests:
                                    if interest.lower() in task.lower():
                                        progress[interest] = min(progress.get(interest, 0) + 20, 100)
                                student_ref.update({'completed_tasks': completed_tasks, 'progress': progress})
                                st.success(f'🎉 Great job! Task completed: {task}')
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Completed tasks history
                st.markdown("""
                <div class="completed-tasks">
                    <h3 style="color: #28a745; margin-bottom: 1.5rem;">🏆 Your Achievement History</h3>
                """, unsafe_allow_html=True)
                
                if tasks:
                    if completed_tasks:
                        st.markdown(f"""
                        <div style="background: #d4edda; color: #155724; padding: 1.5rem; border-radius: 8px; text-align: center; margin-bottom: 1rem;">
                            <h4>🎉 Amazing Progress!</h4>
                            <p style="margin: 0;">You've completed {len(completed_tasks)} tasks so far. Keep it up!</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        for task in completed_tasks:
                            st.markdown(f"""
                            <div style="background: #d4edda; color: #155724; padding: 1rem; border-radius: 8px; border-left: 4px solid #28a745; margin: 0.5rem 0;">
                                ✅ {task}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div style="background: #e3f2fd; color: #1976d2; padding: 1.5rem; border-radius: 8px; text-align: center;">
                            <p style="margin: 0;">🚀 Start completing tasks to see your achievements here!</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    for task in completed_tasks:
                        st.markdown(f"""
                        <div style="background: #d4edda; color: #155724; padding: 1rem; border-radius: 8px; border-left: 4px solid #28a745; margin: 0.5rem 0;">
                            ✅ {task}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    if not completed_tasks:
                        st.markdown("""
                        <div style="background: #e3f2fd; color: #1976d2; padding: 1.5rem; border-radius: 8px; text-align: center;">
                            <p style="margin: 0;">🚀 No tasks completed yet. Start with your first suggestion!</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
                
        else:
            st.markdown("""
            <div style="background: #fff3cd; color: #856404; padding: 2rem; border-radius: 12px; text-align: center; border-left: 4px solid #ffc107; margin: 2rem 0;">
                <h4>⚠️ Student Not Found</h4>
                <p style="margin: 0;">Please check your register number and class. Make sure they match your enrollment records.</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%); 
                    color: white; padding: 3rem; border-radius: 15px; text-align: center; 
                    box-shadow: 0 10px 30px rgba(78, 205, 196, 0.3); margin: 2rem 0;">
            <h2>🚀 Get Started</h2>
            <p style="font-size: 1.2rem; margin: 1rem 0;">Enter your class and register number above to unlock personalized AI-powered suggestions!</p>
            <div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 8px; margin-top: 1.5rem;">
                <p style="margin: 0; font-size: 0.9rem;">💡 Tip: Make sure your details match your enrollment records for the best experience</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

system_prompt = (
    "You are a helpful, practical, and emotionally supportive student assistant. "
    "Always keep your answers short, actionable, and encouraging. "
    "Give specific, lively, and personalized study plans or suggestions for students based on their marks and interests. "
    "Start your response with a friendly greeting using the student's name."
)

def build_student_message(student_name, marks_data, interests, free_period="Free Period"):
    if marks_data:
        focus = min(marks_data, key=lambda m: m.get('marks', 100))
        subject = focus.get('subject', 'your subjects')
        mark = focus.get('marks', 'N/A')
        exam = focus.get('exam', '')
        mark_str = f"{subject} ({mark}%, {exam})"
    else:
        mark_str = "your subjects"
    interest_str = ', '.join(interests) if interests else "your interests"
    return (
        f"Hyy {student_name}! I have a free period now. "
        f"My recent marks: {mark_str}. My interests: {interest_str}. "
        "What is a practical, encouraging, and specific study plan or suggestion for me to use this free time wisely?"
    )

def boldify(text):
    return re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)

def generate_dynamic_suggestions(student_name, marks_data, interests, progress, completed_tasks):
    """Generate personalized suggestions based on student's actual data"""
    suggestions = []
    
    # Analyze academic performance
    subject_performance = {}
    weak_subjects = []
    strong_subjects = []
    
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
    
    # Categorize subjects
    for subject, data in subject_performance.items():
        if data['marks']:
            avg_marks = sum(data['marks']) / len(data['marks'])
            if avg_marks < 50 or any(g in ['C', 'D', 'E', 'F'] for g in data['grades']):
                weak_subjects.append((subject, avg_marks))
            elif avg_marks >= 80:
                strong_subjects.append((subject, avg_marks))
    
    # Generate suggestions based on weak subjects
    if weak_subjects:
        for subject, avg_marks in weak_subjects:
            if 'math' in subject.lower() or 'mathematics' in subject.lower():
                suggestions.append(f"🔢 **{subject}**: Practice 10-15 problems daily. Your average: {avg_marks:.1f}%")
                suggestions.append(f"📚 **{subject}**: Review fundamental concepts and solve previous year papers")
            elif 'science' in subject.lower() or 'physics' in subject.lower() or 'chemistry' in subject.lower():
                suggestions.append(f"🔬 **{subject}**: Conduct practical experiments. Current average: {avg_marks:.1f}%")
                suggestions.append(f"📖 **{subject}**: Watch educational videos and create concept maps")
            elif 'english' in subject.lower() or 'language' in subject.lower():
                suggestions.append(f"📝 **{subject}**: Read daily for 30 minutes. Improve from {avg_marks:.1f}%")
                suggestions.append(f"🗣️ **{subject}**: Practice speaking and vocabulary building")
            elif 'computer' in subject.lower() or 'programming' in subject.lower() or 'coding' in subject.lower():
                suggestions.append(f"💻 **{subject}**: Code for 1 hour daily on LeetCode/HackerRank")
                suggestions.append(f"🛠️ **{subject}**: Build small projects to apply concepts")
            else:
                suggestions.append(f"📖 **{subject}**: Dedicate 45 minutes daily for revision. Target: Improve from {avg_marks:.1f}%")
    
    # Generate suggestions based on strong subjects
    if strong_subjects:
        suggestions.append(f"🌟 **Excellent Performance**: You're excelling in {', '.join([s[0] for s in strong_subjects])}!")
        for subject, avg_marks in strong_subjects:
            suggestions.append(f"🎯 **{subject}**: Challenge yourself with advanced topics and competitions")
    
    # Generate suggestions based on interests (only if no weak subjects)
    if not weak_subjects and interests:
        for interest in interests:
            if 'coding' in interest.lower() or 'programming' in interest.lower():
                suggestions.append("💻 **Coding**: Join coding competitions or contribute to open-source projects")
            elif 'math' in interest.lower() or 'mathematics' in interest.lower():
                suggestions.append("🔢 **Mathematics**: Participate in math olympiads or solve advanced problems")
            elif 'science' in interest.lower():
                suggestions.append("🔬 **Science**: Conduct experiments or read scientific journals")
            elif 'art' in interest.lower() or 'design' in interest.lower():
                suggestions.append("🎨 **Art**: Create a portfolio or learn new techniques")
            elif 'reading' in interest.lower() or 'literature' in interest.lower():
                suggestions.append("📚 **Reading**: Join book clubs or write reviews")
    
    # Generate suggestions based on progress
    if progress:
        low_progress_interests = [interest for interest, pct in progress.items() if pct < 30]
        if low_progress_interests:
            suggestions.append(f"📈 **Progress**: Focus on {', '.join(low_progress_interests)} - current progress is low")
    
    # Generate suggestions based on completed tasks
    if completed_tasks:
        suggestions.append(f"✅ **Great Progress**: You've completed {len(completed_tasks)} tasks! Keep it up!")
    
    # Add general suggestions
    suggestions.append("📝 **Study Technique**: Use active recall and spaced repetition")
    suggestions.append("⏰ **Time Management**: Create a daily study schedule")
    suggestions.append("🌐 **Learning**: Explore online courses on Coursera, edX, or Khan Academy")
    
    return suggestions

if __name__ == '__main__':
    show_suggestion_engine()
