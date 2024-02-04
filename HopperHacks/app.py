from flask import Flask, render_template, request, jsonify
from flask_apscheduler import APScheduler
import mysql.connector
from datetime import datetime
from openai import OpenAI
client = OpenAI()

class Config:
    SCHEDULER_API_ENABLED = True

# Initialize the Flask application
app = Flask(__name__)
app.config.from_object(Config())

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Misha100!',
    'database': 'tasks_db'
}

calendar_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Misha100!',
    'database': 'todo_calendar_db'
}




# Route for displaying the chat interface
@app.route('/')
def home():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    
    # Execute a query
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    
    # Close connection
    cursor.close()
    connection.close()
    return render_template('chat.html', tasks=tasks)

def calendar_background():
    current_month = datetime.now().month
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("SELECT background_color FROM calendar_events WHERE MONTH(event_date) = %s", (current_month,))
    event = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    if event:
        return jsonify(event)
    else:
        return jsonify({"background_color": "#FFFFFF"})  # Default background



# Route to handle the backend communication
@app.route('/ask', methods=['POST'])
def ask():
    user_message = request.json['message']
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a mental health expert, helping everyone with their problems"},
                {"role": "user", "content": user_message}
            ]
        )
        message_content = response.choices[0].message.content
        return jsonify({'message': message_content})
    except Exception as e:
        print(e)
        return jsonify({'message': 'Sorry, something went wrong.'})
    
def calculate_and_reset_tasks():
    connection = mysql.connector.connect(**calendar_config)
    cursor = connection.cursor(dictionary=True)
    
    # Calculate completed and total tasks
    cursor.execute("SELECT COUNT(*) AS total_tasks, SUM(completed) AS tasks_completed FROM tasks")
    result = cursor.fetchone()
    total_tasks, tasks_completed = result['total_tasks'], result['tasks_completed']
    
    print(f"Total Tasks: {total_tasks}, Tasks Completed: {tasks_completed}")
    # Insert into todo_calendar_db.daily_completion
    cursor.execute("""
        INSERT INTO todo_calendar_db.daily_completion (date, tasks_completed, total_tasks)
        VALUES (%s, %s, %s)
    """, (datetime.now().date(), tasks_completed, total_tasks))
    print(f"Total Tasks: {total_tasks}, Tasks Completed: {tasks_completed}")
    
    # Reset completed status in tasks_db.tasks
    cursor.execute("UPDATE tasks SET completed = FALSE")
    
    connection.commit()
    cursor.close()
    connection.close()

# Schedule the task to run daily at 11:59 PM
scheduler.add_job(func=calculate_and_reset_tasks, trigger='cron', hour=23, minute=59, id='daily_task_reset')

calculate_and_reset_tasks()

if __name__ == '__main__':
    app.run(debug=True)
