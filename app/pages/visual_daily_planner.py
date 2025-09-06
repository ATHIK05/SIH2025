import streamlit as st
st.set_page_config(layout="wide")
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
    st.title('📅 Visual Daily Planner')
    db = get_firestore_client()
    class_name = st.text_input('Class (e.g., 10A, 12B, etc.)', max_chars=10, key='planner_class_name')
    register_number = st.text_input('Register Number (e.g., 22ISR026)', max_chars=20, key='planner_register_number')
    date = st.date_input('Date', value=datetime.today(), key='planner_date')
    is_admin = st.checkbox('I am a teacher/admin', key='planner_is_admin')
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
        timetable_df = pd.DataFrame({day: [f"{cell['subject']} ({cell['faculty']})" if cell['subject'] else '' for cell in week_timetable[day]] for day in DAYS}, index=[p['label'] for p in PERIODS])
        timetable_df.index.name = 'Period/Day'
        if is_admin:
            st.subheader('🗓️ Edit Class Week-wise Timetable')
            timetable_input = {}
            for i, period in enumerate(PERIODS):
                cols = st.columns([1] + [2]*len(DAYS))
                cols[0].write(f"**{period['label']}**")
                for j, day in enumerate(DAYS):
                    key_subj = f'edit_{day}_{i}_subject'
                    key_fac = f'edit_{day}_{i}_faculty'
                    subj = cols[j+1].text_input('Subject', value=week_timetable[day][i].get('subject', ''), key=key_subj)
                    fac = cols[j+1].text_input('Faculty', value=week_timetable[day][i].get('faculty', ''), key=key_fac)
                    timetable_input[(day, i)] = {'subject': subj, 'faculty': fac}
            if st.button('Save Week Timetable', key='planner_save_week_timetable'):
                new_week_timetable = {d: [timetable_input[(d, i)] for i in range(len(PERIODS))] for d in DAYS}
                schedule_ref.set({'week_timetable': new_week_timetable})
                st.success('Class week-wise timetable saved!')
                week_timetable = new_week_timetable
        else:
            st.subheader('📅 Class Week Timetable')
            # For display, show subject (faculty) in each cell
            header_cols = st.columns([1] + [1]*len(DAYS))
            header_cols[0].write('**Period/Day**')
            for j, day in enumerate(DAYS):
                header_cols[j+1].write(f'**{day}**')
            for i, period in enumerate(PERIODS):
                row_cols = st.columns([1] + [1]*len(DAYS))
                row_cols[0].write(f"**{period['label']}**")
                for j, day in enumerate(DAYS):
                    cell = week_timetable[day][i]
                    val = f"{cell.get('subject', '')} ({cell.get('faculty', '')})" if cell.get('subject') else '-'
                    row_cols[j+1].write(val)
        # Show today's schedule, factoring in check-ins
        today_str = get_day_str(date)
        st.subheader(f"🗓️ Schedule for {today_str}")
        today_periods = week_timetable.get(today_str, [{'subject': '', 'faculty': ''} for _ in PERIODS])
        today_schedule = []
        for i, cell in enumerate(today_periods):
            start, end = PERIODS[i]['label'].split(' - ')
            # Check for faculty check-in
            checkin_ref = db.collection('checkins').document(f'{date}_{class_name}_{i}')
            checkin_doc = checkin_ref.get()
            is_free = not checkin_doc.exists or not cell['subject']
            today_schedule.append({'period': cell['subject'] if cell['subject'] else 'Free', 'faculty': cell['faculty'] if cell['faculty'] else '-', 'start': start, 'end': end, 'free': is_free})
        if today_schedule:
            st.table(pd.DataFrame(today_schedule))
        else:
            st.info('No schedule set for today!')
        # Gantt chart for today
        if today_schedule:
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
            fig = ff.create_gantt(df, index_col='Type', show_colorbar=True, group_tasks=True, colors=colors, title='Your Day at a Glance', bar_width=0.3, showgrid_x=True, showgrid_y=True)
            st.plotly_chart(fig, use_container_width=True)
        # Daily routine generator
        st.write('---')
        st.subheader('🗓️ Your Personalized Daily Routine')
        if student_data and today_schedule:
            interests = student_data.get('interests', [])
            goals = student_data.get('goals', '')
            progress = student_data.get('progress', {})
            completed_tasks = student_data.get('completed_tasks', [])
            routine = []
            for s in today_schedule:
                if s['free']:
                    suggestions = []
                    if student_data:
                        student_name = student_data.get('name', '')
                        marks_ref = db.collection('students').document(register_number).collection('marks').stream()
                        marks_data = [m.to_dict() for m in marks_ref]
                        user_message = build_student_message(student_name, marks_data, interests, free_period_time=f"{s['start']} - {s['end']}")
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
                        if tasks:
                            suggestions.extend(tasks)
                        else:
                            suggestions.append(response)
                    else:
                        suggestions.append('No student data found.')
                    routine.append({
                        'start': s['start'],
                        'end': s['end'],
                        'suggestions': suggestions
                    })
            if routine:
                for r in routine:
                    st.markdown(f"**Free Period {r['start']} - {r['end']}**")
                    for idx, suggestion in enumerate(r['suggestions']):
                        # Show checkboxes for extracted tasks if available
                        if isinstance(suggestion, list):
                            for t_idx, task in enumerate(suggestion):
                                done = task in completed_tasks
                                if done:
                                    st.checkbox(task, value=True, disabled=True, key=f'daily_done_{r["start"]}_{idx}_{t_idx}')
                                else:
                                    if st.checkbox(task, value=False, key=f'daily_{r["start"]}_{idx}_{t_idx}'):
                                        completed_tasks.append(task)
                                        for interest in interests:
                                            if interest.lower() in task.lower():
                                                progress[interest] = min(progress.get(interest, 0) + 20, 100)
                                        student_ref.update({'completed_tasks': completed_tasks, 'progress': progress})
                                        st.success(f'Marked as done: {task}')
                        else:
                            done = suggestion in completed_tasks
                            if done:
                                st.checkbox(suggestion, value=True, disabled=True, key=f'daily_done_{r["start"]}_{idx}')
                            else:
                                if st.checkbox(suggestion, value=False, key=f'daily_{r["start"]}_{idx}'):
                                    completed_tasks.append(suggestion)
                                    for interest in interests:
                                        if interest.lower() in suggestion.lower():
                                            progress[interest] = min(progress.get(interest, 0) + 20, 100)
                                    student_ref.update({'completed_tasks': completed_tasks, 'progress': progress})
                                    st.success(f'Marked as done: {suggestion}')
            else:
                st.info('No free periods today!')
            st.write('---')
            st.subheader('📈 Progress Dashboard')
            for interest in interests:
                pct = progress.get(interest, 0)
                st.write(f"**{interest.title()}**")
                st.progress(pct)
            st.write('---')
            st.subheader('✅ Completed Tasks History')
            if completed_tasks:
                for task in completed_tasks:
                    st.write(f'✅ {task}')
            else:
                st.info('No tasks completed yet. Start with your first suggestion!')
        else:
            st.info('Enter your register number to see your personalized routine and progress.')
        # Real-time attendance display
        st.write('---')
        st.subheader('🟢 Real-Time Attendance')
        attendance_ref = db.collection('attendance').document(f'{class_name}_{date}')
        attendance_doc = attendance_ref.get()
        if attendance_doc.exists:
            att_data = attendance_doc.to_dict()
            present = att_data.get('present', [])
            absent = att_data.get('absent', [])
            st.success(f"Present: {len(present)} | Absent: {len(absent)}")
            st.write('**Present Students:**')
            st.write(present)
            st.write('**Absent Students:**')
            st.write(absent)
        else:
            st.info('No attendance data found for this class and date.')
    else:
        st.info('Enter your class name to view the daily planner.')

if __name__ == '__main__':
    show_visual_daily_planner()
