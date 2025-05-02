# phase1_financial_wellness_streamlit.py

import streamlit as st
import os
import json
from openai import AzureOpenAI

# Load secrets from Streamlit secrets
try:
    endpoint = st.secrets["AZURE_OPENAI_ENDPOINT"]
    model_name = st.secrets["AZURE_OPENAI_MODEL"]
    deployment = st.secrets["AZURE_OPENAI_DEPLOYMENT"]
    subscription_key = st.secrets["AZURE_OPENAI_KEY"]
    api_version = st.secrets["AZURE_OPENAI_API_VERSION"]
except KeyError as e:
    st.error(f"Missing required secret: {e}")
    st.stop()

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

st.set_page_config(page_title="Incluya: Financial Wellness", layout="centered")
st.title("🧠 Incluya - Financial Wellness Coach")
st.write("Answer these 7 questions to begin your personalized financial healing journey.")

# Intake questions
questions = [
    "1. Let's take it all the way back! What is your earliest money memory from childhood?",
    "2. Take your time with this one- What were your parents' attitudes and discussions about money?",
    "3. Have fun with this, and answer from the heart! What are your aspirations regarding finances?",
    "4. Take a deep breath before answering this one….What does healing your relationship with money feel like and look like to you?",
    "5. Rate how well each money management style reflects your personal financial approach: (1 = Not at all like me, 2 = Slightly like me, 3 = Somewhat like me, 4 = Mostly like me, 5 = Exactly like me)\n"
    "   01) Avoider: prefer not to think about it\n"
    "   02) Vigilant: constant anxiety\n"
    "   03) Spontaneous: live for today\n"
    "   04) Gatherer: never enough savings\n"
    "   05) Planner: detailed budgeter\n"
    "   06) Aspirational: money equals worth\n"
    "   07) Procrastinator: always behind on bills",
    "6. You are being SO brave. Let's go a little deeper. What are some things you're ashamed of or worry about when it comes to finances?",
    "7. Final question, and a sensitive one- so take your time! For each statement below, tell me how strongly you agree or disagree: (1 = Strongly Disagree, 2 = Disagree, 3 = Neutral, 4 = Agree, 5 = Strongly Agree)\n"
    "   01) I worry about not having enough money for emergencies or retirement\n"
    "   02) I worry that I'm falling behind my peers financially\n"
    "   03) I feel shame or embarrassment about my debt\n"
    "   04) I worry about being exposed as financially irresponsible or unknowledgeable\n"
    "   05) I'm embarrassed to ask for financial help or advice, even when I need it\n"
    "   06) I avoid checking my financial accounts because it causes me anxiety\n"
    "   07) I feel guilty spending money on myself, even for necessary items"
]

responses = []

with st.form("intake_form"):
    # Questions 1 to 4
    for q in questions[:4]:
        response = st.text_area(q, height=80)
        responses.append(response)

    # Question 5: Likert scale for money management styles
    st.markdown("### Rate how well each money management style reflects your personal financial approach:")
    money_styles = [
        "Avoider: prefer not to think about it",
        "Vigilant: constant anxiety",
        "Spontaneous: live for today",
        "Gatherer: never enough savings",
        "Planner: detailed budgeter",
        "Aspirational: money equals worth",
        "Procrastinator: always behind on bills"
    ]
    money_style_responses = {}
    for style in money_styles:
        rating = st.radio(f"{style}", options=[1, 2, 3, 4, 5], horizontal=True)
        money_style_responses[style] = rating
    responses.append(money_style_responses)

    # Question 6
    response = st.text_area("6. You are being SO brave. Let's go a little deeper. What are some things you're ashamed of or worry about when it comes to finances?", height=80)
    responses.append(response)

    # Question 7: Likert scale for financial worries
    st.markdown("### Final question: For each statement below, tell me how strongly you agree or disagree:")
    financial_worries = [
        "I worry about not having enough money for emergencies or retirement",
        "I worry that I'm falling behind my peers financially",
        "I feel shame or embarrassment about my debt",
        "I worry about being exposed as financially irresponsible or unknowledgeable",
        "I'm embarrassed to ask for financial help or advice, even when I need it",
        "I avoid checking my financial accounts because it causes me anxiety",
        "I feel guilty spending money on myself, even for necessary items"
    ]
    financial_worry_responses = {}
    for worry in financial_worries:
        agreement = st.radio(f"{worry}", options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"], horizontal=True)
        financial_worry_responses[worry] = agreement
    responses.append(financial_worry_responses)

    # Submit button
    submitted = st.form_submit_button("Generate My Wellness Profile & Plan")

if submitted:
    if not all(responses):
        st.error("Please answer all questions.")
    else:
        with st.spinner("Generating profile with Azure OpenAI..."):
            profile_prompt = (
                "You are a financial therapist AI. Summarize the user's financial origin story, "
                "personality type, major emotional triggers, and money behavior based on the following answers. "
                "Structure the output as a JSON with keys: origin_story, personality_type, emotional_triggers, behavior_patterns.\n"
                "Answers: " + json.dumps(responses, indent=2)
            )

            try:
                profile_completion = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": "You are a compassionate financial wellness assistant."},
                        {"role": "user", "content": profile_prompt}
                    ],
                    temperature=0.6,
                    max_tokens=600
                )
                result_raw = profile_completion.choices[0].message.content

                # Strip code fences if present
                result_clean = result_raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                profile_dict = json.loads(result_clean)
                st.success("Here's your profile summary:")
                st.json(profile_dict)

                # Generate 15–30 day plan
                with st.spinner("Creating your personalized wellness plan..."):
                    plan_prompt = (
                        "Based on the following profile: \n" + json.dumps(profile_dict, indent=2) +
                        "\nGenerate a 15-day personalized financial wellness plan. For each day, return a JSON object with: day, focus, and intervention. "
                        "Keep the tone supportive and use a mix of journaling, small tasks, meditations, affirmations, and reflection prompts. "
                        "Respond as a JSON list of 15 entries."
                    )

                    plan_completion = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": "You are a compassionate financial wellness planner."},
                            {"role": "user", "content": plan_prompt}
                        ],
                        temperature=0.7,
                        max_tokens=1500
                    )

                    plan_raw = plan_completion.choices[0].message.content
                    plan_clean = plan_raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                    plan_data = json.loads(plan_clean)
                    st.subheader("🗓️ Your 15-Day Wellness Plan")
                    for day in plan_data:
                        st.markdown(f"**Day {day['day']} - {day['focus']}**\n\n{day['intervention']}")

            except Exception as e:
                st.error(f"Error: {e}")

# Instructions for API key management
st.markdown("""
This is a sample application, it only performs the basic functionality of the L1 - which
            is to collect the user's responses and generate a profile and plan.
""")
