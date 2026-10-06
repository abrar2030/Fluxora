import importlib.util
import os
import sys

from dotenv import load_dotenv

_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_ML_CORE_SRC = os.path.abspath(os.path.join(_BACKEND_DIR, "..", "ml_core", "src"))

if importlib.util.find_spec("ml_core") is None and os.path.isdir(_ML_CORE_SRC):
    sys.path.insert(0, _ML_CORE_SRC)

load_dotenv(os.path.join(_BACKEND_DIR, ".env"), override=False)
