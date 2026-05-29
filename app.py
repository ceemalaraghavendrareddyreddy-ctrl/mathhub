import os
import json
import sympy
from flask import Flask, render_template, request, jsonify
from database.db import (
    init_db, get_conn, get_levels, get_topics_by_level,
    get_questions_by_topic, get_topic, get_question, search_questions
)

app = Flask(__name__)

# Initialize DB on startup (works with both gunicorn and direct run)
with app.app_context():
    from database.db import init_db
    init_db()

CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))

def _read_config(filename):
    for path in [
        os.path.join(CONFIG_DIR, filename),
        os.path.join(os.getcwd(), filename),
    ]:
        if os.path.exists(path):
            val = open(path, encoding='utf-8').read().strip()
            if val:
                return val
    return ""

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "") or _read_config('config.txt')
GEMINI_API_KEY    = os.environ.get("GEMINI_API_KEY", "")    or _read_config('gemini_key.txt')
GROQ_API_KEY      = os.environ.get("GROQ_API_KEY", "")      or _read_config('groq_key.txt')

if GROQ_API_KEY:
    print(f"[MathApp] Groq key loaded. ({GROQ_API_KEY[:12]}...)")
if GEMINI_API_KEY:
    print(f"[MathApp] Gemini key loaded. ({GEMINI_API_KEY[:12]}...)")
if ANTHROPIC_API_KEY:
    print(f"[MathApp] Anthropic key loaded. ({ANTHROPIC_API_KEY[:12]}...)")
if not GROQ_API_KEY and not GEMINI_API_KEY and not ANTHROPIC_API_KEY:
    print("[MathApp] WARNING: No AI key found. AI Solver will not work.")

@app.route("/")
def index():
    conn = get_conn()
    levels = get_levels(conn)
    conn.close()
    return render_template("index.html", levels=levels)

@app.route("/level/<level>")
def level_page(level):
    conn = get_conn()
    levels = get_levels(conn)
    topics = get_topics_by_level(conn, level)
    conn.close()
    subjects = {}
    for t in topics:
        subjects.setdefault(t["subject"], []).append(t)
    return render_template("level.html", level=level, subjects=subjects, levels=levels)

@app.route("/topic/<int:topic_id>")
def topic_page(topic_id):
    conn = get_conn()
    levels = get_levels(conn)
    topic = get_topic(conn, topic_id)
    questions = get_questions_by_topic(conn, topic_id)
    conn.close()
    if not topic:
        return "Topic not found", 404
    return render_template("topic.html", topic=topic, questions=questions, levels=levels)

@app.route("/question/<int:qid>")
def question_page(qid):
    conn = get_conn()
    levels = get_levels(conn)
    q = get_question(conn, qid)
    conn.close()
    if not q:
        return "Question not found", 404
    return render_template("question.html", q=dict(q), levels=levels)

@app.route("/quiz")
def quiz_setup():
    conn = get_conn()
    levels = get_levels(conn)
    conn.close()
    return render_template("quiz_setup.html", levels=levels)

@app.route("/quiz/play")
def quiz_play():
    level = request.args.get("level", "all")
    num   = int(request.args.get("num", 10))
    diff  = request.args.get("diff", "all")
    conn  = get_conn()
    levels = get_levels(conn)
    query = "SELECT q.*, t.topic, t.level, t.subject FROM questions q JOIN topics t ON q.topic_id=t.id"
    params = []
    conditions = []
    if level != "all":
        conditions.append("t.level=?"); params.append(level)
    if diff != "all":
        conditions.append("q.difficulty=?"); params.append(diff)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY RANDOM() LIMIT ?"
    params.append(num)
    rows = conn.execute(query, params).fetchall()
    questions = [dict(r) for r in rows]
    conn.close()
    if not questions:
        return render_template("quiz_setup.html", levels=levels,
                               error="No questions found for selected filters. Please try different options.")
    return render_template("quiz_play.html", questions=questions, levels=levels)

@app.route("/bookmarks")
def bookmarks_page():
    conn = get_conn()
    levels = get_levels(conn)
    conn.close()
    return render_template("bookmarks.html", levels=levels)

