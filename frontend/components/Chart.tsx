"use client";

import dynamic from "next/dynamic";

const Plot = dynamic(() => import("react-plotly.js"), {
  ssr: false,
});

type ChartConfig = {
  chart_type: "bar" | "line" | "pie" | "scatter" | "kpi";
  x_column: string;
  y_column: string;
  title: string;
  orientation: "horizontal" | "vertical";
};

type ChartProps = {
  columns: string[];
  data: Record<string, unknown>[];
  question?: string;
  chartConfig?: ChartConfig;
};

function formatNumber(value: unknown): string {
  const number = Number(value);

  if (Number.isNaN(number)) {
    return String(value);
  }

  if (Math.abs(number) >= 1_000_000_000) {
    return `${(number / 1_000_000_000).toFixed(2)}B`;
  }

  if (Math.abs(number) >= 1_000_000) {
    return `${(number / 1_000_000).toFixed(2)}M`;
  }

  if (Math.abs(number) >= 1_000) {
    return `${(number / 1_000).toFixed(2)}K`;
  }

  return number.toLocaleString(undefined, {
    maximumFractionDigits: 2,
  });
}

function formatColumnName(column: string): string {
  return column
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

export default function Chart({
  columns,
  data,
  chartConfig,
}: ChartProps) {
  if (!columns || !data || data.length === 0 || !chartConfig) {
    return null;
  }

  const {
    chart_type,
    x_column,
    y_column,
    title,
    orientation,
  } = chartConfig;

  /*
   * Make sure AI-selected columns actually exist
   */
  if (
    !columns.includes(x_column) &&
    chart_type !== "kpi"
  ) {
    return null;
  }

  if (!columns.includes(y_column)) {
    return null;
  }

  /*
   * KPI
   */
  if (chart_type === "kpi") {
    const value = data[0][y_column];

    return (
      <div className="mt-6 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        <h3 className="mb-4 text-lg font-semibold text-gray-900">
          Key Metric
        </h3>

        <div className="py-8 text-center">
          <p className="text-sm font-medium uppercase tracking-wide text-gray-500">
            {y_column.replaceAll("_", " ")}
          </p>

<p className="mt-3 text-4xl font-bold text-blue-600">
  {formatNumber(value)}
</p>
        </div>
      </div>
    );
  }

  const xValues = data.map((row) => row[x_column]);

  const yValues = data.map((row) => {
    const value = row[y_column];

    if (typeof value === "number") {
      return value;
    }

    const parsed = Number(value);

    return Number.isNaN(parsed) ? 0 : parsed;
  });

  /*
   * Pie Chart
   */
  if (chart_type === "pie") {
    return (
      <div className="mt-6 rounded-2xl border border-gray-200 bg-white p-4">
        <h3 className="mb-4 text-lg font-semibold text-gray-900">
          {title}
        </h3>

        <div className="h-[450px] w-full">
          <Plot
            data={[
              {
                labels: xValues,
                values: yValues,
                type: "pie",
                textinfo: "label+percent",
                hoverinfo: "label+value+percent",
              },
            ]}
            layout={{
              autosize: true,
              margin: {
                l: 30,
                r: 30,
                t: 30,
                b: 30,
              },
            }}
            config={{
              responsive: true,
              displaylogo: false,
            }}
            style={{
              width: "100%",
              height: "100%",
            }}
            useResizeHandler={true}
          />
        </div>
      </div>
    );
  }

  /*
   * Scatter Chart
   */
  if (chart_type === "scatter") {
    return (
      <div className="mt-6 rounded-2xl border border-gray-200 bg-white p-4">
        <h3 className="mb-4 text-lg font-semibold text-gray-900">
          {title}
        </h3>

        <div className="h-[450px] w-full">
          <Plot
            data={[
              {
                x: xValues,
                y: yValues,
                type: "scatter",
                mode: "markers",
              },
            ]}
            layout={{
              autosize: true,
              margin: {
                l: 70,
                r: 30,
                t: 30,
                b: 80,
              },
              xaxis: {
                title: x_column,
              },
              yaxis: {
                title: y_column,
              },
            }}
            config={{
              responsive: true,
              displaylogo: false,
            }}
            style={{
              width: "100%",
              height: "100%",
            }}
            useResizeHandler={true}
          />
        </div>
      </div>
    );
  }

  /*
   * Line / Bar Chart
   */
  return (
    <div className="mt-6 rounded-2xl border border-gray-200 bg-white p-4">
      <h3 className="mb-4 text-lg font-semibold text-gray-900">
        {title}
      </h3>

      <div className="h-[450px] w-full">
        <Plot
          data={[
            {
  x:
    chart_type === "bar" && orientation === "horizontal"
      ? yValues
      : xValues,

  y:
    chart_type === "bar" && orientation === "horizontal"
      ? xValues
      : yValues,

  type: chart_type,
  orientation:
    chart_type === "bar" && orientation === "horizontal"
      ? "h"
      : "v",

  mode:
    chart_type === "line"
      ? "lines+markers"
      : undefined,

  marker: {
    opacity: 0.8,
  },
  hovertemplate:
  chart_type === "bar"
    ? `%{x}: %{y:,.2f}<extra></extra>`
    : `%{x}: %{y:,.2f}<extra></extra>`,
},
          ]}
layout={{
  autosize: true,
  title: title,
  margin: {
    l: orientation === "horizontal" ? 120 : 70,
    r: 30,
    t: 60,
    b: 80,
  },

xaxis: {
  title:
    chart_type === "bar" && orientation === "horizontal"
      ? formatColumnName(y_column)
      : formatColumnName(x_column),

  tickformat:
    chart_type === "bar" && orientation === "horizontal"
      ? "~s"
      : undefined,
},

yaxis: {
  title:
    chart_type === "bar" && orientation === "horizontal"
      ? formatColumnName(x_column)
      : formatColumnName(y_column),

  tickformat: "~s",
},
  hovermode: "closest",
}}
          config={{
            responsive: true,
            displaylogo: false,
          }}
          style={{
            width: "100%",
            height: "100%",
          }}
          useResizeHandler={true}
        />
      </div>
    </div>
  );
}