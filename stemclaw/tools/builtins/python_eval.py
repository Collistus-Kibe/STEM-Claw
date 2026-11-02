"""Scientific Python Evaluator built-in tool."""

import io
import math
import re
import statistics
import sys
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from stemclaw.tools.base import BaseTool


class PythonEvalInput(BaseModel):
    code: str = Field(..., description="Python code snippet to execute for scientific calculations or statistics")


class PythonEvalTool(BaseTool):
    name = "python_eval"
    description = (
        "Execute a Python code snippet to perform scientific data calculations, "
        "statistical tests (mean, stdev, p-values), mathematical formulas, or format tables. "
        "Has pre-imported access to math, statistics, re, json, itertools, collections."
    )
    input_model = PythonEvalInput

    def run(self, code: str) -> str:
        # Prepare safe scientific execution namespace
        import collections
        import datetime
        import itertools
        import json

        local_scope: Dict[str, Any] = {}
        global_scope: Dict[str, Any] = {
            "math": math,
            "statistics": statistics,
            "json": json,
            "re": re,
            "datetime": datetime,
            "itertools": itertools,
            "collections": collections,
            "abs": abs,
            "all": all,
            "any": any,
            "bin": bin,
            "bool": bool,
            "dict": dict,
            "enumerate": enumerate,
            "filter": filter,
            "float": float,
            "format": format,
            "int": int,
            "isinstance": isinstance,
            "len": len,
            "list": list,
            "map": map,
            "max": max,
            "min": min,
            "pow": pow,
            "print": print,
            "range": range,
            "reversed": reversed,
            "round": round,
            "set": set,
            "sorted": sorted,
            "str": str,
            "sum": sum,
            "tuple": tuple,
            "zip": zip,
        }

        # Redirect stdout to capture prints
        captured_stdout = io.StringIO()
        original_stdout = sys.stdout

        try:
            sys.stdout = captured_stdout

            # If the code is a single expression, evaluate and print result
            try:
                compiled_expr = compile(code.strip(), "<stemclaw_calc>", "eval")
                eval_val = eval(compiled_expr, global_scope, local_scope)
                if eval_val is not None:
                    captured_stdout.write(f"Result: {eval_val}\n")
            except SyntaxError:
                # Execute as multi-line script
                compiled_exec = compile(code, "<stemclaw_script>", "exec")
                exec(compiled_exec, global_scope, local_scope)

            output = captured_stdout.getvalue()
            if not output.strip():
                # Check if any new variable was assigned
                results = {k: v for k, v in local_scope.items() if not k.startswith("_")}
                if results:
                    output = "Variables assigned:\n" + "\n".join(f"{k} = {v}" for k, v in results.items())
                else:
                    output = "Code executed successfully with no output."

            return f"=== Python Evaluation Output ===\n{output.strip()}"

        except Exception as e:
            return f"Python Execution Error: {type(e).__name__}: {e}"

        finally:
            sys.stdout = original_stdout

