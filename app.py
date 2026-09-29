import os

import streamlit as st
from dotenv import load_dotenv

from Agent01 import TEST_TYPES, generate_qa_test_cases


load_dotenv()
st.set_page_config(page_title="QA Case Generator", page_icon="🧪", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap');

    :root {
        --ink: #172522;
        --muted: #65736e;
        --paper: #f3f5f0;
        --line: #d8dfd7;
        --green: #1f5a49;
        --lime: #cce66d;
        --orange: #e8774b;
    }

    [data-testid="stAppViewContainer"] { background: var(--paper); color: var(--ink); }
    [data-testid="stHeader"] { background: transparent; }
    .block-container { max-width: 1120px; padding-top: 3.2rem; padding-bottom: 4rem; }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    h1, h2, h3 { color: var(--ink); letter-spacing: 0; }
    h1 { font-size: 2.7rem; line-height: 1.08; font-weight: 700; margin-bottom: .4rem; }
    .eyebrow {
        color: var(--green); font: 600 .76rem 'IBM Plex Mono', monospace;
        letter-spacing: 0; text-transform: uppercase; margin-bottom: .75rem;
    }
    .intro { color: var(--muted); font-size: 1.02rem; margin-bottom: 1.8rem; }
    [data-testid="stForm"] {
        background: #fff; border: 1px solid var(--line); border-radius: 6px;
        padding: 1.4rem 1.5rem 1.2rem;
    }
    [data-testid="stTextArea"] textarea, [data-testid="stSelectbox"] [role="combobox"],
    [data-testid="stNumberInput"] input {
        background: #fbfcf9; border-color: var(--line); border-radius: 4px;
    }
    [data-testid="stTextArea"] textarea { min-height: 210px; }
    [data-testid="stFormSubmitButton"] button {
        color: var(--ink); background: var(--lime); border: 0; border-radius: 4px;
        font-weight: 700; min-height: 2.8rem;
    }
    [data-testid="stFormSubmitButton"] button:hover { background: #bbdc52; color: var(--ink); }
    [data-testid="stDownloadButton"] button {
        border-color: var(--green); color: var(--green); border-radius: 4px;
    }
    [data-testid="stMarkdownContainer"] hr { border-color: var(--line); }
    [data-testid="stSpinner"] p { color: var(--green); }
    @media (max-width: 640px) {
        .block-container { padding: 1.5rem 1rem 2.5rem; }
        h1 { font-size: 2rem; }
        [data-testid="stForm"] { padding: 1rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_api_key() -> str | None:
    environment_key = os.getenv("OPENAI_API_KEY")
    if environment_key:
        return environment_key

    try:
        secret_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        return None
    return str(secret_key) if secret_key else None


st.markdown('<div class="eyebrow">QA / TEST DESIGN</div>', unsafe_allow_html=True)
st.title("Test Case Generator")
st.markdown(
    '<p class="intro">Turn a product requirement into a focused, executable QA suite.</p>',
    unsafe_allow_html=True,
)

with st.form("test_case_request"):
    requirement = st.text_area(
        "Requirement",
        placeholder="Describe the feature, user behavior, and acceptance criteria...",
        help="Include observable outcomes and any constraints that should shape the tests.",
    )
    settings_left, settings_right = st.columns([1, 1])
    with settings_left:
        test_type = st.selectbox("Test type", TEST_TYPES)
    with settings_right:
        number_of_cases = st.number_input(
            "Number of test cases", min_value=1, max_value=50, value=8, step=1
        )
    submitted = st.form_submit_button(
        "Generate test cases", type="primary", use_container_width=True
    )

if submitted:
    if not requirement.strip():
        st.error("Enter a requirement to generate test cases.")
    else:
        api_key = get_api_key()
        if not api_key:
            st.error(
                "OpenAI API key not found. Set OPENAI_API_KEY in your local .env "
                "file or in the app's Streamlit secrets."
            )
        else:
            try:
                with st.spinner("Analyzing the requirement and drafting test cases..."):
                    st.session_state["generated_cases"] = generate_qa_test_cases(
                        requirement=requirement.strip(),
                        test_type=test_type,
                        number_of_cases=int(number_of_cases),
                        api_key=api_key,
                    )
                    st.session_state["result_type"] = test_type
                    st.session_state["result_count"] = int(number_of_cases)
            except Exception as error:
                st.error(f"Generation failed: {error}")

if st.session_state.get("generated_cases"):
    st.divider()
    result_title, download_column = st.columns([4, 1])
    with result_title:
        st.markdown(
            f'<div class="eyebrow">{st.session_state["result_type"]} · '
            f'{st.session_state["result_count"]} CASES</div>',
            unsafe_allow_html=True,
        )
        st.subheader("Generated test cases")
    with download_column:
        st.download_button(
            "Download Markdown",
            data=st.session_state["generated_cases"],
            file_name="qa_test_cases.md",
            mime="text/markdown",
            use_container_width=True,
        )
    st.markdown(st.session_state["generated_cases"])
