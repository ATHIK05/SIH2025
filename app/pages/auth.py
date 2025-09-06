import streamlit as st
from firebase.firebase_admin_init import get_firestore_client

def show_auth_page():
    st.title('🔐 Login / Signup')
    db = get_firestore_client()
    mode = st.radio('Choose mode', ['Login', 'Signup'], horizontal=True)
    role = st.selectbox('Role', ['student', 'faculty'])
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    if mode == 'Signup':
        extra = {}
        if role == 'student':
            extra['register_number'] = st.text_input('Register Number')
            extra['name'] = st.text_input('Full Name')
            extra['class'] = st.text_input('Class (e.g., 10A, 12B)')
        else:
            extra['faculty_name'] = st.text_input('Full Name')
            extra['subjects'] = st.text_input('Subjects handled (comma separated)')
        if st.button('Signup'):
            user_ref = db.collection('users').document(username)
            if user_ref.get().exists:
                st.error('Username already exists!')
            else:
                user_ref.set({'username': username, 'password': password, 'role': role, **extra})
                st.success('Signup successful! Please login.')
    else:
        if st.button('Login'):
            user_ref = db.collection('users').document(username)
            doc = user_ref.get()
            if not doc.exists:
                st.error('User not found!')
            elif doc.to_dict().get('password') != password:
                st.error('Incorrect password!')
            elif doc.to_dict().get('role') != role:
                st.error('Role mismatch!')
            else:
                st.session_state['user'] = username
                st.session_state['role'] = role
                st.success(f'Logged in as {role}: {username}')
                st.switch_page('main_dashboard.py')

if __name__ == '__main__':
    show_auth_page()
