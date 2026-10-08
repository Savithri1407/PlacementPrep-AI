import streamlit as st


# --------------------------------------------------
# Page
# --------------------------------------------------

st.title("📊 Interview Performance Dashboard")

st.write(
    "Track your actual mock interview performance."
)


# --------------------------------------------------
# Check Interview Results
# --------------------------------------------------

results = st.session_state.get(
    "interview_results",
    []
)


# --------------------------------------------------
# No Results
# --------------------------------------------------

if not results:

    st.info(
        "📭 No interview results yet."
    )

    st.write(
        "Go to 🎤 Mock Interview, answer a question, "
        "and submit it. Your result will appear here."
    )

    st.stop()


# --------------------------------------------------
# Calculate Statistics
# --------------------------------------------------

total_questions = len(results)

total_score = 0

highest_score = 0


for result in results:

    score = result["score"]

    total_score += score

    if score > highest_score:

        highest_score = score


average_score = (
    total_score / total_questions
)


# --------------------------------------------------
# Dashboard Metrics
# --------------------------------------------------

st.subheader("📈 Overall Performance")

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "🎯 Average Score",
        f"{average_score:.1f}/10"
    )


with col2:

    st.metric(
        "📝 Questions Attempted",
        total_questions
    )


with col3:

    st.metric(
        "🏆 Highest Score",
        f"{highest_score:.1f}/10"
    )


# --------------------------------------------------
# Topic Performance
# --------------------------------------------------

st.divider()

st.subheader("📚 Interview History")


for index, result in enumerate(
    results,
    start=1
):

    topic = result["topic"]

    difficulty = result["difficulty"]

    score = result["score"]

    st.write(
        f"**{index}. {topic}** "
        f"({difficulty}) — **{score}/10**"
    )

    st.progress(
        min(score / 10, 1.0)
    )


# --------------------------------------------------
# Strong and Weak Areas
# --------------------------------------------------

st.divider()

st.subheader("💡 Performance Analysis")


strong_topics = []

weak_topics = []


for result in results:

    topic = result["topic"]

    score = result["score"]


    if score >= 8:

        if topic not in strong_topics:

            strong_topics.append(topic)


    else:

        if topic not in weak_topics:

            weak_topics.append(topic)


col1, col2 = st.columns(2)


# --------------------------------------------------
# Strong Areas
# --------------------------------------------------

with col1:

    st.success("💪 Strong Areas")

    if strong_topics:

        for topic in strong_topics:

            st.write(
                f"✅ {topic}"
            )

    else:

        st.write(
            "No strong areas yet."
        )


# --------------------------------------------------
# Weak Areas
# --------------------------------------------------

with col2:

    st.warning("⚠️ Needs Improvement")

    if weak_topics:

        for topic in weak_topics:

            st.write(
                f"⚠️ {topic}"
            )

    else:

        st.write(
            "Great! No major weak areas."
        )


# --------------------------------------------------
# Recommendation
# --------------------------------------------------

st.divider()

st.subheader("🎯 Recommendation")


if weak_topics:

    st.info(
        "Focus more on: "
        + ", ".join(weak_topics)
    )

else:

    st.success(
        "Excellent performance! Keep practicing."
    )


# --------------------------------------------------
# Clear Results
# --------------------------------------------------

st.divider()

if st.button("🗑️ Clear Interview History"):

    st.session_state.interview_results = []

    st.rerun()