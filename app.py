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

    fig.add_trace(
        go.Table(
            header=dict(values=["Date", "Task", "Start Time", "End Time"],
                        fill_color="lightgrey",
                        align="left"),
            cells=dict(values=[[], [], [], []],
                       fill_color="lavender",
                       align="left")
        )
    )

    # Populate the calendar with tasks
    for task in st.session_state['tasks']:
        start_date = task['start_date']
        end_date = task['end_date']
        summary = task['summary']

        fig.add_trace(
            go.Table(
                cells=dict(values=[[start_date.strftime('%Y-%m-%d')], [summary], [start_date.strftime('%H:%M')], [end_date.strftime('%H:%M')]],
                           fill_color="lavender",
                           align="left")
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

    # Display how to use the app instructions on the sign-up page
    display_how_to_use_instructions()

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

    # Display how to use the app instructions on the login page
    display_how_to_use_instructions()

# Function to display how to use the app instructions
def display_how_to_use_instructions():
    st.write("""
    ### How to Use the Daily Habits Tracker App

    The Daily Habits Tracker is designed to help you organize your tasks, set reminders, and visualize your productivity. Here’s a step-by-step guide to getting started with the app:

    #### 1. Sign Up and Log In:

    - **Sign Up:**  
      - Navigate to the **Sign Up** section on the sidebar.
      - Enter a unique username and a secure password, then confirm your password.
      - Click **Sign Up** to create your account. Once successful, you'll see a confirmation message.

    - **Log In:**  
      - Go to the **Login** section on the sidebar.
      - Enter your username and password.
      - Click **Login** to access your dashboard.

    #### 2. Add a New Task or Habit:

    - **Open the Add Task Form:**  
      - Once logged in, navigate to the **Add Task/Habit** section in the sidebar.

    - **Enter Task Details:**  
      - **Task/Habit Name:** Enter the name of the task or habit you want to track.
      - **Start Date & Time:** Choose the start date and time from the calendar and time selector.
      - **End Date & Time:** Select the end date and time.
      - **Phone Number:** (Optional) Enter your phone number to receive SMS notifications.

    - **Add the Task:**  
      - Click **Add Task/Habit** to save your task. A confirmation message will appear, and the task will be added to your schedule.

    #### 3. View Your Schedule:

    - **Calendar Overview:**  
      - At the bottom of the page, you’ll find an interactive calendar.
      - Each date shows the number of tasks scheduled for that day.

    - **Task Details:**  
      - Click on any date in the calendar to view the list of tasks scheduled for that day.
      - You can see details such as the task name, start time, and end time.

    #### 4. Receive Notifications:

    - **SMS Notifications:**  
      - Ensure you’ve entered your phone number when adding a task to receive SMS reminders.
      - The app will send you a notification 24 hours before the task starts.

    #### 5. Analyze Your Productivity:

    - **Visual Insights:**  
      - Use the calendar heatmap to identify patterns in your task completion.
      - Track which days are most productive and adjust your schedule accordingly.

    **Tips for Getting the Most Out of the App:**

    - **Stay Consistent:** Regularly update your tasks and habits to keep your schedule organized.
    - **Review Daily:** Spend a few minutes each day reviewing your calendar and preparing for upcoming tasks.
    - **Set Realistic Goals:** Break down larger tasks into smaller, manageable actions to avoid feeling overwhelmed.

    By following these steps, you’ll maximize your productivity and stay on top of your daily tasks with ease. Happy tracking!
    """)

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

        # Display the interactive calendar at the bottom
        task_dates = [task['start_date'].date() for task in st.session_state['tasks']]
        task_count = {date: task_dates.count(date) for date in set(task_dates)}

        st.subheader("Task Calendar")
        task_dates_data = {str(date): count for date, count in task_count.items()}

        calplot.calplot(
            task_dates_data,
            years=datetime.now().year,
            cmap='coolwarm',
            figsize=(10, 2),
            colorbar=True
        )

if __name__ == "__main__":
    main()
