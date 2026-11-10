# Live dashboard browser tests

The suite uses Python Playwright to drive the actual Streamlit app with live Yahoo Finance data. It exercises 19 scenarios in separate browser contexts, checks Python exceptions displayed by Streamlit and uncaught browser JavaScript errors, and saves a screenshot, page text, and trace for each scenario. Two checks independently download ticker-aligned reference returns to verify the displayed analytics.

From the repository root, install the test dependency and a browser:

```sh
.venv/bin/python -m pip install -r tests/requirements-e2e.txt
.venv/bin/python -m playwright install chromium
```

Start the app in one terminal:

```sh
.venv/bin/python -m streamlit run src/dashboard.py --server.headless true --server.port 8501
```

Run the suite in another terminal:

```sh
.venv/bin/python -u tests/e2e_dashboard.py
```

To use Chrome already installed on macOS instead of downloading Chromium:

```sh
.venv/bin/python -u tests/e2e_dashboard.py \
  --executable '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
```

Results are written to `test-results/playwright/results.json`. The process exits with status 1 when any check fails. Each run uses fresh browser contexts but shares the running app's server-side Streamlit data cache. Internet access is required, and reference prices may change as Yahoo adjusts historical data. The suite does not mock prices or modify application source.

Run a particular scenario and keep its evidence separate:

```sh
.venv/bin/python -u tests/e2e_dashboard.py --match 'Reset' --output test-results/reset
```

Open a recorded trace:

```sh
.venv/bin/python -m playwright show-trace test-results/playwright/01-default-dashboard-renders-metrics-charts-and-holdings.zip
```

During the initial test session, Playwright was installed outside the project into `/private/tmp/portfolio-playwright-deps`. To reuse that temporary installation while it exists, prefix the test command with `PLAYWRIGHT_PYTHON_PATH=/private/tmp/portfolio-playwright-deps`.

The checks cover browser behavior and selected data correctness, not a complete audit of every financial formula, accessibility requirement, or supported browser.
