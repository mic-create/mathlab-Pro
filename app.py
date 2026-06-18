import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import sympy as sp
import random
from datetime import datetime
from scipy import stats

# ==========================================
# 1. INITIALIZATION & CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="MathLab Pro",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session States
if 'history' not in st.session_state:
    st.session_state.history = []
if 'favorites' not in st.session_state:
    st.session_state.favorites = set()
if 'quiz_score' not in st.session_state:
    st.session_state.quiz_score = {'correct': 0, 'total': 0}
if 'quiz_current' not in st.session_state:
    st.session_state.quiz_current = None
if 'calc_input' not in st.session_state:
    st.session_state.calc_input = ""

# Custom CSS for Background, JAMB Layout Matching & High Responsiveness
st.markdown("""
    <style>
    /* Global App Wallpaper Background Injection */
    .stApp {
        background: linear-gradient(rgba(15, 15, 22, 0.88), rgba(15, 15, 22, 0.94)), 
                    url("app/static/My Logo.png") no-repeat center center fixed;
        background-size: cover !important;
    }
    
    .main .block-container { padding-top: 2rem; }
    
    /* Advanced Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 15, 22, 0.95) !important;
        border-right: 1px solid #222336;
    }
    
    /* Main JAMB Square/Rounded Button Styling */
    div.stButton > button {
        background: #0000FF !important; /* Pure Blue theme from template image */
        color: white !important; 
        border-radius: 14px !important; /* Soft corners exactly like template */
        border: 2px solid #0000CC !important;
        padding: 0.8rem 0rem !important;             
        font-size: 1.2rem !important;     
        font-weight: bold !important;
        width: 100% !important;
        box-shadow: 0 4px 8px rgba(0, 0, 255, 0.2);
        transition: all 0.15s ease;
        touch-action: manipulation !important;
    }
    
    div.stButton > button:hover { 
        background: #0000CC !important;
        transform: scale(1.02);
    }
    
    /* Special Full-Width Red Clear All Layout Button styling */
    div.clear-box div.stButton > button {
        background: #FF0000 !important; /* Pure Red clear bar */
        border: 2px solid #CC0000 !important;
        font-size: 1.1rem !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 8px rgba(255, 0, 0, 0.2);
    }
    div.clear-box div.stButton > button:hover {
        background: #CC0000 !important;
    }
    
    /* Lock elements into a strict 4-Column Grid on Mobile devices */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        width: 100% !important;
        gap: 0.4rem !important;
    }
    
    [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        width: calc(25% - 0.3rem) !important;
        flex: 1 1 calc(25% - 0.3rem) !important;
        min-width: 10px !important;
    }
    
    /* Blueprint display layout mirroring your reference graphic */
    .jamb-display {
        background-color: #0000FF !important;
        border: 2px solid #000000;
        border-radius: 6px;
        color: white !important;
        font-family: 'Courier New', monospace;
        font-size: 2.2rem;
        font-weight: bold;
        text-align: right;
        padding: 1.5rem;
        margin-bottom: 1rem;
        min-height: 5.5rem;
    }
    
    /* Global Selectbox background */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        background-color: #161624 !important;
        border: 1px solid #222336 !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Helper function for bookmarks
def toggle_favorite(item: str):
    if item in st.session_state.favorites:
        st.session_state.favorites.remove(item)
    else:
        st.session_state.favorites.add(item)

# ==========================================
# 2. DICTIONARY & FORMULA DATA ASSETS
# ==========================================
FORMULA_DB = {
    "Algebra": {
        "Quadratic Formula": "$$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$",
        "Binomial Theorem": "$$(a+b)^n = \\sum_{k=0}^n \\binom{n}{k} a^{n-k}b^k$$"
    },
    "Geometry": {
        "Area of Circle": "$$A = \\pi r^2$$",
        "Pythagorean Theorem": "$$a^2 + b^2 = c^2$$"
    },
    "Trigonometry": {
        "Pythagorean Identity": "$$\\sin^2(\\theta) + \\cos^2(\\theta) = 1$$",
        "Double Angle Sine": "$$\\sin(2\\theta) = 2\\sin(\\theta)\\cos(\\theta)$$"
    },
    "Calculus": {
        "Fundamental Theorem": "$$\\int_a^b f(x) dx = F(b) - F(a)$$",
        "Derivative Definition": "$$f'(x) = \\lim_{h \\to 0} \\frac{f(x+h)-f(x)}{h}$$"
    }
}

DICT_DB = {
    "Algorithm": "A step-by-step procedure for solving a problem or accomplishing an end.",
    "Derivative": "The rate of change of a function with respect to a variable.",
    "Eigenvalue": "A scalar associated with a given linear transformation of a vector space.",
    "Matrix": "A rectangular array of quantities or expressions in rows and columns.",
    "Vector": "A quantity having direction as well as magnitude, especially as determining the position of one point in space relative to another."
}

# ==========================================
# 3. SIDEBAR NAVIGATION & LOGO
# ==========================================
with st.sidebar:
    try:
        st.image("My Logo.png", use_container_width=True)
    except Exception:
        st.markdown("<h2 style='color: #6366F1; margin-bottom: 0;'>Overah Core</h2>", unsafe_allow_html=True)
        
    st.title("🧪 MathLab Pro")
    st.caption("Advanced Mathematical Workspace v2.0")
    st.markdown("---")
    
    page = st.selectbox(
        "Navigate Workspace",
        ["🏠 Home", "🧮 Smart Calculator", "📚 Formula Library", "📖 Dictionary", 
         "📈 Graphing Tool", "📐 Geometry Calc", "📊 Statistics Calc", 
         "🔢 Matrix Calc", "🔄 Unit Converter", "📝 Equation Solver", "🎯 Practice Zone"]
    )
    
    st.markdown("---")
    st.markdown("### ⭐ Saved Bookmarks")
    if st.session_state.favorites:
        for fav in st.session_state.favorites:
            st.caption(f"• {fav}")
    else:
        st.caption("No items bookmarked yet.")

# ==========================================
# 4. PAGE IMPLEMENTATIONS
# ==========================================

# --- HOME PAGE ---
if page == "🏠 Home":
    st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(30, 27, 75, 0.6) 0%, rgba(15, 23, 42, 0.7) 100%); 
                    padding: 2.5rem; border-radius: 16px; border: 1px solid #312E81; 
                    margin-bottom: 2rem; backdrop-filter: blur(10px);">
            <h1 style="color: #F8FAFC; margin: 0; font-size: 2.8rem; font-weight: 800; letter-spacing: -0.025em;">
                MathLab <span style="background: linear-gradient(90deg, #6366F1, #3B82F6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Pro</span>
            </h1>
            <p style="color: #94A3B8; margin: 0.75rem 0 0 0; font-size: 1.2rem; max-width: 600px; line-height: 1.6;">
                The high-performance predictive analytics and computational modeling environment for modern engineered workflows.
            </p>
        </div>
    """, unsafe_allow_html=True)

