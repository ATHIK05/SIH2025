import streamlit as st
from firebase.firebase_admin_init import get_firestore_client
import os
import subprocess
import pathlib
from app.pages.student_registration import show_student_registration
from app.pages.live_attendance import show_live_attendance
from app.pages.suggestion_engine import show_suggestion_engine
from app.pages.visual_daily_planner import show_visual_daily_planner
from app.pages.admin_dashboard import show_admin_dashboard

st.set_page_config(page_title='Smart Attendance & Productivity Suite', layout='wide', initial_sidebar_state='collapsed')
st.title('🎓 Smart Attendance & Productivity Suite')

st.markdown('''
Welcome to the all-in-one platform for automated attendance, student productivity, and personalized planning!
''')

class_name = st.text_input('Enter Class Name (e.g., 10A, 12B, etc.)', max_chars=10)
db = get_firestore_client()

if class_name:
    students_ref = db.collection('students').where('class', '==', class_name)
    students = list(students_ref.stream())
    student_list = [(doc.to_dict().get('register_number', ''), doc.to_dict().get('name', '')) for doc in students]
    st.subheader(f'👥 Students in {class_name}')
    st.write([f"{regno} - {name}" for regno, name in student_list] if student_list else 'No students added yet.')
    expected_count = st.number_input('How many students should be in this class?', min_value=1, step=1)
    if len(student_list) < expected_count:
        st.warning(f'Only {len(student_list)} of {expected_count} students added.')
        with st.expander('➕ Add New Student'):
            with st.form('add_student_form'):
                new_regno = st.text_input('Register Number (e.g., 22ISR026)', key='new_regno')
                new_name = st.text_input('Student Name', key='new_name')
                uploaded_images = st.file_uploader('Upload 15 images', type=['jpg', 'jpeg', 'png'], accept_multiple_files=True, key='new_images')
                submit = st.form_submit_button('Add Student')
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
        st.success('✅ All students have been added!')
        if st.button('🚀 Start Model Training'):
            with st.spinner('Training model, please wait...'):
                result = subprocess.run(['python', 'backend/model_training.py'], capture_output=True, text=True)
                if result.returncode == 0:
                    st.success('Model training completed successfully!')
                else:
                    st.error(f'Model training failed: {result.stderr}')
        st.markdown('---')
    st.subheader('🔗 Quick Navigation')
    tabs = st.tabs([
        
        'Student Registration',
        'Live Attendance',
        'Suggestion Engine',
        'Daily Planner',
        'Admin Dashboard'
    ])
    with tabs[0]:
        show_student_registration()
    with tabs[1]:
        show_live_attendance()
    with tabs[2]:
        show_suggestion_engine()
    with tabs[3]:
        show_visual_daily_planner()
    with tabs[4]:
        show_admin_dashboard()
else:
    st.info('Enter a class name to get started!')
