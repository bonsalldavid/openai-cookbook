from flask import Flask, send_from_directory, request, jsonify
from dotenv import load_dotenv
import json
from openai import OpenAI
import time

#Needs Debugging to turn Debugging on :-( ! 
#if __name__ == '__main__':
#    app.run(debug=False)


app = Flask(__name__)

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


def create_thread_and_run(user_input, assistant_name, assistant_instructions, use_code_interpreter):
    global current_thread
    global MATH_ASSISTANT_ID

   # Update assistant if necessary
    if assistant_name or assistant_instructions or use_code_interpreter:
        tools = [{"type": "code_interpreter"}] if use_code_interpreter else []
        assistant = client.beta.assistants.update(
            MATH_ASSISTANT_ID,
            name=assistant_name,
            instructions=assistant_instructions,
            tools=tools
        )
        MATH_ASSISTANT_ID = assistant.id



    if current_thread is None:
        current_thread = client.beta.threads.create()
    run = submit_message(MATH_ASSISTANT_ID, current_thread, user_input)
    return current_thread, run

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
def index():
        return send_from_directory('.', 'ai_interaction.html')

@app.route('/submit', methods=['POST'])
def submit():
    user_input = request.form['userInput']
    assistant_name = request.form.get('assistantName', '')
    assistant_instructions = request.form.get('assistantInstructions', '')
    use_code_interpreter = 'codeInterpreter' in request.form

    # Debugging print statement
    print("Code Interpreter Enabled:", use_code_interpreter)

    thread, run = create_thread_and_run(user_input, assistant_name, assistant_instructions, use_code_interpreter)
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

if __name__ == '__main__':
    app.run(debug=True)