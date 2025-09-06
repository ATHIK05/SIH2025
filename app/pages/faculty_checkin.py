import streamlit as st
from firebase.firebase_admin_init import get_firestore_client
from datetime import datetime
import pandas as pd

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

def show_faculty_checkin():
    st.subheader('⏰ Faculty Period Check-in')
    db = get_firestore_client()
    if 'user' not in st.session_state or st.session_state.get('role') != 'faculty':
        st.error('Please login as faculty.')
        return
    
    faculty_username = st.session_state['user']
    
    # Get faculty details from database
    faculty_doc = db.collection('users').document(faculty_username).get()
    if not faculty_doc.exists:
        st.error('Faculty record not found!')
        return
    
    faculty_data = faculty_doc.to_dict()
    faculty_name = faculty_data.get('faculty_name', faculty_username)
    faculty_subjects = [s.strip() for s in faculty_data.get('subjects', '').split(',')]
    
    st.info(f"**Logged in as:** {faculty_name} ({faculty_username})")
    st.info(f"**Your Subjects:** {', '.join(faculty_subjects) if faculty_subjects else 'Not specified'}")
    
    class_name = st.text_input('Class (e.g., 10A, 12B, etc.)', key='checkin_class_name')
    date = st.date_input('Date', value=datetime.today(), key='checkin_date')
    
    # Time period validation
    from datetime import time
    current_time = datetime.now().time()
    
    # Find current period
    current_period = None
    for i, period in enumerate(PERIODS):
        # Parse time from period label
        time_str = period['label'].split(' - ')[0]  # Get start time
        period_start = datetime.strptime(time_str, '%I:%M %p').time()
        time_str = period['label'].split(' - ')[1]  # Get end time
        period_end = datetime.strptime(time_str, '%I:%M %p').time()
        
        if period_start <= current_time <= period_end:
            current_period = i
            break
    
    if current_period is not None:
        st.success(f"Current period: {PERIODS[current_period]['label']}")
        
        # Check scheduled faculty for this period
        if class_name:
            schedule_ref = db.collection('schedules').document(class_name)
            schedule_doc = schedule_ref.get()
            
            if schedule_doc.exists:
                week_timetable = schedule_doc.to_dict().get('week_timetable', {})
                today_str = datetime.today().strftime('%A')[:3].upper()  # Get day abbreviation
                today_periods = week_timetable.get(today_str, [])
                
                if current_period < len(today_periods):
                    scheduled_period = today_periods[current_period]
                    scheduled_subject = scheduled_period.get('subject', '')
                    scheduled_faculty = scheduled_period.get('faculty', '')
                    
                    if scheduled_subject and scheduled_faculty:
                        st.info(f"**Scheduled:** {scheduled_subject} by {scheduled_faculty}")
                        
                        # Check if this is a substitution
                        if scheduled_faculty != faculty_name:
                            st.warning(f"⚠️ **SUBSTITUTION DETECTED!** You are substituting for {scheduled_faculty}")
                            substitution_reason = st.text_input('Reason for substitution (optional)', key='substitution_reason')
                        else:
                            st.success("✅ You are the scheduled faculty for this period")
                            substitution_reason = ""
                    else:
                        st.info("📝 No scheduled class for this period")
                        substitution_reason = ""
                else:
                    st.info("📝 No schedule found for this period")
                    substitution_reason = ""
            else:
                st.info("📝 No timetable set for this class")
                substitution_reason = ""
        
        if st.button('Check In for Current Period', key='checkin_current_btn'):
            if not class_name:
                st.error("Please enter a class name first!")
            else:
                # Check if already checked in
                existing_checkin = db.collection('checkins').document(f'{date}_{class_name}_{current_period}').get()
                if existing_checkin.exists:
                    existing_data = existing_checkin.to_dict()
                    st.error(f"❌ Already checked in by {existing_data.get('faculty_name', 'Unknown')} at {existing_data.get('timestamp', 'Unknown time')}")
                else:
                    checkin_data = {
                        'faculty_username': faculty_username,
                        'faculty_name': faculty_name,
                        'class': class_name, 
                        'date': str(date), 
                        'period_idx': current_period, 
                        'period_label': PERIODS[current_period]['label'], 
                        'timestamp': datetime.now().isoformat(),
                        'is_substitution': scheduled_faculty != faculty_name if 'scheduled_faculty' in locals() else False,
                        'substitution_reason': substitution_reason if 'substitution_reason' in locals() else "",
                        'scheduled_faculty': scheduled_faculty if 'scheduled_faculty' in locals() else "",
                        'scheduled_subject': scheduled_subject if 'scheduled_subject' in locals() else ""
                    }
                    
                    checkin_ref = db.collection('checkins').document(f'{date}_{class_name}_{current_period}')
                    checkin_ref.set(checkin_data)
                    
                    if checkin_data['is_substitution']:
                        st.success(f'✅ **Substitution Check-in successful!** You are substituting for {scheduled_faculty} in {class_name}')
                    else:
                        st.success(f'✅ **Check-in successful!** You are teaching {PERIODS[current_period]["label"]} in {class_name}')
    else:
        st.warning("No active period at this time. Check-in is only allowed during class periods.")
        st.info("Current time periods:")
        for i, period in enumerate(PERIODS):
            time_str = period['label'].split(' - ')[0]
            period_start = datetime.strptime(time_str, '%I:%M %p').time()
            time_str = period['label'].split(' - ')[1]
            period_end = datetime.strptime(time_str, '%I:%M %p').time()
            
            if period_start <= current_time <= period_end:
                st.write(f"🟢 **{period['label']}** (Current)")
            else:
                st.write(f"- {period['label']}")
        
        # Allow manual period selection for admin purposes
        st.subheader("Manual Check-in (Admin Only)")
        period_idx = st.selectbox('Select Period', list(range(len(PERIODS))), format_func=lambda i: PERIODS[i]['label'], key='checkin_period_select')
        
        if class_name and period_idx is not None:
            # Check scheduled faculty for selected period
            schedule_ref = db.collection('schedules').document(class_name)
            schedule_doc = schedule_ref.get()
            
            if schedule_doc.exists:
                week_timetable = schedule_doc.to_dict().get('week_timetable', {})
                today_str = datetime.today().strftime('%A')[:3].upper()
                today_periods = week_timetable.get(today_str, [])
                
                if period_idx < len(today_periods):
                    scheduled_period = today_periods[period_idx]
                    scheduled_subject = scheduled_period.get('subject', '')
                    scheduled_faculty = scheduled_period.get('faculty', '')
                    
                    if scheduled_subject and scheduled_faculty:
                        st.info(f"**Scheduled:** {scheduled_subject} by {scheduled_faculty}")
                        if scheduled_faculty != faculty_name:
                            st.warning(f"⚠️ **SUBSTITUTION:** You are substituting for {scheduled_faculty}")
                            manual_substitution_reason = st.text_input('Reason for substitution (optional)', key='manual_substitution_reason')
                        else:
                            st.success("✅ You are the scheduled faculty")
                            manual_substitution_reason = ""
                    else:
                        st.info("📝 No scheduled class for this period")
                        manual_substitution_reason = ""
                else:
                    st.info("📝 No schedule found for this period")
                    manual_substitution_reason = ""
            else:
                st.info("📝 No timetable set for this class")
                manual_substitution_reason = ""
        
        if st.button('Manual Check In', key='checkin_manual_btn'):
            if not class_name:
                st.error("Please enter a class name first!")
            else:
                # Check if already checked in
                existing_checkin = db.collection('checkins').document(f'{date}_{class_name}_{period_idx}').get()
                if existing_checkin.exists:
                    existing_data = existing_checkin.to_dict()
                    st.error(f"❌ Already checked in by {existing_data.get('faculty_name', 'Unknown')} at {existing_data.get('timestamp', 'Unknown time')}")
                else:
                    manual_checkin_data = {
                        'faculty_username': faculty_username,
                        'faculty_name': faculty_name,
                        'class': class_name, 
                        'date': str(date), 
                        'period_idx': period_idx, 
                        'period_label': PERIODS[period_idx]['label'], 
                        'timestamp': datetime.now().isoformat(),
                        'manual': True,
                        'is_substitution': scheduled_faculty != faculty_name if 'scheduled_faculty' in locals() else False,
                        'substitution_reason': manual_substitution_reason if 'manual_substitution_reason' in locals() else "",
                        'scheduled_faculty': scheduled_faculty if 'scheduled_faculty' in locals() else "",
                        'scheduled_subject': scheduled_subject if 'scheduled_subject' in locals() else ""
                    }
                    
                    checkin_ref = db.collection('checkins').document(f'{date}_{class_name}_{period_idx}')
                    checkin_ref.set(manual_checkin_data)
                    
                    if manual_checkin_data['is_substitution']:
                        st.success(f'✅ **Manual Substitution Check-in successful!** You are substituting for {scheduled_faculty} in {class_name}')
                    else:
                        st.success(f'✅ **Manual Check-in successful!** You are teaching {PERIODS[period_idx]["label"]} in {class_name}')
    
    # Show check-in history for this faculty
    st.write('---')
    st.subheader('📋 Your Check-in History')
    
    # Get check-in history for this faculty
    checkin_history = db.collection('checkins').where('faculty_username', '==', faculty_username).order_by('timestamp', direction='DESCENDING').limit(10).stream()
    
    history_data = []
    for checkin in checkin_history:
        data = checkin.to_dict()
        history_data.append({
            'Date': data.get('date', ''),
            'Class': data.get('class', ''),
            'Period': data.get('period_label', ''),
            'Type': 'Substitution' if data.get('is_substitution', False) else 'Regular',
            'Scheduled Faculty': data.get('scheduled_faculty', ''),
            'Reason': data.get('substitution_reason', '') if data.get('is_substitution', False) else '-',
            'Time': data.get('timestamp', '')[:16] if data.get('timestamp') else ''
        })
    
    if history_data:
        st.table(pd.DataFrame(history_data))
    else:
        st.info('No check-in history found.')

if __name__ == '__main__':
    show_faculty_checkin()
