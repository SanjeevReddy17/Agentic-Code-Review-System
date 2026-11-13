import ast


def analyze_security(source_code):

    issues = []

    try:
        tree = ast.parse(source_code)

        for node in ast.walk(tree):

            # Detect dangerous eval() usage
            if isinstance(node, ast.Call):

                if isinstance(node.func, ast.Name):

                    if node.func.id == "eval":
                        issues.append({
                            "type": "Security Vulnerability",
                            "line": node.lineno,
                            "message": "Use of eval() can execute arbitrary code.",
                            "severity": "High"
                        })

                    elif node.func.id == "exec":
                        issues.append({
                            "type": "Security Vulnerability",
                            "line": node.lineno,
                            "message": "Use of exec() can execute arbitrary code.",
                            "severity": "High"
                        })

            # Detect hardcoded passwords
            if isinstance(node, ast.Assign):

                for target in node.targets:

                    if isinstance(target, ast.Name):

                        name = target.id.lower()

                        if "password" in name or "secret" in name:

                            issues.append({
                                "type": "Security Vulnerability",
                                "line": node.lineno,
                                "message": "Possible hardcoded password or secret.",
                                "severity": "Medium"
                            })

    except SyntaxError as error:

        issues.append({
            "type": "Syntax Error",
            "line": error.lineno,
            "message": "Security analysis could not complete because the code contains a syntax error.",
            "severity": "High"
        })

    return {
        "total_security_issues": len(issues),
        "security_issues": issues
    }