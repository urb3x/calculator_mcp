# 🧮 Calculator MCP Server

[![GitHub Repository](https://img.shields.io/badge/GitHub-urb3x%2Fcalculator__mcp-blue?logo=github)](https://github.com/urb3x/calculator_mcp)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-brightgreen.svg)](https://python.org)
[![MCP Protocol](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-orange.svg)](https://modelcontextprotocol.io/)

A Model Context Protocol (MCP) server that provides mathematical tools and safe arithmetic expression evaluation for AI models (Claude Desktop, Cursor, Antigravity, Cline, and any other MCP-compatible clients).

🔗 **GitHub Repository & MCP Link:** [https://github.com/urb3x/calculator_mcp](https://github.com/urb3x/calculator_mcp)

---

## ✨ Features

- **Basic Arithmetic:** Addition, subtraction, multiplication, division (with zero-division protection).
- **Advanced Math:** Power, square root, modulo, percentages.
- **Safe Expression Evaluator (`calculate`):** Parses and computes complex expressions using Python's AST (without unsafe `eval()`).
  - Supports trigonometric functions (`sin`, `cos`, `tan`, etc.)
  - Logarithmic functions (`log`, `log10`, `log2`)
  - Rounding & utility functions (`floor`, `ceil`, `round`, `abs`, `factorial`, `gcd`, `lcm`)
  - Mathematical constants (`pi`, `e`, `tau`, `inf`)
  - Operators: `+`, `-`, `*`, `/`, `//`, `%`, `**` (or `^`)

---

## 🛠️ Available MCP Tools

| Tool | Parameters | Description | Example |
| :--- | :--- | :--- | :--- |
| `calculate` | `expression: str` | Safely evaluates a math expression | `calculate("sqrt(25) + 3^2")` -> `14.0` |
| `add` | `a: float, b: float` | Adds two numbers | `add(12, 8)` -> `20.0` |
| `subtract` | `a: float, b: float` | Subtracts `b` from `a` | `subtract(20, 5)` -> `15.0` |
| `multiply` | `a: float, b: float` | Multiplies two numbers | `multiply(6, 7)` -> `42.0` |
| `divide` | `a: float, b: float` | Divides `a` by `b` | `divide(100, 4)` -> `25.0` |
| `power` | `base: float, exponent: float` | Raises base to exponent | `power(2, 8)` -> `256.0` |
| `sqrt` | `n: float` | Calculates square root | `sqrt(144)` -> `12.0` |
| `modulo` | `a: float, b: float` | Calculates `a % b` | `modulo(17, 5)` -> `2.0` |
| `percentage` | `value: float, total: float` | Calculates `(value / total) * 100` | `percentage(25, 200)` -> `12.5` |

---

## 🚀 Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/urb3x/calculator_mcp.git
cd calculator_mcp
```

### 2. Install dependencies

Using `pip`:
```bash
pip install -r requirements.txt
```

Or using `uv`:
```bash
uv pip install -r requirements.txt
```

---

## ⚙️ MCP Client Configuration

### Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "calculator": {
      "command": "python",
      "args": [
        "/ABSOLUTE/PATH/TO/calculator_mcp/server.py"
      ]
    }
  }
}
```

*On Windows, replace with your full path, for example:*
```json
{
  "mcpServers": {
    "calculator": {
      "command": "python",
      "args": [
        "C:\\Users\\pit2\\Desktop\\python\\mcp_calc\\server.py"
      ]
    }
  }
}
```

### Open WebUI

Open WebUI supports connecting to MCP servers via **Server-Sent Events (SSE)** or Streamable HTTP.

1. **Start the MCP server with SSE transport:**
```bash
python server.py --transport sse --port 8000
```

2. **Add to Open WebUI:**
- Go to **Admin Panel** ➔ **Settings** ➔ **External Connections** / **Tools** ➔ **MCP Servers**.
- Add a new server with URL: `http://localhost:8000/sse` (or `http://host.docker.internal:8000/sse` if Open WebUI is running inside Docker).

---

### FastMCP / UVX Execution

You can also run directly with `uvx` / `mcp`:

```bash
uv run python server.py
```

---

## 🧪 Running Tests

```bash
python test_server.py
```

---

## 📄 License

MIT License. Open source and free to use.

