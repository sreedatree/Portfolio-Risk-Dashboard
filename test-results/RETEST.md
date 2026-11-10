# Full dashboard retest

Date: November 10, 2026, America/New_York. Run started at approximately 4:23 PM EST.

**Result: 19/19 live browser scenarios and 11/11 offline regression tests passed.**

This was a fresh run against the current application source using a newly started Streamlit server at `http://127.0.0.1:8502`. Each browser scenario used a separate browser context. Browser checks used headless Google Chrome through Playwright, live Yahoo Finance prices, and independently downloaded reference returns; no application functions or market data were mocked in the browser suite. Offline tests used synthetic provider responses and Streamlit AppTest.

Versions: Streamlit 1.50.0, pandas 2.3.3, yfinance 1.2.0. Desktop viewport: 1440 × 1000; mobile viewport: 390 × 844. Historical checks use January 1, 2022 through January 1, 2025 (exclusive end date).

Displayed Python exceptions: **0**. Uncaught browser JavaScript errors: **0**.

The live dashboard showed NVDA as best performer and JNJ as worst performer. The 100% MSFT allocation matched independently downloaded MSFT returns. No application source changes were needed during this retest.

## Browser results

| Step | Scenario | Result | Duration |
| --- | --- | --- | --- |
| 1 | Default dashboard renders metrics charts and holdings | PASS | 8.76s |
| 2 | Best and worst performer labels match ticker-aligned prices | PASS | 3.42s |
| 3 | Invalid date range shows validation | PASS | 5.14s |
| 4 | Equal start and end years are rejected | PASS | 5.80s |
| 5 | Valid date change recalculates portfolio metrics | PASS | 5.03s |
| 6 | Empty stock input leaves portfolio usable | PASS | 5.45s |
| 7 | Duplicate ticker trims spaces and ignores case | PASS | 4.85s |
| 8 | Invalid ticker is rejected without a crash | PASS | 7.53s |
| 9 | Adding a valid ticker updates holdings and clears input | PASS | 7.22s |
| 10 | Removing a holding updates the dashboard | PASS | 8.34s |
| 11 | Changing weights normalizes allocation and recalculates metrics | PASS | 5.44s |
| 12 | All zero weights show validation instead of invalid metrics | PASS | 9.33s |
| 13 | Reset restores default holdings and equal allocations | PASS | 6.64s |
| 14 | Portfolio B accepts another valid portfolio | PASS | 4.38s |
| 15 | Blank Portfolio B safely hides comparison | PASS | 3.53s |
| 16 | Invalid Portfolio B gives a friendly validation message | PASS | 5.14s |
| 17 | Duplicate Portfolio B tickers are handled safely | PASS | 4.66s |
| 18 | A 100 percent MSFT allocation matches MSFT actual returns | PASS | 12.28s |
| 19 | Mobile viewport renders without horizontal page overflow | PASS | 5.25s |

## Evidence and reproduction

- [Machine-readable browser results](playwright/retest-2026-11-10-162346/results.json)
- [Independent reference returns](playwright/retest-2026-11-10-162346/reference-returns.json)
- [Offline regression log](playwright/retest-2026-11-10-162346/offline-regressions.log)
- [Test commands and setup](../tests/README.md)

Screenshots, page text, and Playwright traces for all 19 scenarios are saved beside the JSON results under `test-results/playwright/retest-2026-11-10-162346/`. Generated evidence is ignored by Git. The baseline report and prior verification artifacts were preserved.

The checks cover the main dashboard workflows and the reported defects. They are not a complete audit of all financial formulas, accessibility, browser engines, or data-provider outages. Historical data can change when Yahoo adjusts prices.
