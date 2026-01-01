from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from openai import OpenAI

# ================= BASIC APP SETUP =================

app = Flask(__name__)

# SQLite database (auto-created)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ================= OPENAI CLIENT =================
# 🔴 VERY IMPORTANT:
# Paste your OWN OpenAI API key between the quotes below

client = OpenAI(
    api_key="g9prj9jd9k@shubham"
)

# ================= DATABASE MODEL =================

class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    info = db.Column(db.Text, nullable=False)

# Create database file automatically
with app.app_context():
    db.create_all()

# ================= ROUTES =================

@app.route("/", methods=["GET", "POST"])
def index():
    answer = None
    stores = Store.query.all()

    if request.method == "POST":
        store_name = request.form.get("store_name")
        store_info = request.form.get("store_info")
        question = request.form.get("question")

        if not store_name or not question:
            return render_template(
                "index.html",
                answer="Store name and question are required.",
                stores=stores
            )

        store = Store.query.filter_by(name=store_name).first()

        # Save store if new
        if not store:
            if not store_info:
                return render_template(
                    "index.html",
                    answer="Please enter store info for new store.",
                    stores=stores
                )

            store = Store(name=store_name, info=store_info)
            db.session.add(store)
            db.session.commit()

        answer = get_ai_response(store.info, question)

    return render_template("index.html", answer=answer, stores=stores)

# ================= WIDGET API =================

@app.route("/widget-chat", methods=["POST"])
def widget_chat():
    data = request.json

    store_name = data.get("store_name")
    question = data.get("question")

    if not store_name or not question:
        return jsonify({"answer": "Invalid request."})

    store = Store.query.filter_by(name=store_name).first()

    if not store:
        return jsonify({"answer": "Store not found."})

    answer = get_ai_response(store.info, question)
    return jsonify({"answer": answer})

# ================= AI FUNCTION =================

def get_ai_response(store_info, question):
    prompt = f"""
You are a professional e-commerce SALES and SUPPORT assistant.

Rules:
- Use ONLY the provided store information
- Be confident, polite, and persuasive
- Highlight benefits clearly
- Encourage purchase naturally
- NEVER invent details

Store Information:
{store_info}

Customer Question:
{question}

Respond like a real online store assistant.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert e-commerce sales assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"AI Error: {str(e)}"

# ================= RUN APP =================

if __name__ == "__main__":
    app.run(debug=True)
