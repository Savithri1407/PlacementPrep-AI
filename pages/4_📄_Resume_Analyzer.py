import streamlit as st
import os
import hashlib
import time

from dotenv import load_dotenv
from google import genai

from utils.pdf_reader import read_pdf


# --------------------------------------------------
# Load API Key
# --------------------------------------------------

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("❌ GOOGLE_API_KEY not found in .env file")
    st.stop()


# --------------------------------------------------
# Gemini Client
# --------------------------------------------------

client = genai.Client(
    api_key=API_KEY
)

MODEL = "gemini-3.6-flash"


# --------------------------------------------------
# Page
# --------------------------------------------------

st.title("📄 Resume Analyzer")

st.write(
    "Upload a resume and get a fresh AI analysis for that resume."
)


# --------------------------------------------------
# Upload Resume
# --------------------------------------------------

st.subheader("📤 Upload Your Resume")

uploaded_file = st.file_uploader(
    "Choose a resume PDF",
    type=["pdf"],
    key="resume_uploader"
)


# --------------------------------------------------
# Analyze Resume
# --------------------------------------------------

if uploaded_file:

    st.success(
        f"✅ {uploaded_file.name} uploaded successfully!"
    )

    # Get actual PDF content
    file_bytes = uploaded_file.getvalue()

    # Create unique ID for this resume
    file_hash = hashlib.md5(
        file_bytes
    ).hexdigest()

    # Analyze button
    if st.button(
        "🔍 Analyze Resume",
        key=f"analyze_{file_hash}"
    ):

        # --------------------------------------------------
        # Save Resume
        # --------------------------------------------------

        os.makedirs(
            "uploads/resumes",
            exist_ok=True
        )

        file_path = os.path.join(
            "uploads/resumes",
            uploaded_file.name
        )

        with open(
            file_path,
            "wb"
        ) as f:

            f.write(file_bytes)


        # --------------------------------------------------
        # Extract Resume Text
        # --------------------------------------------------

        resume_text = read_pdf(
            file_path
        )

        if not resume_text.strip():

            st.error(
                "❌ Could not extract text from this resume."
            )

            st.stop()


        st.success(
            "✅ Resume text extracted successfully!"
        )


        # --------------------------------------------------
        # Resume-Specific Prompt
        # --------------------------------------------------

        prompt = f"""
You are an expert resume reviewer and technical
placement interviewer.

You are analyzing ONE specific resume.

IMPORTANT RULES:

1. Analyze ONLY the resume text provided below.
2. Do NOT use information from previous resumes.
3. Do NOT reuse a previous resume's score.
4. Do NOT reuse a previous resume's skills.
5. Do NOT reuse a previous resume's projects.
6. Do NOT assume skills that are not present.
7. The score must be based on THIS resume.
8. Technical skills must come from THIS resume.
9. Strengths must come from THIS resume.
10. Weak areas must come from THIS resume.
11. ATS score must be based on THIS resume.
12. Interview questions must be based on THIS resume.
13. Do not give a fixed or generic score.
14. Analyze the complete resume carefully.

RESUME TO ANALYZE:

---------------- START RESUME ----------------

{resume_text}

----------------- END RESUME -----------------


Return the analysis in this format:

## 📊 Overall Resume Score

Give a realistic score out of 100.

Explain briefly why this score was given.

## 🛠️ Technical Skills

List ONLY the technical skills actually present
in this resume.

Group them into:

- Programming Languages
- Frameworks
- Databases
- Tools
- Other Technologies

Do not add technologies that are not mentioned.

## 🎓 Education

List the education details found in this resume.

## 💼 Projects

List the projects mentioned in THIS resume.

For each project, mention:
- Project name
- Technologies used
- Main functionality

## 💪 Strengths

List the strongest aspects of THIS resume.

## ⚠️ Weak Areas

List the specific weaknesses found in THIS resume.

## 📈 Improvement Suggestions

Give practical suggestions specifically for THIS resume.

## 🎯 ATS Score

Give an estimated ATS score out of 100.

Consider:

- Keywords
- Formatting
- Technical skills
- Job relevance
- Sections
- Readability

Explain the score briefly.

## 🎤 Resume-Based Interview Questions

Generate 5 technical interview questions based ONLY
on the technologies, projects and skills present
in THIS resume.

Do not ask about technologies that are not present.
"""


        # --------------------------------------------------
        # Generate AI Analysis With Retry
        # --------------------------------------------------

        try:

            with st.spinner(
                "🤖 AI is analyzing this resume..."
            ):

                response = None

                for attempt in range(3):

                    try:

                        response = client.models.generate_content(
                            model=MODEL,
                            contents=prompt
                        )

                        break

                    except Exception as e:

                        error_message = str(e)

                        # Temporary Gemini server overload
                        if (
                            "503" in error_message
                            or "UNAVAILABLE" in error_message
                        ):

                            if attempt < 2:

                                st.warning(
                                    f"⚠️ Gemini is temporarily busy. "
                                    f"Retrying... ({attempt + 1}/3)"
                                )

                                time.sleep(5)

                            else:

                                raise e

                        else:

                            raise e


            # --------------------------------------------------
            # Check Response
            # --------------------------------------------------

            if response is None:

                st.error(
                    "❌ Could not get a response from Gemini."
                )

                st.stop()


            # --------------------------------------------------
            # Get Analysis
            # --------------------------------------------------

            analysis = response.text.strip()


            # --------------------------------------------------
            # Display Result
            # --------------------------------------------------

            st.divider()

            st.subheader(
                f"📊 Analysis: {uploaded_file.name}"
            )

            st.markdown(
                analysis
            )


        except Exception as e:

            error_message = str(e)

            if (
                "503" in error_message
                or "UNAVAILABLE" in error_message
            ):

                st.error(
                    "❌ Gemini is currently experiencing "
                    "high demand. Please click "
                    "'Analyze Resume' again after a few seconds."
                )

            else:

                st.error(
                    f"❌ Error analyzing resume: {e}"
                )