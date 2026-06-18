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

# Custom CSS for Full Background Image, Circular Buttons & Mobile Preservation
st.markdown("""
    <style>
    /* Global App Wallpaper Background Injection */
    .stApp {
        background: linear-gradient(rgba(15, 15, 22, 0.88), rgba(15, 15, 22, 0.94)), 
                    url("app/static/My Logo.png") no-repeat center center fixed;
        background-size: cover !important;
    }
    
    /* Global Page Padding */
    .main .block-container { padding-top: 2rem; }
    
    /* Advanced Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 15, 22, 0.95) !important;
        border-right: 1px solid #222336;
    }
    
    /* Clean Up Native Sidebar Text Spacing */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] span {
        font-family: 'Inter', -apple-system, sans-serif;
        color: #E2E8F0;
    }
    
    /* Transform Buttons into Sleek Circular Layouts */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #4F46E5 0%, #3B82F6 100%); 
        color: white; 
        border-radius: 50% !important;     /* Perfect circle shape */
        border: none;
        padding: 0 !important;             
        width: 3.2rem !important;          /* Width & Height equal to secure circles */
        height: 3.2rem !important;         
        font-size: 1.1rem !important;     
        font-weight: 600;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto !important;         
        box-shadow: 0 4px 10px rgba(79, 70, 229, 0.25);
        transition: all 0.2s ease;
        touch-action: manipulation !important;
    }
    
    div.stButton > button:first-child:hover { 
        background: linear-gradient(135deg, #4338CA 0%, #2563EB 100%); 
        transform: scale(1.08);
        box-shadow: 0 6px 14px rgba(79, 70, 229, 0.35);
    }
    
    /* Force Layout Rows to stay Horizontal and avoid Mobile Stacking */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        width: 100% !important;
        justify-content: center;
        align-items: center;
        gap: 0.5rem !important;
    }
    
    /* Dynamic grid spacing for circular elements */
    [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        width: calc(16.6% - 0.4rem) !important;
        flex: 1 1 calc(16.6% - 0.4rem) !important;
        min-width: 10px !important;
    }
    
    /* Modern Content Cards */
    .metric-card {
        background: rgba(22, 22, 36, 0.75); 
        border-radius: 12px; 
        padding: 1.5rem;
        border: 1px solid #222336; 
        backdrop-filter: blur(8px);
    }
    
    /* Customization for Selectbox background */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        background-color: #161624 !important;
        border: 1px solid #222336 !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Helper function for notifications/bookmarks
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
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div class='metric-card'>
                <p style='color: #64748B; margin:0; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;'>Log Volatility</p>
                <h2 style='color: #F1F5F9; margin:0.3rem 0; font-size: 1.8rem;'>{len(st.session_state.history)} ops</h2>
                <span style='color: #10B981; font-size: 0.8rem; font-weight: 600;'>↑ System Active</span>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class='metric-card'>
                <p style='color: #64748B; margin:0; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;'>Stored Matrices</p>
                <h2 style='color: #F1F5F9; margin:0.3rem 0; font-size: 1.8rem;'>{len(st.session_state.favorites)} index</h2>
                <span style='color: #6366F1; font-size: 0.8rem; font-weight: 600;'>★ Static Variables</span>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        quiz_pct = (st.session_state.quiz_score['correct'] / max(st.session_state.quiz_score['total'], 1)) * 100
        st.markdown(f"""
            <div class='metric-card'>
                <p style='color: #64748B; margin:0; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;'>Core Competency</p>
                <h2 style='color: #F1F5F9; margin:0.3rem 0; font-size: 1.8rem;'>{quiz_pct:.1f}%</h2>
                <span style='color: #3B82F6; font-size: 0.8rem; font-weight: 600;'>⚡ Engine Rating</span>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
            <div class='metric-card'>
                <p style='color: #64748B; margin:0; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;'>Engine Status</p>
                <h2 style='color: #10B981; margin:0.3rem 0; font-size: 1.8rem;'>Nominal</h2>
                <span style='color: #10B981; font-size: 0.8rem; font-weight: 600;'>● SymPy Live</span>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    left_panel, right_panel = st.columns([2, 1])
    
    with left_panel:
        st.markdown("<h3 style='color: #E2E8F0; margin-bottom: 1rem;'>🚀 High-Priority Subsystems</h3>", unsafe_allow_html=True)
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            st.markdown("""
                <div style="background: rgba(22, 22, 36, 0.7); padding: 1.5rem; border-radius: 12px; border: 1px solid #222336; height: 180px; backdrop-filter: blur(5px);">
                    <h4 style="margin: 0 0 0.5rem 0; color: #818CF8;">📈 Advanced Vector Grapher</h4>
                    <p style="margin: 0; color: #94A3B8; font-size: 0.9rem; line-height: 1.5;">
                        Deploy high-resolution Plotly canvases featuring custom range mapping, functional evaluation, and real-time step monitoring.
                    </p>
                </div>
            """, unsafe_allow_html=True)
        with row1_col2:
            st.markdown("""
                <div style="background: rgba(22, 22, 36, 0.7); padding: 1.5rem; border-radius: 12px; border: 1px solid #222336; height: 180px; backdrop-filter: blur(5px);">
                    <h4 style="margin: 0 0 0.5rem 0; color: #34D399;">📝 Analytical Step Solver</h4>
                    <p style="margin: 0; color: #94A3B8; font-size: 0.9rem; line-height: 1.5;">
                        Process symbolic computations and isolate non-linear variables. Powered by direct algorithmic factorization.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #E2E8F0;'>🕒 Recent Session Kernels</h4>", unsafe_allow_html=True)
        if st.session_state.history:
            st.dataframe(pd.DataFrame(st.session_state.history).tail(3), use_container_width=True)
        else:
            st.markdown('<div style="background: rgba(17, 17, 27, 0.8); border: 1px dashed #313244; padding: 1rem; border-radius: 8px; text-align: center; color: #6C7086;">No operational kernels compiled within current memory trace.</div>', unsafe_allow_html=True)

    with right_panel:
        st.markdown("<h3 style='color: #E2E8F0; margin-bottom: 1rem;'>💡 System Insight</h3>", unsafe_allow_html=True)
        st.markdown("""
            <div style="background: rgba(30, 30, 46, 0.8); padding: 1.5rem; border-radius: 12px; border: 1px solid #313244; backdrop-filter: blur(5px);">
                <h5 style="margin: 0 0 0.5rem 0; color: #F5E0DC;">Mathematical Quote of the Day</h5>
                <p style="font-style: italic; color: #A6ADC8; font-size: 0.95rem; line-height: 1.5; margin-bottom: 1rem;">
                    "The study of mathematics, like the Nile, begins in minuteness but ends in magnificence."
                </p>
                <span style="color: #F38BA8; font-size: 0.85rem; font-weight: 600;">— Charles Caleb Colton</span>
            </div>
        """, unsafe_allow_html=True)

# --- SMART CALCULATOR (KEYBOARD OPTIMIZED ARITHMETIC ROW) ---
elif page == "🧮 Smart Calculator":
    st.title("🧮 Smart Calculator Workstation")
    
    calc_mode = st.tabs(["Keyboard Input Interface", "History Logs"])
    
    with calc_mode[0]:
        # Clean Keyboard Input Terminal Box
        text_input_val = st.text_input(
            "Type mathematical formula or digits via your keyboard:", 
            value=st.session_state.calc_input,
            key="calc_keyboard_field"
        )
        # Update input state instantly
        st.session_state.calc_input = text_input_val
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Horizontal Row of Arithmetic Quick-Actions (Circular Matrix Grid)
        col_plus, col_minus, col_mult, col_div, col_del, col_c = st.columns(6)
        
        with col_plus:
            if st.button("+", key="btn_plus"):
                st.session_state.calc_input += "+"
                st.rerun()
        with col_minus:
            if st.button("-", key="btn_minus"):
                st.session_state.calc_input += "-"
                st.rerun()
        with col_mult:
            if st.button("×", key="btn_mult"):
                st.session_state.calc_input += "*"
                st.rerun()
        with col_div:
            if st.button("÷", key="btn_div"):
                st.session_state.calc_input += "/"
                st.rerun()
        with col_del:
            if st.button("⌫", key="btn_del"):
                st.session_state.calc_input = st.session_state.calc_input[:-1]
                st.rerun()
        with col_c:
            if st.button("C", key="btn_clear"):
                st.session_state.calc_input = ""
                st.rerun()
                
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Explicit Submit Action
        if st.button("Calculate Expression (=)", use_container_width=True):
            if st.session_state.calc_input:
                try:
                    parsed_expr = sp.sympify(st.session_state.calc_input)
                    numeric_res = float(parsed_expr.evalf())
                    
                    st.session_state.history.append({
                        "timestamp": datetime.now().strftime("%H:%M:%S"), 
                        "expr": st.session_state.calc_input, 
                        "res": f"{numeric_res:.4f}"
                    })
                    st.session_state.calc_input = f"{numeric_res:.4f}"
                    st.rerun()
                except Exception:
                    st.error("Syntax Validation Failure. Please check syntax elements.")
                            
    with calc_mode[1]:
        if st.session_state.history:
            df_hist = pd.DataFrame(st.session_state.history)
            st.dataframe(df_hist, use_container_width=True)
            st.download_button("Export Logs to CSV", df_hist.to_csv(index=False), "mathlab_history.csv")
        else:
            st.write("No calculations logged yet.")

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