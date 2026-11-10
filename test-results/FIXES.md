# Corrections to the dashboard test findings

The original [REPORT.md](REPORT.md) records the baseline failures and is preserved. The seven failed scenarios map to the corrections below.

1. **Incorrect best/worst performer labels (scenario 2).** Yahoo returns columns in a different order from the portfolio. The holdings table previously assigned unlabeled return values to the portfolio's ticker list. `calculate_stock_performance` now aligns total returns and weights by ticker before building the table, so each return stays with its stock.

2. **Incorrect weighted analytics (scenario 18).** A positional weight list could allocate MSFT's weight to JNJ's prices. The loader now returns price columns in requested order, and dashboard weights are a ticker-indexed Series. Weighted returns explicitly align weights to price columns and reject mismatched labels. Risk metrics, rolling volatility, growth, sector allocation, and both comparison outputs use these labeled weights. A 100% MSFT allocation therefore tracks MSFT's returns regardless of provider column order.

3. **Crash when adding a valid stock (scenario 9).** Clearing `new_ticker` after its widget was instantiated violated Streamlit's session-state rules. The Add button now uses a callback, which validates the stock, appends it, and clears the input before the next page render. Streamlit reruns automatically after the callback; the obsolete rerun call is removed from this path.

4. **Crash when removing a holding (scenario 10).** Removal now calls the supported `st.rerun()` API. Removing the final holding shows an invitation to add a stock or reset, instead of dividing by zero while calculating equal weights. Users can add a new holding from that empty state.

5. **Invalid ticker accepted (scenario 8).** A metadata dictionary without an instrument name no longer falls back to the supplied ticker as if validation had succeeded. Validation accepts a long or short instrument name and also requires usable historical prices in the selected period before changing the holdings. Validation failures leave the portfolio intact and display a recoverable message.

6. **Invalid Portfolio B crashes on empty data (scenario 16).** The loader rejects empty downloads, missing columns, fewer than two valid prices per symbol, and insufficient shared observations. Partial downloads identify the unavailable symbols rather than silently dropping them. Portfolio B catches download/validation failures and displays an error while keeping Portfolio A and the rest of the dashboard available. Missing observations are not forward-filled into fabricated returns.

7. **Duplicate Portfolio B crashes with a shape mismatch (scenario 17).** Portfolio B trims whitespace, converts symbols to uppercase, and removes duplicates while preserving their first-entered order. Equal weights are created for the unique symbols and keyed by ticker. Both its chart and table now use the shared weighted-return function.

## Verification

Verified November 10, 2026 (America/New_York):

- **Live browser suite: 19/19 passed, 0 failed** (baseline: 12/19 passed). All seven previously failing scenarios now pass, including ticker-aligned best/worst performers and the independent 100% MSFT return check. No displayed Python exceptions or uncaught browser JavaScript errors were recorded.
- **Offline regression suite: 11/11 passed.**
- `git diff HEAD --check` passed.

The offline regression suite in [test_regressions.py](../tests/test_regressions.py) covers all seven failure scenarios, reordered provider data, partial downloads, incomplete metadata, empty/insufficient history, and recovery after invalid input or removal of all holdings. Run instructions are in [tests/README.md](../tests/README.md).

Fresh live-browser evidence is saved under `test-results/playwright/fixes/`, separately from the baseline artifacts. See the [machine-readable results](playwright/fixes/results.json) and [independent reference returns](playwright/fixes/reference-returns.json). Generated screenshots, traces, and JSON remain ignored by Git. These checks cover the reported defects and existing workflows; they do not constitute a full audit of every financial formula.
