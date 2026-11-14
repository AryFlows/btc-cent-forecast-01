# Model selection — btc-cent-forecast-01

Data: the kit's six practice cases (checkpoints 2026-11-10 06:00–2026-11-11
02:00 UTC, 4 h apart). The cases overlap, so they stitch into one continuous
72 h + 20 h timeline (2026-11-07 06:01 → 2026-11-11 02:00 UTC, 5,520
one-minute closes; overlap verified byte-equal). Exact actuals for p00–p04
are the next case's checkpoint close; p05's target (2026-11-11 06:00 UTC)
is not in the kit. The reported 6-case persistence baseline is
44,521.576667 cents, consistent with the 5-case figure computed here
(47,054.66) plus an implied p05 error of ~31,856 cents.

Evaluation: (a) official practice cases p00–p04; (b) walk-forward over 33
half-hourly checkpoints, each with a full 72 h history, split into first 16
vs last 17 to check regime stability.

Findings:
- 1 h log-return autocorrelation ≈ −0.25, 4 h ≈ −0.31: mild mean reversion
  at short horizons. But fading the last 4 h return helps only in the
  second half (the bounce) and hurts in the first (the sustained drop) and
  on the official cases (48,528 vs 47,055 for persistence). Rejected.
- Short-window trends (12 h/24 h) and EMA momentum are unstable across
  halves. Rejected.
- Long-window OLS trend (48 h/72 h slope, full extrapolation) beats
  persistence in BOTH halves and on the official cases. 48 h slope:
  walk-forward 46,483, official 41,026. 72 h slope: 47,215 / 41,375.
- Damping d=1.1 looked ~1% better in-sample; not used (over-extrapolation,
  no principled basis). Blend of 48 h + 72 h slopes was not better.
- The chosen model has no tuned parameter beyond the window (48 h) and the
  extrapolation factor (1.0, i.e. no damping) — both round, defensible
  choices, not fitted decimals.

Caveat: one 4-day realisation. The final is a fresh 48 h window; a trend
reversal there would hurt this model versus persistence. The bet is that
multi-day drift persists at the 4 h horizon more often than it reverses —
the only claim the practice data supports.
