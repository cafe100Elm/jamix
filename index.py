import os
import shlex
import subprocess
import sys

# This is the "handler" Vercel is looking for. 
# It starts the Streamlit process in the background.
def handler(event, context):
    cmd = f"streamlit run allergen_app.py --server.port 8080 --server.headless true"
    subprocess.Popen(shlex.split(cmd))
    return {
        "statusCode": 200,
        "body": "Streamlit is starting..."
    }

# This part is for local testing or direct execution
if __name__ == "__main__":
    from streamlit.web.cli import main
    sys.argv = [
        "streamlit",
        "run",
        "allergen_app.py",
        "--server.port", "8080",
        "--server.address", "0.0.0.0",
    ]
    main()
