"""
Run all Samrat tests and exit with appropriate status code.
Used by CI/CD pipeline.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from test_comprehensive import run_all as run_comprehensive
from test_compiler import run_all as run_compiler

success1 = run_comprehensive()
success2 = run_compiler()

sys.exit(0 if (success1 and success2) else 1)