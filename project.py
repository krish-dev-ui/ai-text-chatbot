import streamlit as st
import google.generativeai as genai
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Question Solver",
    page_icon="🤖",
    layout="centered"
)

# --- Initialize Session States ---
if "history" not in st.session_state:
    st.session_state["history"] = []  # Stores past queries: [{"question": "...", "solution": "..."}]

if "current_solution" not in st.session_state:
    st.session_state["current_solution"] = ""

# --- Sidebar Theme, Setup & Controls ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
    st.title("Settings & History")
    
    # Securely input API key 
    # api_key = st.text_input("Enter Gemini API Key:", type="password", placeholder="AIzaSy...")
    # st.markdown("---")
    # Securely input API key
    # api_key = st.text_input("Enter Gemini API Key:", type="password", placeholder="AIzaSy...")
    # st.markdown("---")
    
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
    except Exception:
        st.error("API Key not found! Please check your .streamlit/secrets.toml file.")
        st.stop()

    # NEW FEATURE: Response Style Controls
    # NEW FEATURE: Response Style Controls
    st.subheader("🎨 Response Customization")
    response_style = st.selectbox(
        "Choose explanation style:",
        ["Detailed Step-by-Step", "Short & Concise", "Exam Cheat Sheet Style"]
    )
    st.markdown("---")
    
    # History Log Section
    st.subheader("📜 History Log")
    if not st.session_state["history"]:
        st.caption("No history yet. Start solving questions!")
    # History Log Section
    st.subheader("📜 History Log")
    if not st.session_state["history"]:
        st.caption("No history yet. Start solving questions!")
    else:
        # Create a button for each past item in history
        for idx, item in enumerate(st.session_state["history"]):
            # Truncate title so it fits nicely in the sidebar
            short_title = item["question"][:25] + "..." if len(item["question"]) > 25 else item["question"]
            
            # SAFE FIX: Use .get() to prevent KeyError if old data exists
            style_label = item.get("style", "Standard")
            
            if st.button(f"📄 [{style_label}] {short_title}", key=f"hist_{idx}", use_container_width=True):
                # Restore this history item to the main window view
                st.session_state["current_solution"] = item["solution"]
        
        st.markdown("---")
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state["history"] = []
            st.session_state["current_solution"] = ""
            st.rerun()

    st.markdown("---")
    st.caption("Powered by Gemini 2.5 Flash ⚡")

# --- Main Page Layout ---
st.title("🤖 AI Text Question Solver")
st.markdown("---")

# Text area for user questions
user_input = st.text_area(
    "Paste your question paper or type your questions below:", 
    height=200, 
    placeholder="Type or paste your text here..."
)

# Solve Button
if st.button("🚀 Solve Questions", use_container_width=True):
    if not api_key:
        st.error("🔑 Please enter your Gemini API Key in the sidebar first!")
    elif user_input.strip() == "":
        st.warning("✏️ Please enter some text before clicking the button!")
    else:
        try:
            # Configure API key from sidebar input
            genai.configure(api_key=api_key)
            
            # Dynamically adjust the system prompt instruction based on style selection
            style_prompt = ""
            if response_style == "Detailed Step-by-Step":
                style_prompt = "Provide highly detailed, step-by-step solutions with comprehensive explanations for every sub-point."
            elif response_style == "Short & Concise":
                style_prompt = "Provide crisp, straight-to-the-point answers. Avoid fluff and keep explanations short."
            elif response_style == "Exam Cheat Sheet Style":
                style_prompt = "Provide key definitions, formula callouts, core bullet points, and highlighted solutions ideal for quick study revision."

            # Animation 1: Loading spinner
            with st.spinner(f"🤖 Thinking... Generating {response_style} solutions..."):
                model = genai.GenerativeModel("gemini-2.5-flash")
                
                # Combine instructions with user input
                prompt = f"System Instructions: {style_prompt}\n\nPlease solve this question paper:\n\n{user_input}"
                response = model.generate_content(prompt)
                
                time.sleep(0.5) 
            
            # Animation 2: Success balloons burst
            st.balloons()
            
            # Update Current Solution
            st.session_state["current_solution"] = response.text
            
            # Append to History Log along with chosen style metadata
            st.session_state["history"].append({
                "question": user_input.strip(),
                "solution": response.text,
                "style": response_style
            })
            
            st.success(f"✨ AI Solutions ({response_style}) Generated Successfully!")
            st.rerun()  # Rerun to refresh the sidebar layout immediately
                
        except Exception as e:
            st.error(f"❌ An error occurred: {e}")

# --- Display Active Solutions & Export Feature ---
if st.session_state["current_solution"]:
    with st.container(border=True):
        st.markdown(st.session_state["current_solution"])
    
    st.markdown("---")
    st.subheader("📥 Export Solutions")
    
    # Export / Download Button
    st.download_button(
        label="📄 Download Selected Solutions (.md)",
        data=st.session_state["current_solution"],
        file_name="ai_solutions.md",
        mime="text/markdown",
        use_container_width=True
    )