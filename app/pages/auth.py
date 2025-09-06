import streamlit as st
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
    st.title('🔐 Login / Signup / Check-in')
    db = get_firestore_client()
    
    # Check if user is already logged in and redirect appropriately
    if 'user' in st.session_state and 'role' in st.session_state:
        if st.session_state['role'] == 'student':
            st.switch_page('pages/student_dashboard.py')
        elif st.session_state['role'] == 'faculty':
            st.switch_page('main_dashboard.py')
    
    mode = st.radio('Choose mode', ['Login', 'Signup', 'Check-in'], horizontal=True)
    
    if mode == 'Check-in':
        st.subheader('Faculty Check-in')
        if 'user' not in st.session_state or 'role' not in st.session_state:
            st.warning('Please login first to check-in.')
            return
        
        if st.session_state['role'] != 'faculty':
            st.error('Only faculty members can check-in.')
            return
            
        faculty = st.session_state['user']
        class_name = st.text_input('Class (e.g., 10A, 12B, etc.)')
        
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
            st.success(f"Current period: {PERIODS[current_period]['label']}")
            if st.button('Check In'):
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
                st.success(f'Checked in for {PERIODS[current_period]["label"]} in {class_name}')
        else:
            st.warning("No active period at this time. Check-in is only allowed during class periods.")
            st.info("Current time periods:")
            for period in PERIODS:
                st.write(f"- {period['label']}")
    
    else:
        role = st.selectbox('Role', ['student', 'faculty'])
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')
        
        if mode == 'Signup':
            extra = {}
            if role == 'student':
                extra['register_number'] = st.text_input('Register Number')
                extra['name'] = st.text_input('Full Name')
                extra['class'] = st.text_input('Class (e.g., 10A, 12B)')
                
                # Add photo collection for students
                st.subheader('Upload 15 Photos of Yourself')
                uploaded_images = st.file_uploader(
                    'Upload 15 images of yourself for face recognition', 
                    type=['jpg', 'jpeg', 'png'], 
                    accept_multiple_files=True,
                    help="Upload exactly 15 clear photos of your face from different angles"
                )
                
                if uploaded_images:
                    if len(uploaded_images) != 15:
                        st.error(f'Please upload exactly 15 images. You have uploaded {len(uploaded_images)} images.')
                    else:
                        st.success(f'✅ {len(uploaded_images)} images uploaded successfully!')
            else:
                extra['faculty_name'] = st.text_input('Full Name')
                extra['subjects'] = st.text_input('Subjects handled (comma separated)')
            
            if st.button('Signup'):
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
        
        else:  # Login
            if st.button('Login'):
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
                    st.success(f'Logged in as {role}: {username}')
                    
                    # Role-based redirect
                    if role == 'student':
                        st.switch_page('pages/student_dashboard.py')
                    elif role == 'faculty':
                        st.switch_page('main_dashboard.py')

if __name__ == '__main__':
    show_auth_page()
