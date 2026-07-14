import streamlit as st
import requests

# Setting up Hugging Face Token
HF_TOKEN = st.secrets["HF_TOKEN"]
# Setting up the API URL
API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"
# Setting up the headers for the API request
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

# --- Streamlit page configuration ---
st.set_page_config(page_title="Prism", page_icon="◆", layout="centered")

# --- Custom CSS for styling ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap');

:root {
    --bg: #DDDCD8;
    --card: #C2C1BC;
    --border: #A2A39F;
    --ink: #14191C;
    --ink-soft: #2D3436;
    --gray-mid: #4E5556;
    --gray-light: #6C7373;
    --khaki: #CECBBA;
    --khaki-deep: #A8A594;
}

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer { visibility: hidden; }

.distill-header { padding: 1.5rem 0 0.25rem 0; }
.distill-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--gray-mid);
    margin-bottom: 0.5rem;
}
.distill-title {
    font-family: 'Fraunces', serif;
    font-weight: 500;
    font-size: 2.7rem;
    line-height: 1.05;
    color: var(--ink);
    margin: 0 0 0.6rem 0;
}
.distill-sub {
    color: var(--gray-mid);
    font-size: 0.98rem;
    margin-bottom: 1.75rem;
    max-width: 34rem;
}

.distill-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--gray-light);
    margin: 1.6rem 0 0.5rem 0;
}

.distill-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.5rem 1.6rem;
    margin-top: 0.5rem;
}
.summary-text {
    font-family: 'Fraunces', serif;
    font-weight: 400;
    font-size: 1.15rem;
    line-height: 1.6;
    color: var(--ink);
}

.stButton > button, .stDownloadButton > button {
    background: var(--ink-soft);
    color: var(--bg);
    border: none;
    border-radius: 999px;
    font-weight: 500;
    font-family: 'Inter', sans-serif;
    padding: 0.55rem 1.5rem;
    transition: transform 0.1s ease, box-shadow 0.15s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    box-shadow: 0 4px 14px rgba(20,25,28,0.25);
    transform: translateY(-1px);
    color: var(--bg);
}

.stSlider [data-baseweb="slider"] div div div { background: var(--ink-soft) !important; }

[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace;
    color: var(--ink);
}
[data-testid="stMetricLabel"] {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--gray-light);
}

/* Signature element: the prism spectrum bar — text refracted into
   what's kept (khaki) vs what's filtered out (border-gray) */
.gauge-wrap { margin-top: 0.75rem; }
.gauge-track {
    width: 100%;
    height: 14px;
    background: var(--border);
    border-radius: 7px;
    overflow: hidden;
    position: relative;
}
.gauge-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--khaki-deep), var(--khaki));
    border-radius: 7px;
    transition: width 0.6s ease;
}
.gauge-caption {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: var(--gray-mid);
    margin-top: 0.5rem;
}
.gauge-caption b { color: var(--ink); }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="distill-header">
    <div class="distill-eyebrow">◆ Prism</div>
    <div class="distill-title">Prism</div>
    <div class="distill-sub">Paste a long article, or upload a .txt file, and refract it into
    its essential signal, powered by facebook/bart-large-cnn.</div>
