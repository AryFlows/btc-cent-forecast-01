# Frost Drift — btc-cent-forecast-01

Forecast Bitcoin's (cbBTC/USDC, Orca) price 4 hours ahead from 72 hours of
one-minute closes.

**Model:** the OLS slope of log-price over the last 48 hours (2,880 closes),
extrapolated 240 minutes: `guess = last_close * exp(slope * 240)`. No mean
reversion, no short-window momentum, no fitted intercept — the drift is
re-estimated from each case. See the header comment in `main.ts` for the
full rationale and the rejected alternatives.

**Local practice results** (kit's six practice cases; p05's target is not in
the kit, so p00–p04 are scored against exact actuals, and the walk-forward
uses 33 half-hourly checkpoints over the stitched practice timeline):

| model | walk-forward MAE | practice p00–p04 MAE |
|---|---|---|
| persistence (house baseline) | 50,162 cents | 47,055 cents |
| **Frost Drift (this entry)** | **46,483 cents** | **41,026 cents** |

Per-case practice errors (cents): p00 20,262 / p01 66,532 / p02 37,946 /
p03 66,448 / p04 13,943. Baseline on the same five: 31,711 / 76,697 /
47,033 / 56,685 / 23,147. The reported 6-case baseline is 44,522 cents.

A practice score is no guide to the final. The claim is only that the model
beats persistence on every practice slice measured, with a mechanism —
multi-day drift persistence — that is not fitted to the practice window's
direction.

**Run:** `node main.ts` (Node 22, standard library only). Reads
`$MAKEFUN_INPUT_DIR` (else `/input`), writes `$MAKEFUN_OUTPUT_DIR`
(else `/output`). Deterministic; ~0.2 s for six cases.

**Files:** `main.ts` (entrypoint), `LICENSE` (MIT), `package.json`
(`{"type": "module"}`, silences Node's module-type warning),
`.makefun/owner.json` (claim file), `analysis/` (backtest scripts and
`ANALYSIS.md` documenting the model selection).
