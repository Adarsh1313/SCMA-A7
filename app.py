import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
from twilio.rest import Client
import bcrypt
import pandas as pd
import calplot
import matplotlib.pyplot as plt

# Twilio credentials (replace with your actual credentials)
TWILIO_ACCOUNT_SID = 'AC3938c1f5db3672ebe2863d8977f29bf3'
TWILIO_AUTH_TOKEN = '4e88b05ba12524ee3164f920eef9bc81'
TWILIO_PHONE_NUMBER = '+12085677321'

# Initialize session state for storing user data
if 'users' not in st.session_state:
    st.session_state['users'] = {}  # User data storage

if 'tasks' not in st.session_state:
    st.session_state['tasks'] = []

# Send SMS notifications using Twilio
def send_sms_notification(to_number, message):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=TWILIO_PHONE_NUMBER,
        to=to_number
    )

# Virtual calendar visualization
def create_virtual_calendar():
    fig = go.Figure()

    # Initial table setup with updated colors
    fig.add_trace(
        go.Table(
            header=dict(
                values=["Date", "Task", "Start Time", "End Time"],
                fill_color="#4CAF50",  # Dark green color for header
                align="center",
                font=dict(color="white", size=12)
            ),
            cells=dict(
                values=[[], [], [], []],
                fill_color="#f8f8f8",  # Light grey color for empty cells
                align="center",
                font=dict(color="black", size=11)
            )
        )
    )

    # Populate the calendar with tasks
    for task in st.session_state['tasks']:
        start_date = task['start_date']
        end_date = task['end_date']
        summary = task['summary']

        fig.add_trace(
            go.Table(
                cells=dict(
                    values=[
                        [start_date.strftime('%Y-%m-%d')],
                        [summary],
                        [start_date.strftime('%H:%M')],
                        [end_date.strftime('%H:%M')]
                    ],
                    fill_color="#e6f7ff",  # Light blue color for task cells
                    align="center",
                    font=dict(color="black", size=11)
                )
            )
        )

    fig.update_layout(
        title="Upcoming Tasks and Habits",
        autosize=False,
        width=800,
        height=600,
    )

    return fig

# Add a new task or habit
def add_task():
    st.sidebar.title("Add Task/Habit")
    task_name = st.sidebar.text_input("Task/Habit Name")
    start_date = st.sidebar.date_input("Start Date")
    start_time = st.sidebar.time_input("Start Time")
    end_date = st.sidebar.date_input("End Date")
    end_time = st.sidebar.time_input("End Time")
    phone_number = st.sidebar.text_input("Phone Number")

    if st.sidebar.button("Add Task/Habit"):
        start_datetime = datetime.combine(start_date, start_time)
        end_datetime = datetime.combine(end_date, end_time)

        # Store the task details
        st.session_state['tasks'].append({
            'summary': task_name,
            'start_date': start_datetime,
            'end_date': end_datetime,
            'phone_number': phone_number
        })

        st.sidebar.success("Task/Habit added!")

        # Send notifications if the task is within the next 24 hours
        if start_datetime <= datetime.now() + timedelta(days=1):
            message = f"Upcoming Task/Habit: {task_name} at {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}"
            if phone_number:
                send_sms_notification(phone_number, message)

# Sign up interface
def sign_up():
    st.sidebar.title("Sign Up")
    username = st.sidebar.text_input("New Username")
    password = st.sidebar.text_input("New Password", type="password")
    confirm_password = st.sidebar.text_input("Confirm Password", type="password")

    if st.sidebar.button("Sign Up"):
        if username in st.session_state['users']:
            st.sidebar.error("Username already exists")
        elif password != confirm_password:
            st.sidebar.error("Passwords do not match")
        else:
            # Hash the password and store the user
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            st.session_state['users'][username] = hashed_password
            st.sidebar.success("Account created! Please log in.")
            st.session_state['page'] = 'login'  # Switch to login page

# Login interface
def login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login"):
        user_password_hash = st.session_state['users'].get(username)
        if user_password_hash and bcrypt.checkpw(password.encode(), user_password_hash):
            st.session_state['authenticated'] = True
        else:
            st.sidebar.error("Invalid username or password")

# Create a function to generate the calendar data
def generate_calendar_data():
    # Create a DataFrame with all tasks
    if len(st.session_state['tasks']) == 0:
        return pd.DataFrame(columns=['date', 'task'])

    task_data = []
    for task in st.session_state['tasks']:
        task_data.append({'date': task['start_date'].date(), 'task': task['summary']})

    df_tasks = pd.DataFrame(task_data)

    # Count tasks per day
    df_calendar = df_tasks.groupby('date').count().reset_index()
    df_calendar.rename(columns={'task': 'count'}, inplace=True)
    
    return df_calendar

def plot_calendar(df_calendar):
    # Create a calendar heatmap using calplot
    if not df_calendar.empty:
        # Convert the data to a format suitable for calplot
        s = pd.Series(df_calendar['count'].values, index=pd.to_datetime(df_calendar['date']))

        # Plot the calendar
        calplot.calplot(s, cmap="YlGnBu", colorbar=True, figsize=(10, 4))
        st.pyplot(plt.gcf())  # Get the current figure for rendering
    else:
        st.write("No tasks scheduled yet.")

def main():
    st.title("Task and Habit Tracker")

    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
        st.session_state['page'] = 'login'  # Default page

    if st.session_state['page'] == 'login':
        login()
    elif st.session_state['page'] == 'signup':
        sign_up()

    if st.sidebar.button("Switch to Sign Up"):
        st.session_state['page'] = 'signup'
    elif st.sidebar.button("Switch to Login"):
        st.session_state['page'] = 'login'

    if st.session_state['authenticated']:
        # Add tasks and display the virtual calendar
        add_task()
        calendar_fig = create_virtual_calendar()
        st.plotly_chart(calendar_fig)

        # Add a calendar visualization
        st.header("Task Calendar")

        # Generate the data for the calendar plot
        df_calendar = generate_calendar_data()

        # Plot the calendar heatmap
        plot_calendar(df_calendar)

        # Allow interaction to show tasks for a specific day
        st.write("### Tasks for Selected Day")
        selected_date = st.date_input("Select a date to view tasks:")
        tasks_for_date = [task for task in st.session_state['tasks'] if task['start_date'].date() == selected_date]

        if tasks_for_date:
            for task in tasks_for_date:
                st.write(f"- **Task:** {task['summary']}, **Time:** {task['start_date'].strftime('%H:%M')} - {task['end_date'].strftime('%H:%M')}")
        else:
            st.write("No tasks scheduled for this day.")

if __name__ == "__main__":
    main()

