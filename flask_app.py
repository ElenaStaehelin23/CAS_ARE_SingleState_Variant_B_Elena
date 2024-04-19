import os
from flask import Flask, jsonify, render_template, request, send_file

from chatbot.chatbot import Chatbot

PYTHONANYWHERE_USERNAME = "carvice"
PYTHONANYWHERE_WEBAPPNAME = "mysite"

app = Flask(__name__)

my_type_role = """
    ​​ich bin hier, um dir zu helfen, dich an Dinge zu erinnern, die dir gerade schwerfallen zu greifen. 
    Bitte erzähle mir etwas über das, was dir 'auf der Zunge liegt'. 
    Ich werde dir einige Fragen stellen, um dir zu helfen, deine Gedanken zu klären. 
    Deine Antworten werden mir helfen, präzisere Fragen zu formulieren, die den Nebel um deine flüchtigen Erinnerungen lichten sollen.
    Lass uns gemeinsam herausfinden, woran du denkst.
"""

my_instance_context = """
    Um deine Erinnerung präzise zu unterstützen, werde ich nun einige spezifische, geschlossene Fragen stellen. Diese Fragen erfordern nur kurze Antworten wie 'ja', 'nein' oder ein spezifisches Schlüsselwort. 
    Zum Beispiel, war das Ereignis, an das du dich zu erinnern versuchst, in den letzten fünf Jahren? War es ein persönliches Erlebnis oder beruflich? Bitte antworte so konkret wie möglich.
"""

my_instance_starter = """
Willkommen! Ich bin dein Erinnerungs-Assistent. Wenn du jemals das Gefühl hast, dass dir etwas 'auf der Zunge liegt' und du es gerade nicht greifen kannst, bin ich hier, um dir zu helfen. 
Erzähl mir einfach, worüber du nachdenkst oder was du zu erinnern versuchst, und wir werden gemeinsam daran arbeiten, deine Gedanken zu klären. Wie kann ich dir heute helfen?
"""

bot = Chatbot(
    database_file="database/chatbot.db", 
    type_id="coach",
    user_id="daniel",
    type_name="Health Coach",
    type_role=my_type_role,
    instance_context=my_instance_context,
    instance_starter=my_instance_starter
)

bot.start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/mockups.pdf', methods=['GET'])
def get_first_pdf():
    script_directory = os.path.dirname(os.path.realpath(__file__))
    files = [f for f in os.listdir(script_directory) if os.path.isfile(os.path.join(script_directory, f))]
    pdf_files = [f for f in files if f.lower().endswith('.pdf')]
    if pdf_files:
        # Get the path to the first PDF file
        pdf_path = os.path.join(script_directory, pdf_files[0])

        # Send the PDF file as a response
        return send_file(pdf_path, as_attachment=True)

    return "No PDF file found in the root folder."

@app.route("/<type_id>/<user_id>/chat")
def chatbot(type_id: str, user_id: str):
    return render_template("chat.html")


@app.route("/<type_id>/<user_id>/info")
def info_retrieve(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: dict[str, str] = bot.info_retrieve()
    return jsonify(response)


@app.route("/<type_id>/<user_id>/conversation")
def conversation_retrieve(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: list[dict[str, str]] = bot.conversation_retrieve()
    return jsonify(response)


@app.route("/<type_id>/<user_id>/response_for", methods=["POST"])
def response_for(type_id: str, user_id: str):
    user_says = None
    # content_type = request.headers.get('Content-Type')
    # if (content_type == 'application/json; charset=utf-8'):
    user_says = request.json
    # else:
    #    return jsonify('/response_for request must have content_type == application/json')

    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    assistant_says_list: list[str] = bot.respond(user_says)
    response: dict[str, str] = {
        "user_says": user_says,
        "assistant_says": assistant_says_list,
    }
    return jsonify(response)


@app.route("/<type_id>/<user_id>/reset", methods=["DELETE"])
def reset(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    bot.reset()
    assistant_says_list: list[str] = bot.start()
    response: dict[str, str] = {
        "assistant_says": assistant_says_list,
    }
    return jsonify(response)
