import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load the hidden passwords from the .env file
load_dotenv()

# Retrieve them AND aggressively strip any hidden Windows characters
url: str = os.environ.get("SUPABASE_URL").strip()
key: str = os.environ.get("SUPABASE_KEY").strip()

# Connect to the Database
print("Attempting to connect to Supabase securely...")
supabase: Client = create_client(url, key)

# Ask the database for all the Processes
response = supabase.table("pmp_processes").select("*").execute()
processes = response.data

# Display the results
print("\n--- SECURE CONNECTION SUCCESS! ---")
for process in processes:
    print(f"- Process ID: {process['id']} | Name: {process['process_name']}")