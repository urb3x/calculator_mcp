"""
title: Calculator & Math Tools
author: urb3x
author_url: https://github.com/urb3x/calculator_mcp
description: Advanced, safe mathematical calculation tools and expression evaluator for Open WebUI with exact arbitrary precision and comma parsing.
version: 1.1.0
license: MIT
"""

from __future__ import annotations

import ast
import math
import operator
import re
from typing import Any, Callable, Union


class Tools:
    def __init__(self):
        self._operators: dict[type[ast.AST], Callable[..., Any]] = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.FloorDiv: operator.floordiv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }

        self._functions: dict[str, Callable[..., Any]] = {
            "abs": abs,
            "round": round,
            "sqrt": math.sqrt,
            "cbrt": math.cbrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "asin": math.asin,
            "acos": math.acos,
            "atan": math.atan,
            "atan2": math.atan2,
            "sinh": math.sinh,
            "cosh": math.cosh,
            "tanh": math.tanh,
            "exp": math.exp,
            "log": math.log,
            "log10": math.log10,
            "log2": math.log2,
            "floor": math.floor,
            "ceil": math.ceil,
            "factorial": math.factorial,
            "gcd": math.gcd,
            "lcm": math.lcm,
            "degrees": math.degrees,
            "radians": math.radians,
        }

        self._constants: dict[str, float] = {
            "pi": math.pi,
            "e": math.e,
            "tau": math.tau,
            "inf": math.inf,
        }

    def _parse_num(self, val: Union[int, float, str]) -> Union[int, float]:
        if isinstance(val, (int, float)):
            return val
        cleaned = str(val).strip().replace(" ", "").replace(",", "")
        if not cleaned:
            raise ValueError("Number value cannot be empty")
        try:
            if "." in cleaned or "e" in cleaned.lower():
                return float(cleaned)
            return int(cleaned)
        except ValueError:
            return float(cleaned)

    def _clean_expr(self, expr: str) -> str:
        s = str(expr).strip()
        s = re.sub(r"(?<=\d),(?=\d)", "", s)
        s = s.replace("×", "*").replace("÷", "/").replace("^", "**")
        s = re.sub(r"\b(multiplied\s+by|pomnoz\s+przez)\b", "*", s, flags=re.I)
        s = re.sub(r"\b(divided\s+by|div\s+by|podziel\s+przez)\b", "/", s, flags=re.I)
        s = re.sub(r"\b(times|by|razy)\b", "*", s, flags=re.I)
        s = re.sub(r"\b(div|przez)\b", "/", s, flags=re.I)
        s = re.sub(r"\b(plus|dodaj)\b", "+", s, flags=re.I)
        s = re.sub(r"\b(minus|odejmij)\b", "-", s, flags=re.I)
        return s.strip()


    def _eval_node(self, node: ast.AST) -> Union[int, float]:
        if isinstance(node, ast.Expression):
            return self._eval_node(node.body)

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Unsupported constant type: {type(node.value).__name__}")

        if isinstance(node, ast.Name):
            name = node.id.lower()
            if name in self._constants:
                return self._constants[name]
            raise ValueError(f"Unknown constant or variable: '{node.id}'")

        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in self._operators:
                raise ValueError(f"Unsupported binary operator: {op_type.__name__}")
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right == 0:
                raise ZeroDivisionError("Division by zero in expression")
            res = self._operators[op_type](left, right)
            if isinstance(res, float) and res.is_integer() and abs(res) < 1e16:
                return int(res)
            return res

        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in self._operators:
                raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
            operand = self._eval_node(node.operand)
            return self._operators[op_type](operand)

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Only direct function calls are allowed (e.g. sqrt(9))")
            func_name = node.func.id.lower()
            if func_name not in self._functions:
                raise ValueError(f"Unsupported function: '{node.func.id}'")
            args = [self._eval_node(arg) for arg in node.args]
            res = self._functions[func_name](*args)
            if isinstance(res, float) and res.is_integer() and abs(res) < 1e16:
                return int(res)
            return res

        raise ValueError(f"Unsupported expression syntax: {type(node).__name__}")

    def calculate(self, expression: str) -> str:
        """
        Evaluate a mathematical expression safely with exact integer and float precision.

        :param expression: Mathematical expression string (e.g. '1,232,483,204 * 8,435,639,485,639', '3242 * 435', 'sqrt(144) + 2^4')
        :return: String with calculation result
        """
        try:
            cleaned = self._clean_expr(expression)
            parsed = ast.parse(cleaned, mode="eval")
            result = self._eval_node(parsed)
            return str(result)
        except Exception as e:
            return f"Error evaluating expression: {e}"

    def multiply(self, a: Union[float, int, str], b: Union[float, int, str]) -> str:
        """
        Multiply two numbers (supports arbitrary precision large numbers and numbers with commas).
        :param a: First number
        :param b: Second number
        :return: Product of a and b
        """
        try:
            res = self._parse_num(a) * self._parse_num(b)
            return str(res)
        except Exception as e:
            return f"Error: {e}"

    def add(self, a: Union[float, int, str], b: Union[float, int, str]) -> str:
        """
        Add two numbers.
        :param a: First number
        :param b: Second number
        :return: Sum of a and b
        """
        try:
            res = self._parse_num(a) + self._parse_num(b)
            return str(res)
        except Exception as e:
            return f"Error: {e}"

    def divide(self, a: Union[float, int, str], b: Union[float, int, str]) -> str:
        """
        Divide a by b.
        :param a: Dividend
        :param b: Divisor
        :return: Quotient of a and b
        """
        try:
            num_a = self._parse_num(a)
            num_b = self._parse_num(b)
            if num_b == 0:
                return "Error: Cannot divide by zero"
            res = num_a / num_b
            if isinstance(res, float) and res.is_integer() and abs(res) < 1e16:
                return str(int(res))
            return str(res)
        except Exception as e:
            return f"Error: {e}"

    def sqrt(self, n: Union[float, int, str]) -> str:
        """
        Calculate square root of n.
        :param n: Number
        :return: Square root of n
        """
        try:
            num_n = self._parse_num(n)
            if num_n < 0:
                return "Error: Cannot take square root of negative number"
            res = math.sqrt(num_n)
            if res.is_integer() and abs(res) < 1e16:
                return str(int(res))
            return str(res)
        except Exception as e:
            return f"Error: {e}"
