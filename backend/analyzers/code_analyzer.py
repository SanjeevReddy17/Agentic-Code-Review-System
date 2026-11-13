import ast
import io
import tokenize


def analyze_code(source_code):

    results = []

    # Check Python syntax
    try:
        ast.parse(source_code)
        syntax_status = "Valid"
    except SyntaxError as error:
        syntax_status = "Error"

        results.append({
            "type": "Syntax Error",
            "line": error.lineno,
            "message": error.msg,
            "severity": "High"
        })

    if syntax_status == "Valid":

        # Check for long lines
        lines = source_code.splitlines()

        for line_number, line in enumerate(lines, start=1):

            if len(line) > 100:
                results.append({
                    "type": "Code Quality",
                    "line": line_number,
                    "message": "Line exceeds 100 characters.",
                    "severity": "Low"
                })

        # Check for unused-looking imports (basic heuristic)
        try:
            tokens = tokenize.generate_tokens(
                io.StringIO(source_code).readline
            )

            import_count = sum(
                1 for token in tokens
                if token.type == tokenize.NAME
                and token.string in ["import", "from"]
            )

            if import_count > 0:
                results.append({
                    "type": "Code Quality",
                    "line": 1,
                    "message": f"Found {import_count} import statement(s). "
                               "Review whether all imports are needed.",
                    "severity": "Info"
                })

        except tokenize.TokenError:
            pass

    return {
        "syntax_status": syntax_status,
        "total_issues": len(results),
        "issues": results
    }