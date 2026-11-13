from analyzers.code_analyzer import analyze_code
from analyzers.security_analyzer import analyze_security
from agents.review_agent import generate_ai_review


def run_agentic_workflow(source_code):

    # Agent 1: Code Analysis
    code_results = analyze_code(source_code)

    # Agent 2: Security Analysis
    security_results = analyze_security(source_code)

    # Agent 3: AI Review
    ai_results = generate_ai_review(
        source_code,
        code_results,
        security_results
    )

    # Agent 4: Review Summary
    workflow_results = {
        "workflow": "Agentic Code Review Workflow",
        "code_analysis": code_results,
        "security_analysis": security_results,
        "ai_review": ai_results,
        "status": "Workflow completed"
    }

    return workflow_results