
import streamlit as st
import google.generativeai as genai
import time
from PIL import Image

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Question Solver",
    page_icon="😎",
    layout="centered"
)

# --- Initialize Session State ---
if "history" not in st.session_state:
    st.session_state["history"] = []

if "current_solution" not in st.session_state:
    st.session_state["current_solution"] = ""

# --- Sidebar ---
with st.sidebar:
    st.image(
        "https://cdn-icons-png.flaticon.com/512/4712/4712035.png",
        width=80
    )

    st.title("Settings & History")

    # Load API key securely
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
    except Exception:
        st.error(
            "API Key not found! Check "
            ".streamlit/secrets.toml"
        )
        st.stop()

    st.subheader("🎨 Response Customization")

    response_style = st.selectbox(
        "Choose explanation style:",
        [
            "Detailed Step-by-Step",
            "Short & Concise",
            "Exam Cheat Sheet Style"
        ]
    )

    st.markdown("---")
    st.subheader("📜 History Log")

    if not st.session_state["history"]:
        st.caption("No history yet. Start solving!")

    else:
        for idx, item in enumerate(
            st.session_state["history"]
        ):
            question = item["question"]
            short_title = (
                question[:25] + "..."
                if len(question) > 25
                else question
            )

            style = item.get("style", "Standard")

            if st.button(
                f"📄 [{style}] {short_title}",
                key=f"hist_{idx}",
                use_container_width=True
            ):
                st.session_state["current_solution"] = (
                    item["solution"]
                )

        st.markdown("---")

        if st.button(
            "🗑️ Clear History",
            use_container_width=True
        ):
            st.session_state["history"] = []
            st.session_state["current_solution"] = ""
            st.rerun()

    st.markdown("---")
    st.caption("Powered by Gemini 2.5 Flash ⚡")

# --- Helper: Response Style ---
def get_style_prompt(style):
    if style == "Detailed Step-by-Step":
        return (
            "Explain in simple language with detailed "
            "step-by-step reasoning and examples."
        )

    elif style == "Short & Concise":
        return (
            "Give a short, clear, direct answer in "
            "simple language."
        )

    return (
        "Format the answer like exam revision notes. "
        "Include definitions, key points, formulas "
        "and examples wherever relevant."
    )


# --- Main Page ---
st.title("🤖 AI Question Solver")

st.markdown(
    "Solve text questions and understand images "
    "with the help of AI."
)

st.markdown("---")

# --- Text Input ---
st.subheader("📝 Ask a Question")

user_input = st.text_area(
    "Type your question or instructions:",
    height=130,
    placeholder=(
        "Example: Explain this question in simple "
        "language..."
    )
)

# --- Image Upload ---
st.markdown("---")
st.subheader("🖼️ Upload an Image")

uploaded_image = st.file_uploader(
    "Choose an image from your device",
    type=["png", "jpg", "jpeg", "webp"],
    help="Upload a photo, question paper, diagram or object."
)

if uploaded_image is not None:
    try:
        image = Image.open(uploaded_image)
        st.image(
            image,
            caption="Your Uploaded Image",
            use_container_width=True
        )
    except Exception:
        st.error("Unable to open this image.")
        uploaded_image = None

st.caption(
    "Tip: You can upload an image and leave the "
    "question box empty to get a general explanation."
)

# --- Solve Text Questions ---
if st.button(
    "🚀 Solve Text Question",
    use_container_width=True
):
    if not user_input.strip():
        st.warning("Please type a question first.")

    else:
        try:
            model = genai.GenerativeModel(
                "gemini-2.5-flash"
            )

            prompt = (
                f"{get_style_prompt(response_style)}\n\n"
                "Solve the following question:\n\n"
                f"{user_input}"
            )

            with st.spinner("🤖 Solving your question..."):
                response = model.generate_content(prompt)

            if not response.text:
                st.error("AI returned an empty response.")
            else:
                solution = response.text

                st.session_state["current_solution"] = solution

                st.session_state["history"].append({
                    "question": user_input.strip(),
                    "solution": solution,
                    "style": response_style
                })

                st.success("✅ Question solved!")
                st.rerun()

        except Exception as e:
            st.error(f"Error: {e}")


# --- Analyze Image ---
if st.button(
    "🔍 Analyze Image",
    use_container_width=True
):
    if uploaded_image is None:
        st.warning("Please upload an image first.")

    else:
        try:
            image = Image.open(uploaded_image).convert("RGB")

            instructions = get_style_prompt(response_style)

            question = user_input.strip()

            if question:
                image_prompt = (
                    f"{instructions}\n\n"
                    "Carefully analyze the uploaded image. "
                    "Answer the user's question using the "
                    "visible information. If it contains "
                    "a written question, explain and solve it. "
                    "If some text is unclear, say so instead "
                    "of guessing.\n\n"
                    f"User's question: {question}"
                )
            else:
                image_prompt = (
                    f"{instructions}\n\n"
                    "Describe the uploaded image in simple "
                    "language. Explain the main objects, "
                    "visible text, diagrams or important "
                    "details. Do not guess information that "
                    "cannot be determined from the image."
                )

            model = genai.GenerativeModel(
                "gemini-2.5-flash"
            )

            with st.spinner(
                "👀 AI is looking at your image..."
            ):
                response = model.generate_content(
                    [image_prompt, image]
                )

                time.sleep(0.3)

            if not response.text:
                st.error("AI returned an empty response.")
            else:
                solution = response.text

                history_question = (
                    f"🖼️ Image: {question}"
                    if question
                    else "🖼️ Image explanation"
                )

                st.session_state["current_solution"] = solution

                st.session_state["history"].append({
                    "question": history_question,
                    "solution": solution,
                    "style": response_style
                })

                st.success("✅ Image analyzed successfully!")
                st.balloons()
                st.rerun()

        except Exception as e:
            st.error(f"Image analysis failed: {e}")


# --- Display Answer & Download ---
if st.session_state["current_solution"]:
    st.markdown("---")
    st.subheader("💡 AI Answer")

    with st.container(border=True):
        st.markdown(
            st.session_state["current_solution"]
        )

    st.download_button(
        label="📥 Download Answer (.md)",
        data=st.session_state["current_solution"],
        file_name="ai_answer.md",
        mime="text/markdown",
        use_container_width=True
    )