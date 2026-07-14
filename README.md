# ◆ Prism 🔷 AI Text Summarizer

## 📌 What is this project?

Prism is a web application that takes long-form text — pasted directly or uploaded as a `.txt` file — and generates a concise AI-written summary. It's built with [Streamlit](https://streamlit.io/) for the interface and connects to Hugging Face's hosted inference API to run the summarization model, so no model weights are downloaded or run locally.

The name "Prism" reflects what the app does conceptually: it takes a large body of text and refracts it down into its essential signal, much like a prism splits light into its core components.

---

<img width="400" height="279" alt="Screen Recording 2026-07-14 104337" src="https://github.com/user-attachments/assets/66762af0-bdf7-4c34-971c-904b0eddaa07" />


## ⚙️ What does it do?

- **Paste or upload text** — type directly into the text box, or upload a `.txt` file and have its contents load automatically.
- **Generate an AI summary** — sends the text to Hugging Face's `facebook/bart-large-cnn` summarization model and displays the result.
- **Control summary length** — a slider lets you set the maximum length of the generated summary before running it.
- **View text analytics** — after summarizing, a dashboard shows the original word count, the summary word count, and how much the text was compressed, including a visual "retained volume" gauge.
- **Download the summary** — a button lets you save the generated summary as a clean `.txt` file (`ai_summary.txt`).

---

## 🧠 What I learned

Building Prism taught me how to connect a Streamlit app to an external AI model through an API, rather than running a model locally.

### 🔑 Connecting to Hugging Face's API
I learned how to authenticate requests using a Hugging Face access token. The token is stored securely using `st.secrets`, then attached to every request as an `Authorization` header using the standard "Bearer token" format:

```python
HF_TOKEN = st.secrets["HF_TOKEN"]
API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}
```

### 📡 Sending requests and controlling model behavior
I learned how to build a JSON payload to send to the model, including using `parameters` to control the `max_length` and `min_length` of the generated summary, and how to use the `requests` library to POST that payload to the Hugging Face API and parse the JSON response that comes back:

```python
payload = {
    "inputs": text_input,
    "parameters": {"max_length": max_len, "min_length": min_len},
}
response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=60)
response.raise_for_status()
result = response.json()
summary = result[0]["summary_text"]
```

### 🎨 Styling Streamlit with custom CSS and HTML
By default, Streamlit's widgets look fairly generic. I learned that `st.markdown()` can render raw HTML and CSS if you pass `unsafe_allow_html=True`, which let me define a custom color palette, typography, and layout using CSS variables, then apply it across the whole app — including overriding Streamlit's own built-in components like buttons and sliders.

```python
st.markdown("""
<style>
:root { --bg: #DDDCD8; --ink: #14191C; }
.distill-title { font-family: 'Fraunces', serif; color: var(--ink); }
</style>
""", unsafe_allow_html=True)
```

### 🤖 About the model
This project uses `facebook/bart-large-cnn`, a summarization model from Meta available on Hugging Face. According to its model card, BART is a transformer model that works especially well when fine-tuned for text generation tasks like summarization and translation, and this specific checkpoint was fine-tuned on the CNN/Daily Mail dataset, a large set of news articles paired with human-written summaries. You can read more on the [official model page](https://huggingface.co/facebook/bart-large-cnn).

I built and understood this project with the help of AI collaboration and Hugging Face's documentation, using it as a learning tool to understand how API-based AI integration, request/response handling, and custom UI styling work together in a real application.

---

## 💻 How to run this project

### 1. Clone the repository
```bash
git clone https://github.com/FreezerTheGod/Prism-AI-Text-Summarizer.git
cd Prism-AI-Text-Summarizer
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux
```

### 3. Install the dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your Hugging Face API token
Create a file at `.streamlit/secrets.toml` in the project root and add:
```toml
HF_TOKEN = "your_hugging_face_token_here"
```
You can generate a token from your [Hugging Face account settings](https://huggingface.co/settings/tokens). This file is listed in `.gitignore` and should never be committed to GitHub.

### 5. Run the app
```bash
streamlit run app.py
```
The app will open automatically in your browser at `http://localhost:8501`. 🎉
