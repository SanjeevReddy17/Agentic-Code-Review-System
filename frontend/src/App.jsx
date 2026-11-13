import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:5000";

function App() {
  const [code, setCode] = useState(
`def calculate(a, b):
    result = eval("a + b")
    return result`
  );

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState("");

  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState("");

  const [selectedReview, setSelectedReview] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);

  const [statistics, setStatistics] = useState(null);
  const [statisticsLoading, setStatisticsLoading] = useState(false);

  const [searchId, setSearchId] = useState("");
  const [searchResult, setSearchResult] = useState(null);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState("");

  const [deletingId, setDeletingId] = useState(null);

  // Analyze Python code
  const analyzeCode = async () => {
    if (!code.trim()) {
      setError("Please enter Python code before analysis.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/api/review`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          source_code: code,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Analysis failed.");
      }

      setResult(data);

      await Promise.all([
        loadHistory(),
        loadStatistics(),
      ]);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Download PDF report
  const downloadReport = async () => {
    if (!result) return;

    setDownloading(true);
    setError("");

    try {
      const response = await fetch(
        `${API_URL}/api/download-report`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            results: result,
            source_code: code,
          }),
        }
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || "PDF generation failed.");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = url;
      link.download = "Agentic_Code_Review_Report.pdf";

      document.body.appendChild(link);
      link.click();
      link.remove();

      window.URL.revokeObjectURL(url);

    } catch (err) {
      setError(err.message);
    } finally {
      setDownloading(false);
    }
  };

  // Load review history
  const loadHistory = async () => {
    setHistoryLoading(true);
    setHistoryError("");

    try {
      const response = await fetch(`${API_URL}/api/history`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Unable to load history.");
      }

      setHistory(data);

    } catch (err) {
      setHistoryError(err.message);
    } finally {
      setHistoryLoading(false);
    }
  };

  // Load statistics
  const loadStatistics = async () => {
    setStatisticsLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/statistics`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Unable to load statistics.");
      }

      setStatistics(data);

    } catch (err) {
      setHistoryError(err.message);
    } finally {
      setStatisticsLoading(false);
    }
  };

  // View complete review details
  const openReview = async (reviewId) => {
    setDetailsLoading(true);
    setHistoryError("");
    setSelectedReview(null);

    try {
      const response = await fetch(
        `${API_URL}/api/history/${reviewId}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Review not found.");
      }

      setSelectedReview(data);

    } catch (err) {
      setHistoryError(err.message);
    } finally {
      setDetailsLoading(false);
    }
  };

  // Search review by ID
  const searchReview = async (event) => {
    event.preventDefault();

    const id = Number(searchId);

    if (!Number.isSafeInteger(id) || id <= 0) {
      setSearchError("Enter a valid positive Review ID.");
      setSearchResult(null);
      return;
    }

    setSearchLoading(true);
    setSearchError("");
    setSearchResult(null);

    try {
      const response = await fetch(
        `${API_URL}/api/search/${id}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Review not found.");
      }

      setSearchResult(data);

    } catch (err) {
      setSearchError(err.message);
    } finally {
      setSearchLoading(false);
    }
  };

  // Delete review
  const deleteReview = async (reviewId) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete Review #${reviewId}? This cannot be undone.`
    );

    if (!confirmed) return;

    setDeletingId(reviewId);
    setHistoryError("");
    setSearchError("");

    try {
      const response = await fetch(
        `${API_URL}/api/history/${reviewId}`,
        {
          method: "DELETE",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Unable to delete review.");
      }

      setHistory((previous) =>
        previous.filter((item) => item.id !== reviewId)
      );

      if (searchResult?.id === reviewId) {
        setSearchResult(null);
        setSearchId("");
      }

      if (selectedReview?.id === reviewId) {
        setSelectedReview(null);
      }

      await Promise.all([
        loadHistory(),
        loadStatistics(),
      ]);

      window.alert(data.message || "Review deleted successfully.");

    } catch (err) {
      setHistoryError(err.message);
    } finally {
      setDeletingId(null);
    }
  };

  // Quality calculations
  const codeIssues =
    result?.code_analysis?.total_issues ?? 0;

  const securityIssues =
    result?.security_analysis?.total_security_issues ?? 0;

  const qualityScore = Math.max(
    0,
    Math.min(100, 100 - codeIssues * 10 - securityIssues * 15)
  );

  return (
    <div className="app">

      {/* Header */}
      <header className="header">
        <div className="logo">AI</div>

        <div>
          <h1>Agentic Code Review</h1>
          <p>Intelligent AI-Powered Code Analysis Platform</p>
        </div>

        <span className="status">● AI REVIEW SYSTEM</span>
      </header>

      <main className="container">

        {/* Welcome */}
        <section className="welcome">
          <h2>Welcome to Smart Code Review</h2>

          <p>
            Analyze your source code, detect security issues,
            and receive AI-powered suggestions for improvement.
          </p>
        </section>

        {/* Statistics Dashboard */}
        <section className="statistics-section">
          <h2>Review Statistics Dashboard</h2>

          <p>Monitor your overall code review performance.</p>

          <button
            className="analyze-btn"
            onClick={loadStatistics}
            disabled={statisticsLoading}
          >
            {statisticsLoading
              ? "Loading Statistics..."
              : "Load Statistics"}
          </button>

          {statistics && (
            <div className="quality-dashboard">

              <div className="quality-card">
                <h3>Total Reviews</h3>
                <div className="quality-number">
                  {statistics.total_reviews}
                </div>
                <p>Completed Code Reviews</p>
              </div>

              <div className="quality-card">
                <h3>Average Quality Score</h3>
                <div className="quality-score">
                  {statistics.average_quality_score}
                  <span>/100</span>
                </div>
                <p>Average Code Quality</p>
              </div>

              <div className="quality-card">
                <h3>Security Vulnerabilities</h3>
                <div className="quality-number">
                  {statistics.total_security_issues}
                </div>
                <p>Total Security Issues</p>
              </div>

              <div className="quality-card">
                <h3>Programming Issues</h3>
                <div className="quality-number">
                  {statistics.total_code_issues}
                </div>
                <p>Total Code Issues</p>
              </div>

            </div>
          )}
        </section>

        {/* Code Editor */}
        <section className="editor-card">

          <div className="section-heading">
            <h2>Source Code Editor</h2>
            <span>Python</span>
          </div>

          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="Paste your Python code here..."
            spellCheck="false"
          />

          <button
            className="analyze-btn"
            onClick={analyzeCode}
            disabled={loading || !code.trim()}
          >
            {loading ? "Analyzing Code..." : "Analyze Code with AI"}
          </button>

        </section>

        {error && <div className="error">{error}</div>}

        {/* Current Review Results */}
        {result && (
          <section className="results">

            <h2>Code Review Results</h2>

            <div className="result-card">
              <h3>Workflow Status</h3>
              <p>{result.status || "Completed"}</p>
              <p>
                <strong>Review ID:</strong> {result.review_id}
              </p>
            </div>

            <h2 className="dashboard-title">
              Code Quality Dashboard
            </h2>

            <div className="quality-dashboard">

              <div className="quality-card">
                <h3>Code Quality Score</h3>
                <div className="quality-score">
                  {qualityScore}<span>/100</span>
                </div>
                <p>Estimated Quality Score</p>
              </div>

              <div className="quality-card">
                <h3>Code Issues</h3>
                <div className="quality-number">
                  {codeIssues}
                </div>
                <p>Programming Issues</p>
              </div>

              <div className="quality-card">
                <h3>Security Issues</h3>
                <div className="quality-number">
                  {securityIssues}
                </div>
                <p>Security Vulnerabilities</p>
              </div>

              <div className="quality-card">
                <h3>Syntax Status</h3>
                <div className="syntax-status">
                  {result.code_analysis?.syntax_status || "Unknown"}
                </div>
                <p>Python Code Validation</p>
              </div>

            </div>

            <div className="result-card">
              <h3>Code Analysis</h3>
              <pre>
                {JSON.stringify(result.code_analysis, null, 2)}
              </pre>
            </div>

            <div className="result-card">
              <h3>Security Analysis</h3>
              <pre>
                {JSON.stringify(result.security_analysis, null, 2)}
              </pre>
            </div>

            <div className="result-card">
              <h3>AI-Powered Review</h3>
              <pre>
                {result.ai_review || "No AI review available."}
              </pre>
            </div>

            <button
              className="download-btn"
              onClick={downloadReport}
              disabled={downloading}
            >
              {downloading
                ? "Generating PDF..."
                : "Download PDF Report"}
            </button>

          </section>
        )}

        {/* Review History */}
        <section className="history-section">

          <h2>Review History</h2>

          <p>
            View, search and manage your previously saved code reviews.
          </p>

          <button
            className="analyze-btn"
            onClick={loadHistory}
            disabled={historyLoading}
          >
            {historyLoading
              ? "Loading History..."
              : "View Review History"}
          </button>

          {historyError && (
            <div className="error">{historyError}</div>
          )}

          {/* Search Reviews */}
          <div className="search-section">

            <h3>Search Review by ID</h3>

            <form onSubmit={searchReview}>

              <input
                type="number"
                min="1"
                value={searchId}
                onChange={(e) => setSearchId(e.target.value)}
                placeholder="Enter Review ID"
              />

              <button
                type="submit"
                className="analyze-btn"
                disabled={searchLoading}
              >
                {searchLoading ? "Searching..." : "Search Review"}
              </button>

            </form>

            {searchError && (
              <div className="error">{searchError}</div>
            )}

            {searchResult && (
              <div className="history-card">

                <h3>Search Result: Review #{searchResult.id}</h3>

                <p>
                  <strong>Date:</strong> {searchResult.created_at}
                </p>

                <p>
                  <strong>Quality Score:</strong>{" "}
                  {searchResult.quality_score}/100
                </p>

                <p>
                  <strong>Security Issues:</strong>{" "}
                  {searchResult.security_issues}
                </p>

                <button
                  className="analyze-btn"
                  onClick={() => openReview(searchResult.id)}
                >
                  View Full Details
                </button>

                <button
                  className="delete-btn"
                  onClick={() => deleteReview(searchResult.id)}
                  disabled={deletingId === searchResult.id}
                >
                  {deletingId === searchResult.id
                    ? "Deleting..."
                    : "Delete Review"}
                </button>

              </div>
            )}

          </div>

          {/* Previous Reviews */}
          {history.length > 0 && (
            <div className="history-list">

              <h3>Previous Code Reviews</h3>

              {history.map((item) => (
                <div className="history-card" key={item.id}>

                  <h3>Review #{item.id}</h3>

                  <p>
                    <strong>Date:</strong> {item.created_at}
                  </p>

                  <p>
                    <strong>Quality Score:</strong>{" "}
                    {item.quality_score}/100
                  </p>

                  <p>
                    <strong>Code Issues:</strong> {item.code_issues}
                  </p>

                  <p>
                    <strong>Security Issues:</strong> {item.security_issues}
                  </p>

                  <p>
                    <strong>Syntax Status:</strong> {item.syntax_status}
                  </p>

                  <button
                    className="analyze-btn"
                    onClick={() => openReview(item.id)}
                    disabled={detailsLoading}
                  >
                    View Full Details
                  </button>

                  <button
                    className="delete-btn"
                    onClick={() => deleteReview(item.id)}
                    disabled={deletingId === item.id}
                  >
                    {deletingId === item.id
                      ? "Deleting..."
                      : "Delete Review"}
                  </button>

                </div>
              ))}

            </div>
          )}

          {history.length === 0 &&
            !historyLoading &&
            !historyError && (
              <p>No review history loaded yet.</p>
            )}

          {detailsLoading && (
            <p>Loading review details...</p>
          )}

          {/* Full Review Details */}
          {selectedReview && (
            <div className="result-card">

              <h2>Complete Review Details</h2>

              <h3>Review ID: {selectedReview.id}</h3>

              <p>
                <strong>Date:</strong> {selectedReview.created_at}
              </p>

              <p>
                <strong>Quality Score:</strong>{" "}
                {selectedReview.quality_score}/100
              </p>

              <h3>Submitted Source Code</h3>
              <pre>{selectedReview.source_code}</pre>

              <h3>Code Analysis</h3>
              <pre>
                {JSON.stringify(
                  selectedReview.full_results?.code_analysis,
                  null,
                  2
                )}
              </pre>

              <h3>Security Analysis</h3>
              <pre>
                {JSON.stringify(
                  selectedReview.full_results?.security_analysis,
                  null,
                  2
                )}
              </pre>

              <h3>Gemini AI Review</h3>
              <pre>
                {selectedReview.ai_review || "No AI review available."}
              </pre>

              <button
                className="download-btn"
                onClick={() => setSelectedReview(null)}
              >
                Close Details
              </button>

            </div>
          )}

        </section>

      </main>

      <footer>
        Agentic Code Review System | AI-Powered Software Analysis
      </footer>

    </div>
  );
}

export default App;