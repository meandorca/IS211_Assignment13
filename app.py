from flask import Flask, render_template, request, redirect, session, g
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"

DATABASE = "hw13.db"


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@app.route("/")
def home():
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "password":
            session["logged_in"] = True
            return redirect("/dashboard")
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)


@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect("/login")

    db = get_db()

    students = db.execute(
        "SELECT * FROM students"
    ).fetchall()

    quizzes = db.execute(
        "SELECT * FROM quizzes"
    ).fetchall()

    return render_template(
        "dashboard.html",
        students=students,
        quizzes=quizzes
    )

@app.route("/student/add", methods=["GET", "POST"])
def add_student():
    if not session.get("logged_in"):
        return redirect("/login")

    error = None

    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]

        if not first_name or not last_name:
            error = "Both fields are required"
        else:
            db = get_db()
            db.execute(
                "INSERT INTO students (first_name, last_name) VALUES (?, ?)",
                (first_name, last_name)
            )
            db.commit()
            return redirect("/dashboard")

    return render_template("add_student.html", error=error)

@app.route("/quiz/add", methods=["GET", "POST"])
def add_quiz():
    if not session.get("logged_in"):
        return redirect("/login")

    error = None

    if request.method == "POST":
        subject = request.form["subject"]
        questions = request.form["questions"]
        quiz_date = request.form["quiz_date"]

        if not subject or not questions or not quiz_date:
            error = "All fields are required"
        else:
            db = get_db()
            db.execute(
                "INSERT INTO quizzes (subject, questions, quiz_date) VALUES (?, ?, ?)",
                (subject, questions, quiz_date)
            )
            db.commit()
            return redirect("/dashboard")

    return render_template("add_quiz.html", error=error)

@app.route("/student/<int:student_id>")
def student_results(student_id):
    if not session.get("logged_in"):
        return redirect("/login")

    db = get_db()

    results = db.execute(
        """
        SELECT
            quizzes.id AS quiz_id,
            quizzes.subject,
            quizzes.quiz_date,
            results.score
        FROM results
        JOIN quizzes
            ON results.quiz_id = quizzes.id
        WHERE results.student_id = ?
        """,
        (student_id,)
    ).fetchall()

    return render_template(
        "student_results.html",
        results=results,
        student_id=student_id
    )

@app.route("/results/add", methods=["GET", "POST"])
def add_result():
    if not session.get("logged_in"):
        return redirect("/login")

    db = get_db()
    error = None

    students = db.execute(
        "SELECT * FROM students"
    ).fetchall()

    quizzes = db.execute(
        "SELECT * FROM quizzes"
    ).fetchall()

    if request.method == "POST":
        student_id = request.form["student_id"]
        quiz_id = request.form["quiz_id"]
        score = request.form["score"]

        if not student_id or not quiz_id or not score:
            error = "All fields are required"
        else:
            db.execute(
                """
                INSERT INTO results (student_id, quiz_id, score)
                VALUES (?, ?, ?)
                """,
                (student_id, quiz_id, score)
            )
            db.commit()
            return redirect("/dashboard")

    return render_template(
        "add_result.html",
        students=students,
        quizzes=quizzes,
        error=error
    )

if __name__ == "__main__":
    app.run(debug=True)