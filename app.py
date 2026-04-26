import os
import random
import streamlit as st
from supabase import create_client, Client

# 1. Setup the Web Page settings
st.set_page_config(page_title="PMP Quizzer", page_icon="🚀", layout="centered")

# 2. Securely connect to Supabase (Cloud & Local)
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
except KeyError:
    from dotenv import load_dotenv
    load_dotenv()
    url = os.environ.get("SUPABASE_URL").strip()
    key = os.environ.get("SUPABASE_KEY").strip()

supabase: Client = create_client(url, key)

# 3. Fetch Data
@st.cache_data
def get_processes():
    response = supabase.table("pmp_processes").select("*").execute()
    return response.data

processes = get_processes()

# 4. App Memory (State Management)
if 'current_process' not in st.session_state:
    st.session_state.current_process = random.choice(processes)
    # Randomly pick which ITTO category to test
    st.session_state.question_category = random.choice(["Input", "Tool", "Output"])
    st.session_state.show_answer = False
    st.session_state.user_attempt = ""

def next_question():
    st.session_state.current_process = random.choice(processes)
    st.session_state.question_category = random.choice(["Input", "Tool", "Output"])
    st.session_state.show_answer = False
    st.session_state.user_attempt = ""

# 5. The User Interface
st.title("🚀 PMP Active Recall Engine")
st.markdown("---")

p = st.session_state.current_process
cat = st.session_state.question_category
display_cat = {"Input": "INPUTS", "Tool": "TOOLS & TECHNIQUES", "Output": "OUTPUTS"}[cat]

# Display the Question
st.caption(f"Domain: {p['process_group']} | Area: {p['knowledge_area']}")
st.subheader(f"Process: {p['process_name']}")
st.write(f"**Question:** What are the main **{display_cat}** of this process?")

# The Text Box
user_answer = st.text_area("Type your answers here (separate with commas):", value=st.session_state.user_attempt)

# Submit Button
if not st.session_state.show_answer:
    if st.button("Check Answer", type="primary"):
        st.session_state.user_attempt = user_answer
        st.session_state.show_answer = True
        st.rerun()

# Grading & Results Screen
if st.session_state.show_answer:
    st.markdown("### 📊 Results")
    
    # Query Supabase for the correct answers
    answers = supabase.table("pmp_ittos").select("item_name").eq("process_id", p['id']).eq("category", cat).execute()
    correct_items = [item['item_name'] for item in answers.data]
    
    if not correct_items:
        st.warning("No data recorded in the database for this category yet.")
    else:
        # Smart Grading Logic
        user_list = [x.strip().lower() for x in st.session_state.user_attempt.split(",") if x.strip()]
        db_list_lower = [x.lower() for x in correct_items]
        
        found_matches = []
        for typed in user_list:
            for correct_ans in db_list_lower:
                # Soft match: checks if typed word is in the answer, or answer is in the typed word
                if typed in correct_ans or correct_ans in typed: 
                    found_matches.append(correct_ans)
                    break
        
        score = len(set(found_matches))
        total = len(correct_items)
        
        # Display Score
        st.info(f"**You typed:** {st.session_state.user_attempt}")
        if score == total:
            st.success(f"Perfect! You got {score} out of {total} right.")
        elif score > 0:
            st.warning(f"Close! You got about {score} out of {total} right.")
        else:
            st.error(f"Oof. You got 0 out of {total} right.")

        # Show the official list for Self-Grading
        st.markdown("#### ✅ Official Answers:")
        for item in correct_items:
            st.write(f"- {item}")
            
    st.markdown("---")
    st.button("Next Question", on_click=next_question)