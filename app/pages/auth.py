import streamlit as st

# Enhanced page configuration
st.set_page_config(
    page_title='Authentication - Smart Attendance Suite',
    page_icon='🔐',
    layout='centered'
)

# Custom CSS for premium authentication UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .auth-container {
        background: white;
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        margin: 2rem auto;
        max-width: 500px;
    }
    
    .auth-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .auth-header h1 {
        color: #667eea;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .auth-header p {
        color: #666;
        font-size: 1.1rem;
        margin: 0;
    }
    
    .stRadio > div {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 12px;
        border: 2px solid #e1e5e9;
    }
    
    .stRadio > div > label {
        font-weight: 600;
        color: #333;
    }
    
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 10px;
        border: 2px solid #e1e5e9;
        padding: 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 1rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .period-info {
        background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(78, 205, 196, 0.3);
    }
    
    .period-list {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .success-message {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(76, 175, 80, 0.3);
        margin: 1rem 0;
    }
    
    .warning-message {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(255, 152, 0, 0.3);
        margin: 1rem 0;
    }
    
    .stFileUploader > div {
        border: 2px dashed #667eea;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        background: #f8f9ff;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div:hover {
        border-color: #764ba2;
        background: #f0f4ff;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

from firebase.firebase_admin_init import get_firestore_client
import io
import base64
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

def show_auth_page():
    # Main authentication container
    st.markdown("""
    <div class="auth-container">
        <div class="auth-header">
            <h1>🔐 Authentication</h1>
            <p>Access your Smart Attendance Suite</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    db = get_firestore_client()
    
    # Check if user is already logged in and redirect appropriately
    if 'user' in st.session_state and 'role' in st.session_state:
        if st.session_state['role'] == 'student':
            st.switch_page('pages/student_dashboard.py')
        elif st.session_state['role'] == 'faculty':
            st.switch_page('main_dashboard.py')
    
    # Enhanced mode selection
    st.markdown("### 🎯 Choose Action")
    mode = st.radio(
        'Select what you want to do:', 
        ['🔑 Login', '📝 Signup', '⏰ Check-in'], 
        horizontal=True,
        help="Choose your desired action"
    )
    
    if mode == '⏰ Check-in':
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 2rem; border-radius: 15px; text-align: center; 
                    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3); margin: 2rem 0;">
            <h2>⏰ Faculty Check-in</h2>
            <p>Mark your attendance for the current period</p>
        </div>
        """, unsafe_allow_html=True)
        
        if 'user' not in st.session_state or 'role' not in st.session_state:
            st.markdown("""
            <div class="warning-message">
                <h4>⚠️ Authentication Required</h4>
                <p>Please login first to check-in.</p>
            </div>
            """, unsafe_allow_html=True)
            return
        
        if st.session_state['role'] != 'faculty':
            st.error('Only faculty members can check-in.')
            return
            
        faculty = st.session_state['user']
        
        st.markdown("#### 📚 Class Information")
        class_name = st.text_input(
            'Class (e.g., 10A, 12B, etc.)',
            help="Enter the class you are teaching",
            placeholder="Enter class name..."
        )
        
        # Time period validation
        from datetime import datetime, time
        current_time = datetime.now().time()
        
        PERIODS = [
            {'label': '8:45 am - 9:40 am', 'start': time(8, 45), 'end': time(9, 40)},
            {'label': '9:40 am - 10:25 am', 'start': time(9, 40), 'end': time(10, 25)},
            {'label': '10:45 am - 11:30 am', 'start': time(10, 45), 'end': time(11, 30)},
            {'label': '11:30 am - 12:15 pm', 'start': time(11, 30), 'end': time(12, 15)},
            {'label': '1:15 pm - 2:00 pm', 'start': time(13, 15), 'end': time(14, 0)},
            {'label': '2:00 pm - 2:45 pm', 'start': time(14, 0), 'end': time(14, 45)},
            {'label': '3:00 pm - 3:45 pm', 'start': time(15, 0), 'end': time(15, 45)},
            {'label': '3:45 pm - 4:30 pm', 'start': time(15, 45), 'end': time(16, 30)},
        ]
        
        # Find current period
        current_period = None
        for i, period in enumerate(PERIODS):
            if period['start'] <= current_time <= period['end']:
                current_period = i
                break
        
        if current_period is not None:
            st.markdown(f"""
            <div class="success-message">
                <h4>✅ Active Period Detected</h4>
                <p><strong>Current Period:</strong> {PERIODS[current_period]['label']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button('✅ Check In Now', use_container_width=True):
                    if not class_name:
                        st.error("⚠️ Please enter a class name first!")
                        return
                        
                from datetime import datetime
                date = datetime.today().date()
                checkin_ref = db.collection('checkins').document(f'{date}_{class_name}_{current_period}')
                checkin_ref.set({
                    'faculty': faculty, 
                    'class': class_name, 
                    'date': str(date), 
                    'period_idx': current_period, 
                    'period_label': PERIODS[current_period]['label'], 
                    'timestamp': datetime.now().isoformat()
                })
                    
                    st.markdown(f"""
                    <div class="success-message">
                        <h4>🎉 Check-in Successful!</h4>
                        <p>You have been checked in for <strong>{PERIODS[current_period]["label"]}</strong> in class <strong>{class_name}</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="warning-message">
                <h4>⏰ No Active Period</h4>
                <p>Check-in is only allowed during class periods.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="period-list">
                <h4>📅 Today's Time Periods:</h4>
            """, unsafe_allow_html=True)
            
            for period in PERIODS:
                st.markdown(f"• **{period['label']}**")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    else:
        # Enhanced login/signup form
        st.markdown("### 👤 Account Details")
        
        col1, col2 = st.columns(2)
        with col1:
            role = st.selectbox(
                '👥 Select Role', 
                ['student', 'faculty'],
                help="Choose your role in the system"
            )
        
        with col2:
            st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)
        
        username = st.text_input(
            '👤 Username',
            placeholder="Enter your username...",
            help="Your unique username for the system"
        )
        
        password = st.text_input(
            '🔒 Password', 
            type='password',
            placeholder="Enter your password...",
            help="Your secure password"
        )
        
        if mode == '📝 Signup':
            st.markdown("---")
            st.markdown("### 📋 Additional Information")
            
            extra = {}
            if role == 'student':
                col1, col2 = st.columns(2)
                with col1:
                    extra['register_number'] = st.text_input(
                        '🎓 Register Number',
                        placeholder="e.g., 22ISR026",
                        help="Your unique student registration number"
                    )
                    extra['class'] = st.text_input(
                        '📚 Class',
                        placeholder="e.g., 10A, 12B",
                        help="Your class/section"
                    )
                
                with col2:
                    extra['name'] = st.text_input(
                        '👤 Full Name',
                        placeholder="Enter your full name...",
                        help="Your complete name as per records"
                    )
                
                # Add photo collection for students
                st.markdown("---")
                st.markdown("### 📸 Face Recognition Setup")
                st.markdown("""
                <div style="background: #e3f2fd; padding: 1rem; border-radius: 8px; border-left: 4px solid #2196f3; margin: 1rem 0;">
                    <strong>📋 Photo Requirements:</strong>
                    <ul style="margin: 0.5rem 0;">
                        <li>Upload exactly 15 clear photos of your face</li>
                        <li>Include different angles and expressions</li>
                        <li>Ensure good lighting and clear visibility</li>
                        <li>Photos will be used for attendance recognition</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                uploaded_images = st.file_uploader(
                    '📷 Upload Your Photos (Exactly 15 required)', 
                    type=['jpg', 'jpeg', 'png'], 
                    accept_multiple_files=True,
                    help="Select 15 clear photos of your face from different angles"
                )
                
                if uploaded_images:
                    if len(uploaded_images) != 15:
                        st.markdown(f"""
                        <div style="background: #ffebee; color: #c62828; padding: 1rem; border-radius: 8px; border-left: 4px solid #f44336;">
                            <strong>⚠️ Incorrect Image Count</strong><br>
                            Please upload exactly 15 images. You have uploaded {len(uploaded_images)} images.
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="success-message">
                            <h4>✅ Perfect!</h4>
                            <p>{len(uploaded_images)} images uploaded successfully!</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                col1, col2 = st.columns(2)
                with col1:
                    extra['faculty_name'] = st.text_input(
                        '👨‍🏫 Full Name',
                        placeholder="Enter your full name...",
                        help="Your complete name as faculty member"
                    )
                
                with col2:
                    extra['subjects'] = st.text_input(
                        '📖 Subjects Handled',
                        placeholder="Math, Physics, Chemistry",
                        help="Enter subjects separated by commas"
                    )
            
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button('🚀 Create Account', use_container_width=True):
                # Check for duplicate username
                user_ref = db.collection('users').document(username)
                if user_ref.get().exists:
                    st.error('Username already exists! Please choose a different username.')
                else:
                    # For students, also check for duplicate register number
                    if role == 'student':
                        regno = extra.get('register_number', '')
                        if regno and db.collection('users').where('register_number', '==', regno).get():
                            st.error('A student with this register number already exists!')
                            return
                        
                        # Check if student record already exists
                        if regno and db.collection('students').document(regno).get().exists:
                            st.error('A student record with this register number already exists!')
                            return
                    
                    # Validate photo upload for students
                    if role == 'student' and (not uploaded_images or len(uploaded_images) != 15):
                        st.error('Please upload exactly 15 images of yourself.')
                        return
                    
                    try:
                        # Create user account
                        user_data = {'username': username, 'password': password, 'role': role, **extra}
                        user_ref.set(user_data)
                        
                        # For students, also create student record with photos
                        if role == 'student' and uploaded_images:
                            images_b64 = [compress_and_encode_image(img) for img in uploaded_images]
                            student_ref = db.collection('students').document(extra['register_number'])
                            student_ref.set({
                                'register_number': extra['register_number'],
                                'name': extra['name'],
                                'class': extra['class'],
                                'images': images_b64,
                                'username': username  # Link to user account
                            })
                        
                        st.success('Signup successful! Please login.')
                        st.rerun()
                    except Exception as e:
                        st.error(f'Error during signup: {e}')
        
        else:  # Login mode
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button('🔑 Sign In', use_container_width=True):
                user_ref = db.collection('users').document(username)
                doc = user_ref.get()
                if not doc.exists:
                    st.error('User not found!')
                elif doc.to_dict().get('password') != password:
                    st.error('Incorrect password!')
                elif doc.to_dict().get('role') != role:
                    st.error('Role mismatch! Please select the correct role.')
                else:
                    st.session_state['user'] = username
                    st.session_state['role'] = role
                    
                    st.markdown(f"""
                    <div class="success-message">
                        <h4>🎉 Welcome Back!</h4>
                        <p>Successfully logged in as <strong>{role.title()}</strong>: {username}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Role-based redirect
                    if role == 'student':
                        st.switch_page('pages/student_dashboard.py')
                    elif role == 'faculty':
                        st.switch_page('main_dashboard.py')

# Call the main function
if __name__ == '__main__':
    show_auth_page()
else:
    show_auth_page()
