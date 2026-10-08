import streamlit as st
import os
import re

from dotenv import load_dotenv
from google import genai


# ---------------------------------------
# Load API Key
# ---------------------------------------

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("❌ GOOGLE_API_KEY not found in .env")
    st.stop()


# ---------------------------------------
# Gemini Client
# ---------------------------------------

client = genai.Client(
    api_key=API_KEY
)

MODEL = "gemini-3.6-flash"


# ---------------------------------------
# Page
# ---------------------------------------

st.title("🎤 Mock Interview")

st.write(
    "Practice technical interview questions with PrepGenius AI."
)


# ---------------------------------------
# Initialize Interview Results
# ---------------------------------------

if "interview_results" not in st.session_state:

    st.session_state.interview_results = []


# ---------------------------------------
# Topic
# ---------------------------------------

st.subheader("🎯 Choose Interview Topic")

topic = st.selectbox(
    "Select a topic",
    [
        "Java",
        "Spring Boot",
        "SQL",
        "DBMS",
        "Operating Systems",
        "Computer Networks",
        "DSA",
        "React"
    ]
)


# ---------------------------------------
# Difficulty
# ---------------------------------------

difficulty = st.selectbox(
    "Select difficulty",
    [
        "Easy",
        "Medium",
        "Hard"
    ]
)


# ---------------------------------------
# Start Interview
# ---------------------------------------

if st.button("🚀 Start Interview"):

    prompt = f"""
You are an expert technical interviewer.

Generate ONE technical interview question.

Topic:
{topic}

Difficulty:
{difficulty}

Rules:

- Ask ONLY about {topic}.
- Do NOT use uploaded PDFs.
- Do NOT use uploaded notes.
- Do NOT use FAISS.
- Do NOT use RAG.
- Do NOT ask about another technology.
- Match the requested difficulty.
- Do not give the answer.
- Return only the question.

Generate one question now.
"""

    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        question = response.text.strip()

        # Store current interview
        st.session_state.interview_started = True

        st.session_state.interview_question = question

        st.session_state.interview_topic = topic

        st.session_state.interview_difficulty = difficulty

        # Reset answer and evaluation for new question
        st.session_state.pop(
            "current_answer",
            None
        )

        st.session_state.pop(
            "current_evaluation",
            None
        )

        st.session_state.pop(
            "current_score",
            None
        )

        st.session_state.pop(
            "result_saved",
            None
        )

    except Exception as e:

        st.error(
            f"❌ Error generating question: {e}"
        )


# ---------------------------------------
# Show Question
# ---------------------------------------

if st.session_state.get(
    "interview_started",
    False
):

    st.divider()

    st.subheader("🤖 Interview Question")

    st.info(
        f"Topic: {st.session_state.interview_topic} | "
        f"Difficulty: {st.session_state.interview_difficulty}"
    )

    st.write(
        st.session_state.interview_question
    )


    # ---------------------------------------
    # Answer
    # ---------------------------------------

    st.subheader("✍️ Your Answer")

    answer = st.text_area(
        "Type your answer here",
        height=200,
        placeholder="Write your answer...",
        key="current_answer"
    )


    # ---------------------------------------
    # Evaluate
    # ---------------------------------------

    if st.button("📤 Submit Answer"):

        if not answer.strip():

            st.warning(
                "⚠️ Please enter your answer first."
            )

        else:

            evaluation_prompt = f"""
You are an expert technical interviewer.

Evaluate this candidate's answer.

Topic:
{st.session_state.interview_topic}

Difficulty:
{st.session_state.interview_difficulty}

Question:
{st.session_state.interview_question}

Candidate Answer:
{answer}

Evaluate ONLY according to the selected topic.

IMPORTANT:
Give a score strictly between 0 and 10.

Return exactly this format:

Score: X/10

Correctness:
Explain whether the answer is correct.

What was good:
Mention the good points.

What is missing:
Mention important missing concepts.

Improved Answer:
Give a clear interview-ready answer.
"""

            try:

                evaluation_response = client.models.generate_content(
                    model=MODEL,
                    contents=evaluation_prompt
                )

                evaluation = (
                    evaluation_response
                    .text
                    .strip()
                )


                # ---------------------------------------
                # Extract Score
                # ---------------------------------------

                score = 0.0

                score_match = re.search(
                    r"Score\s*:\s*(\d+(?:\.\d+)?)\s*/\s*10",
                    evaluation,
                    re.IGNORECASE
                )

                if score_match:

                    score = float(
                        score_match.group(1)
                    )

                # Keep score between 0 and 10
                score = max(
                    0.0,
                    min(score, 10.0)
                )


                # ---------------------------------------
                # Save Current Evaluation
                # ---------------------------------------

                st.session_state.current_evaluation = (
                    evaluation
                )

                st.session_state.current_score = (
                    score
                )


                # ---------------------------------------
                # Save Result Only Once
                # ---------------------------------------

                if not st.session_state.get(
                    "result_saved",
                    False
                ):

                    result = {

                        "topic":
                            st.session_state.interview_topic,

                        "difficulty":
                            st.session_state.interview_difficulty,

                        "question":
                            st.session_state.interview_question,

                        "answer":
                            answer,

                        "score":
                            score
                    }

                    st.session_state.interview_results.append(
                        result
                    )

                    st.session_state.result_saved = True


                # ---------------------------------------
                # Display Evaluation
                # ---------------------------------------

                st.divider()

                st.subheader(
                    "📊 AI Evaluation"
                )

                st.write(
                    evaluation
                )

                st.success(
                    f"🎯 Your Score: {score}/10"
                )


            except Exception as e:

                st.error(
                    f"❌ Error evaluating answer: {e}"
                )


# ---------------------------------------
# Show Previous Evaluation
# ---------------------------------------

if (
    st.session_state.get(
        "current_evaluation",
        None
    )
    and not st.session_state.get(
        "result_saved",
        False
    )
):

    st.divider()

    st.subheader(
        "📊 AI Evaluation"
    )

    st.write(
        st.session_state.current_evaluation
    )