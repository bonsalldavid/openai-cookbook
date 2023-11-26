
from dotenv import load_dotenv
import json
from openai import OpenAI
import time
from werkzeug.utils import secure_filename
import os
from flask import Flask, send_from_directory, request, jsonify, flash, redirect, url_for, render_template
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from github import Github
import subprocess

g = Github(os.getenv('GITHUB'))




#Needs Debugging to turn Debugging on :-( ! 
#if __name__ == '__main__':
#    app.run(debug=False)


app = Flask(__name__)

# Secret key for sessions
app.secret_key = os.getenv('SECRET_KEY')

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# Now get the user details from the environment variables
users = {
    os.getenv('USER1_NAME'): {'password': os.getenv('USER1_PASSWORD')},
    os.getenv('USER2_NAME'): {'password': os.getenv('USER2_PASSWORD')}
}



@login_manager.user_loader
def load_user(user_id):
    user_info = users.get(user_id)
    if user_info:
        return User(id=user_id, username=user_id, password=user_info['password'])
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_info = users.get(username)
        
        if user_info and user_info['password'] == password:
            user = User(id=username, username=username, password=password)
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

load_dotenv()

client = OpenAI()

#Improve JSON inline display
#def show_json(obj):
#    display(json.loads(obj.model_dump_json()))

def show_json(obj):
    return json.dumps(obj, indent=4)


#Set the client
client = OpenAI()

#Create the assistant
assistant = client.beta.assistants.create(
    name="Math Tutor",
    instructions="You are a personal math tutor. Answer questions briefly, in a sentence or less.",
    model="gpt-4-1106-preview",
)

#Create a thread for the message
thread = client.beta.threads.create()


def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

MATH_ASSISTANT_ID = assistant.id  # or a hard-coded ID like "asst-..."

def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")

current_thread = None  # Global variable to store the current thread


def create_thread_and_run(user_input, assistant_name, assistant_instructions, use_code_interpreter, file_ids):
    global current_thread
    global MATH_ASSISTANT_ID

    # Update assistant if necessary
    if assistant_name or assistant_instructions or use_code_interpreter or file_ids:
        tools = [{"type": "code_interpreter"}] if use_code_interpreter else []
        assistant = client.beta.assistants.update(
            MATH_ASSISTANT_ID,
            name=assistant_name,
            instructions=assistant_instructions,
            tools=tools,
            file_ids=file_ids,
        )
        MATH_ASSISTANT_ID = assistant.id

    if current_thread is None:
        current_thread = client.beta.threads.create()
    run = submit_message(MATH_ASSISTANT_ID, current_thread, user_input)
    return current_thread, run


##### Upload file

def upload_file_to_openai():
    if 'file' not in request.files:
        return None  # or handle error

    file = request.files['file']
    if file.filename == '':
        return None  # or handle error

    uploaded_file = client.files.create(
        file=file.read(),
        purpose="assistants"
    )
    return uploaded_file.id



# Pretty printing helper
def pretty_print(messages):
    print("# Messages")
    for m in messages:
        print(f"{m.role}: {m.content[0].text.value}")
    print()


# Waiting in a loop
def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

@app.route('/')
@login_required
def index():
    return render_template('ai_interaction.html')



@app.route('/submit', methods=['POST'])
def submit():
    user_input = request.form['userInput']
    assistant_name = request.form.get('assistantName', '')
    assistant_instructions = request.form.get('assistantInstructions', '')
    use_code_interpreter = 'codeInterpreter' in request.form

    # Handling multiple file uploads
    files = request.files.getlist('fileUpload')
    file_ids = []
    for file in files:
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join('uploads', filename)
            file.save(file_path)

            # Upload the file to OpenAI
            uploaded_file = client.files.create(
                file=open(file_path, "rb"),
                purpose="assistants",
            )
            file_ids.append(uploaded_file.id)

    # Debugging print statement
    print("Code Interpreter Enabled:", use_code_interpreter)

    # Pass file_ids to create_thread_and_run
    thread, run = create_thread_and_run(user_input, assistant_name, assistant_instructions, use_code_interpreter, file_ids)
    run = wait_on_run(run, thread)
    messages = get_response(thread)

    # Format the messages for display
    response = "\n".join([f"{m.role}: {m.content[0].text.value}" for m in messages])

    if use_code_interpreter:
        run_steps = client.beta.threads.runs.steps.list(
            thread_id=thread.id, run_id=run.id, order="asc"
        )
        for step in run_steps.data:
            step_details = step.step_details
            if 'code_interpreter' in step_details:
                code_input = step_details['code_interpreter']['input']
                code_output = step_details['code_interpreter']['outputs'][0]['logs']
                response += f"\nCode Interpreter Input:\n{code_input}\nOutput:\n{code_output}"

    return jsonify(response)

### Github

@app.route('/request-change', methods=['POST'])
def request_change():
    data = request.json
    change_request = data.get('request')

    if not change_request:
        return jsonify({"error": "No request provided"}), 400

    # Process the change request
    generated_content = "Generated content based on request: " + change_request
    proposed_changes = {
        "file_name": "new_file.txt",
        "content": generated_content
    }

    file_path = save_proposed_changes(proposed_changes)
    return jsonify({"message": "Changes prepared. Please confirm and provide a commit message."})

def save_proposed_changes(changes):
    file_path = f"app_changes/{changes['file_name']}"
    with open(file_path, "w") as file:
        file.write(changes['content'])
    return file_path


@app.route('/confirm-commit', methods=['POST'])
def confirm_commit():
    data = request.json
    commit_message = data.get('commit_message')
    confirm = data.get('confirm')

    if confirm and commit_message:
        pull_result = pull_latest_changes()
        if pull_result:
            return jsonify({"error": pull_result}), 500

        push_result = push_changes(commit_message)
        if push_result.startswith("Error"):
            return jsonify({"error": push_result}), 500

        return jsonify({"message": "Changes have been committed and pushed to the repository."})
    else:
        return jsonify({"message": "Commit cancelled."})

def pull_latest_changes():
    try:
        subprocess.check_call(['git', 'pull', 'origin', 'main'])
    except subprocess.CalledProcessError as e:
        return f"Error pulling changes: {e}"

def push_changes(commit_message):
    try:
        subprocess.check_call(['git', 'add', '.'])
        subprocess.check_call(['git', 'commit', '-m', commit_message])
        subprocess.check_call(['git', 'push', 'origin', 'main'])
        return "Changes committed and pushed successfully."
    except subprocess.CalledProcessError as e:
        return f"Error pushing changes: {e}"


if __name__ == '__main__':
    app.run(debug=True)