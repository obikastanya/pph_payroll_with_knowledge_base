"""Demo of the PPh 21 knowledge-based system: the application of system/app in demo mode.

    env\\Scripts\\streamlit run mini_demo\\mockup\\main.py --server.port 8503

Same program as system/app/main.py, with the fixed initial state of the demo (the gold knowledge base up to 27 Feb
2025, eight documents waiting with the AI results of the research) and the reset button. Everything done during a
demo is kept in mini_demo/mockup/workspace/. See README.md.
"""
import os
import runpy
from pathlib import Path

os.environ["PPH21_APP_MODE"] = "demo"
runpy.run_path(str(Path(__file__).resolve().parents[2] / "system" / "app" / "main.py"), run_name="__main__")