# --- SMART CALCULATOR (JAMB STYLE MATRIX REPLICA) ---
elif page == "🧮 Smart Calculator":
    st.title("🧮 JAMB Layout Calculator")
    
    calc_mode = st.tabs(["Calculator Matrix Terminal", "Calculations History Log"])
    
    with calc_mode[0]:
        # Blue background screen panel display matching user's reference blueprint image
        st.markdown(f"""
            <div class="jamb-display">
                {st.session_state.calc_input if st.session_state.calc_input else "0"}
            </div>
        """, unsafe_allow_html=True)
        
        # Interactive text field fallback allowing clean user keyboard entry processing
        typed_input = st.text_input("Keyboard Entry Stream Listener:", value=st.session_state.calc_input, label_visibility="collapsed")
        if typed_input != st.session_state.calc_input:
            st.session_state.calc_input = typed_input
            st.rerun()
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Comprehensive 4-Column layout matrix mirroring configuration
        # Row 1: Scientific extensions
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("sin", key="sin"): st.session_state.calc_input += "sin("; st.rerun()
        with c2:
            if st.button("cos", key="cos"): st.session_state.calc_input += "cos("; st.rerun()
        with c3:
            if st.button("tan", key="tan"): st.session_state.calc_input += "tan("; st.rerun()
        with c4:
            if st.button("√", key="sqrt"): st.session_state.calc_input += "sqrt("; st.rerun()

        # Row 2: Scientific extensions contd.
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("log", key="log"): st.session_state.calc_input += "log("; st.rerun()
        with c2:
            if st.button("^", key="pow"): st.session_state.calc_input += "**"; st.rerun()
        with c3:
            if st.button("(", key="op_par"): st.session_state.calc_input += "("; st.rerun()
        with c4:
            if st.button(")", key="cl_par"): st.session_state.calc_input += ")"; st.rerun()

        # Row 3: Image Blueprint row 1
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("1", key="num1"): st.session_state.calc_input += "1"; st.rerun()
        with c2:
            if st.button("2", key="num2"): st.session_state.calc_input += "2"; st.rerun()
        with c3:
            if st.button("3", key="num3"): st.session_state.calc_input += "3"; st.rerun()
        with c4:
            if st.button("+", key="op_add"): st.session_state.calc_input += "+"; st.rerun()
            
        # Row 4: Image Blueprint row 2
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("4", key="num4"): st.session_state.calc_input += "4"; st.rerun()
        with c2:
            if st.button("5", key="num5"): st.session_state.calc_input += "5"; st.rerun()
        with c3:
            if st.button("6", key="num6"): st.session_state.calc_input += "6"; st.rerun()
        with c4:
            if st.button("-", key="op_sub"): st.session_state.calc_input += "-"; st.rerun()
            
        # Row 5: Image Blueprint row 3
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("7", key="num7"): st.session_state.calc_input += "7"; st.rerun()
        with c2:
            if st.button("8", key="num8"): st.session_state.calc_input += "8"; st.rerun()
        with c3:
            if st.button("9", key="num9"): st.session_state.calc_input += "9"; st.rerun()
        with c4:
            if st.button("*", key="op_mul"): st.session_state.calc_input += "*"; st.rerun()
            
        # Row 6: Image Blueprint row 4
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("/", key="op_div"): st.session_state.calc_input += "/"; st.rerun()
        with c2:
            if st.button("0", key="num0"): st.session_state.calc_input += "0"; st.rerun()
        with c3:
            if st.button(".", key="dec_pt"): st.session_state.calc_input += "."; st.rerun()
        with c4:
            if st.button("=", key="eval_eq"):
                if st.session_state.calc_input:
                    try:
                        clean_expr = st.session_state.calc_input
                        if 'log(' in clean_expr:
                            parsed_val = sp.sympify(clean_expr, local_dict={'log': lambda x: sp.log(x, 10)})
                        else:
                            parsed_val = sp.sympify(clean_expr)
                            
                        numeric_res = float(parsed_val.evalf())
                        st.session_state.history.append({
                            "timestamp": datetime.now().strftime("%H:%M:%S"), 
                            "expr": st.session_state.calc_input, 
                            "res": f"{numeric_res:.4f}"
                        })
                        st.session_state.calc_input = f"{numeric_res:.4f}"
                        st.rerun()
                    except Exception:
                        st.error("Syntax Error")
                        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Red Full-Width Clear Bar container exactly matching your image mockup
        st.markdown('<div class="clear-box">', unsafe_allow_html=True)
        if st.button("Clear All", key="clear_all_bar", use_container_width=True):
            st.session_state.calc_input = ""
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
                            
    with calc_mode[1]:
        if st.session_state.history:
            df_hist = pd.DataFrame(st.session_state.history)
            st.dataframe(df_hist, use_container_width=True)
        else:
            st.write("No execution tracking loops logged within this operational buffer frame.")

