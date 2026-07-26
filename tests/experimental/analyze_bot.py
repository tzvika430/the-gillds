import ast

FILE = "bot/src/bot.py"

print("=== BOT STATIC ANALYSIS ===")

with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

tree = ast.parse(code)

functions = []
handlers = []

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        functions.append(node.name)

    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == "message_handler":
                handlers.append("message_handler")

print("\nFunctions:")
for f in functions:
    print("-", f)

print("\nHandlers found:", len(handlers))
print("Lines:", len(code.splitlines()))
print("\nSTATUS: COMPLETE")
