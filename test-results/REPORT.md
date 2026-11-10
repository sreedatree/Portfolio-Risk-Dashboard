# Portfolio Risk Dashboard — Playwright test report

**Final result: 12/19 passed; 7/19 failed.**

Test date: November 10, 2026, America/New_York.

The actual Streamlit application at `http://127.0.0.1:8501` was tested with Python Playwright 1.60.0 and installed Google Chrome in headless mode. Desktop viewport: 1440 × 1000. Mobile viewport: 390 × 844. Market data came from Yahoo Finance; no prices or application functions were mocked. Each scenario used a separate browser context. Historical return checks used January 1, 2022 through January 1, 2025, with the end date excluded by Yahoo Finance.

The app's installed versions were Streamlit 1.50.0, pandas 2.3.3, and yfinance 1.2.0. The existing user edit in `src/dashboard.py` was preserved. Added files contain tests, instructions, and evidence; application behavior was not changed.

## How the test proceeded

1. Inspected the app and identified its entry point and controls.
2. Started Streamlit locally using the project's existing virtual environment.
3. Installed Playwright in a temporary directory and launched Chrome. The integrated browser was unavailable, so standalone Playwright was used.
4. Loaded the default six-stock portfolio and checked numeric metrics, six charts, and two tables.
5. Downloaded independent reference prices and matched each return explicitly to its ticker.
6. Exercised valid, reversed, and equal year selections.
7. Submitted blank, duplicate, invalid, and valid stock inputs, then tried removing a holding.
8. Dragged allocation sliders, verified normalization, tested all-zero allocation, and used Reset after changing a weight.
9. Submitted valid, blank, invalid, and duplicate Portfolio B tickers.
10. Set a 100% MSFT allocation and compared the displayed return with independently calculated MSFT performance.
11. Reloaded at a mobile viewport and checked for horizontal page overflow.
12. Saved screenshots, visible page text, traces, and machine-readable results for every final scenario.

The test harness was corrected after preliminary runs: year controls include the selected year in their accessible names, charts render asynchronously, and the sliders do not implement Home/End keyboard shortcuts. Final allocation checks use real mouse dragging and assert the slider value before checking dashboard output.

## Confirmed findings and reproduction

### High: ticker ordering corrupts holdings labels and weighted analytics

On the default dashboard, Best Performer is shown as JNJ at 346.58%, while Worst Performer is shown as MSFT at −8.03%. Independent ticker-aligned prices give NVDA at approximately 346.58% and JNJ at approximately −8.03%.

Yahoo's returned price columns are ordered `AAPL, JNJ, JPM, MSFT, NVDA, XOM`, while the portfolio order is `AAPL, MSFT, NVDA, JPM, JNJ, XOM`. `calculate_stock_performance` attaches `total_returns.values` to the separate ticker list, discarding the return index. `calculate_portfolio_returns` applies an unlabeled list of weights positionally. This also affects risk calculations after unequal weights are selected. The browser test confirmed that a 100% MSFT allocation displays -8.03%, while ticker-aligned MSFT prices give +29.18% for the same period.

