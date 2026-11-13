from flask import Blueprint, request, jsonify, send_from_directory
from agents.workflow_agent import run_agentic_workflow
from utils.report_generator import generate_pdf_report
from database.db import get_connection

import os
import json

review_bp = Blueprint("review", __name__)


# Calculate code quality score
def calculate_quality_score(results):

    code_issues = results.get("code_analysis", {}).get(
        "total_issues", 0
    )

    security_issues = results.get("security_analysis", {}).get(
        "total_security_issues", 0
    )

    score = 100 - (code_issues * 10) - (security_issues * 15)

    return max(0, min(100, score))


# Save review results into SQLite
def save_review(source_code, results):

    code_analysis = results.get("code_analysis", {})
    security_analysis = results.get("security_analysis", {})

    quality_score = calculate_quality_score(results)

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO reviews (
                source_code,
                syntax_status,
                code_issues,
                security_issues,
                quality_score,
                ai_review,
                full_results_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source_code,
                code_analysis.get("syntax_status", "Unknown"),
                code_analysis.get("total_issues", 0),
                security_analysis.get("total_security_issues", 0),
                quality_score,
                results.get("ai_review", ""),
                json.dumps(results)
            )
        )

        review_id = cursor.lastrowid
        connection.commit()

        return review_id

    finally:
        connection.close()


# Analyze submitted Python code
@review_bp.route("/api/review", methods=["POST"])
def review_code():

    data = request.get_json(silent=True) or {}

    source_code = data.get("source_code", "")

    if not isinstance(source_code, str) or not source_code.strip():
        return jsonify({
            "error": "Please provide valid Python source code."
        }), 400

    try:
        results = run_agentic_workflow(source_code)

        review_id = save_review(source_code, results)

        results["review_id"] = review_id

        return jsonify(results)

    except Exception as error:
        return jsonify({
            "error": f"Code review failed: {str(error)}"
        }), 500


# Download PDF report
@review_bp.route("/api/download-report", methods=["POST"])
def download_report():

    data = request.get_json(silent=True) or {}

    results = data.get("results")
    source_code = data.get("source_code", "")

    if not isinstance(results, dict) or not isinstance(source_code, str):
        return jsonify({
            "error": "Invalid report data."
        }), 400

    try:
        filename = generate_pdf_report(results, source_code)

        reports_folder = os.path.abspath("reports")

        return send_from_directory(
            reports_folder,
            filename,
            as_attachment=True
        )

    except Exception as error:
        return jsonify({
            "error": f"PDF generation failed: {str(error)}"
        }), 500


# Get all previous reviews
@review_bp.route("/api/history", methods=["GET"])
def get_review_history():

    connection = get_connection()

    try:
        reviews = connection.execute(
            """
            SELECT
                id,
                created_at,
                syntax_status,
                code_issues,
                security_issues,
                quality_score
            FROM reviews
            ORDER BY id DESC
            """
        ).fetchall()

        return jsonify([
            dict(review) for review in reviews
        ])

    finally:
        connection.close()


# Get complete details of one review
@review_bp.route("/api/history/<int:review_id>", methods=["GET"])
def get_review_details(review_id):

    connection = get_connection()

    try:
        review = connection.execute(
            "SELECT * FROM reviews WHERE id = ?",
            (review_id,)
        ).fetchone()

        if review is None:
            return jsonify({
                "error": "Review not found."
            }), 404

        review_data = dict(review)

        review_data["full_results"] = json.loads(
            review_data.pop("full_results_json")
        )

        return jsonify(review_data)

    except json.JSONDecodeError:
        return jsonify({
            "error": "Stored review data is invalid."
        }), 500

    finally:
        connection.close()


# Get overall review statistics
@review_bp.route("/api/statistics", methods=["GET"])
def get_review_statistics():

    connection = get_connection()

    try:
        statistics = connection.execute(
            """
            SELECT
                COUNT(*) AS total_reviews,
                COALESCE(AVG(quality_score), 0) AS average_quality_score,
                COALESCE(SUM(security_issues), 0) AS total_security_issues,
                COALESCE(SUM(code_issues), 0) AS total_code_issues
            FROM reviews
            """
        ).fetchone()

        return jsonify({
            "total_reviews": statistics["total_reviews"],
            "average_quality_score": round(
                statistics["average_quality_score"], 2
            ),
            "total_security_issues": statistics["total_security_issues"],
            "total_code_issues": statistics["total_code_issues"]
        })

    finally:
        connection.close()


# Search a review by ID
@review_bp.route("/api/search/<int:review_id>", methods=["GET"])
def search_review(review_id):

    connection = get_connection()

    try:
        review = connection.execute(
            """
            SELECT
                id,
                created_at,
                syntax_status,
                code_issues,
                security_issues,
                quality_score
            FROM reviews
            WHERE id = ?
            """,
            (review_id,)
        ).fetchone()

        if review is None:
            return jsonify({
                "error": "Review not found."
            }), 404

        return jsonify(dict(review))

    finally:
        connection.close()


# Delete a review by ID
@review_bp.route("/api/history/<int:review_id>", methods=["DELETE"])
def delete_review(review_id):

    connection = get_connection()

    try:
        cursor = connection.execute(
            "DELETE FROM reviews WHERE id = ?",
            (review_id,)
        )

        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({
                "error": "Review not found."
            }), 404

        return jsonify({
            "message": "Review deleted successfully.",
            "deleted_review_id": review_id
        })

    finally:
        connection.close()