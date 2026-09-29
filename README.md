# QA Test Case Generator

A Streamlit interface for the LangChain QA requirement analyzer and test case generator.

## Run locally

Use Python 3.12 or 3.13 for a compatible LangChain runtime. In PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create `.env` in the project root:

```dotenv
OPENAI_API_KEY=your_actual_api_key
OPENAI_MODEL=gpt-4o-mini
```

Start the app:

```powershell
streamlit run app.py
```

## Deploy to Streamlit Community Cloud

1. Push this project to a GitHub repository. `.env`, `.venv`, and Streamlit secrets are excluded by `.gitignore`.
2. In Streamlit Community Cloud, create an app from the repository and set the main file path to `app.py`.
3. In the app's Settings > Secrets, add:

   ```toml
   OPENAI_API_KEY = "your_actual_api_key"
   OPENAI_MODEL = "gpt-4o-mini"
   ```

4. Deploy. The app reads the key from Streamlit secrets in the hosted environment and from `.env` when run locally.
