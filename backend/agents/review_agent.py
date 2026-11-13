from google import genai
from google.genai import types

from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-3.5-flash-lite"


def generate_ai_review(source_code, code_results, security_results):

    prompt = f"""
    You are an expert AI Code Review Assistant.

    Analyze the following Python source code.

    SOURCE CODE:
    {source_code}

    CODE ANALYSIS:
    {code_results}

    SECURITY ANALYSIS:
    {security_results}

    Tasks:
    1. Explain programming errors.
    2. Identify security vulnerabilities.
    3. Explain why issues are dangerous.
    4. Suggest solutions.
    5. Generate improved Python code.
    6. Recommend performance improvements.
    7. Assess overall code quality.

    Never execute the submitted code.
    Clearly distinguish potential issues from confirmed issues.
    """

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=3000
            )
        )

        return response.text or "No AI response received."

    except Exception as error:
        return f"AI review failed: {str(error)}"