@app.route("/progress")
def progress_page():
    conn = get_conn()
    levels = get_levels(conn)
    conn.close()
    return render_template("progress.html", levels=levels)

@app.route("/solver")
def solver_page():
    conn = get_conn()
    levels = get_levels(conn)
    conn.close()
    return render_template("solver.html", levels=levels)

@app.route("/search")
def search_page():
    query = request.args.get("q", "").strip()
    conn = get_conn()
    levels = get_levels(conn)
    results = []
    if query:
        results = search_questions(conn, query)
    conn.close()
    return render_template("search.html", query=query, results=results, levels=levels)

@app.route("/api/solve", methods=["POST"])
def api_solve():
    data = request.get_json()
    problem = data.get("problem", "").strip()
    if not problem:
        return jsonify({"error": "No problem provided"}), 400

    sympy_result = try_sympy_solve(problem)

    if GROQ_API_KEY:
        ai_result = ask_groq(problem, sympy_result)
    elif GEMINI_API_KEY:
        ai_result = ask_gemini(problem, sympy_result)
    elif ANTHROPIC_API_KEY:
        ai_result = ask_claude(problem, sympy_result)
    else:
        ai_result = None

    return jsonify({
        "sympy": sympy_result,
        "ai_explanation": ai_result,
        "problem": problem
    })

def try_sympy_solve(problem):
    try:
        x, y, z, t, n = sympy.symbols('x y z t n')
        expr = sympy.sympify(problem)
        result = sympy.simplify(expr)
        return str(result)
    except Exception:
        pass

    try:
        import re
        eq_match = re.match(r'^(.+)=(.+)$', problem.strip())
        if eq_match:
            lhs = sympy.sympify(eq_match.group(1))
            rhs = sympy.sympify(eq_match.group(2))
            x = sympy.Symbol('x')
            sols = sympy.solve(lhs - rhs, x)
            if sols:
                return "x = " + ", ".join(str(s) for s in sols)
    except Exception:
        pass

    try:
        result = sympy.sympify(problem)
        return str(float(result))
    except Exception:
        pass

    return None

def ask_claude(problem, sympy_hint=None):
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        hint_text = f"\n\nSymPy computed result: {sympy_hint}" if sympy_hint else ""
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": (
                    f"Solve this math problem with clear step-by-step explanation. "
                    f"Use plain text (no LaTeX). Show all working clearly.\n\n"
                    f"Problem: {problem}{hint_text}"
                )
            }]
        )
        return message.content[0].text
    except Exception as e:
        err = str(e)
        if "credit balance is too low" in err or "credit" in err.lower():
            return "⚠️ Anthropic account has no credits. Please visit console.anthropic.com → Billing → Add Credits (minimum $5). Your API key is working correctly."
        return f"AI explanation unavailable: {err}"

def ask_groq(problem, sympy_hint=None):
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        hint_text = f"\n\nSymPy computed result: {sympy_hint}" if sympy_hint else ""
        prompt = (
            f"Solve this math problem with clear step-by-step explanation. "
            f"Use plain text (no LaTeX). Show all working clearly.\n\n"
            f"Problem: {problem}{hint_text}"
        )
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI explanation unavailable: {str(e)}"

def ask_gemini(problem, sympy_hint=None):
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        hint_text = f"\n\nSymPy computed result: {sympy_hint}" if sympy_hint else ""
        prompt = (
            f"Solve this math problem with clear step-by-step explanation. "
            f"Use plain text (no LaTeX). Show all working clearly.\n\n"
            f"Problem: {problem}{hint_text}"
        )
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        err = str(e)
        if "API_KEY_INVALID" in err or "invalid" in err.lower():
            return "⚠️ Gemini API key is invalid. Please check gemini_key.txt."
        return f"AI explanation unavailable: {err}"

if __name__ == "__main__":
    print("=" * 50)
    print("  Math App — One Stop Math Solution")
    print("  Open in browser: http://127.0.0.1:5000")
    print("  Mobile: use your PC's IP address")
    print("=" * 50)
    app.run(debug=False, host="0.0.0.0", port=5050)
