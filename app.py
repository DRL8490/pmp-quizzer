import os
import random
import streamlit as st
from supabase import create_client, Client

# 1. Setup the Web Page settings
st.set_page_config(page_title="PMP Quizzer", page_icon="🚀", layout="centered")

# 2. Securely connect to Supabase (Cloud & Local Hybrid)
try:
    # This runs when deployed on Streamlit Cloud
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
except KeyError:
    # This runs when testing locally on your PC
    from dotenv import load_dotenv
    load_dotenv()
    url = os.environ.get("SUPABASE_URL").strip()
    key = os.environ.get("SUPABASE_KEY").strip()

supabase: Client = create_client(url, key)

# 3. Fetch Data (Cached so it doesn't slow down the website)
@st.cache_data
def get_processes():
    response = supabase.table("pmp_processes").select("*").execute()
    return response.data

processes = get_processes()

# 4. App Memory (Keeps track of current question and button clicks)
if 'current_process' not in st.session_state:
    st.session_state.current_process = random.choice(processes)
    st.session_state.show_answer = False

def next_question():
    st.session_state.current_process = random.choice(processes)
    st.session_state.show_answer = False

# 5. The User Interface (What you see on the screen)
st.title("🚀 PMP Flashcard Engine")
st.markdown("---")

# Display the Question
st.caption(f"Domain: {st.session_state.current_process['process_group']} | Area: {st.session_state.current_process['knowledge_area']}")
st.subheader(f"Process: {st.session_state.current_process['process_name']}")
st.write("**Question:** What are the main **OUTPUTS** of this process?")

# The Button Logic
if not st.session_state.show_answer:
    if st.button("Show Answer", type="primary"):
        st.session_state.show_answer = True
        st.rerun()

# Show Answers if button was clicked
if st.session_state.show_answer:
    st.markdown("### ✅ Correct Outputs:")
    
    # Query Supabase for the specific ITTOs
    answers = supabase.table("pmp_ittos").select("item_name").eq("process_id", st.session_state.current_process['id']).eq("category", "Output").execute()
    
    if not answers.data:
        st.warning("No outputs recorded for this process yet.")
    else:
        for item in answers.data:
            st.success(f"- {item['item_name']}")
            
    st.markdown("---")
    st.button("Next Question", on_click=next_question)