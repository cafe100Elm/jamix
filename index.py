import os
import sys
from streamlit.web.cli import main

# This line is the magic spell for Vercel. 
# It creates the 'app' variable it's looking for.
app = None 

def handler(event, context):
    return {
        "statusCode": 200,
        "body": "Streamlit is starting..."
    }

if __name__ == "__main__":
    sys.argv = [
        "streamlit",
        "run",
        "allergen_app.py",
        "--server.port", "8080",
        "--server.address", "0.0.0.0",
    ]
    main()
