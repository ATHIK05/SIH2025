import streamlit as st
from firebase.firebase_admin_init import get_firestore_client

def show_suggestion_engine():
    st.title('Personalized Suggestions for Free Periods')
    class_name = st.text_input('Class (e.g., 10A, 12B, etc.)', max_chars=10, key='suggestion_class_name')
    register_number = st.text_input('Register Number (e.g., 22ISR026)', max_chars=20, key='suggestion_register_number')
    db = get_firestore_client()
    if class_name and register_number:
        student_ref = db.collection('students').document(register_number)
        doc = student_ref.get()
        if doc.exists and doc.to_dict().get('class') == class_name:
            data = doc.to_dict()
            student_name = data.get('name', '')
            interests = data.get('interests', [])
            goals = data.get('goals', '')
            st.write(f"**Student:** {student_name} ({register_number})")
            if not interests:
                st.info('No interests found. Please enter your interests (comma separated):')
                new_interests = st.text_input('Interests', key='suggestion_new_interests')
                if st.button('Save Interests', key='suggestion_save_interests') and new_interests:
                    student_ref.update({'interests': [i.strip() for i in new_interests.split(',')]})
                    st.success('Interests saved! Please reload to see suggestions.')
            else:
                st.write(f"**Your Interests:** {', '.join(interests)}")
                st.write(f"**Your Goal:** {goals if goals else 'Not set'}")
                if st.button('Update Interests/Goal', key='suggestion_update_interests_goal'):
                    new_interests = st.text_input('Update Interests', value=','.join(interests), key='suggestion_update_interests')
                    new_goals = st.text_input('Update Goal', value=goals, key='suggestion_update_goals')
                    if st.button('Save Updates', key='suggestion_save_updates'):
                        student_ref.update({'interests': [i.strip() for i in new_interests.split(',')], 'goals': new_goals})
                        st.success('Updated! Please reload to see new suggestions.')
                st.write('---')
                st.write('### Suggestions for Your Free Period:')
                for interest in interests:
                    if 'coding' in interest.lower():
                        st.write('- Practice coding on LeetCode or HackerRank')
                    if 'math' in interest.lower():
                        st.write('- Solve math puzzles or Olympiad problems')
                    if 'reading' in interest.lower():
                        st.write('- Read a book or article related to your goal')
                    if 'science' in interest.lower():
                        st.write('- Watch a science documentary or experiment video')
                    if 'art' in interest.lower():
                        st.write('- Work on a drawing or digital art project')
                st.write('- Review your class notes or prepare for upcoming exams')
                st.write('- Explore online courses related to your interests (Coursera, edX, etc.)')
        else:
            st.warning('Student not found. Please check your register number and class.')
    else:
        st.info('Enter your class and register number to get personalized suggestions.')

if __name__ == '__main__':
    show_suggestion_engine()
