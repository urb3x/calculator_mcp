"""
title: Calculator & Math Tools
author: urb3x
author_url: https://github.com/urb3x/calculator_mcp
description: Advanced, safe mathematical calculation tools and expression evaluator for Open WebUI.
version: 1.0.0
license: MIT
"""

from __future__ import annotations

import ast
import math
import operator
from typing import Any, Callable


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

    def _eval_node(self, node: ast.AST) -> float:
        """Recursively and safely evaluate an AST node."""
        if isinstance(node, ast.Expression):
            return self._eval_node(node.body)

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return float(node.value)
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
            return float(self._operators[op_type](left, right))

        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in self._operators:
                raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
            operand = self._eval_node(node.operand)
            return float(self._operators[op_type](operand))

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Only direct function calls are allowed (e.g. sqrt(9))")
            func_name = node.func.id.lower()
            if func_name not in self._functions:
                raise ValueError(f"Unsupported function: '{node.func.id}'")
            args = [self._eval_node(arg) for arg in node.args]
            return float(self._functions[func_name](*args))

        raise ValueError(f"Unsupported expression syntax: {type(node).__name__}")

    def calculate(self, expression: str) -> str:
        """
        Evaluate a mathematical expression safely without using eval().

        Supports:
          - Basic operators: +, -, *, /, //, %, ** (or ^)
          - Functions: sqrt, sin, cos, tan, log, log10, exp, floor, ceil, round, abs, factorial
          - Constants: pi, e, tau

        :param expression: Mathematical expression string (e.g. 'sqrt(16) + 2^3', 'sin(pi / 2)')
        :return: String with calculation result or error description
        """
        try:
            normalized = expression.replace("^", "**").strip()
            if not normalized:
                return "Error: Expression cannot be empty"
            parsed = ast.parse(normalized, mode="eval")
            result = self._eval_node(parsed)
            # Format cleanly as integer if whole number
            if result.is_integer():
                return str(int(result))
            return str(result)
        except Exception as e:
            return f"Error evaluating expression: {e}"

    def add(self, a: float, b: float) -> str:
        """
        Add two numbers.
        :param a: First number
        :param b: Second number
        :return: Sum of a and b
        """
        res = a + b
        return str(int(res) if res.is_integer() else res)

    def subtract(self, a: float, b: float) -> str:
        """
        Subtract b from a.
        :param a: Number to subtract from
        :param b: Number to subtract
        :return: Difference of a and b
        """
        res = a - b
        return str(int(res) if res.is_integer() else res)

    def multiply(self, a: float, b: float) -> str:
        """
        Multiply two numbers.
        :param a: First number
        :param b: Second number
        :return: Product of a and b
        """
        res = a * b
        return str(int(res) if res.is_integer() else res)

    def divide(self, a: float, b: float) -> str:
        """
        Divide a by b.
        :param a: Dividend
        :param b: Divisor
        :return: Quotient of a and b
        """
        if b == 0:
            return "Error: Cannot divide by zero"
        res = a / b
        return str(int(res) if res.is_integer() else res)

    def power(self, base: float, exponent: float) -> str:
        """
        Raise base to the power of exponent.
        :param base: Base number
        :param exponent: Exponent
        :return: base raised to exponent
        """
        try:
            res = math.pow(base, exponent)
            return str(int(res) if res.is_integer() else res)
        except Exception as e:
            return f"Error: {e}"

    def sqrt(self, n: float) -> str:
        """
        Calculate square root of n.
        :param n: Number
        :return: Square root of n
        """
        if n < 0:
            return "Error: Cannot take square root of negative number"
        res = math.sqrt(n)
        return str(int(res) if res.is_integer() else res)

    def percentage(self, value: float, total: float) -> str:
        """
        Calculate percentage (value / total * 100).
        :param value: Part value
        :param total: Total value
        :return: Percentage formatted string
        """
        if total == 0:
            return "Error: Total cannot be zero"
        return f"{(value / total) * 100:.2f}%"
