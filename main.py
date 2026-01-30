import sys
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

# --- Path setup so we can import from src/ ---
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Lazy imports inside route handlers so that missing credentials
# (AWS, CMC, Binance, etc.) don\'t break app startup.

app = FastAPI(title="Crypto Bot Demo", version="1.0.0")


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    """Simple interactive UI for recruiters to play with."""
    return """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <title>Crypto Bot – Interactive Demo</title>
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <style>
    :root { font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
    body { margin: 0; padding: 0; background: #050816; color: #e5e7eb; }
    .page { max-width: 960px; margin: 0 auto; padding: 24px 16px 48px; }
    h1 { font-size: 2rem; margin-bottom: 0.25rem; }
    h2 { font-size: 1.25rem; margin-top: 2rem; }
    p { color: #9ca3af; line-height: 1.5; }
    .pill { display: inline-flex; align-items: center; gap: 6px; padding: 2px 10px; border-radius: 999px; font-size: 0.75rem; background: rgba(59,130,246,0.1); color: #93c5fd; border: 1px solid rgba(59,130,246,0.4); }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; margin-top: 18px; }
    .card { background: linear-gradient(135deg, #020617, #020617); border-radius: 14px; border: 1px solid rgba(148,163,184,0.35); padding: 16px 16px 18px; box-shadow: 0 18px 45px rgba(15,23,42,0.9); position: relative; overflow: hidden; }
    .card h3 { margin: 0 0 6px; font-size: 1.05rem; }
    .badge { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em; color: #6b7280; }
    .btn { display: inline-flex; align-items: center; justify-content: center; gap: 6px; margin-top: 12px; padding: 8px 14px; border-radius: 999px; border: none; cursor: pointer; font-size: 0.9rem; font-weight: 500; }
    .btn-primary { background: linear-gradient(135deg, #2563eb, #4f46e5); color: white; box-shadow: 0 18px 30px rgba(37,99,235,0.45); }
    .btn-primary:hover { filter: brightness(1.05); }
    .btn-secondary { background: transparent; border: 1px solid rgba(148,163,184,0.5); color: #e5e7eb; }
    .btn-secondary:hover { background: rgba(15,23,42,0.8); }
    .status { margin-top: 12px; font-size: 0.85rem; color: #9ca3af; min-height: 1.2em; }
    .status.error { color: #fca5a5; }
    .status.ok { color: #6ee7b7; }
    table { width: 100%; border-collapse: collapse; font-size: 0.85rem; margin-top: 10px; }
    th, td { padding: 6px 4px; border-bottom: 1px solid rgba(31,41,55,0.9); text-align: left; }
    th { color: #9ca3af; font-weight: 500; font-size: 0.8rem; }
    tbody tr:hover { background: rgba(15,23,42,0.8); }
    code { font-size: 0.8rem; padding: 2px 5px; border-radius: 4px; background: #020617; color: #e5e7eb; }
    .footer { margin-top: 32px; font-size: 0.8rem; color: #6b7280; }
    .tagline { font-size: 0.95rem; color: #9ca3af; margin-bottom: 1rem; }
  </style>
</head>
<body>
  <div class=\"page\">
    <span class=\"pill\">Crypto • ML • Quant</span>
    <h1>Crypto Bot – Interactive Demo</h1>
    <p class=\"tagline\">Sentiment-driven recommendations, iceberg order detection, and arbitrage logic exposed as a simple web experience.</p>

    <div class=\"grid\">
      <section class=\"card\">\r
        <div class=\"badge\">Module · Sentiment Engine</div>\r
        <h3>Generate Investment Recommendations</h3>\r
        <p>Runs the sentiment + market pipeline (or a deterministic demo fallback) and returns the top picks with risk &amp; confidence.</p>\r
        <div style=\"margin-top:10px;font-size:0.8rem;color:#9ca3af;\">\r
          <label>Top N:&nbsp;<input id=\"top-n\" type=\"number\" min=\"1\" max=\"20\" value=\"5\" style=\"width:56px;padding:2px 4px;border-radius:6px;border:1px solid rgba(148,163,184,0.6);background:#020617;color:#e5e7eb;\" /></label>&nbsp;\r
          <label>Max risk:&nbsp;\r
            <select id=\"max-risk\" style=\"padding:2px 6px;border-radius:6px;border:1px solid rgba(148,163,184,0.6);background:#020617;color:#e5e7eb;\">\r
              <option value=\"Any\">Any</option>\r
              <option value=\"Low\">Low</option>\r
              <option value=\"Medium\" selected>Medium</option>\r
              <option value=\"High\">High</option>\r
            </select>\r
          </label>&nbsp;\r
          <label>Min confidence:&nbsp;<input id=\"min-confidence\" type=\"number\" min=\"0\" max=\"1\" step=\"0.05\" value=\"0.0\" style=\"width:64px;padding:2px 4px;border-radius:6px;border:1px solid rgba(148,163,184,0.6);background:#020617;color:#e5e7eb;\" /></label>\r
          <div style=\"margin-top:6px;\">Focus symbol (optional):&nbsp;<input id=\"symbol-filter\" type=\"text\" placeholder=\"e.g. BTC\" style=\"width:90px;padding:2px 4px;border-radius:6px;border:1px solid rgba(148,163,184,0.6);background:#020617;color:#e5e7eb;\" /></div>\r
        </div>\r
        <button class=\"btn btn-primary\" onclick=\"runRecommendations()\">▶ Run Recommendations</button>\r
        <div id=\"rec-status\" class=\"status\"></div>\r
        <div id=\"rec-results\"></div>\r
      </section>

      <section class=\"card\">
        <div class=\"badge\">Module · Iceberg Detection</div>
        <h3>Iceberg Order Detector</h3>
        <p>Neural network over live Binance order book data to flag hidden liquidity. Keeps errors isolated if credentials aren\'t set.</p>
        <button class=\"btn btn-secondary\" onclick=\"runIceberg()\">▶ Analyze BTCUSDT</button>
        <div id=\"iceberg-status\" class=\"status\"></div>
        <pre id=\"iceberg-output\" style=\"margin-top:6px;font-size:0.8rem;white-space:pre-wrap;color:#e5e7eb;\"></pre>
      </section>

      <section class=\"card\">
        <div class=\"badge\">Module · Arbitrage Logic</div>
        <h3>How the Arbitrage Scanner Works</h3>
        <p>Streams live order books from Binance &amp; Kraken, surfaces cross-exchange spreads, and lets a human confirm execution.</p>
        <button class=\"btn btn-secondary\" onclick=\"showArbInfo()\">ℹ View Architecture Notes</button>
        <div id=\"arb-info\" class=\"status\"></div>
      </section>
    </div>

    <div class=\"footer\">
      <p><strong>How to run locally</strong>: <code>uvicorn main:app --reload</code></p>
      <p>Designed to be deployed as a single FastAPI app on Render or any container-based host.</p>
    </div>
  </div>

  <script>
    async function runRecommendations() {
      const status = document.getElementById('rec-status');
      const resultsEl = document.getElementById('rec-results');
      status.textContent = 'Running pipeline… this can take a few seconds.';
      status.className = 'status';
      resultsEl.innerHTML = '';

      const topN = parseInt(document.getElementById('top-n').value, 10) || 5;
      const maxRisk = document.getElementById('max-risk').value || 'Any';
      const minConfidence = parseFloat(document.getElementById('min-confidence').value) || 0.0;
      const symbolRaw = document.getElementById('symbol-filter').value || '';
      const payload = {
        top_n: Math.min(Math.max(topN, 1), 20),
        max_risk: maxRisk,
        min_confidence: Math.min(Math.max(minConfidence, 0.0), 1.0),
        symbol: symbolRaw.trim() ? symbolRaw.trim().toUpperCase() : null,
      };

      try {
        const res = await fetch('/api/recommendations', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!res.ok || data.status === 'error') {
          status.textContent = data.message || 'Pipeline failed. See server logs.';
          status.className = 'status error';
          return;
        }

        const mode = data.mode === 'live' ? 'Live data' : 'Demo fallback';
        status.textContent = `Success (${mode}). Showing top ${data.recommendations.length} assets.`;
        status.className = 'status ok';

        if (!data.recommendations.length) {
          resultsEl.innerHTML = '<p>No recommendations available.</p>';
          return;
        }

        const rows = data.recommendations.map((rec, idx) => `
          <tr>
            <td>${idx + 1}</td>
            <td>${rec.name} <span style=\"color:#9ca3af;font-size:0.8rem;\">(${rec.symbol})</span></td>
            <td>${rec.recommendation}</td>
            <td>${rec.risk_level}</td>
            <td>${rec.potential}</td>
            <td>${rec.metrics ? '$' + rec.metrics.price.toFixed(2) : '–'}</td>
            <td>${rec.metrics ? rec.metrics.percent_change_24h.toFixed(2) + '%' : '–'}</td>
            <td>${rec.confidence ? rec.confidence.toFixed(3) : '–'}</td>
          </tr>`).join('');

        resultsEl.innerHTML = `
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Asset</th>
                <th>Call</th>
                <th>Risk</th>
                <th>Potential</th>
                <th>Price</th>
                <th>24h</th>
                <th>Confidence</th>
              </tr>
            </thead>
            <tbody>${rows}</tbody>
          </table>`;
      } catch (err) {
        status.textContent = 'Unexpected error. See console/logs.';
        status.className = 'status error';
        console.error(err);
      }
    }

    async function runIceberg() {
      const status = document.getElementById('iceberg-status');
      const out = document.getElementById('iceberg-output');
      status.textContent = 'Contacting iceberg detector…';
      status.className = 'status';
      out.textContent = '';

      try {
        const res = await fetch('/api/iceberg-demo', { method: 'POST' });
        const data = await res.json();
        if (!res.ok || data.status === 'error') {
          status.textContent = data.message || 'Iceberg detector is not configured.';
          status.className = 'status error';
          return;
        }
        status.textContent = 'Request completed.';
        status.className = 'status ok';
        out.textContent = data.output;
      } catch (err) {
        status.textContent = 'Unexpected error. See console/logs.';
        status.className = 'status error';
        console.error(err);
      }
    }

    function showArbInfo() {
      const el = document.getElementById('arb-info');
      el.className = 'status';
      el.innerHTML = `
        <strong>Design:</strong> <code>src/arbitrage/arbitrage_checker.py</code> maintains WebSocket connections to
        Binance and Kraken, continuously watches the spread on BTC/USDT, then asks the human whether to execute the
        paired limit orders when a profitable opportunity appears. Credentials are pulled securely from AWS Secrets Manager.
      `;
    }
  </script>
</body>
</html>
"""


