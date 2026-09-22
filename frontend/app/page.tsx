"use client";

import { useEffect, useState } from "react";
import Chart from "../components/Chart";

type Result = {
  success: boolean;
  question?: string;
  sql?: string;
  columns?: string[];
  data?: Record<string, unknown>[];
  insight?: string;
  error?: string;

  chart_config?: {
  chart_type: "bar" | "line" | "pie" | "scatter" | "kpi";
  x_column: string;
  y_column: string;
  title: string;
  orientation: "horizontal" | "vertical";
};
};

export default function Home() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<Result | null>(null);
  const [loading, setLoading] = useState(false);

  const [conversation, setConversation] = useState<
    { question: string; answer: string; sql?: string }[]
  >([]);

  useEffect(() => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      window.location.href = "/login";
    }
  }, []);

  function handleLogout() {
    localStorage.removeItem("access_token");
    window.location.href = "/login";
  }

  const askQuestion = async () => {
    if (!question.trim()) return;

    const token = localStorage.getItem("access_token");

    // If token is missing, go back to login
    if (!token) {
      window.location.href = "/login";
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(
        "https://ai-business-intelligence-1-pwvg.onrender.com/api/ask",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            question: question.trim(),
            conversation,
          }),
        }
      );

      const data = await response.json();

      // If token expired or invalid
      if (response.status === 401) {
        localStorage.removeItem("access_token");
        window.location.href = "/login";
        return;
      }

      setResult(data);

      if (data.success && data.insight) {
        setConversation((prev) => [
          ...prev,
          {
            question: question.trim(),
            answer: data.insight,
            sql: data.sql,
          },
        ]);
      }
    } catch {
      setResult({
        success: false,
        error: "Could not connect to the backend.",
      });
    } finally {
      setLoading(false);
    }
  };

  const examples = [
    "What was our total sales?",
    "Which product had the highest sales?",
    "Show me monthly sales for 2026.",
    "Which products are running low in inventory?",
  ];

  return (
    <main className="min-h-screen bg-gray-100 p-6 md:p-10">
      <div className="mx-auto max-w-6xl">

        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              AI Business Intelligence
            </h1>

            <p className="mt-2 text-gray-600">
              Ask questions about your business data using natural language.
            </p>
          </div>

          <button
            onClick={handleLogout}
            className="cursor-pointer rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700"
          >
            Logout
          </button>
        </div>

        {/* Question Card */}
        <div className="rounded-2xl bg-white p-6 shadow-sm">
          <label className="mb-3 block text-sm font-semibold text-gray-700">
            Ask a business question
          </label>

          <div className="flex flex-col gap-3 md:flex-row">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  askQuestion();
                }
              }}
              placeholder="Example: What was our total sales?"
              className="flex-1 rounded-xl border border-gray-300 px-4 py-3 text-gray-900 outline-none focus:border-blue-500"
            />

            <button
              onClick={askQuestion}
              disabled={loading || !question.trim()}
              className="rounded-xl bg-blue-600 px-7 py-3 font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Asking..." : "Ask"}
            </button>
          </div>
        </div>

        {/* Example Questions */}
        <div className="mt-6">
          <p className="mb-3 text-sm font-semibold text-gray-700">
            Try an example
          </p>

          <div className="flex flex-wrap gap-3">
            {examples.map((example) => (
              <button
                key={example}
                onClick={() => setQuestion(example)}
                className="rounded-full border border-gray-300 bg-white px-4 py-2 text-sm text-gray-700 transition hover:bg-gray-50"
              >
                {example}
              </button>
            ))}
          </div>
        </div>

        {/* Loading */}
        {loading && (
          <div className="mt-8 rounded-2xl bg-white p-8 text-center shadow-sm">
            <p className="font-medium text-gray-700">
              AI is analyzing your question...
            </p>

            <p className="mt-1 text-sm text-gray-500">
              Generating SQL and querying the database.
            </p>
          </div>
        )}

        {/* Result */}
        {result && !loading && (
          <div className="mt-8 space-y-6">
            {result.success ? (
              <>
                {/* Result Header */}
                <div className="rounded-2xl bg-white p-6 shadow-sm">
                  <p className="text-sm font-medium text-gray-500">
                    Your question
                  </p>

                  <h2 className="mt-1 text-xl font-semibold text-gray-900">
                    {result.question}
                  </h2>
                </div>

                {/* AI Insight */}
                {result.insight && (
                  <div className="rounded-2xl bg-blue-50 p-6 shadow-sm">
                    <h3 className="mb-2 text-lg font-semibold text-blue-900">
                      AI Business Insight
                    </h3>

                    <p className="leading-7 text-blue-800">
                      {result.insight}
                    </p>
                  </div>
                )}

                {/* SQL */}
                <div className="rounded-2xl bg-white p-6 shadow-sm">
                  <h3 className="mb-3 text-lg font-semibold text-gray-900">
                    Generated SQL
                  </h3>

                  <pre className="overflow-x-auto rounded-xl bg-gray-900 p-5 text-sm leading-6 text-green-400">
                    {result.sql}
                  </pre>
                </div>

                {/* Data */}
                <div className="rounded-2xl bg-white p-6 shadow-sm">
                  <h3 className="mb-4 text-lg font-semibold text-gray-900">
                    Query Result
                  </h3>

                  {result.data && result.data.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="min-w-full border-collapse">
                        <thead>
                          <tr className="border-b bg-gray-50">
                            {result.columns?.map((column) => (
                              <th
                                key={column}
                                className="px-4 py-3 text-left text-sm font-semibold text-gray-700"
                              >
                                {column}
                              </th>
                            ))}
                          </tr>
                        </thead>

                        <tbody>
                          {result.data.map((row, rowIndex) => (
                            <tr
                              key={rowIndex}
                              className="border-b last:border-b-0"
                            >
                              {result.columns?.map((column) => (
                                <td
                                  key={column}
                                  className="px-4 py-3 text-sm text-gray-800"
                                >
                                  {String(row[column])}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <p className="text-gray-500">
                      No data was returned.
                    </p>
                  )}
                </div>

                {/* Chart */}
                {result.columns &&
                  result.data &&
                  result.columns.length >= 2 && (
                    <Chart
                      columns={result.columns}
                      data={result.data}
                      question={result.question}
                      chartConfig={result.chart_config}
                    />
                  )}
              </>
            ) : (
              <div className="rounded-2xl bg-red-50 p-6 text-red-700">
                <h3 className="font-semibold">
                  Something went wrong
                </h3>

                <p className="mt-1 text-sm">
                  {result.error}
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}