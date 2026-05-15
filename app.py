import streamlit as st
import google.generativeai as genai

# =========================================================
# CONFIGURE GEMINI
# =========================================================

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=GEMINI_API_KEY)

# =========================================================
# AUTO DISCOVER AVAILABLE MODELS
# =========================================================

available_models = []

try:
    models = genai.list_models()

    for m in models:
        model_name = m.name

        # Only include models that support generateContent
        if "generateContent" in m.supported_generation_methods:
            available_models.append(model_name)

    print("Available Models:")
    for m in available_models:
        print("-", m)

except Exception as e:
    st.error(f"Failed to list Gemini models: {e}")
    st.stop()

# =========================================================
# FIND BEST FLASH MODEL
# =========================================================

selected_model = None

# Priority order
preferred_keywords = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "flash"
]

for keyword in preferred_keywords:
    for model_name in available_models:

        clean_name = model_name.lower()

        if keyword in clean_name:
            selected_model = model_name
            break

    if selected_model:
        break

# =========================================================
# FAIL SAFELY
# =========================================================

if not selected_model:

    st.error(
        f"""
No compatible Gemini Flash model found.

Available models:

{available_models}
"""
    )

    st.stop()

# =========================================================
# INITIALIZE MODEL
# =========================================================

try:
    model = genai.GenerativeModel(selected_model)

    st.success(f"Using Gemini model: {selected_model}")

except Exception as e:

    st.error(
        f"""
Failed to initialize Gemini model.

Error:
{e}

Available models:
{available_models}
"""
    )

    st.stop()

# =========================================================
# TEST PROMPT
# =========================================================

try:

    response = model.generate_content(
        "Write a short Islamic motivational quote."
    )

    st.write("Gemini Response:")
    st.write(response.text)

except Exception as e:

    st.error(
        f"""
Gemini generation failed.

Error:
{e}

Current model:
{selected_model}

Available models:
{available_models}
"""
    )
