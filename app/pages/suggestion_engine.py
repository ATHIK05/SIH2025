import streamlit as st
st.set_page_config(layout="wide")
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
            progress = data.get('progress', {})
            completed_tasks = data.get('completed_tasks', [])
            st.write(f"**Student:** {student_name} ({register_number})")
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
                st.warning('Academic Focus Needed!')
                for alert in academic_alerts:
                    st.write(f'⚠️ {alert}')
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
                st.write('### Progress Overview')
                for interest in interests:
                    pct = progress.get(interest, 0)
                    st.write(f"**{interest.title()}**")
                    st.progress(pct)
                st.write('---')
                st.write('### Suggestions for Your Free Period:')
                user_message = build_student_message(student_name, marks_data, interests)
                with st.spinner("Thinking..."):
                    response = call_mistral_api(system_prompt, user_message, max_tokens=768)
                response = boldify(response)
                st.markdown(
                    f'''
                    <div style="background: linear-gradient(135deg, #1e5631 0%, #4caf50 100%); padding: 24px 24px 16px 24px; border-radius: 16px; color: #fff; box-shadow: 0 4px 24px rgba(30,86,49,0.15); font-size: 1.1rem; margin-bottom: 1.5rem; max-height: 500px; overflow-y: auto;">
                        {response}
                    </div>
                    ''',
                    unsafe_allow_html=True
                )
                # Extract tasks from response (bulleted or numbered points)
                tasks = re.findall(r'\n\s*[-*•]\s+(.+)', response)
                if not tasks:
                    tasks = re.findall(r'\n\s*\d+\.\s+(.+)', response)
                st.write('---')
                st.write('### Completed Tasks History')
                if tasks:
                    for idx, task in enumerate(tasks):
                        done = task in completed_tasks
                        if done:
                            st.checkbox(task, value=True, disabled=True, key=f'sugg_done_{idx}')
                        else:
                            if st.checkbox(task, value=False, key=f'sugg_{idx}'):
                                completed_tasks.append(task)
                                for interest in interests:
                                    if interest.lower() in task.lower():
                                        progress[interest] = min(progress.get(interest, 0) + 20, 100)
                                student_ref.update({'completed_tasks': completed_tasks, 'progress': progress})
                                st.success(f'Marked as done: {task}')
                elif completed_tasks:
                    for task in completed_tasks:
                        st.write(f'✅ {task}')
                else:
                    st.info('No tasks completed yet. Start with your first suggestion!')
        else:
            st.warning('Student not found. Please check your register number and class.')
    else:
        st.info('Enter your class and register number to get personalized suggestions.')

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

if __name__ == '__main__':
    show_suggestion_engine()
