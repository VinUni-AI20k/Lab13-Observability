import os
from dotenv import load_dotenv
from langfuse.decorators import observe, langfuse_context

load_dotenv()

@observe(name="connectivity_test")
def run_trace():
    print("Executing traced function...")
    langfuse_context.update_current_trace(
        tags=["debug", "test"],
        user_id="test_user"
    )

def debug():
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    host = os.getenv("LANGFUSE_HOST")

    print(f"Checking connection to: {host}")
    print(f"Public Key starts with: {public_key[:8]}...")
    
    try:
        print("Sending test trace...")
        run_trace()
        langfuse_context.flush()
        print("Success! Data sent to Langfuse.")
        print("Please check your Langfuse dashboard for a trace named 'connectivity_test'.")
    except Exception as e:
        print(f"Error sending to Langfuse: {e}")

if __name__ == "__main__":
    debug()
