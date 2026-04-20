import os
from dotenv import load_dotenv
from langfuse import Langfuse

load_dotenv()

def test_connection():
    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        base_url=os.getenv("LANGFUSE_HOST")
    )
    
    print(f"Public Key: {os.getenv('LANGFUSE_PUBLIC_KEY')}")
    print(f"Host: {os.getenv('LANGFUSE_HOST')}")
    print("Sending test trace (v4 API)...")
    
    # In v4, we use start_as_current_observation or start_observation
    with langfuse.start_as_current_observation(name="test-connection-v4") as span:
        span.update(output="Connection successful!")
        print("Span created and updated.")
    
    # Flush to ensure data is sent immediately in script
    # Note: v4 uses background threads, Langfuse object doesn't have .flush()?
    # Actually it might be langfuse._resources.flush() but not public.
    # We'll just wait a bit.
    import time
    time.sleep(2)
    print("Done. Please check your Langfuse Dashboard.")

if __name__ == "__main__":
    test_connection()
