from flask import Flask, render_template, request, redirect, session
import sqlite3, pickle, pandas as pd, os, random

app = Flask(__name__)
app.secret_key = "secret123"

# Load ML model
model = pickle.load(open("model.pkl","rb"))
scaler = pickle.load(open("scaler.pkl","rb"))

os.makedirs("static", exist_ok=True)

# ---------------- DB ----------------
def init_db():
    conn = sqlite3.connect("students.db")
    cur = conn.cursor()

    # Users table
    cur.execute('''CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role TEXT DEFAULT 'user')''')

    # Results table
    cur.execute('''CREATE TABLE IF NOT EXISTS results(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        result TEXT,
        score REAL)''')

    # ✅ Create admin user if not exists (IMPORTANT FIX)
    cur.execute("SELECT * FROM users WHERE username=?", ("admin",))
    if not cur.fetchone():
        cur.execute("INSERT INTO users(username,password,role) VALUES(?,?,?)",
                    ("admin","admin123","admin"))

    conn.commit()
    conn.close()

init_db()

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST":
        u=request.form["username"]
        p=request.form["password"]

        conn=sqlite3.connect("students.db")
        cur=conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p))
        user=cur.fetchone()
        conn.close()

        if user:
            session["user"]=u
            session["role"]=user[3] if len(user)>3 else "user"

            if session["role"]=="admin":
                return redirect("/admin")
            return redirect("/dashboard")

    return render_template("login.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        conn=sqlite3.connect("students.db")
        conn.execute("INSERT INTO users(username,password) VALUES(?,?)",
                     (request.form["username"], request.form["password"]))
        conn.commit()
        conn.close()
        return redirect("/")
    return render_template("register.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    conn=sqlite3.connect("students.db")
    cur=conn.cursor()

    cur.execute("SELECT COUNT(*) FROM results")
    total=cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM results WHERE result='Good Performance'")
    good=cur.fetchone()[0]

    bad=total-good
    conn.close()

    return render_template("dashboard.html", total=total, good=good, bad=bad)

# ---------------- PREDICT ----------------
@app.route("/predict", methods=["GET","POST"])
def predict():
    if "user" not in session:
        return redirect("/")

    if request.method=="POST":
        try:
            data = [
                float(request.form.get("hours") or 0),
                float(request.form.get("attendance") or 0),
                float(request.form.get("previous") or 0),
                float(request.form.get("assignments") or 0),
                float(request.form.get("extra") or 0),
                float(request.form.get("sleep") or 0)
            ]
        except:
            return render_template("predict.html", error="Enter valid numbers")

        scaled=scaler.transform([data])
        res=model.predict(scaled)[0]

        result="Good Performance" if res==1 else "Needs Improvement"
        rec="Keep it up!" if res==1 else "Improve your study habits"

        score=sum(data)

        conn=sqlite3.connect("students.db")
        conn.execute("INSERT INTO results(username,result,score) VALUES(?,?,?)",
                     (session["user"], result, score))
        conn.commit()
        conn.close()

        return render_template("predict.html", result=result, rec=rec)

    return render_template("predict.html")

# ---------------- ADMIN ----------------
@app.route("/admin")
def admin():
    if session.get("role")!="admin":
        return redirect("/")

    conn=sqlite3.connect("students.db")
    cur=conn.cursor()

    cur.execute("SELECT * FROM users")
    users=cur.fetchall()

    cur.execute("SELECT * FROM results")
    results=cur.fetchall()

    conn.close()

    return render_template("admin.html", users=users, results=results)

# ---------------- DELETE ----------------
@app.route("/delete_user/<int:id>")
def delete_user(id):
    if session.get("role")!="admin":
        return redirect("/")

    conn=sqlite3.connect("students.db")
    conn.execute("DELETE FROM users WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/admin")

@app.route("/delete_result/<int:id>")
def delete_result(id):
    if session.get("role")!="admin":
        return redirect("/")

    conn=sqlite3.connect("students.db")
    conn.execute("DELETE FROM results WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/admin")

# ---------------- CHARTS ----------------
@app.route("/charts")
def charts():
    conn=sqlite3.connect("students.db")
    cur=conn.cursor()

    cur.execute("SELECT result, COUNT(*) FROM results GROUP BY result")
    data=cur.fetchall()

    conn.close()

    labels=[x[0] for x in data]
    values=[x[1] for x in data]

    return render_template("charts.html", labels=labels, values=values)

# ---------------- CHATBOT ----------------
@app.route("/chatbot", methods=["GET","POST"])
def chatbot():
    reply=""
    if request.method=="POST":
        msg=request.form["msg"].lower()
        if "study" in msg:
            reply="Study daily 📚"
        elif "sleep" in msg:
            reply="Sleep well 😴"
        else:
            reply="Stay consistent 💪"

    return render_template("chatbot.html", reply=reply)

# ---------------- UPLOAD ----------------
@app.route("/upload", methods=["GET","POST"])
def upload():
    if "user" not in session:
        return redirect("/")

    file_path=None

    if request.method=="POST":
        file=request.files["file"]
        if file:
            df=pd.read_csv(file)
            X_scaled=scaler.transform(df)
            pred=model.predict(X_scaled)
            df["Prediction"]=pred
            file_path="static/output.csv"
            df.to_csv(file_path,index=False)

    return render_template("upload.html", file=file_path)

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)