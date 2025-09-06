import streamlit as st
st.set_page_config(
    page_title='Smart Attendance & Productivity Suite', 
    layout='wide', 
    initial_sidebar_state='collapsed',
    page_icon='🎓'
)

# Custom CSS for premium UI
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Card Styling */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    .success-card {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(76, 175, 80, 0.3);
        margin-bottom: 1rem;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(255, 152, 0, 0.3);
        margin-bottom: 1rem;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Input Styling */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e1e5e9;
        padding: 0.75rem;
        font-size: 1rem;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 8px;
        padding: 0 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Metrics Styling */
    .metric-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 4px solid #667eea;
    }
    
    /* Student List Styling */
    .student-list {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    /* Form Styling */
    .stForm {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border: 1px solid #e1e5e9;
    }
    
    /* File Uploader Styling */
    .stFileUploader > div {
        border: 2px dashed #667eea;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        background: #f8f9ff;
    }
    
    /* Progress Bar Styling */
    .stProgress > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Alert Styling */
    .stAlert {
        border-radius: 8px;
        border: none;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: #f8f9fa;
        border-radius: 8px;
        border: 1px solid #e1e5e9;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

from firebase.firebase_admin_init import get_firestore_client
import os
import subprocess
import pathlib
from app.pages.student_registration import show_student_registration
from app.pages.live_attendance import show_live_attendance
from app.pages.admin_dashboard import show_admin_dashboard
from app.pages.marks_feedback import show_marks_feedback_entry
from app.pages.daily_feedback import show_daily_feedback_entry
from app.pages.faculty_student_records import show_faculty_student_records
from app.pages.faculty_checkin import show_faculty_checkin

# Require login and restrict to faculty/admin only
if 'user' not in st.session_state or 'role' not in st.session_state:
    st.switch_page('pages/auth.py')

# Restrict access to faculty/admin only
if st.session_state.get('role') != 'faculty':
    st.markdown("""
    <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%); 
                padding: 2rem; border-radius: 12px; color: white; text-align: center; 
                box-shadow: 0 4px 20px rgba(255, 107, 107, 0.3); margin-bottom: 2rem;">
        <h2>🚫 Access Denied</h2>
        <p style="font-size: 1.1rem; margin: 0;">This dashboard is only for faculty and admin members.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%); 
                padding: 1.5rem; border-radius: 12px; color: white; text-align: center; 
                box-shadow: 0 4px 20px rgba(78, 205, 196, 0.3); margin-bottom: 2rem;">
        <p style="font-size: 1.1rem; margin: 0;">Students should use the Student Dashboard.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button('Go to Student Dashboard', key='main_go_to_student_btn'):
        st.switch_page('pages/student_dashboard.py')
    st.stop()

# Enhanced Sidebar
st.sidebar.markdown(f"""
<div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
    <h3 style="color: white; margin: 0;">👤 Welcome</h3>
    <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0;">
        {st.session_state['user']}<br>
        <small>({st.session_state['role'].title()})</small>
    </p>
</div>
""", unsafe_allow_html=True)

if st.sidebar.button('Logout'):
    st.session_state.clear()
    st.experimental_rerun()

# Main Header
st.markdown("""
<div class="main-header">
    <h1>🎓 Smart Attendance & Productivity Suite</h1>
    <p>Welcome to the all-in-one platform for automated attendance, student productivity, and personalized planning!</p>
</div>
""", unsafe_allow_html=True)

# Enhanced Class Input
st.markdown("### 📚 Class Management")
class_name = st.text_input(
    'Enter Class Name (e.g., 10A, 12B, etc.)', 
    max_chars=10, 
    key='main_class_name',
    help="Enter the class identifier to manage students and attendance"
)
db = get_firestore_client()

if class_name:
    students_ref = db.collection('students').where('class', '==', class_name)
    students = list(students_ref.stream())
    student_list = [(doc.to_dict().get('register_number', ''), doc.to_dict().get('name', '')) for doc in students]
    
    # Enhanced Student Display
    st.markdown(f"""
    <div class="info-card">
        <h3>👥 Students in {class_name}</h3>
        <div class="student-list">
    """, unsafe_allow_html=True)
    
    if student_list:
        for regno, name in student_list:
            st.markdown(f"• **{regno}** - {name}")
    else:
        st.markdown("*No students added yet.*")
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        expected_count = st.number_input(
            'How many students should be in this class?', 
            min_value=1, 
            step=1, 
            key='main_expected_count',
            help="Set the expected number of students for this class"
        )
    
    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <h4>Current Count</h4>
            <h2 style="color: #667eea; margin: 0;">{len(student_list)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    if len(student_list) < expected_count:
        st.markdown(f"""
        <div class="warning-card">
            <h4>⚠️ Incomplete Class</h4>
            <p>Only {len(student_list)} of {expected_count} students added.</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander('➕ Add New Student', expanded=False):
            with st.form('add_student_form'):
                st.markdown("#### 📝 Student Information")
                col1, col2 = st.columns(2)
                with col1:
                    new_regno = st.text_input(
                        'Register Number (e.g., 22ISR026)', 
                        key='new_regno',
                        help="Enter unique student registration number"
                    )
                with col2:
                    new_name = st.text_input(
                        'Student Name', 
                        key='new_name',
                        help="Enter full name of the student"
                    )
                
                st.markdown("#### 📸 Face Recognition Images")
                uploaded_images = st.file_uploader(
                    'Upload exactly 15 images for face recognition training', 
                    type=['jpg', 'jpeg', 'png'], 
                    accept_multiple_files=True, 
                    key='new_images',
                    help="Upload clear face images from different angles for better recognition accuracy"
                )
                
                if uploaded_images:
                    st.info(f"📊 {len(uploaded_images)} images uploaded")
                
                submit = st.form_submit_button('✅ Add Student', use_container_width=True)
                if submit:
                    if not new_regno or not new_name or not uploaded_images or len(uploaded_images) < 15:
                        st.error('Please provide a register number, name, and exactly 15 images.')
                    elif len(uploaded_images) > 15:
                        st.error('Please provide exactly 15 images.')
                    elif any(regno == new_regno for regno, _ in student_list):
                        st.error('A student with this register number already exists.')
                    else:
                        import io, base64
                        from PIL import Image
                        def compress_and_encode_image(image_file, quality=60, max_size=(300, 300)):
                            image = Image.open(image_file)
                            image = image.convert('RGB')
                            image.thumbnail(max_size)
                            buffer = io.BytesIO()
                            image.save(buffer, format='JPEG', quality=quality)
                            img_bytes = buffer.getvalue()
                            img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                            return img_b64
                        images_b64 = [compress_and_encode_image(img) for img in uploaded_images]
                        db.collection('students').document(new_regno).set({
                            'register_number': new_regno,
                            'name': new_name,
                            'class': class_name,
                            'images': images_b64
                        })
                        st.success(f'Student {new_name} ({new_regno}) added!')
                        st.rerun()
    elif len(student_list) == expected_count:
        st.markdown("""
        <div class="success-card">
            <h4>✅ Class Complete!</h4>
            <p>All students have been added successfully.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button('🚀 Start Model Training', key='main_start_training_btn', use_container_width=True):
                st.markdown("""
                <div style="text-align: center; padding: 2rem;">
                    <div style="border: 4px solid #667eea; border-top: 4px solid transparent; 
                                border-radius: 50%; width: 40px; height: 40px; 
                                animation: spin 1s linear infinite; margin: 0 auto 1rem;"></div>
                    <p>Training AI model, please wait...</p>
                </div>
                <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                </style>
                """, unsafe_allow_html=True)
                
                with st.spinner('Training model, please wait...'):
                result = subprocess.run(['python', 'backend/model_training.py'], capture_output=True, text=True)
                if result.returncode == 0:
                    st.success('Model training completed successfully!')
                else:
                    st.error(f'Model training failed: {result.stderr}')
    
    # Enhanced Faculty Tools Section
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h2 style="color: #667eea;">🔗 Faculty Tools</h2>
        <p style="color: #666; font-size: 1.1rem;">Access all faculty features in one place</p>
    </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs([
        '👤 Student Registration',
        '📹 Live Attendance',
        '📝 Marks & Feedback',
        '📅 Daily Feedback',
        '📊 Student Records',
        '⏰ Period Check-in',
        '📈 Admin Dashboard'
    ])
    
    with tabs[0]:
        show_student_registration()
    with tabs[1]:
        show_live_attendance()
    with tabs[2]:
        show_marks_feedback_entry()
    with tabs[3]:
        show_daily_feedback_entry()
    with tabs[4]:
        show_faculty_student_records()
    with tabs[5]:
        show_faculty_checkin()
    with tabs[6]:
        show_admin_dashboard()
else:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%); 
                padding: 3rem; border-radius: 15px; color: white; text-align: center; 
                box-shadow: 0 10px 30px rgba(78, 205, 196, 0.3); margin: 2rem 0;">
        <h2>🚀 Get Started</h2>
        <p style="font-size: 1.2rem; margin: 1rem 0;">Enter a class name above to begin managing students and attendance!</p>
        <div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 8px; margin-top: 1.5rem;">
            <p style="margin: 0; font-size: 0.9rem;">💡 Tip: Use format like "10A", "12B", "CS101" for class names</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Navigation sidebar - Faculty only
st.sidebar.markdown('---')
st.sidebar.markdown("""
<div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;">
    <h4 style="color: white; margin: 0 0 0.5rem 0;">⚡ Quick Actions</h4>
    <p style="color: rgba(255,255,255,0.8); font-size: 0.9rem; margin: 0;">
        All faculty tools are now available in the tabs above. No need to navigate to separate pages!
    </p>
</div>
""", unsafe_allow_html=True)