# --- FORMULA LIBRARY ---
elif page == "📚 Formula Library":
    st.title("📚 Academic Formula Reference Manual")
    search_q = st.text_input("🔍 Search Formulas Across Domains").lower()
    
    for category, formulas in FORMULA_DB.items():
        with st.expander(f"{category} Matrices", expanded=True):
            for name, formula in formulas.items():
                if search_q in name.lower() or search_q in category.lower():
                    col_f, col_b = st.columns([0.8, 0.2])
                    with col_f:
                        st.markdown(f"**{name}**")
                        st.markdown(formula)
                    with col_b:
                        fav_label = "⭐ Bookmarked" if name in st.session_state.favorites else "☆ Bookmark"
                        if st.button(fav_label, key=f"f_{name}"):
                            toggle_favorite(name)
                            st.rerun()

# --- DICTIONARY ---
elif page == "📖 Dictionary":
    st.title("📖 Mathematical Terminologies Dictionary")
    search_d = st.text_input("Search Dictionary Catalog")
    
    for term, definition in DICT_DB.items():
        if search_d.lower() in term.lower() or search_d.lower() in definition.lower():
            st.markdown(f"### {term}")
            st.write(definition)
            st.markdown("---")

# --- GRAPHING TOOL ---
elif page == "📈 Graphing Tool":
    st.title("📈 Interactive Advanced Plot Engine")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        func_str = st.text_input("Enter Function f(x)", "x**2 - 4*x + 3")
        x_min = st.number_input("X Min", value=-10.0)
        x_max = st.number_input("X Max", value=10.0)
        points = st.slider("Resolution Sample Points", 50, 1000, 200)
        
    with col2:
        try:
            x_vals = np.linspace(x_min, x_max, points)
            x = sp.symbols('x')
            sym_func = sp.sympify(func_str)
            f_num = sp.lambdify(x, sym_func, "numpy")
            y_vals = f_num(x_vals)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name=f"f(x) = {func_str}", line=dict(color='#636EFA', width=3)))
            fig.update_layout(title=f"Plot Architecture: {func_str}", template="plotly_dark", xaxis_title="X", yaxis_title="Y")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Plot generation failed: {e}")