RISK_ORDER = {"Low": 0, "Medium": 1, "High": 2}


class RecommendationRequest(BaseModel):
    top_n: int = 5
    max_risk: str = "Any"  # One of: Any, Low, Medium, High
    min_confidence: float = 0.0
    symbol: Optional[str] = None


def _apply_filters(raw_recs: List[Dict[str, Any]], params: RecommendationRequest) -> List[Dict[str, Any]]:
    """Apply user-provided filters (top_n, risk, confidence, symbol) to recommendations."""
    recs = list(raw_recs)

    # Normalize confidence to float and drop clearly invalid entries
    cleaned: List[Dict[str, Any]] = []
    for r in recs:
        conf_val = r.get("confidence", 0.0)
        try:
            r["confidence"] = float(conf_val)
        except Exception:
            r["confidence"] = 0.0
        cleaned.append(r)
    recs = cleaned

    # Optional symbol focus
    if params.symbol:
        sym = params.symbol.upper()
        recs = [r for r in recs if str(r.get("symbol", "")).upper() == sym]

    # Minimum confidence filter
    recs = [r for r in recs if float(r.get("confidence", 0.0)) >= params.min_confidence]

    # Risk filter (Low < Medium < High)
    if params.max_risk != "Any":
        max_idx = RISK_ORDER.get(params.max_risk, 2)
        filtered: List[Dict[str, Any]] = []
        for r in recs:
            risk_label = str(r.get("risk_level", "")).title()
            idx = RISK_ORDER.get(risk_label)
            if idx is None or idx <= max_idx:
                filtered.append(r)
        recs = filtered

    # Bound top_n for safety
    top_n = max(1, min(params.top_n, 20))
    return recs[:top_n]


