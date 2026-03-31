import os
import sys
from streamlit.web.cli import main

# This script redirects Vercel's execution to the Streamlit CLI
if __name__ == "__main__":
    sys.argv = [
        "streamlit",
        "run",
        "allergen_app.py",
        "--server.port", "8080",
        "--server.address", "0.0.0.0",
    ]
    sys.exit(main())