# --- GEOMETRY CALCULATOR ---
elif page == "📐 Geometry Calc":
    st.title("📐 Dynamic Shape Geometry Solver")
    shape = st.selectbox("Select Shape Matrix", ["Circle", "Triangle", "Rectangle", "Cylinder"])
    
    if shape == "Circle":
        r = st.number_input("Radius ($r$)", min_value=0.0, value=1.0)
        st.metric("Calculated Area", f"{np.pi * r**2:.4f}")
        st.metric("Calculated Circumference", f"{2 * np.pi * r:.4f}")
    elif shape == "Rectangle":
        w = st.number_input("Width ($w$)", min_value=0.0, value=1.0)
        h = st.number_input("Height ($h$)", min_value=0.0, value=1.0)
        st.metric("Calculated Area", f"{w * h:.4f}")
        st.metric("Calculated Perimeter", f"{2 * (w + h):.4f}")
    elif shape == "Triangle":
        b = st.number_input("Base ($b$)", min_value=0.0, value=1.0)
        h = st.number_input("Height ($h$)", min_value=0.0, value=1.0)
        st.metric("Calculated Area", f"{0.5 * b * h:.4f}")
    elif shape == "Cylinder":
        r = st.number_input("Radius ($r$)", min_value=0.0, value=1.0)
        h = st.number_input("Height ($h$)", min_value=0.0, value=1.0)
        st.metric("Volume", f"{np.pi * r**2 * h:.4f}")

# --- STATISTICS CALCULATOR ---
elif page == "📊 Statistics Calc":
    st.title("📊 Statistical Computational Engine")
    data_input = st.text_area("Input Sample Dataset (Comma separated entries)", "12, 15, 12, 18, 22, 15, 14, 19, 20")
    
    if data_input:
        try:
            arr = np.array([float(x.strip()) for x in data_input.split(",") if x.strip()])
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Arithmetic Mean (μ)", f"{np.mean(arr):.4f}")
                st.metric("Median Target", f"{np.median(arr):.4f}")
            with col2:
                st.metric("Sample Variance (σ²)", f"{np.var(arr, ddof=1):.4f}")
                st.metric("Std Deviation (σ)", f"{np.std(arr, ddof=1):.4f}")
        except Exception as e:
            st.error(f"Parsing error: {e}")

