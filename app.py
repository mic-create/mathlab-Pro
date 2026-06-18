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

# Advanced CSS Injection for a Premium Digital Lab Environment
st.markdown("""
    <style>
    /* Global Background Accent Framework - Adjusted to look for 'My Logo.png' in root directory */
    .stApp {
        background: linear-gradient(rgba(10, 10, 20, 0.94), rgba(12, 12, 24, 0.97)), 
                    url("My Logo.png") no-repeat center center fixed;
        background-size: cover !important;
    }
    
    .main .block-container { padding-top: 1.5rem; }
    
    /* Sidebar Aesthetics */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(14, 14, 26, 0.98) 0%, rgba(8, 8, 16, 1) 100%) !important;
        border-right: 1px solid rgba(99, 102, 241, 0.25);
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.6);
    }
    
    /* Branding Header Card */
    .sidebar-brand-box {
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.18) 0%, rgba(59, 130, 246, 0.06) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 1.2rem;
        border-radius: 14px;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    /* Status Micro-Pill */
    .sidebar-status-pill {
        display: inline-block;
        background: rgba(16, 185, 129, 0.15);
        color: #10B981;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        border: 1px solid rgba(16, 185, 129, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    
    /* Sophisticated UI Container Cards */
    .metric-card {
        background: rgba(20, 20, 38, 0.65); 
        border-radius: 14px; 
        padding: 1.5rem;
        border: 1px solid rgba(99, 102, 241, 0.15); 
        backdrop-filter: blur(12px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        margin-bottom: 1rem;
    }
    
    /* Document/Dictionary Item Cards */
    .dict-card {
        background: rgba(24, 24, 48, 0.5);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 12px;
        padding: 1.6rem;
        margin-bottom: 1.2rem;
        backdrop-filter: blur(6px);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
    }
    
    /* Interactive Live Textbook Preview Shield */
    .real-display-panel {
        background: rgba(12, 12, 24, 0.85);
        border-left: 4px solid #6366F1;
        padding: 1.2rem;
        border-radius: 4px 12px 12px 4px;
        margin-top: 0.6rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    /* Frame Tables Content Wrap */
    .stDataFrame {
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
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
# 2. DATA ASSETS & FORMULA INDEX
# ==========================================
FORMULA_DB = {
    "Algebraic Structures": {
        "Quadratic Formula Identity": "$$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$",
        "Generalized Binomial Theorem": "$$(a+b)^n = \\sum_{k=0}^n \\binom{n}{k} a^{n-k}b^k$$"
    },
    "Differential & Spatial Geometry": {
        "Area Boundary of a Circle": "$$A = \\pi r^2$$",
        "Classic Pythagorean Theorem": "$$a^2 + b^2 = c^2$$"
    },
    "Trigonometric Analysis": {
        "Pythagorean Angular Identity": "$$\\sin^2(\\theta) + \\cos^2(\\theta) = 1$$",
        "Double Angle Sine Reduction": "$$\\sin(2\\theta) = 2\\sin(\\theta)\\cos(\\theta)$$"
    },
    "Infinitesimal Calculus Core": {
        "Fundamental Theorem of Calculus": "$$\\int_a^b f(x) dx = F(b) - F(a)$$",
        "Derivative from First Principles Limit": "$$f'(x) = \\lim_{h \\to 0} \\frac{f(x+h)-f(x)}{h}$$"
    }
}

DICT_DB = {
    "Arithmetic Progression (AP)": {
        "def": "A sequential mathematical progression of values where the incremental step difference between neighboring terms remains strictly constant.",
        "formula": "$$a_n = a_1 + (n - 1)d$$"
    },
    "Bayes' Theorem": {
        "def": "A probability identity that quantifies conditional state probabilities based on relevant prior information parameters.",
        "formula": "$$P(A|B) = \\frac{P(B|A) \\cdot P(A)}{P(B)}$$"
    },
    "Binomial Coefficient": {
        "def": "The structural combination counting factor used to choose subset groups of k elements from an n size set collection.",
        "formula": "$$\\binom{n}{k} = \\frac{n!}{k!(n-k)!}$$"
    },
    "Derivative (First Principles)": {
        "def": "The limiting slope rate value mapping the dynamic variation change of functional coordinates across infintesimal spans.",
        "formula": "$$f'(x) = \\lim_{h \\to 0} \\frac{f(x+h) - f(x)}{h}$$"
    },
    "Euler's Identity": {
        "def": "A famous transcendental system benchmark statement combining five foundational constants of analytical computation.",
        "formula": "$$e^{i\\pi} + 1 = 0$$"
    },
    "Fourier Series Expansion": {
        "def": "The breakdown orchestration mapping cyclic wave functions into sum series coordinates of sines and cosines.",
        "formula": "$$f(x) = \\frac{a_0}{2} + \\sum_{n=1}^{\\infty} \\left[ a_n \\cos(nx) + b_n \\sin(nx) \\right]$$"
    },
    "Geometric Progression (GP) Sum": {
        "def": "The calculated total accumulation aggregation of values structured around consistent geometric step scales.",
        "formula": "$$S_n = \\frac{a(1 - r^n)}{1 - r} \\quad (r \\neq 1)$$"
    },
    "Laplace Transform": {
        "def": "An operator conversion equation modifying continuous temporal systems into functional complex space coordinates.",
        "formula": "$$\\mathcal{L}\\{f(t)\\} = \\int_{0}^{\\infty} e^{-st} f(t) \\, dt$$"
    },
    "Matrix Determinant (2x2)": {
        "def": "The scale coefficient factor characterizing structural multi-dimensional array mapping bounds.",
        "formula": "$$\\det\\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix} = ad - bc$$"
    },
    "Normal Distribution PDF": {
        "def": "The classic continuous bell curve probability density density equation mapped across standard standard variance indicators.",
        "formula": "$$f(x) = \\frac{1}{\\sigma\\sqrt{2\\pi}} e^{-\\frac{1}{2}\\left(\\frac{x-\\mu}{\\sigma}\\right)^2}$$"
    }
}

# ==========================================
# 3. SIDEBAR NAVIGATION CONTROLLER
# ==========================================
with st.sidebar:
    st.markdown("""
        <div class="sidebar-brand-box">
            <h3 style="color: #F8FAFC; margin: 0; font-size: 1.4rem; font-weight: 800; letter-spacing: 0.05em;">MATHLAB <span style="color:#6366F1;">PRO</span></h3>
            <p style="color: #94A3B8; margin: 0.2rem 0 0.6rem 0; font-size: 0.78rem;">Quantum Architecture Environment</p>
            <div class="sidebar-status-pill">● System Matrix Active</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Safe multi-path asset checkpoint fallback loader
    try:
        st.image("My Logo.png", use_container_width=True)
    except Exception:
        try:
            st.image("app/static/My Logo.png", use_container_width=True)
        except Exception:
            st.caption("⚠️ [My Logo.png asset placeholder trace]")
            
    st.markdown("<p style='color: #64748B; font-size:0.75rem; font-weight:700; text-transform:uppercase; margin-bottom: 0.4rem;'>Nav Matrix</p>", unsafe_allow_html=True)
    page = st.selectbox(
        "Navigation Select",
        ["🏠 Dashboard Matrix", "📖 Operational System Manual", "⚡ Derivative Vector Engine", "🔗 Definite Integration Core", "📐 High-Precision Trig Array", "💎 Spatial Solid Dimensions", "📚 Formula Reference Matrix", "📖 Lexicon Dictionary", 
         "📈 Visual Graph Matrix", "📊 Dataset Analytical Core", "🔢 Matrix Vector Solver", "🔄 Metric Transformation Shield", "🎯 Operational Practice Arena"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    with st.expander("🛠️ Kernel Configuration", expanded=False):
        if st.checkbox("Override Standard Computing Stack", value=False):
            st.session_state.system_kernel_status = "OVERRIDE"
            st.warning("Kernel executing via bypass track.")
        else:
            st.session_state.system_kernel_status = "ONLINE"
        st.caption(f"Port Execution Vector: `CPU-THREAD-ACTIVE`")
        st.caption(f"Kernel Profile State: `{st.session_state.system_kernel_status}`")
        
    with st.expander("📊 Volatile Analytics Tracker", expanded=False):
        st.metric("Operations Logged", f"{len(st.session_state.history)} entries")
        st.metric("Active Bookmarks", f"{len(st.session_state.favorites)} items")
        if st.button("Purge Array Frame Memory Cache"):
            st.session_state.history = []
            st.rerun()

    st.markdown("### ⭐ Tracked Flag Stack")
    if st.session_state.favorites:
        for fav in st.session_state.favorites:
            st.markdown(f"<code style='color:#818CF8; background:rgba(129,140,248,0.1); padding:3px 8px; border-radius:6px; font-size:0.78rem; display:inline-block; margin:2px;'>{fav}</code>", unsafe_allow_html=True)
    else:
        st.caption("No markers active inside lookup tracks.")

# ==========================================
# 4. ARCHITECTURAL INTERACTIVE WORKSPACES
# ==========================================

# --- DASHBOARD MATRIX ---
if page == "🏠 Dashboard Matrix":
    st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(24, 24, 48, 0.7) 0%, rgba(12, 12, 24, 0.9) 100%); 
                    padding: 2.5rem; border-radius: 16px; border: 1px solid rgba(99, 102, 241, 0.25); 
                    margin-bottom: 2rem; backdrop-filter: blur(12px); box-shadow: 0 8px 32px rgba(0,0,0,0.4);">
            <h1 style="color: #F8FAFC; margin: 0; font-size: 2.8rem; font-weight: 800; letter-spacing: -0.03em;">
                Analytical Laboratory <span style="background: linear-gradient(90deg, #6366F1, #3B82F6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Pro v3.0</span>
            </h1>
            <p style="color: #94A3B8; margin: 0.8rem 0 0 0; font-size: 1.15rem; max-width: 800px; line-height: 1.6;">
                An enterprise-tier computing workspace engineered for clean symbolic calculus parsing, high-precision geometry matrix arrays, and fluid structural dataset evaluation.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div class='metric-card'>
                <h4 style='color: #6366F1; margin-top:0; font-weight:700;'>⚡ Symbolic Calculus Core</h4>
                <p style='color: #94A3B8; font-size:0.92rem; line-height:1.6; margin-bottom:0;'>
                    Execute exact derivation sequences and definitive area boundaries under real-time textbook formula compilation views.
                </p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class='metric-card'>
                <h4 style='color: #10B981; margin-top:0; font-weight:700;'>📐 Spatial Form Arrays</h4>
                <p style='color: #94A3B8; font-size:0.92rem; line-height:1.6; margin-bottom:0;'>
                    Model and measure structural parameters for intricate volumetric spaces, spheres, cones, and vector bounds dynamically.
                </p>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class='metric-card'>
                <h4 style='color: #3B82F6; margin-top:0; font-weight:700;'>📚 Structural Dictionary</h4>
                <p style='color: #94A3B8; font-size:0.92rem; line-height:1.6; margin-bottom:0;'>
                    Navigate complex mathematical terminology connected seamlessly with verified academic definitions and clean equation templates.
                </p>
            </div>
        """, unsafe_allow_html=True)

# --- SYSTEM MANUAL WORKSPACE ---
elif page == "📖 Operational System Manual":
    st.markdown("""
        <div class="metric-card" style="border-left: 4px solid #3B82F6;">
            <h2 style="color:#F8FAFC; margin-top:0;">📖 System Operational Matrix Manual</h2>
            <p style="color:#94A3B8;">Guidelines detailing data entry standards for running accurate analytical calculations.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_m1, col_m2 = st.columns([3, 2])
    with col_m1:
        st.markdown("### 🔣 Calculus & Equation Plot Input Rules")
        st.write("When operating the **Derivative Vector Engine**, **Definite Integration Core**, or **Visual Graph Matrix**, mathematical entry sequences must conform to standard computational operators. The system converts raw expressions instantly into beautiful textbook styles.")
        
        syntax_df = pd.DataFrame({
            "Mathematical Matrix Target": ["Multiplication Scale", "Exponentiation / Power", "Rational Division", "Sine Wave Form", "Exponential E Base", "Square Root Base"],
            "Functional Input Code Syntax": ["a * x", "x ** 4", "2 / (x + 3)", "sin(x)", "exp(x)", "sqrt(x)"],
            "System Rendering Display Look": ["$$a \\cdot x$$", "$$x^4$$", "$$\\frac{2}{x+3}$$", "$$\\sin(x)$$", "$$e^x$$", "$$\\sqrt{x}$$"]
        })
        st.table(syntax_df)
        
    with col_m2:
        st.markdown("### 📋 Section Operational Directives")
        with st.expander("⚡ Calculus Core Solvers", expanded=True):
            st.caption("1. Input function code strings based on the rules grid table.\n2. Observe the real-display live tracking board view to confirm expression design.\n3. Identify evaluation target parameters and execute calculation steps.")
        with st.expander("📐 Data Matrices & Data Arrays", expanded=False):
            st.caption("1. Provide clean numerical inputs separated accurately by commas for statistical distributions.\n2. When configuring multidimensional solid volumes, confirm parameter boundaries are above 0 threshold values.")

# --- DERIVATIVE ENGINE ---
elif page == "⚡ Derivative Vector Engine":
    st.markdown("<div class='metric-card'><h2>⚡ Symbolic Derivative Vector Engine</h2><p style='color:#94A3B8;'>Compute exact expressions and differential gradients through live textbook display updates.</p></div>", unsafe_allow_html=True)
    
    col_d1, col_d2 = st.columns([2, 2])
    with col_d1:
        diff_expr_str = st.text_input("Assign Target Expression Function f(x):", "x**3 - 4*x**2 + 5*x - 12")
        order_val = st.number_input("Derivative Order Sequence Level ($n$-th order)", min_value=1, max_value=5, value=1)
    
    with col_d2:
        st.markdown("<p style='font-size:0.85rem; color:#818CF8; margin-bottom:2px; font-weight:600;'>✨ Live Real Display Math Preview Panel:</p>", unsafe_allow_html=True)
        try:
            x = sp.symbols('x')
            parsed_live = sp.sympify(diff_expr_str)
            st.markdown('<div class="real-display-panel">', unsafe_allow_html=True)
            st.latex(f"f(x) = {sp.latex(parsed_live)}")
            st.markdown('</div>', unsafe_allow_html=True)
        except Exception:
            st.caption("(Awaiting correct operational syntax format entry...)")
            
    if st.button("Execute Differential Sequence Computation", type="primary"):
        try:
            derived_sol = sp.diff(parsed_live, x, order_val)
            st.markdown("---")
            st.markdown("### 📋 Calculation Tracking Matrix Output")
            
            c_res1, c_res2 = st.columns(2)
            with c_res1:
                st.markdown("<div class='metric-card' style='text-align:center;'>", unsafe_allow_html=True)
                st.caption("Input Matrix State:")
                st.latex(f"f(x) = {sp.latex(parsed_live)}")
                st.markdown("</div>", unsafe_allow_html=True)
            with c_res2:
                st.markdown("<div class='metric-card' style='text-align:center; border: 1px solid #10B981;'>", unsafe_allow_html=True)
                st.caption("Resolved Real-Display Derivative Output:")
                if order_val == 1:
                    st.latex(f"f'(x) = {sp.latex(derived_sol)}")
                else:
                    st.latex(f"\\frac{{d^{order_val}}}{{dx^{order_val}}} f(x) = {sp.latex(derived_sol)}")
                st.markdown("</div>", unsafe_allow_html=True)
                
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.subheader("📍 Precise Coordinate Gradient Evaluation")
            col_eval1, col_eval2 = st.columns(2)
            with col_eval1:
                eval_pt = st.number_input("Target Evaluation Point Coordinate ($x_0$):", value=2.0)
            with col_eval2:
                numeric_slope = float(derived_sol.subs(x, eval_pt).evalf())
                st.metric(f"Instantaneous Tangent Gradient Velocity at x = {eval_pt}", f"{numeric_slope:.4f}")
            st.markdown("</div>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Differential engine validation execution error: {e}")

# --- INTEGRATION CORE ---
elif page == "🔗 Definite Integration Core":
    st.markdown("<div class='metric-card'><h2>🔗 Analytical Integration Core Studio</h2><p style='color:#94A3B8;'>Resolve continuous integration primitives or evaluate coordinate bounding structures.</p></div>", unsafe_allow_html=True)
    
    int_type = st.radio("Select Integration Framework Structure Mode:", ["Indefinite Calculus Track", "Definite Coordinate Boundary Matrix"], horizontal=True)
    
    col_i1, col_i2 = st.columns(2)
    with col_i1:
        int_expr_str = st.text_input("Enter Core Integrand Formula String f(x):", "4*x**3 + 3*x**2")
    with col_i2:
        st.markdown("<p style='font-size:0.85rem; color:#818CF8; margin-bottom:2px; font-weight:600;'>✨ Live Real Display Math Preview Panel:</p>", unsafe_allow_html=True)
        try:
            x = sp.symbols('x')
            parsed_int = sp.sympify(int_expr_str)
            st.markdown('<div class="real-display-panel">', unsafe_allow_html=True)
            if int_type == "Indefinite Calculus Track":
                st.latex(f"\\int \\left({sp.latex(parsed_int)}\\right) dx")
            else:
                st.latex(f"\\int_{{a}}^{{b}} \\left({sp.latex(parsed_int)}\\right) dx")
            st.markdown('</div>', unsafe_allow_html=True)
        except Exception:
            st.caption("(Awaiting continuous function sequence entry configuration...)")
            
    if int_type == "Indefinite Calculus Track":
        if st.button("Compute Primitive Integral Solution Matrix", type="primary"):
            try:
                sol_int = sp.integrate(parsed_int, x)
                st.markdown("<div class='metric-card' style='text-align:center; border:1px solid #10B981;'>", unsafe_allow_html=True)
                st.subheader("Resolved Anti-Derivative Formulation Matrix")
                st.latex(f"\\int \\left({sp.latex(parsed_int)}\\right) dx = {sp.latex(sol_int)} + C")
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Solver fault event: {e}")
    else:
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            lower_bound = st.number_input("Lower Vector Limit Matrix Boundary ($a$)", value=0.0)
        with col_b2:
            upper_bound = st.number_input("Upper Vector Limit Matrix Boundary ($b$)", value=3.0)
            
        if st.button("Execute Definite Boundary Calculation Enclosure", type="primary"):
            try:
                sol_def_int = sp.integrate(parsed_int, (x, lower_bound, upper_bound))
                st.markdown("<div class='metric-card' style='text-align:center; border:1px solid #10B981;'>", unsafe_allow_html=True)
                st.subheader("Resolved Bounding Area Definite Value Matrix")
                st.latex(f"\\int_{{{lower_bound}}}^{{{upper_bound}}} \\left({sp.latex(parsed_int)}\\right) dx = {float(sol_def_int.evalf()):.5f}")
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Solver boundary constraint error: {e}")

# --- HIGH-PRECISION TRIG ARRAY ---
elif page == "📐 High-Precision Trig Array":
    st.markdown("<div class='metric-card'><h2>📐 High-Precision Trigonometric Data Matrix Array</h2><p style='color:#94A3B8;'>Generate systematic custom geometric ratio datasets based on flexible angle frequency configurations.</p></div>", unsafe_allow_html=True)
    
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        angle_mode = st.radio("Angular Base Mapping Standard System:", ["Degrees", "Radians"])
    with col_t2:
        step_val = st.number_input("Incremental Grid Step Vector Frequency Size:", min_value=0.1, max_value=90.0, value=15.0 if angle_mode == "Degrees" else 0.2)
    with col_t3:
        precision_val = st.slider("Float Fraction Decimal Rounding Precision", 2, 10, 6)
        
    if angle_mode == "Degrees":
        angles = np.arange(0, 360 + step_val, step_val)
        rad_angles = np.radians(angles)
    else:
        angles = np.arange(0, (2 * np.pi) + step_val, step_val)
        rad_angles = angles
        
    trig_data = {
        f"Angle Scalar ({angle_mode})": np.round(angles, precision_val),
        "Sine Ratio Vector (sin)": np.round(np.sin(rad_angles), precision_val),
        "Cosine Ratio Vector (cos)": np.round(np.cos(rad_angles), precision_val),
        "Tangent Ratio Vector (tan)": [f"±∞" if np.isclose(np.abs(np.cos(r)), 0.0, atol=1e-10) else str(np.round(np.tan(r), precision_val)) for r in rad_angles]
    }
    
    df_trig = pd.DataFrame(trig_data)
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.dataframe(df_trig, use_container_width=True, height=400)
    st.download_button("Download Compiled Trigonometric Reference Table Array Block", df_trig.to_csv(index=False), "trig_matrix_export.csv")
    st.markdown("</div>", unsafe_allow_html=True)

# --- SPATIAL SOLID DIMENSIONS ---
elif page == "💎 Spatial Solid Dimensions":
    st.markdown("<div class='metric-card'><h2>💎 Spatial Geometric Volumetric Matrix Core</h2><p style='color:#94A3B8;'>Analyze parameters, total surface spatial areas, and displacement boundaries for three-dimensional geometries.</p></div>", unsafe_allow_html=True)
    
    solid_type = st.selectbox("Select Target Solid Object Vector Configuration:", ["Sphere Form Solid", "Right Circular Cone Structure", "Ellipsoidal Core Space"])
    
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    if solid_type == "Sphere Form Solid":
        sphere_r = st.number_input("Sphere Radius Vector length ($r$)", min_value=0.01, value=6.0)
        vol_sph = (4/3) * np.pi * (sphere_r**3)
        area_sph = 4 * np.pi * (sphere_r**2)
        
        c_v1, c_v2 = st.columns(2)
        c_v1.metric("Enclosed Volumetric Space Displacement ($V$)", f"{vol_sph:.5f}")
        c_v2.metric("Boundary Total Surface Area Enclosure ($A$)", f"{area_sph:.5f}")
        
    elif solid_type == "Right Circular Cone Structure":
        cone_r = st.number_input("Base Base Aperture Radius ($r$)", min_value=0.01, value=4.0)
        cone_h = st.number_input("Vertical Altitude Vector Height Dimension ($h$)", min_value=0.01, value=9.0)
        slant_s = np.sqrt(cone_r**2 + cone_h**2)
        vol_cone = (1/3) * np.pi * (cone_r**2) * cone_h
        area_cone = np.pi * cone_r * (cone_r + slant_s)
        
        c_v1, c_v2 = st.columns(2)
        c_v1.metric("Computed Enclosed Interior Volume", f"{vol_cone:.5f}")
        c_v2.metric("Computed Boundary Exterior Surface Area", f"{area_cone:.5f}")
        
    elif solid_type == "Ellipsoidal Core Space":
        semi_a = st.number_input("Semi-Principal Axis Vector Dimension (X Axis - $a$)", min_value=0.01, value=5.0)
        semi_b = st.number_input("Semi-Principal Axis Vector Dimension (Y Axis - $b$)", min_value=0.01, value=4.0)
        semi_c = st.number_input("Semi-Principal Axis Vector Dimension (Z Axis - $c$)", min_value=0.01, value=6.0)
        vol_ellip = (4/3) * np.pi * semi_a * semi_b * semi_c
        st.metric("Total Ellipsoidal Core Volume Enclosure", f"{vol_ellip:.5f}")
    st.markdown("</div>", unsafe_allow_html=True)

# --- FORMULA LIBRARY ---
elif page == "📚 Formula Reference Matrix":
    st.markdown("<div class='metric-card'><h2>📚 Reference Manual Identity Formula Matrix</h2><p style='color:#94A3B8;'>Browse and bookmark rigorous algebraic, geometric, and calculus formulation profiles.</p></div>", unsafe_allow_html=True)
    
    search_q = st.text_input("🔍 Filter formulas and identities via custom domain keywords:").lower()
    
    for category, formulas in FORMULA_DB.items():
        with st.expander(f"📦 Category Domain Matrix: {category}", expanded=True):
            for name, formula in formulas.items():
                if search_q in name.lower() or search_q in category.lower():
                    st.markdown(f"""
                        <div class="dict-card">
                            <h4 style="color:#6366F1; margin:0 0 0.5rem 0;">{name}</h4>
                        </div>
                    """, unsafe_allow_html=True)
                    st.latex(formula.replace("$$", ""))
                    
                    fav_label = "⭐ Identity Bookmarked" if name in st.session_state.favorites else "☆ Add Marker"
                    if st.button(fav_label, key=f"f_lib_{name}"):
                        toggle_favorite(name)
                        st.rerun()

# --- LEXICON DICTIONARY ---
elif page == "📖 Lexicon Dictionary":
    st.markdown("<div class='metric-card'><h2>📖 Mathematical Terms Lexicon Dictionary</h2><p style='color:#94A3B8;'>Verified academic dictionary entries rendered alongside underlying formulas.</p></div>", unsafe_allow_html=True)
    
    search_d = st.text_input("🔍 Search terminology indexes, definitions, or equations:")
    
    found_any = False
    for term, data in DICT_DB.items():
        if search_d.lower() in term.lower() or search_d.lower() in data["def"].lower():
            found_any = True
            
            st.markdown(f"""
                <div class="dict-card">
                    <h3 style="color: #818CF8; margin: 0 0 0.5rem 0; font-size: 1.35rem;">{term}</h3>
                    <p style="color: #E2E8F0; font-size: 0.98rem; line-height: 1.6; margin-bottom: 1rem;">{data['def']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.latex(data["formula"].replace("$$", ""))
            
            fav_label = "⭐ Flagged inside Sidebar Stack" if term in st.session_state.favorites else "☆ Flag Definition Matrix"
            if st.button(fav_label, key=f"lex_fav_{term}"):
                toggle_favorite(term)
                st.rerun()
                
            st.markdown("<br>", unsafe_allow_html=True)
            
    if not found_any:
        st.info("No matching mathematical vocabulary entries discovered in local registry indexes.")

# --- VISUAL GRAPH MATRIX ---
elif page == "📈 Visual Graph Matrix":
    st.markdown("<div class='metric-card'><h2>📈 Interactive Vector Function Visualizer</h2><p style='color:#94A3B8;'>Plot two-dimensional wave trajectories across fine sample boundaries.</p></div>", unsafe_allow_html=True)
    
    col_g1, col_g2 = st.columns([1, 2])
    with col_g1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        func_str = st.text_input("Define Coordinate Curve f(x):", "x**2 - 5*x + 6")
        x_min = st.number_input("Grid Start Axis Range Min", value=-8.0)
        x_max = st.number_input("Grid End Axis Range Max", value=8.0)
        points = st.slider("Coordinate Variable Resolution Samples", 60, 1200, 300)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_g2:
        try:
            x_vals = np.linspace(x_min, x_max, points)
            x = sp.symbols('x')
            sym_func = sp.sympify(func_str)
            f_num = sp.lambdify(x, sym_func, "numpy")
            y_vals = f_num(x_vals)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name=f"f(x)", line=dict(color='#6366F1', width=3)))
            fig.update_layout(title=f"Plot Core Frame Output Matrix: {func_str}", template="plotly_dark", xaxis_title="Independent Axis X", yaxis_title="Dependent Axis Y")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Plot layout composition matrix generation failed: {e}")

# --- DATASET ANALYTICAL CORE ---
elif page == "📊 Dataset Analytical Core":
    st.markdown("<div class='metric-card'><h2>📊 Continuous Dataset Statistical Analytics Core</h2><p style='color:#94A3B8;'>Evaluate dispersion trends, averages, deviations, and standard variance parameters.</p></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    data_input = st.text_area("Input Real Values Sample Vector Dataset (Separate via comma formatting breaks):", "14, 18, 14, 22, 26, 18, 16, 21, 24")
    
    if data_input:
        try:
            arr = np.array([float(x.strip()) for x in data_input.split(",") if x.strip()])
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.metric("Calculated Arithmetic Mean Distribution (μ)", f"{np.mean(arr):.4f}")
                st.metric("Calculated Median Center Position Value", f"{np.median(arr):.4f}")
            with col_s2:
                st.metric("Calculated Unbiased Sample Variance (σ²)", f"{np.var(arr, ddof=1):.4f}")
                st.metric("Calculated Standard Deviation Deviation (σ)", f"{np.std(arr, ddof=1):.4f}")
        except Exception as e:
            st.error(f"Dataset numerical evaluation breakdown fault event: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# --- MATRIX CALCULATOR ---
elif page == "🔢 Matrix Vector Solver":
    st.markdown("<div class='metric-card'><h2>🔢 Linear Algebra Array Matrix Vector Solver</h2><p style='color:#94A3B8;'>Map square 2x2 vector transformations, calculate determinants, and extract configuration matrix inversions.</p></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.caption("Construct Coefficients for Array Matrix A Structure Workspace Matrix Layer:")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        a11 = st.number_input("Row index 1, Col index 1 Element [1,1]", value=2.0)
        a21 = st.number_input("Row index 2, Col index 1 Element [2,1]", value=1.0)
    with col_m2:
        a12 = st.number_input("Row index 1, Col index 2 Element [1,2]", value=3.0)
        a22 = st.number_input("Row index 2, Col index 2 Element [2,2]", value=4.0)
        
    mat_A = np.array([[a11, a12], [a21, a22]])
    
    st.markdown("---")
    st.subheader("Calculated Matrix Operations Matrix Summary")
    det = np.linalg.det(mat_A)
    st.metric("Extracted Transform Matrix Determinant Factor Value", f"{det:.4f}")
    
    c_mr1, c_mr2 = st.columns(2)
    with c_mr1:
        st.write("Current Input Matrix Configuration A State:")
        st.code(str(mat_A))
    with c_mr2:
        if not np.isclose(det, 0.0):
            st.write("Computed Inverse Transform Array Matrix Workspace ($A^{-1}$):")
            st.code(str(np.linalg.inv(mat_A)))
        else:
            st.warning("Determinant evaluates to zero value. System cannot execute array matrix inversion sequence operations.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- METRIC CONVERTER ---
elif page == "🔄 Metric Transformation Shield":
    st.markdown("<div class='metric-card'><h2>🔄 Multi-Dimensional Metric Conversion Matrix Core</h2><p style='color:#94A3B8;'>Calculate standard displacement variables and weight scale variables instantly.</p></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    conv_type = st.selectbox("Identify Spatial System Dimension Type Category:", ["Linear Length Bounds", "Mass Weight Boundaries"])
    
    if conv_type == "Linear Length Bounds":
        val = st.number_input("Input Dimension Scalar Value To Convert", value=5.0)
        unit_from = st.selectbox("Baseline Metric Origin Unit:", ["Meters Scale", "Kilometers Scale", "Miles Vector Unit"])
        unit_to = st.selectbox("Objective Metric Target Transform Unit Location:", ["Meters Scale", "Kilometers Scale", "Miles Vector Unit"])
        
        factors = {"Meters Scale": 1.0, "Kilometers Scale": 1000.0, "Miles Vector Unit": 1609.344}
        base_val = val * factors[unit_from]
        target_val = base_val / factors[unit_to]
        
        st.markdown("---")
        st.metric("Resolved Metric Equivalent Output Transformation Vector:", f"{target_val:.5f} {unit_to}")
    else:
        st.write("(Mass weighting scales run symmetrically along proportional calculation frameworks.)")
    st.markdown("</div>", unsafe_allow_html=True)

# --- PRACTICE ZONE ---
elif page == "🎯 Operational Practice Arena":
    st.markdown("<div class='metric-card'><h2>🎯 Interactive Core Evaluation Training Arena</h2><p style='color:#94A3B8;'>Maintain calculations competence index stats through verified numerical testing.</p></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    if st.button("Generate Dynamic Training Matrix Matrix Core Question Variant") or st.session_state.quiz_current is None:
        val1 = random.randint(4, 14)
        val2 = random.randint(3, 13)
        ans = val1 * val2
        options = [ans, ans + random.randint(2, 6), ans - random.randint(2, 6), random.randint(20, 180)]
        random.shuffle(options)
        st.session_state.quiz_current = {"question": f"Determine product result matrix matching: {val1} \\times {val2}", "options": options, "answer": ans}
        
    st.markdown("##### Assessment Target Focus Challenge Element:")
    st.latex(st.session_state.quiz_current['question'])
    
    user_choice = st.radio("Identify proper numerical evaluation solution verification sequence configuration options:", st.session_state.quiz_current['options'])
    
    if st.button("Submit Verification Answer Vector Array Matrix", type="primary"):
        st.session_state.quiz_score['total'] += 1
        if user_choice == st.session_state.quiz_current['answer']:
            st.success("Correct numerical operational response. Mathematical validation check verification successfully confirmed.")
            st.session_state.quiz_score['correct'] += 1
        else:
            st.error(f"Operational breakdown calculation variation anomaly. Expected objective matching value state was: {st.session_state.quiz_current['answer']}")
            
    st.markdown("---")
    st.caption(f"Score Record Tracking Core Dashboard Accumulator Matrix Metrics: {st.session_state.quiz_score['correct']} / {st.session_state.quiz_score['total']} solutions verified.")
    st.markdown("</div>", unsafe_allow_html=True)