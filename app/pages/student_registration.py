import streamlit as st
import io
import base64
from PIL import Image
from firebase.firebase_admin_init import get_firestore_client

def compress_and_encode_image(image_file, quality=60, max_size=(300, 300)):
    image = Image.open(image_file)
    image = image.convert('RGB')
    image.thumbnail(max_size)
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG', quality=quality)
    img_bytes = buffer.getvalue()
    img_b64 = base64.b64encode(img_bytes).decode('utf-8')
    return img_b64

def show_student_registration():
    st.title('Student Registration')
    db = get_firestore_client()
    with st.form('register_student'):
        register_number = st.text_input('Register Number (e.g., 22ISR026)', max_chars=20, key='reg_register_number')
        student_name = st.text_input('Student Name', max_chars=50, key='reg_student_name')
        student_class = st.text_input('Class (e.g., 10A, 12B, etc.)', max_chars=10, key='reg_student_class')
        uploaded_images = st.file_uploader('Upload 15 images of the student', type=['jpg', 'jpeg', 'png'], accept_multiple_files=True, key='reg_uploaded_images')
        submit = st.form_submit_button('Register Student')
        if submit:
            if not register_number or not student_name or not student_class:
                st.error('Please enter register number, student name, and class.')
            elif not uploaded_images or len(uploaded_images) < 15:
                st.error('Please upload exactly 15 images of the student.')
            elif len(uploaded_images) > 15:
                st.error('Please upload exactly 15 images of the student.')
            elif len(uploaded_images) < 15:
                st.error('Please upload exactly 15 images of the student.')
            else:
                # Check for duplicate register number
                if db.collection('students').document(register_number).get().exists:
                    st.error('A student with this register number already exists.')
                else:
                    try:
                        images_b64 = [compress_and_encode_image(img) for img in uploaded_images]
                        doc_ref = db.collection('students').document(register_number)
                        doc_ref.set({
                            'register_number': register_number,
                            'name': student_name,
                            'class': student_class,
                            'images': images_b64
                        })
                        st.success(f'Student {student_name} ({register_number}) registered successfully!')
                    except Exception as e:
                        st.error(f'Error registering student: {e}')

if __name__ == '__main__':
    show_student_registration()
