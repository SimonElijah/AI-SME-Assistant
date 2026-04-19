from flask import Flask, request, render_template, redirect, url_for, send_file
from openai import OpenAI
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import Flask, request, render_template, redirect, url_for, send_file, session

import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import json
import base64
import datetime

# =========================
# USER DATABASE
# =========================

USER_DB = "users.json"

def load_users():
    if not os.path.exists(USER_DB):
        return {}
    with open(USER_DB, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_DB, "w") as f:
        json.dump(users, f)

# =========================
# HELPER FUNCTION
# =========================

def save_result_per_user(username, text):
    folder = f"user_data/{username}"
    os.makedirs(folder, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"{folder}/result_{timestamp}.txt"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

    return file_path

import json
import datetime

def save_chat(username, chat_data):
    folder = f"user_data/{username}"
    os.makedirs(folder, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"{folder}/chat_{timestamp}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(chat_data, f, indent=2)

    return file_path

def get_user_chats(username):
    folder = f"user_data/{username}"
    if not os.path.exists(folder):
        return []

    files = [f for f in os.listdir(folder) if f.startswith("chat_") and f.endswith(".json")]
    files.sort(reverse=True)  # newest first
    return files

def load_chat_file(username, filename):
    path = f"user_data/{username}/{filename}"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
# =========================
# APP SETUP
# =========================

app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.errorhandler(500)
def internal_error(e):
   return f"SERVER ERROR: {str(e)}", 500

# =========================
# LOGIN SETUP
# =========================

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# =========================
# LOGIN ROUTE
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()

        if username in users and users[username]["password"] == password:
            login_user(User(username))
            return redirect("/dashboard")

    return render_template("login.html")

# =========================
# SIGNUP ROUTE
# =========================

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()

        if username in users:
            return "User already exists"

        users[username] = {"password": password}
        save_users(users)

        os.makedirs(f"user_data/{username}", exist_ok=True)
        os.makedirs(f"static/{username}", exist_ok=True)

        return redirect("/login")

    return render_template("signup.html")

# =========================
# LOGOUT
# =========================

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
@login_required
def dashboard():
    text_folder = f"user_data/{current_user.id}"
    text_files = os.listdir(text_folder) if os.path.exists(text_folder) else []

    image_folder = f"static/{current_user.id}"
    images = os.listdir(image_folder) if os.path.exists(image_folder) else []

    return render_template(
        "dashboard.html",
        user=current_user.id,
        files=text_files,
        images=images
    )

# =========================
# AI GENERATOR (HOME)
# =========================

@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    result = ""

    if request.method == "POST":
        business = request.form["business"]
        audience = request.form["audience"]
        platform = request.form["platform"]

        response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {
            "role": "user",
            "content": f"""
You are a business and content expert.

Business: {business}
Audience: {audience}
Platform: {platform}

Give:
1. 5 viral content ideas
2. 3 digital product ideas
3. 1 short video script
4. 1 caption with hashtags
"""
        }
    ]
)

        result = response.choices[0].message.content

        save_result_per_user(current_user.id, result)

    return render_template("generator.html", result=result, user=current_user.id)

# =========================
# DOWNLOAD / DELETE
# =========================

@app.route("/download/<filename>")
@login_required
def download_file(filename):
    path = f"user_data/{current_user.id}/{filename}"

    if os.path.exists(path):
        return send_file(path, as_attachment=True)

    return "File not found"

@app.route("/delete/<filename>")
@login_required
def delete_file(filename):
    path = f"user_data/{current_user.id}/{filename}"

    if os.path.exists(path):
        os.remove(path)

    return redirect("/dashboard")

@app.route("/delete_image/<filename>")
@login_required
def delete_image(filename):
    path = f"static/{current_user.id}/{filename}"

    if os.path.exists(path):
        os.remove(path)

    return redirect("/dashboard")

# =========================
# IMAGE GENERATOR
# =========================
def enhance_prompt(user_input):
    return f"""
Create a high-quality, detailed image based on this idea:

{user_input}

Make it realistic, cinematic lighting, ultra-detailed, 4k, professional photography, sharp focus.
"""

@app.route("/image", methods=["GET","POST"])
# @login_required
def image_generator():

    image_url = None
    error = None

    if request.method == "POST":

        user_input = request.form.get("prompt")

        if not user_input:
            error = "Please enter a prompt"
            return render_template("image.html", image_url=image_url, error=error)

        prompt = enhance_prompt(user_input)

        try:
            result = client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size="1024x1024"
            )

            user_id = current_user.id if current_user.is_authenticated else "guest"
            folder = f"static/{user_id}"
            os.makedirs(folder, exist_ok=True)

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"{folder}/image_{timestamp}.png"

            image_base64 = result.data[0].b64_json
            image_bytes = base64.b64decode(image_base64)

            with open(file_path, "wb") as f:
                f.write(image_bytes)

            image_url = "/" + file_path

        except Exception as e:
            print("IMAGE ERROR:", e)
            return f"IMAGE ERROR: {str(e)}"

    return render_template("image.html", image_url=image_url, error=error)

@app.route("/chat", methods=["GET", "POST"])
@login_required
def chat():

    if "chat_history" not in session:
        session["chat_history"] = []

    error = None

    if request.method == "POST":
        user_message = request.form.get("message")

        if user_message and user_message.strip() != "":
            try:
                response = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful AI assistant."}
                    ] + session["chat_history"] + [
                        {"role": "user", "content": user_message}
                    ]
                )

                ai_reply = response.choices[0].message.content

                session["chat_history"].append({"role": "user", "content": user_message})
                session["chat_history"].append({"role": "assistant", "content": ai_reply})

            except Exception as e:
                error = str(e)

    return render_template(
    "chat.html",
    chat=session["chat_history"],
    error=error,
    chats=get_user_chats(current_user.id)
)

@app.route("/clear_chat")
@login_required
def clear_chat():
    session["chat_history"] = []
    return redirect("/chat")

@app.route("/save_chat")
@login_required
def save_chat_route():
    chat_data = session.get("chat_history", [])
    save_chat(current_user.id, chat_data)
    return redirect("/chat")

@app.route("/load_chat/<filename>")
@login_required
def load_chat(filename):
    session["chat_history"] = load_chat_file(current_user.id, filename)
    return redirect("/chat")
# =========================
# RUN APP
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)