Relevant code: [holdings performance](../src/calculations.py#L126), [weighted returns](../src/calculations.py#L12), [downloaded prices](../src/data_loader.py#L6).

Suggested correction: explicitly align price columns and weights by ticker before calculating or displaying any result. Preserve ticker labels when building holdings performance.

### High: adding a valid stock crashes

Enter ` googl ` in Add Stock and click Add. The app raises `StreamlitAPIException: st.session_state.new_ticker cannot be modified after the widget with key new_ticker is instantiated.` The holding is appended before the exception. The input cannot be cleared this way after the text widget has been created in the same run.

Relevant code: [Add handler](../src/dashboard.py#L84), especially line 96. An obsolete `st.experimental_rerun()` call also exists immediately afterward and would need updating once the first exception is resolved.

Suggested correction: handle stock additions and input clearing in a widget callback or a supported state transition, and use `st.rerun()`.

### High: removing a stock crashes

Click the first ✕ button beside AAPL. The app raises `AttributeError: module 'streamlit' has no attribute 'experimental_rerun'` after removing the holding from session state.

Relevant code: [Remove handler](../src/dashboard.py#L116).

Suggested correction: replace the removed rerun API with the supported rerun call.

### Medium: invalid stock validation accepts incomplete Yahoo metadata

Enter `ZZZZINVALID123` in Add Stock and click Add. Yahoo reports that the symbol does not exist, but the app still enters the successful-add branch and then hits the same input-clearing exception. `get_stock_info` falls back to the supplied ticker as the company name when Yahoo returns a dictionary without `longName`; the caller checks only whether the company equals `Invalid Ticker`.

Relevant code: [metadata fallback](../src/stock_info.py#L15), [validation decision](../src/dashboard.py#L93).

Suggested correction: validate that meaningful instrument metadata and usable price data exist before appending a symbol.

### Medium: Portfolio B accepts unusable input and then crashes

Enter `ZZZZINVALID123` in Portfolio B and press Enter: the app raises `IndexError: single positional indexer is out-of-bounds` while trying to read the last value of an empty growth series.

Enter `AAPL, AAPL` and press Enter: Yahoo returns one price column, but the app creates two weights. The app raises `ValueError: Dot product shape mismatch, (752, 1) vs (2,)`.

Relevant code: [Portfolio B parsing and calculations](../src/dashboard.py#L567), [comparison](../src/calculations.py#L45).

Suggested correction: deduplicate symbols, validate downloaded price coverage, and show a recoverable error for invalid or missing data before running comparison calculations.

### Allocation validation and Reset passed

Dragging AAPL's raw weight to 1.0 normalized its allocation to 54.5%, with each other holding at 9.1%, and changed the portfolio metrics. Dragging every raw weight to zero displayed the expected validation message and stopped metric calculations. After changing a weight, Reset restored the default six holdings at 16.7% each.

## Limits

These checks exercise the main browser workflows and selected data correctness. They are not a complete audit of financial formulas, accessibility, all screen sizes, multiple browser engines, or data-provider outages. Historical reference prices can change due to provider adjustments. Screenshots capture the visible Streamlit scrolling surface; traces contain additional DOM snapshots and interaction history. Raw artifacts are ignored by Git to avoid committing large generated files.

## Reproduce

See [test setup and commands](../tests/README.md) and the [test runner](../tests/e2e_dashboard.py). Each failing scenario includes a screenshot, page text, and trace in the table below. Raw assertions and Python exceptions are recorded in [results.json](playwright/results.json).


## Final step-by-step results

| Step | Browser check | Result | What happened | Evidence |
| --- | --- | --- | --- | --- |
| 1 | Default dashboard renders metrics charts and holdings | **PASS** | Six holdings, six charts, two tables, and numeric metrics rendered. | [screenshot](playwright/01-default-dashboard-renders-metrics-charts-and-holdings.png) / [text](playwright/01-default-dashboard-renders-metrics-charts-and-holdings.txt) / [trace](playwright/01-default-dashboard-renders-metrics-charts-and-holdings.zip) |
| 2 | Best and worst performer labels match ticker-aligned prices | **FAIL** | JNJ/MSFT shown as best/worst; reference data identifies NVDA/JNJ. | [screenshot](playwright/02-best-and-worst-performer-labels-match-ticker-aligned-prices.png) / [text](playwright/02-best-and-worst-performer-labels-match-ticker-aligned-prices.txt) / [trace](playwright/02-best-and-worst-performer-labels-match-ticker-aligned-prices.zip) |
| 3 | Invalid date range shows validation | **PASS** | 2024 to 2023 shows the date error and hides metrics. | [screenshot](playwright/03-invalid-date-range-shows-validation.png) / [text](playwright/03-invalid-date-range-shows-validation.txt) / [trace](playwright/03-invalid-date-range-shows-validation.zip) |
| 4 | Equal start and end years are rejected | **PASS** | 2023 to 2023 shows the date error. | [screenshot](playwright/04-equal-start-and-end-years-are-rejected.png) / [text](playwright/04-equal-start-and-end-years-are-rejected.txt) / [trace](playwright/04-equal-start-and-end-years-are-rejected.zip) |
| 5 | Valid date change recalculates portfolio metrics | **PASS** | Changing the start year to 2024 changes portfolio return. | [screenshot](playwright/05-valid-date-change-recalculates-portfolio-metrics.png) / [text](playwright/05-valid-date-change-recalculates-portfolio-metrics.txt) / [trace](playwright/05-valid-date-change-recalculates-portfolio-metrics.zip) |
| 6 | Empty stock input leaves portfolio usable | **PASS** | Empty Add preserves the six-stock portfolio. | [screenshot](playwright/06-empty-stock-input-leaves-portfolio-usable.png) / [text](playwright/06-empty-stock-input-leaves-portfolio-usable.txt) / [trace](playwright/06-empty-stock-input-leaves-portfolio-usable.zip) |
| 7 | Duplicate ticker trims spaces and ignores case | **PASS** | Input ` aapl ` shows the AAPL duplicate warning. | [screenshot](playwright/07-duplicate-ticker-trims-spaces-and-ignores-case.png) / [text](playwright/07-duplicate-ticker-trims-spaces-and-ignores-case.txt) / [trace](playwright/07-duplicate-ticker-trims-spaces-and-ignores-case.zip) |
| 8 | Invalid ticker is rejected without a crash | **FAIL** | ZZZZINVALID123 is accepted by validation, then input clearing raises StreamlitAPIException. | [screenshot](playwright/08-invalid-ticker-is-rejected-without-a-crash.png) / [text](playwright/08-invalid-ticker-is-rejected-without-a-crash.txt) / [trace](playwright/08-invalid-ticker-is-rejected-without-a-crash.zip) |
| 9 | Adding a valid ticker updates holdings and clears input | **FAIL** | Input ` googl ` raises StreamlitAPIException while clearing the widget state. | [screenshot](playwright/09-adding-a-valid-ticker-updates-holdings-and-clears-input.png) / [text](playwright/09-adding-a-valid-ticker-updates-holdings-and-clears-input.txt) / [trace](playwright/09-adding-a-valid-ticker-updates-holdings-and-clears-input.zip) |
| 10 | Removing a holding updates the dashboard | **FAIL** | Removing AAPL raises AttributeError for st.experimental_rerun. | [screenshot](playwright/10-removing-a-holding-updates-the-dashboard.png) / [text](playwright/10-removing-a-holding-updates-the-dashboard.txt) / [trace](playwright/10-removing-a-holding-updates-the-dashboard.zip) |
| 11 | Changing weights normalizes allocation and recalculates metrics | **PASS** | AAPL normalizes to 54.5%; the other holdings to 9.1%; metrics change. | [screenshot](playwright/11-changing-weights-normalizes-allocation-and-recalculates-metrics.png) / [text](playwright/11-changing-weights-normalizes-allocation-and-recalculates-metrics.txt) / [trace](playwright/11-changing-weights-normalizes-allocation-and-recalculates-metrics.zip) |
| 12 | All zero weights show validation instead of invalid metrics | **PASS** | All-zero allocation shows validation and stops metric calculations. | [screenshot](playwright/12-all-zero-weights-show-validation-instead-of-invalid-metrics.png) / [text](playwright/12-all-zero-weights-show-validation-instead-of-invalid-metrics.txt) / [trace](playwright/12-all-zero-weights-show-validation-instead-of-invalid-metrics.zip) |
| 13 | Reset restores default holdings and equal allocations | **PASS** | Reset restores the default six holdings at 16.7% each. | [screenshot](playwright/13-reset-restores-default-holdings-and-equal-allocations.png) / [text](playwright/13-reset-restores-default-holdings-and-equal-allocations.txt) / [trace](playwright/13-reset-restores-default-holdings-and-equal-allocations.zip) |
| 14 | Portfolio B accepts another valid portfolio | **PASS** | Input ` googl, aapl ` renders a comparison chart and table. | [screenshot](playwright/14-portfolio-b-accepts-another-valid-portfolio.png) / [text](playwright/14-portfolio-b-accepts-another-valid-portfolio.txt) / [trace](playwright/14-portfolio-b-accepts-another-valid-portfolio.zip) |
| 15 | Blank Portfolio B safely hides comparison | **PASS** | Input ` , , ` safely hides the comparison chart and table. | [screenshot](playwright/15-blank-portfolio-b-safely-hides-comparison.png) / [text](playwright/15-blank-portfolio-b-safely-hides-comparison.txt) / [trace](playwright/15-blank-portfolio-b-safely-hides-comparison.zip) |
| 16 | Invalid Portfolio B gives a friendly validation message | **FAIL** | Invalid Portfolio B causes IndexError on an empty growth series. | [screenshot](playwright/16-invalid-portfolio-b-gives-a-friendly-validation-message.png) / [text](playwright/16-invalid-portfolio-b-gives-a-friendly-validation-message.txt) / [trace](playwright/16-invalid-portfolio-b-gives-a-friendly-validation-message.zip) |
| 17 | Duplicate Portfolio B tickers are handled safely | **FAIL** | AAPL, AAPL causes a one-column/two-weight dot-product shape mismatch. | [screenshot](playwright/17-duplicate-portfolio-b-tickers-are-handled-safely.png) / [text](playwright/17-duplicate-portfolio-b-tickers-are-handled-safely.txt) / [trace](playwright/17-duplicate-portfolio-b-tickers-are-handled-safely.zip) |
| 18 | A 100 percent MSFT allocation matches MSFT actual returns | **FAIL** | 100% MSFT displays -8.03%; independently calculated MSFT return is +29.18%. | [screenshot](playwright/18-a-100-percent-msft-allocation-matches-msft-actual-returns.png) / [text](playwright/18-a-100-percent-msft-allocation-matches-msft-actual-returns.txt) / [trace](playwright/18-a-100-percent-msft-allocation-matches-msft-actual-returns.zip) |
| 19 | Mobile viewport renders without horizontal page overflow | **PASS** | 390 x 844 viewport renders without horizontal page overflow. | [screenshot](playwright/19-mobile-viewport-renders-without-horizontal-page-overflow.png) / [text](playwright/19-mobile-viewport-renders-without-horizontal-page-overflow.txt) / [trace](playwright/19-mobile-viewport-renders-without-horizontal-page-overflow.zip) |

No uncaught browser JavaScript errors were recorded. The crashes listed above are Python exceptions displayed by Streamlit.
