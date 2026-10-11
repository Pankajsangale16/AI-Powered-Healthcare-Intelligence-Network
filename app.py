"""
Streamlit Community Cloud Entry Point.
Delegates execution to home.py to support default deployment paths (app.py).
"""
import runpy
from pathlib import Path

home_file = Path(__file__).resolve().parent / "home.py"
runpy.run_path(str(home_file), run_name="__main__")
