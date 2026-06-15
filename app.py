from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.pdfgen import canvas
from flask import send_file
from datetime import datetime
from flask import Flask, render_template, request, redirect, session
import joblib
import sqlite3

app = Flask(__name__)
app.secret_key = "placement_secret_key"

model = joblib.load("model.pkl")
latest_report = {}


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()

        try:
            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (username, hashed_password)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )

        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[2], password):
            session["user"] = username
            return redirect("/")

    return render_template("login.html")


@app.route("/")
def home():

    if "user" not in session:
        return redirect("/login")

    return render_template("index.html")

@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/login")

@app.route("/predict", methods=["POST"])
def predict():

    name = request.form["name"]
    cgpa = float(request.form["cgpa"])
    aptitude = float(request.form["aptitude"])
    communication = float(request.form["communication"])
    projects = float(request.form["projects"])
    internships = float(request.form["internships"])
    certifications = float(request.form["certifications"])
    dsa = float(request.form["dsa"])

    data = [[
        cgpa,
        aptitude,
        communication,
        projects,
        internships,
        certifications,
        dsa
    ]]

    prediction = model.predict(data)
    probability = model.predict_proba(data)[0][1] * 100

    skills = []

    if aptitude < 70:
        skills.append("Improve Aptitude Skills")

    if communication < 70:
        skills.append("Improve Communication Skills")

    if dsa < 70:
        skills.append("Practice DSA Regularly")

    if projects < 2:
        skills.append("Build More Projects")

    if internships < 1:
        skills.append("Gain Internship Experience")

    if certifications < 2:
        skills.append("Complete More Certifications")

    if prediction[0] == 1:
        result = "High Placement Chance"
    else:
        result = "Low Placement Chance"
    global latest_report
    latest_report = {
        "name": name,
        "cgpa": cgpa,
        "probability": round(probability, 2),
        "result": result,
        "skills": skills
    }


    # Save to database
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO students(
    name,
    cgpa,
    aptitude,
    communication,
    projects,
    internships,
    certifications,
    dsa,
    probability,
    result
    )
    VALUES(?,?,?,?,?,?,?,?,?,?)
    """,
    (
        name,
        cgpa,
        aptitude,
        communication,
        projects,
        internships,
        certifications,
        dsa,
        probability,
        result
    ))

    conn.commit()
    conn.close()

    return render_template(
        "index.html",
        prediction=result,
        probability=round(probability, 2),
        skills=skills
    )


@app.route("/dashboard")
def dashboard():

    lr_accuracy = 99
    rf_accuracy = 95.5

    search = request.args.get("search")

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    if search:
        cursor.execute("""
        SELECT * FROM students
        ORDER BY probability DESC
        """)
    else:
        cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    cursor.execute("""
        SELECT COUNT(*)
        FROM students
        WHERE result='High Placement Chance'
    """)
    high = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM students
        WHERE result='Low Placement Chance'
    """)
    low = cursor.fetchone()[0]

    cursor.execute("""
        SELECT AVG(probability)
        FROM students
    """)
    avg_probability = cursor.fetchone()[0]

    conn.close()

    if avg_probability is None:
        avg_probability = 0

    return render_template(
        "dashboard.html",
        students=students,
        high=high,
        low=low,
        avg_probability=round(avg_probability, 2),
        lr_accuracy=lr_accuracy,
        rf_accuracy=rf_accuracy
    )

@app.route("/delete/<int:id>")
def delete(id):

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM students WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")


@app.route("/export")
def export():

    import pandas as pd

    conn = sqlite3.connect("students.db")

    df = pd.read_sql_query(
        "SELECT * FROM students",
        conn
    )

    df.to_excel(
        "students.xlsx",
        index=False
    )

    conn.close()

    return "students.xlsx created successfully!"

@app.route("/download_pdf")
def download_pdf():

    pdf_file = "placement_report.pdf"

    c = canvas.Canvas(pdf_file)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(180, 800, "Placement Report")

    c.setFont("Helvetica", 12)

    c.drawString(50, 750,
                 f"Student Name: {latest_report.get('name','')}")

    c.drawString(50, 720,
                 f"CGPA: {latest_report.get('cgpa','')}")

    c.drawString(50, 690,
                 f"Result: {latest_report.get('result','')}")

    c.drawString(50, 660,
                 f"Probability: {latest_report.get('probability','')}%")

    y = 620

    c.drawString(50, y, "Suggestions:")

    for skill in latest_report.get("skills", []):

        y -= 25
        c.drawString(70, y, f"- {skill}")

    if len(latest_report.get("skills", [])) == 0:
        c.drawString(70, y - 25,
                     "Excellent Profile!")

    c.drawString(
        50,
        100,
        f"Generated On: {datetime.now()}"
    )

    c.save()

    return send_file(
        pdf_file,
        as_attachment=True
    )

@app.route("/student/<int:id>")
def student(id):

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE id=?",
        (id,)
    )

    student = cursor.fetchone()

    conn.close()

    return render_template(
        "student.html",
        student=student
    )

if __name__ == "__main__":
    app.run(debug=True)