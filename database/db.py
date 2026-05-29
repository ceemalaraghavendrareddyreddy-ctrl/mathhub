import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'math.db')

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            sort_order INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            solution TEXT NOT NULL,
            explanation TEXT NOT NULL,
            difficulty TEXT DEFAULT 'Medium',
            FOREIGN KEY (topic_id) REFERENCES topics(id)
        );
    """)
    conn.commit()

    # Seed topics if empty
    if c.execute("SELECT COUNT(*) FROM topics").fetchone()[0] == 0:
        seed_topics(c)
        conn.commit()

    # Seed questions if empty
    if c.execute("SELECT COUNT(*) FROM questions").fetchone()[0] == 0:
        seed_questions(c)
        conn.commit()

    conn.close()

TOPICS = [
    # (level, subject, topic, sort_order)
    ("Grade 1", "Arithmetic", "Counting & Numbers (1-100)", 1),
    ("Grade 1", "Arithmetic", "Addition (single digit)", 2),
    ("Grade 1", "Arithmetic", "Subtraction (single digit)", 3),
    ("Grade 2", "Arithmetic", "Addition (2-digit)", 4),
    ("Grade 2", "Arithmetic", "Subtraction (2-digit)", 5),
    ("Grade 2", "Arithmetic", "Multiplication Tables (2-5)", 6),
    ("Grade 3", "Arithmetic", "Multiplication Tables (6-12)", 7),
    ("Grade 3", "Arithmetic", "Division (basic)", 8),
    ("Grade 3", "Arithmetic", "Fractions (introduction)", 9),
    ("Grade 4", "Arithmetic", "Fractions (addition & subtraction)", 10),
    ("Grade 4", "Arithmetic", "Decimals (introduction)", 11),
    ("Grade 4", "Arithmetic", "Factors & Multiples", 12),
    ("Grade 5", "Arithmetic", "Decimals (operations)", 13),
    ("Grade 5", "Arithmetic", "Percentages (basic)", 14),
    ("Grade 5", "Geometry", "Perimeter & Area", 15),
    ("Grade 6", "Arithmetic", "Ratios & Proportions", 16),
    ("Grade 6", "Arithmetic", "Integers (negative numbers)", 17),
    ("Grade 6", "Algebra", "Introduction to Algebra", 18),
    ("Grade 7", "Algebra", "Linear Equations (one variable)", 19),
    ("Grade 7", "Geometry", "Triangles & Properties", 20),
    ("Grade 7", "Arithmetic", "Profit & Loss", 21),
    ("Grade 8", "Algebra", "Linear Equations (two variables)", 22),
    ("Grade 8", "Algebra", "Exponents & Powers", 23),
    ("Grade 8", "Geometry", "Quadrilaterals & Polygons", 24),
    ("Grade 9", "Algebra", "Polynomials", 25),
    ("Grade 9", "Geometry", "Circles", 26),
    ("Grade 9", "Algebra", "Coordinate Geometry (basics)", 27),
    ("Grade 10", "Algebra", "Quadratic Equations", 28),
    ("Grade 10", "Trigonometry", "Trigonometric Ratios", 29),
    ("Grade 10", "Arithmetic", "Statistics & Probability (basic)", 30),
    ("Grade 11", "Algebra", "Sequences & Series (AP/GP)", 31),
    ("Grade 11", "Calculus", "Limits & Continuity", 32),
    ("Grade 11", "Algebra", "Binomial Theorem", 33),
    ("Grade 11", "Trigonometry", "Trigonometric Identities", 34),
    ("Grade 12", "Calculus", "Differentiation", 35),
    ("Grade 12", "Calculus", "Integration", 36),
    ("Grade 12", "Algebra", "Matrices & Determinants", 37),
    ("Grade 12", "Algebra", "Probability (advanced)", 38),
    ("University", "Calculus", "Multivariable Calculus", 39),
    ("University", "Calculus", "Differential Equations", 40),
    ("University", "Algebra", "Linear Algebra", 41),
    ("University", "Algebra", "Abstract Algebra", 42),
    ("University", "Analysis", "Real Analysis", 43),
    ("University", "Statistics", "Probability Theory", 44),
    ("University", "Statistics", "Statistical Inference", 45),
    ("University", "Algebra", "Complex Numbers & Functions", 46),
]

def seed_topics(c):
    c.executemany(
        "INSERT INTO topics (level, subject, topic, sort_order) VALUES (?,?,?,?)",
        TOPICS
    )

QUESTIONS = [
    # (topic_id_placeholder=topic_name, question, solution, explanation, difficulty)
    # Grade 1 - Counting
    ("Counting & Numbers (1-100)", "What comes after 47?", "48",
     "When counting forward, each number is 1 more than the previous. 47 + 1 = 48.", "Easy"),
    ("Counting & Numbers (1-100)", "Which number is greater: 63 or 36?", "63",
     "Compare the tens digit first: 6 > 3, so 63 > 36.", "Easy"),
    ("Counting & Numbers (1-100)", "Write the number sixty-five in digits.", "65",
     "Sixty = 60, Five = 5. Together: 65.", "Easy"),

    # Grade 1 - Addition
    ("Addition (single digit)", "3 + 5 = ?", "8",
     "Start at 3, count forward 5 steps: 4, 5, 6, 7, 8. Answer = 8.", "Easy"),
    ("Addition (single digit)", "7 + 6 = ?", "13",
     "7 + 6: Add 3 to make 10, then add remaining 3. So 7+3=10, 10+3=13.", "Easy"),
    ("Addition (single digit)", "9 + 9 = ?", "18",
     "9 + 9 = double of 9 = 18. Or: 9+1=10, then add 8 more = 18.", "Easy"),

    # Grade 1 - Subtraction
    ("Subtraction (single digit)", "9 - 4 = ?", "5",
     "Start at 9, count back 4 steps: 8, 7, 6, 5. Answer = 5.", "Easy"),
    ("Subtraction (single digit)", "8 - 3 = ?", "5",
     "8 - 3: Think of it as 3 + ? = 8. The answer is 5.", "Easy"),

    # Grade 2 - Addition 2-digit
    ("Addition (2-digit)", "34 + 25 = ?", "59",
     "Add tens: 30+20=50. Add ones: 4+5=9. Total = 50+9 = 59.", "Easy"),
    ("Addition (2-digit)", "47 + 38 = ?", "85",
     "Add ones: 7+8=15, write 5 carry 1. Add tens: 4+3+1(carry)=8. Answer = 85.", "Medium"),

    # Grade 3 - Fractions intro
    ("Fractions (introduction)", "What is 1/2 of 10?", "5",
     "1/2 means divide by 2. 10 ÷ 2 = 5.", "Easy"),
    ("Fractions (introduction)", "Which is bigger: 1/2 or 1/4?", "1/2",
     "Same numerator (1), larger denominator means smaller fraction. 1/2 > 1/4.", "Easy"),

    # Grade 5 - Percentages
    ("Percentages (basic)", "What is 20% of 150?", "30",
     "20% = 20/100 = 1/5. So 150 ÷ 5 = 30.", "Easy"),
    ("Percentages (basic)", "A shirt costs ₹500. It has a 15% discount. What is the sale price?", "₹425",
     "Discount = 15% of 500 = 75. Sale price = 500 - 75 = ₹425.", "Medium"),

    # Grade 6 - Ratios
    ("Ratios & Proportions", "If 3 pens cost ₹12, how much do 7 pens cost?", "₹28",
     "Cost per pen = 12/3 = ₹4. For 7 pens: 7 × 4 = ₹28.", "Easy"),
    ("Ratios & Proportions", "Divide 90 in the ratio 2:3.", "36 and 54",
     "Total parts = 2+3 = 5. Each part = 90/5 = 18. So: 2×18=36 and 3×18=54.", "Medium"),

    # Grade 7 - Linear Equations
    ("Linear Equations (one variable)", "Solve: 2x + 5 = 13", "x = 4",
     "Step 1: 2x = 13 - 5 = 8. Step 2: x = 8/2 = 4. Check: 2(4)+5 = 13 ✓", "Easy"),
    ("Linear Equations (one variable)", "Solve: 3x - 7 = 2x + 4", "x = 11",
     "Step 1: 3x - 2x = 4 + 7. Step 2: x = 11. Check: 3(11)-7=26, 2(11)+4=26 ✓", "Medium"),

    # Grade 7 - Profit & Loss
    ("Profit & Loss", "A shopkeeper buys an item for ₹200 and sells it for ₹250. Find profit%.", "25%",
     "Profit = 250-200 = ₹50. Profit% = (50/200)×100 = 25%.", "Easy"),
    ("Profit & Loss", "Cost price = ₹400, Loss% = 10%. Find selling price.", "₹360",
     "Loss = 10% of 400 = 40. Selling Price = 400 - 40 = ₹360.", "Medium"),

    # Grade 8 - Exponents
    ("Exponents & Powers", "Simplify: 2³ × 2⁴", "2⁷ = 128",
     "When multiplying same base, add exponents: 2^(3+4) = 2⁷ = 128.", "Easy"),
    ("Exponents & Powers", "Simplify: (3²)³", "3⁶ = 729",
     "Power of a power: multiply exponents. (3²)³ = 3^(2×3) = 3⁶ = 729.", "Medium"),

    # Grade 9 - Polynomials
    ("Polynomials", "Find the value of p(x) = 2x² - 3x + 1 at x = 2", "3",
     "p(2) = 2(4) - 3(2) + 1 = 8 - 6 + 1 = 3.", "Easy"),
    ("Polynomials", "Factorize: x² - 5x + 6", "(x-2)(x-3)",
     "Find two numbers that multiply to 6 and add to -5: -2 and -3. So (x-2)(x-3).", "Medium"),

    # Grade 10 - Quadratic
    ("Quadratic Equations", "Solve: x² - 5x + 6 = 0", "x = 2 or x = 3",
     "Factorize: (x-2)(x-3)=0. So x=2 or x=3. Check: 4-10+6=0 ✓, 9-15+6=0 ✓", "Medium"),
    ("Quadratic Equations", "Solve using formula: 2x² - 7x + 3 = 0", "x = 3 or x = 1/2",
     "a=2,b=-7,c=3. D = 49-24 = 25. x = (7±5)/4. x=12/4=3 or x=2/4=1/2.", "Medium"),

    # Grade 10 - Trigonometry
    ("Trigonometric Ratios", "In a right triangle, if sin θ = 3/5, find cos θ.", "4/5",
     "Use: sin²θ + cos²θ = 1. (3/5)² + cos²θ = 1. cos²θ = 1-9/25 = 16/25. cos θ = 4/5.", "Medium"),
    ("Trigonometric Ratios", "Find the value of sin 30° + cos 60°.", "1",
     "sin 30° = 1/2. cos 60° = 1/2. Sum = 1/2 + 1/2 = 1.", "Easy"),

    # Grade 11 - AP/GP
    ("Sequences & Series (AP/GP)", "Find the 10th term of AP: 3, 7, 11, ...", "39",
     "a=3, d=4. aₙ = a+(n-1)d = 3+(10-1)4 = 3+36 = 39.", "Medium"),
    ("Sequences & Series (AP/GP)", "Sum of first 20 terms of AP: 1, 3, 5, ...", "400",
     "a=1, d=2, n=20. Sₙ = n/2[2a+(n-1)d] = 20/2[2+38] = 10×40 = 400.", "Medium"),

    # Grade 11 - Limits
    ("Limits & Continuity", "Find: lim(x→2) (x² - 4)/(x - 2)", "4",
     "Factor numerator: (x+2)(x-2)/(x-2) = x+2. At x=2: 2+2 = 4.", "Medium"),
    ("Limits & Continuity", "Find: lim(x→0) sin(x)/x", "1",
     "This is a standard limit result. lim(x→0) sin(x)/x = 1. (Proof uses squeeze theorem.)", "Hard"),

    # Grade 12 - Differentiation
    ("Differentiation", "Find dy/dx if y = x³ + 2x² - 5x + 3", "3x² + 4x - 5",
     "Differentiate term by term: d/dx(x³)=3x², d/dx(2x²)=4x, d/dx(-5x)=-5, d/dx(3)=0.", "Easy"),
    ("Differentiation", "Find dy/dx if y = sin(x²)", "2x·cos(x²)",
     "Chain rule: dy/dx = cos(x²) × d/dx(x²) = cos(x²) × 2x = 2x·cos(x²).", "Medium"),
    ("Differentiation", "Find the derivative of y = eˣ·sin(x)", "eˣ(sin x + cos x)",
     "Product rule: d/dx(u·v) = u'v + uv'. u=eˣ,u'=eˣ; v=sinx,v'=cosx. = eˣsinx + eˣcosx.", "Medium"),

    # Grade 12 - Integration
    ("Integration", "Find ∫(3x² + 2x + 1)dx", "x³ + x² + x + C",
     "Integrate term by term: ∫3x²dx=x³, ∫2xdx=x², ∫1dx=x. Add constant C.", "Easy"),
    ("Integration", "Find ∫sin(x)dx", "-cos(x) + C",
     "Standard result: ∫sin(x)dx = -cos(x) + C. Verify by differentiating: d/dx(-cosx) = sinx ✓", "Easy"),
    ("Integration", "Find ∫x·eˣ dx", "eˣ(x-1) + C",
     "Integration by parts: ∫u dv = uv - ∫v du. u=x,dv=eˣdx; du=dx,v=eˣ. = xeˣ - ∫eˣdx = xeˣ-eˣ+C.", "Hard"),

    # Grade 12 - Matrices
    ("Matrices & Determinants", "Find det of [[2,3],[1,4]]", "5",
     "det = ad - bc = (2)(4) - (3)(1) = 8 - 3 = 5.", "Easy"),
    ("Matrices & Determinants", "Find the inverse of A = [[2,1],[5,3]]", "[[3,-1],[-5,2]]",
     "det(A)=6-5=1. Inverse=(1/det)×adj. adj=[[3,-1],[-5,2]]. Since det=1, inv=[[3,-1],[-5,2]].", "Medium"),

    # University - Differential Equations
    ("Differential Equations", "Solve: dy/dx = y", "y = Ceˣ",
     "Separable ODE: dy/y = dx. Integrate both sides: ln|y| = x + C₀. So y = eˣ·e^C₀ = Ceˣ.", "Medium"),
    ("Differential Equations", "Solve: dy/dx + 2y = 0", "y = Ce^(-2x)",
     "Integrating factor or separable: dy/y = -2dx. ln|y| = -2x + C₀. y = Ce^(-2x).", "Medium"),

    # University - Linear Algebra
    ("Linear Algebra", "Find eigenvalues of A = [[4,1],[2,3]]", "λ = 5 or λ = 2",
     "char eq: det(A-λI)=0. (4-λ)(3-λ)-2=0. λ²-7λ+10=0. (λ-5)(λ-2)=0. λ=5,2.", "Hard"),
    ("Linear Algebra", "Is the set {[1,0],[0,1],[1,1]} linearly independent in R²?", "No, linearly dependent",
     "In R², any 3 vectors are dependent (dimension=2). [1,1]=[1,0]+[0,1], confirming dependence.", "Medium"),

    # University - Complex Numbers
    ("Complex Numbers & Functions", "Find |3 + 4i|", "5",
     "Modulus = √(3² + 4²) = √(9+16) = √25 = 5.", "Easy"),
    ("Complex Numbers & Functions", "Find (1+i)⁸", "16",
     "(1+i)²=2i. (2i)²=-4. (-4)²=16. So (1+i)⁸=16.", "Hard"),

    # University - Probability
    ("Probability Theory", "Two dice are rolled. P(sum = 7)?", "1/6",
     "Favorable: (1,6)(2,5)(3,4)(4,3)(5,2)(6,1) = 6 outcomes. Total = 36. P = 6/36 = 1/6.", "Medium"),
    ("Probability Theory", "P(A)=0.4, P(B)=0.3, A and B independent. Find P(A∪B).", "0.58",
     "P(A∪B)=P(A)+P(B)-P(A∩B). P(A∩B)=0.4×0.3=0.12. P(A∪B)=0.4+0.3-0.12=0.58.", "Medium"),
]

def seed_questions(c):
    topic_map = {}
    rows = c.execute("SELECT id, topic FROM topics").fetchall()
    for row in rows:
        topic_map[row[1]] = row[0]

    for topic_name, question, solution, explanation, difficulty in QUESTIONS:
        tid = topic_map.get(topic_name)
        if tid:
            c.execute(
                "INSERT INTO questions (topic_id, question, solution, explanation, difficulty) VALUES (?,?,?,?,?)",
                (tid, question, solution, explanation, difficulty)
            )

def get_levels(conn):
    return [r[0] for r in conn.execute(
        "SELECT DISTINCT level FROM topics ORDER BY sort_order"
    ).fetchall()]

def get_topics_by_level(conn, level):
    return conn.execute(
        "SELECT * FROM topics WHERE level=? ORDER BY sort_order", (level,)
    ).fetchall()

def get_questions_by_topic(conn, topic_id):
    return conn.execute(
        "SELECT * FROM questions WHERE topic_id=? ORDER BY difficulty", (topic_id,)
    ).fetchall()

def get_topic(conn, topic_id):
    return conn.execute("SELECT * FROM topics WHERE id=?", (topic_id,)).fetchone()

def get_question(conn, qid):
    return conn.execute(
        """SELECT q.*, t.topic, t.level, t.subject
           FROM questions q JOIN topics t ON q.topic_id=t.id
           WHERE q.id=?""", (qid,)
    ).fetchone()

def search_questions(conn, query):
    q = f"%{query}%"
    return conn.execute(
        """SELECT q.*, t.topic, t.level, t.subject
           FROM questions q JOIN topics t ON q.topic_id=t.id
           WHERE q.question LIKE ? OR q.solution LIKE ? OR t.topic LIKE ?
           ORDER BY t.sort_order""",
        (q, q, q)
    ).fetchall()
