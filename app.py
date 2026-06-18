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
    page_title="MathLab Pro v3.0",
    page_icon="📐",
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
if 'system_kernel_status' not in st.session_state:
    st.session_state.system_kernel_status = "ONLINE"

# Custom CSS for Sleek Glassmorphic Sidebar, Background Wallpaper & Typography
st.markdown("""
    <style>
    /* Global App Wallpaper Background Injection */
    .stApp {
        background: linear-gradient(rgba(10, 10, 18, 0.92), rgba(10, 10, 18, 0.96)), 
                    url("app/static/My Logo.png") no-repeat center center fixed;
        background-size: cover !important;
    }
    
    .main .block-container { padding-top: 1.5rem; }
    
    /* Advanced Ultra-Sophisticated Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(16, 16, 28, 0.98) 0%, rgba(10, 10, 16, 1) 100%) !important;
        border-right: 1px solid rgba(99, 102, 241, 0.2);
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.5);
    }
    
    /* Custom Decorative Header Container inside Sidebar */
    .sidebar-brand-box {
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.15) 0%, rgba(59, 130, 246, 0.05) 100%);
        border: 1px solid rgba(99, 102, 241, 0.25);
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    /* Custom Sidebar Metrics Panel */
    .sidebar-status-pill {
        display: inline-block;
        background: rgba(16, 185, 129, 0.15);
        color: #10B981;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        border: 1px solid rgba(16, 185, 129, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Formatted Content Cards */
    .metric-card {
        background: rgba(22, 22, 38, 0.7); 
        border-radius: 12px; 
        padding: 1.2rem;
        border: 1px solid rgba(255, 255, 255, 0.05); 
        backdrop-filter: blur(8px);
    }
    
    /* Control Form Elements and Tables Typography */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        background-color: #141423 !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        border-radius: 8px !important;
    }
    
    .stDataFrame {
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        overflow: hidden;
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
# 3. HIGHLY SOPHISTICATED SIDEBAR WORKSPACE
# ==========================================
with st.sidebar:
    # Top Level Interactive Header Branding Container
    st.markdown("""
        <div class="sidebar-brand-box">
            <h3 style="color: #F8FAFC; margin: 0; font-size: 1.4rem; font-weight: 800;">MATHLAB <span style="color:#6366F1;">PRO</span></h3>
            <p style="color: #94A3B8; margin: 0.2rem 0 0.6rem 0; font-size: 0.8rem;">Computational Engine v3.0</p>
            <div class="sidebar-status-pill">● Engine Live</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Try embedding localized structural branding logo asset
    try:
        st.image("My Logo.png", use_container_width=True)
    except Exception:
        pass
        
    st.markdown("<p style='color: #64748B; font-size:0.75rem; font-weight:700; text-transform:uppercase; margin-bottom: 0.3rem;'>Navigation Matrix</p>", unsafe_allow_html=True)
    page = st.selectbox(
        "Workspace Viewport selector",
        ["🏠 Home Dashboard", "📐 Trig Table Generator", "⚡ Differentiation Solver", "integral_view", "Advanced Geometry", "📚 Formula Library", "📖 Dictionary", 
         "📈 Graphing Tool", "📊 Statistics Calc", "🔢 Matrix Calc", "🔄 Unit Converter", "🎯 Practice Zone"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # NEW SIDEBAR FEATURE 1: System Hardware/Kernel Status Diagnostics Controller Panel
    with st.expander("🛠️ System Diagnostics", expanded=False):
        st.caption("Computational Kernel Status")
        if st.checkbox("Toggle Engine Override Mode", value=False):
            st.session_state.system_kernel_status = "OVERRIDE"
            st.warning("Kernel running in experimental bypass.")
        else:
            st.session_state.system_kernel_status = "ONLINE"
        st.write(f"Active Port State: `CPU-THREAD-LIVE`")
        st.write(f"Workspace Mode: `{st.session_state.system_kernel_status}`")
        
    # NEW SIDEBAR FEATURE 2: Real-time Session Activity Metrics Tracker
    with st.expander("📊 Runtime Analytics", expanded=False):
        st.metric("Logged Operations", f"{len(st.session_state.history)} entries")
        st.metric("Total Favorites", f"{len(st.session_state.favorites)} bookmarked")
        if st.button("Purge Temporary Volatile Memory"):
            st.session_state.history = []
            st.rerun()

    # NEW SIDEBAR FEATURE 3: Elegant Bookmark Registry Viewport
    st.markdown("### ⭐ Active Bookmarks")
    if st.session_state.favorites:
        for fav in st.session_state.favorites:
            st.markdown(f"<code style='color:#818CF8; background:rgba(129,140,248,0.1); padding:2px 6px; border-radius:4px; font-size:0.8rem;'>{fav}</code>", unsafe_allow_html=True)
    else:
        st.caption("No operational definitions flagged inside lookup stack.")

# ==========================================
# 4. PRIMARY VIEWPORT SUBSYSTEMS
# ==========================================

# --- HOME DASHBOARD ---
if page == "🏠 Home Dashboard":
    st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(30, 27, 75, 0.6) 0%, rgba(15, 23, 42, 0.7) 100%); 
                    padding: 2.2rem; border-radius: 16px; border: 1px solid rgba(99, 102, 241, 0.2); 
                    margin-bottom: 2rem; backdrop-filter: blur(10px);">
            <h1 style="color: #F8FAFC; margin: 0; font-size: 2.6rem; font-weight: 800; letter-spacing: -0.025em;">
                Welcome to MathLab <span style="background: linear-gradient(90deg, #6366F1, #3B82F6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Pro v3.0</span>
            </h1>
            <p style="color: #94A3B8; margin: 0.6rem 0 0 0; font-size: 1.1rem; max-width: 700px; line-height: 1.6;">
                An integrated analytical development environment specialized in symbolic calculus transformations, advanced spatial geometric coordinates, and numeric matrix mapping.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div class='metric-card'>
                <h4 style='color: #6366F1; margin-top:0;'>⚡ High-Speed Calculus</h4>
                <p style='color: #94A3B8; font-size:0.9rem; line-height:1.5; margin-bottom:0;'>
                    Execute direct integration transformations or differentiation limits symbolically with instant SymPy computation chains.
                </p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class='metric-card'>
                <h4 style='color: #34D399; margin-top:0;'>📐 Advanced Geometry</h4>
                <p style='color: #94A3B8; font-size:0.9rem; line-height:1.5; margin-bottom:0;'>
                    Analyze complex multidimensional solids including spheres, cones, and composite parameters instantly with absolute accuracy.
                </p>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class='metric-card'>
                <h4 style='color: #3B82F6; margin-top:0;'>📊 Trigonometric Indices</h4>
                <p style='color: #94A3B8; font-size:0.9rem; line-height:1.5; margin-bottom:0;'>
                    Generate completely customizable modular grid mapping structures across customized step boundaries for high-precision validation.
                </p>
            </div>
        """, unsafe_allow_html=True)

# --- NEW WORKSPACE: TRIGONOMETRIC TABLE GENERATOR ---
elif page == "📐 Trig Table Generator":
    st.title("📐 Dynamic Trigonometric Reference Array Matrix")
    st.write("Generate customized, high-precision trigonometric data grids across flexible interval configurations.")
    
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        angle_mode = st.radio("Angle Measurement Base Scale Unit:", ["Degrees", "Radians"])
    with col_t2:
        step_val = st.number_input("Incremental Step Frequency Bounds", min_value=0.1, max_value=45.0, value=15.0 if angle_mode == "Degrees" else 0.25)
    with col_t3:
        precision_val = st.slider("Decimal Fraction Precision Cutoff", 2, 10, 5)
        
    # Boundary Arrays Calculation Setup
    if angle_mode == "Degrees":
        angles = np.arange(0, 360 + step_val, step_val)
        rad_angles = np.radians(angles)
    else:
        angles = np.arange(0, (2 * np.pi) + step_val, step_val)
        rad_angles = angles
        
    # Generate Compute Map Frame
    trig_data = {
        f"Angle ({angle_mode})": np.round(angles, precision_val),
        "Sine (sin)": np.round(np.sin(rad_angles), precision_val),
        "Cosine (cos)": np.round(np.cos(rad_angles), precision_val),
        "Tangent (tan)": [f"±∞" if np.isclose(np.abs(np.cos(r)), 0.0, atol=1e-10) else str(np.round(np.tan(r), precision_val)) for r in rad_angles]
    }
    
    df_trig = pd.DataFrame(trig_data)
    st.dataframe(df_trig, use_container_width=True, height=450)
    st.download_button("Export Compiled Trigonometric Matrix Data Block", df_trig.to_csv(index=False), "trig_matrix_export.csv")

# --- NEW WORKSPACE: DIFFERENTIATION SOLVER ---
elif page == "⚡ Differentiation Solver":
    st.title("⚡ Symbolic Differentiation Engine")
    st.write("Compute exact derivatives, higher-order multi-derivatives, and evaluate slope gradients at custom coordinates.")
    
    diff_expr_str = st.text_input("Enter Function Equation Expression f(x):", "x**3 - 5*x**2 + 2*x - 10")
    order_val = st.number_input("Derivative Order Sequence Iteration ($n$-th derivative)", min_value=1, max_value=5, value=1)
    
    if st.button("Execute Numerical Differentiation"):
        try:
            x = sp.symbols('x')
            parsed_diff_expr = sp.sympify(diff_expr_str)
            derived_sol = sp.diff(parsed_diff_expr, x, order_val)
            
            st.markdown("### Structural Transformation Analytics")
            st.write("Original Equation Function Input:")
            st.latex(f"f(x) = {sp.latex(parsed_diff_expr)}")
            st.write(f"Resulting Derivative State Order ({order_val}):")
            st.latex(f"\\frac{{d^{order_val}}}{{dx^{order_val}}} f(x) = {sp.latex(derived_sol)}")
            
            # Interactive point evaluation module addition
            st.markdown("---")
            st.subheader("Point Coordinate Gradient Evaluator")
            eval_pt = st.number_input("Evaluate Target Axis Point location ($x_0$):", value=2.0)
            numeric_slope = float(derived_sol.subs(x, eval_pt).evalf())
            st.metric(f"Instantaneous Tangent Slope Velocity Value at x = {eval_pt}", f"{numeric_slope:.4f}")
        except Exception as e:
            st.error(f"Symbolic validation compilation processing error: {e}")

# --- NEW WORKSPACE: INTEGRATION SOLVER ---
elif page == "integral_view":
    st.title("🔗 Analytical Integration Modeling Studio")
    st.write("Resolve exact symbolic primitives or map computational bounding regions via definite integral boundaries.")
    
    int_type = st.radio("Integration Operational Calculus Framework Type:", ["Indefinite Calculus", "Definite Calculus Boundary Matrix"])
    int_expr_str = st.text_input("Enter Integrand Function Expression f(x):", "3*x**2 + 2*x")
    
    x = sp.symbols('x')
    try:
        parsed_int_expr = sp.sympify(int_expr_str)
        
        if int_type == "Indefinite Calculus":
            if st.button("Compute Indefinite Primitive Matrix"):
                sol_int = sp.integrate(parsed_int_expr, x)
                st.markdown("### Primitive Indefinite Anti-Derivative Map Result")
                st.latex(f"\\int f(x) dx = {sp.latex(sol_int)} + C")
                
        else:
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                lower_bound = st.number_input("Lower Range Matrix Limit Boundary ($a$)", value=0.0)
            with col_b2:
                upper_bound = st.number_input("Upper Range Matrix Limit Boundary ($b$)", value=2.0)
                
            if st.button("Compute Definite Boundary Area Enclosure"):
                sol_def_int = sp.integrate(parsed_int_expr, (x, lower_bound, upper_bound))
                st.markdown("### Area Vector Definite Sum Result")
                st.latex(f"\\int_{{{lower_bound}}}^{{{upper_bound}}} f(x) dx = {float(sol_def_int.evalf()):.5f}")
    except Exception as e:
        st.error(f"Integration Engine parse stack overflow event: {e}")

# --- NEW WORKSPACE: ADVANCED GEOMETRY ---
elif page == "Advanced Geometry":
    st.title("💎 Advanced 3D Spatial Solid Geometry Core")
    st.write("Compute surface areas, volumes, and directional space constraints for multidimensional geometric structures.")
    
    solid_type = st.selectbox("Select Target Solid Structure Matrix:", ["Sphere", "Right Circular Cone", "Ellipsoid Core"])
    
    if solid_type == "Sphere":
        sphere_r = st.number_input("Sphere Radius ($r$)", min_value=0.01, value=5.0)
        vol_sph = (4/3) * np.pi * (sphere_r**3)
        area_sph = 4 * np.pi * (sphere_r**2)
        st.metric("Total Enclosed Volume ($V$)", f"{vol_sph:.5f}")
        st.metric("Total Surface Area Boundary ($A$)", f"{area_sph:.5f}")
        
    elif solid_type == "Right Circular Cone":
        cone_r = st.number_input("Base Aperture Radius ($r$)", min_value=0.01, value=3.0)
        cone_h = st.number_input("Vertical Altitude Displacement Height ($h$)", min_value=0.01, value=7.0)
        slant_s = np.sqrt(cone_r**2 + cone_h**2)
        vol_cone = (1/3) * np.pi * (cone_r**2) * cone_h
        area_cone = np.pi * cone_r * (cone_r + slant_s)
        st.metric("Calculated Enclosed Volume", f"{vol_cone:.5f}")
        st.metric("Calculated Total Boundary Surface Area", f"{area_cone:.5f}")
        
    elif solid_type == "Ellipsoid Core":
        semi_a = st.number_input("Semi-Principal X Axis Dimension Vector ($a$)", min_value=0.01, value=4.0)
        semi_b = st.number_input("Semi-Principal Y Axis Dimension Vector ($b$)", min_value=0.01, value=3.0)
        semi_c = st.number_input("Semi-Principal Z Axis Dimension Vector ($c$)", min_value=0.01, value=5.0)
        vol_ellip = (4/3) * np.pi * semi_a * semi_b * semi_c
        st.metric("Ellipsoidal Interior Spatial Volume Enclosure", f"{vol_ellip:.5f}")

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