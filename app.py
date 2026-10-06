import streamlit as st
import base64
import os
from PIL import Image
from llm_backend import ask_llm_intent, build_response, detect_query_language

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

# Try to load custom favicon, fallback to Saudi flag emoji
try:
    page_icon = Image.open("icon.png")
except FileNotFoundError:
    page_icon = "🇸🇦"

st.set_page_config(
    page_title="Saudi Gov Services Navigator",
    page_icon=page_icon,
    layout="centered",
)

# ============================================================================
# COLOR THEME (Saudi Government Colors)
# ============================================================================

MAIN_BG = "#F8F6EF"       
INPUT_BG = "#E4DECF"      
ABS_GREEN = "#006C35"    
LIGHT_GREEN = "#B9D7C4"   
TEXT_COLOR = "#006C35"    
GRAY_TEXT = "#5a8a6a"    

# ============================================================================
# SESSION STATE
# ============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_background_css():
    """Load background image and return CSS if file exists."""
    for ext in ["png", "jpg", "jpeg"]:
        path = f"background.{ext}"
        if os.path.exists(path):
            with open(path, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            return f"""
                <style>
                .stApp {{
                    background-image: url('data:image/{ext};base64,{data}') !important;
                    background-size: cover !important;
                    background-position: center !important;
                    background-attachment: fixed !important;
                }}
                </style>
            """
    return ""

def make_css(is_ar):
    """Generate all CSS styles based on language direction (RTL/LTR)."""
    direction = "rtl" if is_ar else "ltr"
    text_align = "right" if is_ar else "left"
    
    return f"""
    <style>
    /* Font Import */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    * {{ font-family: 'Cairo', sans-serif !important; }}
    .stApp {{ background-color: {MAIN_BG} !important; }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    
    /* Layout Container */
    .block-container {{
        max-width: 900px !important;
        padding-top: 2rem !important;
        padding-bottom: 100px !important;
    }}
    
    /* User Message Bubble */
    .user-message {{
        background-color: {INPUT_BG};
        color: {TEXT_COLOR};
        padding: 1rem 1.5rem;
        border-radius: 20px;
        margin-left: auto;
        max-width: 80%;
        direction: {direction};
        text-align: {text_align};
        border: 1px solid {LIGHT_GREEN};
    }}
    
    /* AI Response Bubble */
    .ai-message {{
        background-color: white;
        color: {TEXT_COLOR};
        padding: 1.2rem 1.5rem;
        border-radius: 15px;
        border: 1px solid {LIGHT_GREEN};
        margin: 0.5rem 0;
        direction: {direction};
        text-align: {text_align};
    }}
    
    .ai-message h3 {{ color: {ABS_GREEN} !important; font-size: 1.3rem; }}
    .ai-message .label {{ color: {GRAY_TEXT} !important; font-size: 0.9rem; }}
    .ai-message .step {{
        background-color: {INPUT_BG};
        padding: 0.8rem 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 3px solid {ABS_GREEN};
    }}
    .ai-message a {{ color: {ABS_GREEN} !important; }}
    
    /* Welcome Screen */
    .welcome-container {{
        text-align: center;
        padding: 1rem 1rem;
        margin-top: 6rem;
        color: {TEXT_COLOR};
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }}
    
    .welcome-title {{
        font-size: 2rem;
        font-weight: 600;
        color: {ABS_GREEN};
        margin-bottom: 0.5rem;
        text-align: center;
        width: 100%;
    }}
    
    .welcome-subtitle {{
        color: {GRAY_TEXT};
        font-size: 1rem;
        max-width: 600px;
        margin: 0 auto;
        text-align: center;
        width: 100%;
    }}
    
    /* Text Input Field */
    .stTextInput,
    .stTextInput > div,
    .stTextInput > div > div,
    [data-testid="stTextInput"],
    [data-testid="stTextInput"] > div,
    [data-testid="stTextInput"] > div > div {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        border-radius: 999px !important;
    }}
    
    .stTextInput input,
    [data-testid="stTextInput"] input {{
        background-color: {INPUT_BG} !important;
        color: {TEXT_COLOR} !important;
        border: none !important;
        border-radius: 999px !important;
        padding: 1.1rem 1.8rem !important;
        font-size: 1.05rem !important;
        direction: {direction} !important;
        text-align: {text_align} !important;
        box-shadow: none !important;
        outline: none !important;
    }}
    
    .stTextInput input::placeholder,
    [data-testid="stTextInput"] input::placeholder {{
        color: {GRAY_TEXT} !important;
        font-weight: 400 !important;
    }}
    
    .stTextInput input:hover,
    .stTextInput input:focus,
    [data-testid="stTextInput"] input:hover,
    [data-testid="stTextInput"] input:focus {{
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }}
    
    [data-baseweb="input"]::before,
    [data-baseweb="input"]::after {{
        display: none !important;
    }}
    
    /* Form Container */
    [data-testid="stForm"] {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin-top: 16rem !important;
    }}
    
    [data-testid="stForm"] > div {{
        padding: 0 !important;
    }}
    
    [data-testid="stForm"] [data-testid="InputInstructions"] {{
        display: none !important;
    }}
    
    /* Submit Button */
    [data-testid="stFormSubmitButton"] > button {{
        background: linear-gradient(135deg, {ABS_GREEN} 0%, #008542 100%) !important;
        color: white !important;
        border-radius: 50% !important;
        border: none !important;
        width: 52px !important;
        height: 52px !important;
        min-width: 52px !important;
        min-height: 52px !important;
        font-size: 1.3rem !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 108, 53, 0.3) !important;
    }}
    
    [data-testid="stFormSubmitButton"] > button:hover {{
        background: linear-gradient(135deg, #008542 0%, #006C35 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 108, 53, 0.4) !important;
    }}
    
    /* Language Selector */
    [data-testid="stSelectbox"] > div > div {{
        background-color: {INPUT_BG} !important;
        color: {TEXT_COLOR} !important;
        border: 1px solid {LIGHT_GREEN} !important;
        border-radius: 20px !important;
        min-width: 100px !important;
    }}
    
    [data-testid="stSelectbox"] span {{
        color: {TEXT_COLOR} !important;
    }}
    
    [data-testid="stSelectbox"] svg {{
        fill: {TEXT_COLOR} !important;
    }}
    
    /* Dropdown Menu */
    [data-baseweb="popover"] {{
        background-color: {INPUT_BG} !important;
        border-radius: 12px !important;
        border: 1px solid {LIGHT_GREEN} !important;
    }}
    
    [data-baseweb="popover"] > div {{
        background-color: {INPUT_BG} !important;
    }}
    
    [data-baseweb="menu"] {{
        background-color: {INPUT_BG} !important;
    }}
    
    [data-baseweb="menu"] ul {{
        background-color: {INPUT_BG} !important;
    }}
    
    [data-baseweb="menu"] li {{
        background-color: {INPUT_BG} !important;
        color: {TEXT_COLOR} !important;
    }}
    
    [data-baseweb="menu"] li:hover {{
        background-color: #d4cfc0 !important;
    }}
    
    [role="listbox"] {{
        background-color: {INPUT_BG} !important;
    }}
    
    [role="option"] {{
        background-color: {INPUT_BG} !important;
        color: {TEXT_COLOR} !important;
    }}
    
    [role="option"]:hover {{
        background-color: #d4cfc0 !important;
    }}
    
    /* Loading Spinner */
    .stSpinner > div {{
        border-color: #b8a4e2 transparent transparent transparent !important;
    }}
    
    .stSpinner > div > div {{
        color: #b8a4e2 !important;
    }}
    
    /* Alert Messages */
    .stAlert {{
        background-color: {INPUT_BG} !important;
        color: {TEXT_COLOR} !important;
        border: 1px solid {LIGHT_GREEN} !important;
        border-radius: 12px !important;
    }}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {MAIN_BG};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {LIGHT_GREEN};
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {ABS_GREEN};
    }}
    </style>
    """

def render_ai_response(msg_data, use_ar):
    """
    Generate HTML for AI response display.
    
    Handles:
    - Conversational responses (greetings, clarifications)
    - Single service display
    - Multiple services display
    """
    lang = "ar" if use_ar else "en"
    direction = "rtl" if use_ar else "ltr"
    text_align = "right" if use_ar else "left"
    
    # Handle conversational responses (greetings, clarifications)
    if msg_data.get("custom_message") and not msg_data.get("service_key") and not msg_data.get("service_keys"):
        return f"""
            <div class="ai-message" style="direction:{direction}; text-align:{text_align};">
                <p style="font-size:1.1rem; line-height:1.8;">{msg_data['custom_message']}</p>
            </div>
        """
    
    # Handle no service match
    if not msg_data.get("service_key") and not msg_data.get("service_keys"):
        msg = "لم أجد خدمة مطابقة." if use_ar else "No matching service found."
        return f'<div class="ai-message" style="direction:{direction};"><p>{msg}</p></div>'
    
    # Labels in Arabic/English
    labels = {
        "ar": ("المنصة", "الفئة", "الخطوات", "المتطلبات", "الرابط"),
        "en": ("Platform", "Category", "Steps", "Requirements", "Link")
    }
    platform_l, category_l, steps_l, req_l, link_l = labels[lang]
    
    # Handle SINGLE or MULTIPLE services
    service_keys_to_render = msg_data.get("service_keys") or ([msg_data["service_key"]] if msg_data.get("service_key") else [])
    
    if not service_keys_to_render:
        msg = "لم أجد خدمة مطابقة." if use_ar else "No matching service found."
        return f'<div class="ai-message" style="direction:{direction};"><p>{msg}</p></div>'

    html = f'<div class="ai-message" style="direction:{direction}; text-align:{text_align};">'
    
    for i, svc_key in enumerate(service_keys_to_render):
        data = build_response(svc_key, lang)
        steps_html = "".join(f'<div class="step">{j}. {s}</div>' for j, s in enumerate(data["steps"], 1))
        reqs_html = "".join(f'<div>• {r}</div>' for r in data["requirements"])
        link_html = f'<p><span class="label">{link_l}:</span> <a href="{data["official_link"]}" target="_blank">{data["official_link"]}</a></p>' if data["official_link"] else ""
        
        # Add separator between services
        if i > 0:
            html += '<hr style="margin: 2rem 0; border-color: #ddd;">'
        
        html += f'''
            <h3>{data['title']}</h3>
            <p><span class="label">{platform_l}:</span> {data['platform']} | <span class="label">{category_l}:</span> {data['category']}</p>
            <p>{data['description']}</p>
            <p style="margin-top:1rem;"><strong>{steps_l}:</strong></p>
            {steps_html}
            <p style="margin-top:1rem;"><strong>{req_l}:</strong></p>
            {reqs_html}
            {link_html}
        '''
    
    html += '</div>'
    return html

# ============================================================================
# USER INTERFACE
# ============================================================================

# Language Selector
col_lang, col_spacer = st.columns([1, 5])
with col_lang:
    ui_lang = st.selectbox(
        "",
        options=[("ar", "العربية"), ("en", "English")],
        format_func=lambda x: x[1],
        label_visibility="collapsed"
    )[0]

is_ar = ui_lang == "ar"

# Apply CSS Styles
st.markdown(make_css(is_ar), unsafe_allow_html=True)

# Apply background image if exists
bg_css = get_background_css()
if bg_css:
    st.markdown(bg_css, unsafe_allow_html=True)

# Logo Display
try:
    logo = Image.open("logo.png")
    cols = st.columns([1.5, 1, 1.5] if st.session_state.messages else [1, 2, 1])
    with cols[1]:
        st.image(logo, use_container_width=True)
except FileNotFoundError:
    pass

# Welcome Message (shown when no chat history)
if not st.session_state.messages:
    title = "كيف يمكنني مساعدتك؟" if is_ar else "How can I help you today?"
    subtitle = "اسألني عن أي خدمة حكومية سعودية" if is_ar else "Ask me about any Saudi government service"
    st.markdown(
        f'<div class="welcome-container">'
        f'<h1 class="welcome-title">{title}</h1>'
        f'<p class="welcome-subtitle">{subtitle}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

# Chat History Display
for msg in st.session_state.messages:
    if msg["role"] == "user":
        # User message - align based on message language
        msg_ar = msg.get("msg_is_ar", is_ar)
        d, a = ("rtl", "right") if msg_ar else ("ltr", "left")
        st.markdown(
            f'<div class="user-message" style="direction:{d}; text-align:{a};">{msg["content"]}</div>',
            unsafe_allow_html=True
        )
    else:
        # AI response
        st.markdown(
            render_ai_response(msg, msg.get("response_is_ar", is_ar)),
            unsafe_allow_html=True
        )

# Input Form
placeholder = "مثال: أريد أن أجدد رخصة القيادة..." if is_ar else "Example: I want to renew my driving license..."

with st.form("chat_form", clear_on_submit=True):
    col_input, col_btn = st.columns([9, 1])
    with col_input:
        user_input = st.text_input("", placeholder=placeholder, label_visibility="collapsed")
    with col_btn:
        submitted = st.form_submit_button("➤")

# ============================================================================
# QUERY PROCESSING
# ============================================================================

if submitted and user_input.strip():
    # Detect query language
    query_is_ar = detect_query_language(user_input) == "ar"
    
    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "msg_is_ar": query_is_ar
    })
    
    # Process with LLM
    with st.spinner("جاري البحث..." if is_ar else "Searching..."):
        result = ask_llm_intent(user_input)
    
    # Add AI response to history
    st.session_state.messages.append({
        "role": "assistant",
        "result_type": result["type"],
        "service_key": result.get("service_key"),
        "service_keys": result.get("service_keys"),
        "custom_message": result.get("message"),
        "response_is_ar": query_is_ar
    })
    
    # Refresh to show new messages
    st.rerun()
