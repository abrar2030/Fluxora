import importlib.util
import os
import sys

from dotenv import load_dotenv

_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_ML_CORE_DIR = os.path.abspath(os.path.join(_BACKEND_DIR, "..", "ml_core"))

if importlib.util.find_spec("src") is None and os.path.isfile(
    os.path.join(_ML_CORE_DIR, "src", "__init__.py")
):
    sys.path.insert(0, _ML_CORE_DIR)

load_dotenv(os.path.join(_BACKEND_DIR, ".env"), override=False)