# --- MATRIX CALCULATOR ---
elif page == "🔢 Matrix Calc":
    st.title("🔢 Linear Algebra Matrix Engine")
    
    st.write("Construct Matrix A (2x2 Matrix Block)")
    col1, col2 = st.columns(2)
    with col1:
        a11 = st.number_input("A[1,1]", value=1.0)
        a21 = st.number_input("A[2,1]", value=0.0)
    with col2:
        a12 = st.number_input("A[1,2]", value=0.0)
        a22 = st.number_input("A[2,2]", value=1.0)
        
    mat_A = np.array([[a11, a12], [a21, a22]])
    
    st.markdown("### Computations Matrix Output")
    st.write("Matrix array state:", mat_A)
    det = np.linalg.det(mat_A)
    st.metric("Determinant value", f"{det:.4f}")
    
    if det != 0:
        st.write("Inverse Matrix Workspace:", np.linalg.inv(mat_A))
    else:
        st.warning("Determinant is zero; computing an inverse matrix structure is impossible.")

# --- UNIT CONVERTER ---
elif page == "🔄 Unit Converter":
    st.title("🔄 Multi-Domain Unit Transform Engine")
    conv_type = st.selectbox("Measurement Dimension", ["Length", "Weight"])
    
    if conv_type == "Length":
        val = st.number_input("Input Value Value", value=1.0)
        unit_from = st.selectbox("From Unit", ["Meters", "Kilometers", "Miles"])
        unit_to = st.selectbox("Target Transform Unit", ["Meters", "Kilometers", "Miles"])
        
        factors = {"Meters": 1.0, "Kilometers": 1000.0, "Miles": 1609.34}
        base_val = val * factors[unit_from]
        target_val = base_val / factors[unit_to]
        st.metric("Resulting Dimension Conversion", f"{target_val:.4f} {unit_to}")

# --- EQUATION SOLVER ---
elif page == "📝 Equation Solver":
    st.title("📝 Analytical & Symbolic Equation Engine")
    eq_str = st.text_input("Enter Equation equaled to zero state f(x) = 0", "x**2 - 5*x + 6")
    
    if st.button("Resolve System Roots"):
        try:
            x = sp.symbols('x')
            parsed_eq = sp.sympify(eq_str)
            solutions = sp.solve(parsed_eq, x)
            
            st.success("### Solutions Found")
            for idx, sol in enumerate(solutions):
                st.latex(f"x_{{{idx+1}}} = {sp.latex(sol)}")
        except Exception as e:
            st.error(f"Solver Engine error processing inputs: {e}")

# --- PRACTICE ZONE ---
elif page == "🎯 Practice Zone":
    st.title("🎯 Training Core / Mathematical Arena")
    
    if st.button("Generate New Training Problem") or st.session_state.quiz_current is None:
        val1 = random.randint(1, 12)
        val2 = random.randint(1, 12)
        ans = val1 * val2
        options = [ans, ans + random.randint(1, 5), ans - random.randint(1, 5), random.randint(1, 144)]
        random.shuffle(options)
        st.session_state.quiz_current = {"question": f"What is {val1} × {val2}?", "options": options, "answer": ans}
        
    st.markdown(f"#### Question: {st.session_state.quiz_current['question']}")
    user_choice = st.radio("Choose correct structural verification element:", st.session_state.quiz_current['options'])
    
    if st.button("Submit Answer Vector"):
        st.session_state.quiz_score['total'] += 1
        if user_choice == st.session_state.quiz_current['answer']:
            st.success("Correct Evaluation!")
            st.session_state.quiz_score['correct'] += 1
        else:
            st.error(f"Incorrect result structure. Right option variant was: {st.session_state.quiz_current['answer']}")