</div>
""", unsafe_allow_html=True)

# --- Session state setup ---
# check text input if it exists in session state, otherwise initialize it
if "text_input" not in st.session_state:
    st.session_state.text_input = ""
# check summary if it exists in session state, otherwise initialize it    
if "summary" not in st.session_state:
    st.session_state.summary = ""
# check last_uploaded_name if it exists in session state, otherwise initialize it    
if "last_uploaded_name" not in st.session_state:
    st.session_state.last_uploaded_name = ""

# --- Feature 1: File upload support ---
st.markdown('<div class="distill-label">Source Material</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload a .txt file (optional)", type=["txt"], label_visibility="collapsed")

# Checking if a new file has been uploaded
if uploaded_file is not None:
    # Read the uploaded file only if it's different from the last uploaded file
    if st.session_state.get("last_uploaded_name") != uploaded_file.name:
        # Read the uploaded file and decode it to a string
        file_text = uploaded_file.read().decode("utf-8", errors="ignore")
        # Update the session state with the new text input and the name of the uploaded file
        st.session_state.text_input = file_text
        # Store the name of the uploaded file to avoid re-reading it on subsequent runs
        st.session_state.last_uploaded_name = uploaded_file.name

# --- Feature 2: Text input area ---
text_input = st.text_area(
    "Enter your long text here:",
    height=250,
    placeholder="Paste your article...",
    key="text_input",
    label_visibility="collapsed",
)

# --- Feature 3: Summary length slider and run button ---
# We use a slider to allow the user to select the maximum summary length, and we provide a caption to indicate the approximate word count of the summary.
st.markdown('<div class="distill-label">Refraction Strength</div>', unsafe_allow_html=True)
max_len = st.slider("Maximum Summary Length (words)", min_value=30, max_value=200, value=100, label_visibility="collapsed")
# We provide a caption to indicate the approximate word count of the summary.
st.caption(f"Summary will run up to ~{max_len} words")

# --- Feature 4: Run button and API call ---
# We check if the user has entered any text
if st.button("◆ Run Prism", use_container_width=False):
    # If the user has not entered any text, we display a warning message.
    if not text_input.strip():
        # If the user has not entered any text, we display a warning message.
        st.warning("Please enter some text to summarize.")
    else:
        # If the user has entered text, we proceed to call the Hugging Face API to summarize the text.
        with st.spinner("Refracting your text..."):
            try:
                min_len = max(5, int(max_len * 0.3))
                payload = {
                    "inputs": text_input,
                    "parameters": {"max_length": max_len, "min_length": min_len},
                }
                # We make a POST request to the Hugging Face API with the text input and the specified parameters for summary length.
                response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=60)
                response.raise_for_status()
                result = response.json()
                
                # We check if the result is a list and contains the key "summary_ text"
                if isinstance(result, list) and len(result) > 0 and "summary_text" in result[0]:
                    # We store the summary in the session state and display a success message.
                    st.session_state.summary = result[0]["summary_text"]
                    st.success("Done!")
                # We check if the result is a dictionary and contains the key "error"    
                elif isinstance(result, dict) and "error" in result:
                    st.error(f"Model error: {result['error']}")
                else:
                    # If the response format is unexpected, we display an error message with the result for debugging purposes.
                    st.error(f"Unexpected response format: {result}")
            except Exception as e:
                st.error(f"An error occurred: {e}")

# --- Feature 5: Displaying the summary and analytics ---
# We check if a summary has been generated and stored in the session state.
if st.session_state.summary:
    clean_summary = st.session_state.summary
     
     # We display the refracted result in a styled card.
    st.markdown('<div class="distill-label">Refracted Result</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="distill-card"><div class="summary-text">{clean_summary}</div></div>', unsafe_allow_html=True)
    
    # We calculate the word counts for the original text and the summary, as well as the percentage reduction and retention.
    original_word_count = len(text_input.split())
    summary_word_count = len(clean_summary.split())
    # We calculate the percentage reduction in word count and the percentage of the original text that was retained in the summary.
    reduction_pct = round((1 - summary_word_count / original_word_count) * 100, 1) if original_word_count > 0 else 0
    kept_pct = max(0, min(100, 100 - reduction_pct))
    
    # We display the analytics metrics in three columns: original word count, summary word count, and percentage reduction.
    st.markdown('<div class="distill-label">Analytics</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.metric("Original Words", original_word_count)
    col2.metric("Summary Words", summary_word_count)
    col3.metric("Reduced By", f"{reduction_pct}%")
    
    # We display a visual gauge to represent the percentage of the original text that was retained in the summary, using a styled div with a fill that corresponds to the kept percentage.
    st.markdown(f"""
    <div class="gauge-wrap">
        <div class="gauge-track"><div class="gauge-fill" style="width:{kept_pct}%;"></div></div>
        <div class="gauge-caption">Retained <b>{kept_pct}%</b> of original volume</div>
    </div>
    """, unsafe_allow_html=True)
    
    # We provide an option for the user to download the generated summary as a .txt file, using a download button that triggers the download of the summary text.
    st.markdown('<div class="distill-label">Export</div>', unsafe_allow_html=True)
    st.download_button(
        label="⬇ Download Summary as .txt",
        data=clean_summary,
        file_name="ai_summary.txt",
        mime="text/plain",
    )