"""Calculator MCP Server.

Provides arithmetic, mathematical operations, and safe expression evaluation
for MCP (Model Context Protocol) clients.
"""

from __future__ import annotations

import ast
import math
import operator
from typing import Any, Callable

# Disable MCP 2.x DNS rebinding protection globally for cloud reverse proxies (Render, Cloudflare, etc.)
try:
    import mcp.server.transport_security as _ts

    async def _allow_all_requests(self, request, is_post=False):
        return None

    _ts.TransportSecurityMiddleware.validate_request = _allow_all_requests
except Exception:
    pass

# Patch SSE transport to handle CORS OPTIONS preflight requests properly on /messages/
try:
    from mcp.server.sse import SseServerTransport
    from starlette.responses import Response as _StarletteResponse
    from starlette.types import Scope, Receive, Send

    _orig_handle_post_message = SseServerTransport.handle_post_message

    async def _patched_handle_post_message(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["method"] == "OPTIONS":
            res = _StarletteResponse(
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Max-Age": "86400",
                },
            )
            return await res(scope, receive, send)
        return await _orig_handle_post_message(self, scope, receive, send)

    SseServerTransport.handle_post_message = _patched_handle_post_message
except Exception:
    pass


# Support both mcp 2.x (MCPServer) and mcp 1.x / fastmcp (FastMCP)
try:
    from mcp.server.mcpserver import MCPServer
    mcp = MCPServer("calculator-mcp")
except (ImportError, ModuleNotFoundError):
    try:
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("calculator-mcp")
    except (ImportError, ModuleNotFoundError):
        from fastmcp import FastMCP
        mcp = FastMCP("calculator-mcp")


# Supported operators for safe AST expression evaluation
_OPERATORS: dict[type[ast.AST], Callable[..., Any]] = {
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

# Supported mathematical functions
_FUNCTIONS: dict[str, Callable[..., Any]] = {
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

# Supported constants
_CONSTANTS: dict[str, float] = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
    "inf": math.inf,
}


def _eval_node(node: ast.AST) -> float:
    """Recursively evaluate an AST node safely."""
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError(f"Unsupported constant type: {type(node.value).__name__}")

    if isinstance(node, ast.Name):
        name = node.id.lower()
        if name in _CONSTANTS:
            return _CONSTANTS[name]
        raise ValueError(f"Unknown constant or variable: '{node.id}'")

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _OPERATORS:
            raise ValueError(f"Unsupported binary operator: {op_type.__name__}")
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right == 0:
            raise ZeroDivisionError("Division by zero in expression")
        return float(_OPERATORS[op_type](left, right))

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _OPERATORS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        operand = _eval_node(node.operand)
        return float(_OPERATORS[op_type](operand))

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only direct function calls are allowed (e.g. sqrt(9))")
        func_name = node.func.id.lower()
        if func_name not in _FUNCTIONS:
            raise ValueError(f"Unsupported function: '{node.func.id}'")
        args = [_eval_node(arg) for arg in node.args]
        return float(_FUNCTIONS[func_name](*args))

    raise ValueError(f"Unsupported expression syntax: {type(node).__name__}")


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together.

    Args:
        a: First number
        b: Second number
    """
    return a + b


@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract the second number from the first.

    Args:
        a: Number to subtract from
        b: Number to subtract
    """
    return a - b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers.

    Args:
        a: First number
        b: Second number
    """
    return a * b


@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide the first number by the second.

    Args:
        a: Dividend
        b: Divisor

    Raises:
        ValueError: If b is zero.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


@mcp.tool()
def power(base: float, exponent: float) -> float:
    """Raise base to the power of exponent.

    Args:
        base: Base number
        exponent: Exponent to raise the base to
    """
    return math.pow(base, exponent)


@mcp.tool()
def sqrt(n: float) -> float:
    """Calculate the square root of a number.

    Args:
        n: Number to find the square root of

    Raises:
        ValueError: If n is negative.
    """
    if n < 0:
        raise ValueError("Cannot take square root of a negative number")
    return math.sqrt(n)


@mcp.tool()
def modulo(a: float, b: float) -> float:
    """Compute the modulo (remainder of division) of a by b.

    Args:
        a: Dividend
        b: Divisor
    """
    if b == 0:
        raise ValueError("Cannot perform modulo by zero")
    return a % b


@mcp.tool()
def percentage(value: float, total: float) -> float:
    """Calculate what percentage 'value' is of 'total'.

    Args:
        value: Portion value
        total: Total value (100%)
    """
    if total == 0:
        raise ValueError("Total cannot be zero when calculating percentage")
    return (value / total) * 100.0


@mcp.tool()
def calculate(expression: str) -> float:
    """Evaluate a mathematical expression safely without using eval().

    Supports:
      - Basic operators: +, -, *, /, //, %, ** (or ^)
      - Functions: sqrt, sin, cos, tan, asin, acos, atan, log, log10, log2, exp,
                  floor, ceil, round, abs, factorial, gcd, lcm, degrees, radians
      - Constants: pi, e, tau, inf

    Examples:
      - "2 + 2 * 2" -> 6.0
      - "(10 + 5) / 3" -> 5.0
      - "sqrt(16) + 2^3" -> 12.0
      - "sin(pi / 2) + cos(0)" -> 2.0

    Args:
        expression: Mathematical expression string to evaluate
    """
    # Normalize expression (replace ^ with ** for power convenience)
    normalized = expression.replace("^", "**").strip()
    if not normalized:
        raise ValueError("Expression cannot be empty")

    try:
        parsed = ast.parse(normalized, mode="eval")
    except SyntaxError as err:
        raise ValueError(f"Syntax error in expression: {err}") from err

    return _eval_node(parsed)


def main() -> None:
    """Run the MCP calculator server."""
    import argparse
    import uvicorn
    from starlette.middleware.cors import CORSMiddleware

    import os

    default_port = int(os.environ.get("PORT", 8008))

    parser = argparse.ArgumentParser(description="Calculator MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="sse",
        help="Transport type (default: sse)",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to when using SSE or HTTP transport (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=default_port,
        help=f"Port to bind to when using SSE or HTTP transport (default: {default_port})",
    )

    args = parser.parse_args()


    if args.transport == "stdio":
        mcp.run(transport="stdio")
    elif args.transport == "sse":
        from starlette.responses import RedirectResponse
        try:
            from mcp.server.transport_security import TransportSecuritySettings
            sec = TransportSecuritySettings(enable_dns_rebinding_protection=False)
            app = mcp.sse_app(transport_security=sec, host=args.host)
        except Exception:
            app = mcp.sse_app()

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        app.add_route("/", lambda req: RedirectResponse("/sse"), methods=["GET", "POST"])
        print(f"Starting MCP Calculator Server on http://{args.host}:{args.port}/sse (CORS enabled)")
        uvicorn.run(app, host=args.host, port=args.port)
    else:
        mcp.run(transport=args.transport, host=args.host, port=args.port)




if __name__ == "__main__":
    main()