@app.post("/api/recommendations")
async def api_recommendations(payload: RecommendationRequest) -> JSONResponse:
    """Run the sentiment pipeline if possible; otherwise return a clean demo fallback.

    This is designed so that the hosted demo never completely fails just because
    live API keys / AWS credentials are missing.
    """

    # Attempt live pipeline first
    try:
        from sentiment.main import CryptoBot  # type: ignore[import]

        bot = CryptoBot()
        results: Dict[str, Any] = bot.run_pipeline()
        raw_recs: List[Dict[str, Any]] = list(results.get("recommendations") or [])
        recs = _apply_filters(raw_recs, payload)

        return JSONResponse(
            {
                "status": "ok",
                "mode": "live",
                "recommendations": recs,
            }
        )
    except Exception as exc:  # noqa: BLE001
        logging.exception("Live pipeline failed; falling back to static demo data: %s", exc)

        # Static, deterministic demo data so the UI still looks good
        demo_recs: List[Dict[str, Any]] = [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "recommendation": "STRONG BUY",
                "risk_level": "Medium",
                "potential": "High",
                "confidence": 0.91,
                "metrics": {
                    "price": 68000.0,
                    "percent_change_24h": 2.35,
                },
            },
            {
                "symbol": "ETH",
                "name": "Ethereum",
                "recommendation": "BUY",
                "risk_level": "Medium",
                "potential": "High",
                "confidence": 0.83,
                "metrics": {
                    "price": 3400.0,
                    "percent_change_24h": 1.12,
                },
            },
            {
                "symbol": "SOL",
                "name": "Solana",
                "recommendation": "MODERATE BUY",
                "risk_level": "High",
                "potential": "High",
                "confidence": 0.74,
                "metrics": {
                    "price": 150.0,
                    "percent_change_24h": 4.8,
                },
            },
        ]

        recs = _apply_filters(demo_recs, payload)

        return JSONResponse(
            {
                "status": "ok",
                "mode": "demo",
                "message": "Running in demo mode – live APIs / credentials are not configured on this server.",
                "recommendations": recs,
            }
        )


@app.post("/api/iceberg-demo")
async def api_iceberg_demo() -> JSONResponse:
    """Best-effort wrapper around the iceberg detector.

    In hosted environments without Binance credentials this will return a
    friendly explanatory message instead of a hard error.
    """

    try:
        from iceberg import iceberg_detector  # type: ignore[import]
        import io
        import contextlib

        buf = io.StringIO()
        # Capture stdout so we can surface the pretty CLI output in the UI
        with contextlib.redirect_stdout(buf):
            iceberg_detector.predict_iceberg("BTCUSDT")
        output = buf.getvalue().strip() or "Iceberg detector ran, but produced no output."

        return JSONResponse({"status": "ok", "output": output})
    except Exception as exc:  # noqa: BLE001
        logging.exception("Iceberg detector failed: %s", exc)
        return JSONResponse(
            {
                "status": "error",
                "message": (
                    "Iceberg detector is not configured on this deployment. "
                    "Set BINANCE_API_KEY / BINANCE_API_SECRET in config/.env.iceberg "
                    "and ensure the file is available at runtime."
                ),
            },
            status_code=500,
        )
