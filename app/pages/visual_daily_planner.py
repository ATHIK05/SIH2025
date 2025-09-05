import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
from firebase.firebase_admin_init import get_firestore_client
import plotly.figure_factory as ff

def show_visual_daily_planner():
    st.title('📅 Visual Daily Planner')
    class_name = st.text_input('Class (e.g., 10A, 12B, etc.)', max_chars=10, key='planner_class_name')
    register_number = st.text_input('Register Number (e.g., 22ISR026)', max_chars=20, key='planner_register_number')
    date = st.date_input('Date', value=datetime.today(), key='planner_date')
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
            # Fetch or enter schedule
            schedule_ref = db.collection('schedules').document(f'{class_name}')
            schedule_doc = schedule_ref.get()
            if not schedule_doc.exists:
                st.info('No schedule found for this class. Please enter your daily schedule:')
                schedule_data = []
                for i in range(1, 9):
                    col1, col2, col3 = st.columns([2,2,2])
                    with col1:
                        period = st.text_input(f'Period {i} Name', key=f'planner_period_{i}')
                    with col2:
                        start = st.time_input(f'Start Time {i}', value=time(8+i,0), key=f'planner_start_{i}')
                    with col3:
                        end = st.time_input(f'End Time {i}', value=time(9+i,0), key=f'planner_end_{i}')
                    if period:
                        schedule_data.append({'period': period, 'start': str(start), 'end': str(end)})
                if st.button('Save Schedule', key='planner_save_schedule'):
                    schedule_ref.set({'schedule': schedule_data})
                    st.success('Schedule saved! Please reload to see your planner.')
            else:
                schedule = schedule_doc.to_dict().get('schedule', [])
                planner = []
                for s in schedule:
                    planner.append({
                        'Task': s['period'],
                        'Start': datetime.combine(date, datetime.strptime(s['start'], '%H:%M:%S').time()),
                        'Finish': datetime.combine(date, datetime.strptime(s['end'], '%H:%M:%S').time()),
                        'Type': 'Class' if s['period'].lower() != 'free' else 'Free'
                    })
                df = pd.DataFrame(planner)
                colors = {'Class': 'rgb(66, 135, 245)', 'Free': 'rgb(0, 204, 150)'}
                fig = ff.create_gantt(df, index_col='Type', show_colorbar=True, group_tasks=True, colors=colors, title='Your Day at a Glance', bar_width=0.3, showgrid_x=True, showgrid_y=True)
                st.plotly_chart(fig, use_container_width=True)
                st.write('---')
                st.write('### Free Period Suggestions')
                for s in schedule:
                    if s['period'].lower() == 'free':
                        st.markdown(f"**{s['start']} - {s['end']}**: ")
                        if interests:
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
                            st.info('No interests set. Add your interests in the suggestion engine!')
                st.write('---')
                st.write('### Update Your Goals/Interests')
                new_interests = st.text_input('Update Interests', value=','.join(interests), key='planner_update_interests')
                new_goals = st.text_input('Update Goal', value=goals, key='planner_update_goals')
                if st.button('Save Updates', key='planner_save_updates'):
                    student_ref.update({'interests': [i.strip() for i in new_interests.split(',')], 'goals': new_goals})
                    st.success('Updated! Please reload to see new suggestions.')
        else:
            st.warning('Student not found. Please check your register number and class.')
    else:
        st.info('Enter your class and register number to view your daily planner.')

if __name__ == '__main__':
    show_visual_daily_planner()
