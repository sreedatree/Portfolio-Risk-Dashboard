"""Run live-data browser checks: python tests/e2e_dashboard.py --help."""

import argparse
import json
import math
import os
from pathlib import Path
import re
import sys
import time
import traceback

if os.environ.get("PLAYWRIGHT_PYTHON_PATH"):
    sys.path.insert(0, os.environ["PLAYWRIGHT_PYTHON_PATH"])

from playwright.sync_api import sync_playwright, expect


DEFAULTS = ["AAPL", "MSFT", "NVDA", "JPM", "JNJ", "XOM"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8501")
    parser.add_argument("--output", default="test-results/playwright")
    parser.add_argument("--executable", help="Installed Chrome/Chromium executable")
    parser.add_argument("--match", default="", help="Only run checks whose names contain this text")
    args = parser.parse_args()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    results = []
    reference = {}
    print("Fetching independent ticker-aligned reference returns...", flush=True)
    try:
        import yfinance as yf
        prices = yf.download(DEFAULTS, start="2022-01-01", end="2025-01-01",
                             auto_adjust=True, progress=False)["Close"]
        reference = {ticker: float(prices[ticker].iloc[-1] / prices[ticker].iloc[0] - 1)
                     for ticker in DEFAULTS}
        assert all(math.isfinite(value) for value in reference.values())
        (output / "reference-returns.json").write_text(json.dumps(reference, indent=2))
    except Exception as error:
        print(f"Reference data unavailable: {error}", flush=True)

    with sync_playwright() as playwright:
        launch = {"headless": True, "timeout": 30000}
        if args.executable:
            launch["executable_path"] = args.executable
        browser = playwright.chromium.launch(**launch)

        def settled(page, complete=True):
            # Streamlit reruns over WebSocket; networkidle cannot identify completion.
            page.wait_for_function("""() => {
                const app = document.querySelector('[data-testid="stApp"]');
                return app && app.getAttribute('data-test-script-state') === 'notRunning';
            }""", timeout=90000)
            if complete:
                expect(page.get_by_text("Portfolio Risk Dashboard v3.1 Beta", exact=False)).to_be_visible(timeout=10000)

        def fresh(page):
            page.goto(args.url, wait_until="domcontentloaded")
            expect(page.get_by_role("heading", name="Portfolio Risk Dashboard", exact=True)).to_be_visible(timeout=30000)
            expect(page.get_by_role("textbox", name="Enter Portfolio B tickers")).to_be_visible(timeout=90000)
            settled(page)
            expect(page.get_by_test_id("stPlotlyChart")).to_have_count(6, timeout=15000)
            expect(page.get_by_test_id("stDataFrame")).to_have_count(2, timeout=15000)

        def sidebar(page):
            return page.get_by_test_id("stSidebar")

        def metric(page, label):
            return page.get_by_test_id("stMetric").filter(
                has=page.get_by_test_id("stMetricLabel").get_by_text(label, exact=True))

        def value(page, label):
            return metric(page, label).get_by_test_id("stMetricValue").inner_text()

        def change_slider(page, ticker, key):
            slider = page.get_by_role("slider", name=ticker, exact=True)
            # BaseWeb sliders do not implement Home/End. Drag the real thumb to
            # a track endpoint and verify it moved before checking the rerun.
            slider.scroll_into_view_if_needed()
            thumb = slider.bounding_box()
            track = slider.locator("..").bounding_box()
            assert thumb and track, f"Slider {ticker} has no visible track"
            destination = track["x"] - 5 if key == "Home" else track["x"] + track["width"] + 5
            page.mouse.move(thumb["x"] + thumb["width"] / 2, thumb["y"] + thumb["height"] / 2)
            page.mouse.down()
            page.mouse.move(destination, thumb["y"] + thumb["height"] / 2, steps=8)
            page.mouse.up()
            target = "0" if key == "Home" else "1"
            expect(slider).to_have_attribute("aria-valuenow", re.compile(target + r"(\.0+)?"))
            # Wait for the widget event to reach Streamlit before checking completion.
            page.wait_for_timeout(250)
            settled(page, complete=False)

        def choose_year(page, label, year):
            page.get_by_role("combobox", name=re.compile(re.escape(label) + r"$")).click()
            page.get_by_role("option", name=str(year), exact=True).click()
            page.wait_for_timeout(250)
            settled(page, complete=False)

        def submit_comparison(page, text):
            field = page.get_by_role("textbox", name="Enter Portfolio B tickers")
            field.fill(text)
            field.press("Enter")
            page.wait_for_timeout(250)
            settled(page, complete=False)

        def no_exception(page):
            expect(page.get_by_test_id("stException")).to_have_count(0)

        def run(name, action):
            if args.match.lower() not in name.lower():
                return
            index = len(results) + 1
            slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
            context = browser.new_context(viewport={"width": 1440, "height": 1000})
            context.tracing.start(screenshots=True, snapshots=True, sources=True)
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            started = time.monotonic()
            result = {"step": index, "name": name, "status": "PASS"}
            print(f"STEP {index}: {name}", flush=True)
            try:
                fresh(page)
                action(page)
                assert not errors, f"Browser JavaScript errors: {errors}"
            except Exception as error:
                result.update(status="FAIL", error=str(error), traceback=traceback.format_exc())
            result["seconds"] = round(time.monotonic() - started, 2)
            result["browser_errors"] = errors
            result["app_exceptions"] = page.get_by_test_id("stException").all_inner_texts()
            try:
                if result["app_exceptions"]:
                    page.get_by_test_id("stException").first.scroll_into_view_if_needed()
                page.screenshot(path=str(output / f"{index:02d}-{slug}.png"), full_page=True, timeout=15000)
                (output / f"{index:02d}-{slug}.txt").write_text(page.locator("body").inner_text())
            except Exception as error:
                result["capture_error"] = str(error)
            context.tracing.stop(path=str(output / f"{index:02d}-{slug}.zip"))
            context.close()
            results.append(result)
            (output / "results.json").write_text(json.dumps(results, indent=2))
            print(f"  {result['status']} ({result['seconds']}s) {result.get('error', '')[:900]}", flush=True)

        def initial(page):
            no_exception(page)
            assert page.get_by_role("slider").count() == 6
            expect(page.get_by_test_id("stPlotlyChart")).to_have_count(6)
            expect(page.get_by_test_id("stDataFrame")).to_have_count(2)
            for label in ["Portfolio Return", "S&P 500 Return", "Outperformance", "Volatility",
                          "Beta", "Sharpe Ratio", "Sortino Ratio", "Max Drawdown", "Value at Risk (95%)"]:
                assert re.fullmatch(r"-?\d+(\.\d+)?%?", value(page, label)), label
            for ticker in DEFAULTS:
                expect(sidebar(page).get_by_text(f"{ticker}: 16.7%", exact=True)).to_be_visible()
            print("  Live metrics:", {label: value(page, label) for label in
                  ["Portfolio Return", "S&P 500 Return", "Best Performer", "Worst Performer"]}, flush=True)

        run("Default dashboard renders metrics charts and holdings", initial)

        def performer(page):
            assert reference, "Independent price data unavailable; cannot verify ticker labels"
            expected_best = max(reference, key=reference.get)
            expected_worst = min(reference, key=reference.get)
            actual_best = value(page, "Best Performer")
            actual_worst = value(page, "Worst Performer")
            assert (actual_best, actual_worst) == (expected_best, expected_worst), (
                f"Displayed best/worst {actual_best}/{actual_worst}; ticker-aligned prices give "
                f"{expected_best}/{expected_worst}. Reference returns: {reference}")

        run("Best and worst performer labels match ticker-aligned prices", performer)

        def invalid_dates(page):
            choose_year(page, "Start Year", 2024)
            choose_year(page, "End Year", 2023)
            expect(page.get_by_text("The end year must be after the start year.", exact=True)).to_be_visible()
            no_exception(page)
            assert page.get_by_test_id("stMetric").count() == 0
        run("Invalid date range shows validation", invalid_dates)

        def equal_dates(page):
            choose_year(page, "Start Year", 2023)
            choose_year(page, "End Year", 2023)
            expect(page.get_by_text("The end year must be after the start year.", exact=True)).to_be_visible()
            no_exception(page)
        run("Equal start and end years are rejected", equal_dates)

        def valid_dates(page):
            before = value(page, "Portfolio Return")
            choose_year(page, "Start Year", 2024)
            settled(page)
            no_exception(page)
            assert value(page, "Portfolio Return") != before
        run("Valid date change recalculates portfolio metrics", valid_dates)

        def empty_add(page):
            sidebar(page).get_by_role("button", name="Add", exact=True).click()
            page.wait_for_timeout(250)
            settled(page)
            no_exception(page)
            assert page.get_by_role("slider").count() == 6
        run("Empty stock input leaves portfolio usable", empty_add)

        def duplicate(page):
            sidebar(page).get_by_role("textbox", name="Add Stock").fill("  aapl  ")
            sidebar(page).get_by_role("button", name="Add", exact=True).click()
            expect(page.get_by_text("Ticker 'AAPL' is already in the portfolio.", exact=True)).to_be_visible(timeout=30000)
            settled(page)
            no_exception(page)
            assert page.get_by_role("slider").count() == 6
        run("Duplicate ticker trims spaces and ignores case", duplicate)

        def invalid_ticker(page):
            sidebar(page).get_by_role("textbox", name="Add Stock").fill("ZZZZINVALID123")
            sidebar(page).get_by_role("button", name="Add", exact=True).click()
            message = page.get_by_text("Ticker 'ZZZZINVALID123' is invalid.", exact=True)
            expect(message.or_(page.get_by_test_id("stException"))).to_be_visible(timeout=90000)
            no_exception(page)
            expect(message).to_be_visible()
            settled(page)
            no_exception(page)
            assert page.get_by_role("slider").count() == 6
        run("Invalid ticker is rejected without a crash", invalid_ticker)

        def add_valid(page):
            sidebar(page).get_by_role("textbox", name="Add Stock").fill("  googl  ")
            sidebar(page).get_by_role("button", name="Add", exact=True).click()
            page.wait_for_timeout(400)
            settled(page, complete=False)
            no_exception(page)
            expect(page.get_by_role("slider", name="GOOGL", exact=True)).to_be_visible(timeout=30000)
            expect(sidebar(page).get_by_role("textbox", name="Add Stock")).to_have_value("")
        run("Adding a valid ticker updates holdings and clears input", add_valid)

        def remove(page):
            sidebar(page).get_by_role("button", name="✕", exact=True).nth(0).click()
            page.wait_for_timeout(300)
            settled(page, complete=False)
            no_exception(page)
            expect(page.get_by_role("slider", name="AAPL", exact=True)).to_have_count(0)
            assert page.get_by_role("slider").count() == 5
        run("Removing a holding updates the dashboard", remove)

        def normalization(page):
            before = value(page, "Portfolio Return")
            change_slider(page, "AAPL", "End")
            settled(page)
            no_exception(page)
            expect(sidebar(page).get_by_text("AAPL: 54.5%", exact=True)).to_be_visible()
            for ticker in DEFAULTS[1:]:
                expect(sidebar(page).get_by_text(f"{ticker}: 9.1%", exact=True)).to_be_visible()
            assert value(page, "Portfolio Return") != before
        run("Changing weights normalizes allocation and recalculates metrics", normalization)

        def zero_weights(page):
            for ticker in DEFAULTS:
                change_slider(page, ticker, "Home")
            expect(page.get_by_text("Please give at least one stock a weight greater than 0.", exact=True)).to_be_visible()
            no_exception(page)
            assert page.get_by_test_id("stMetric").count() == 0
        run("All zero weights show validation instead of invalid metrics", zero_weights)

        def reset(page):
            change_slider(page, "AAPL", "End")
            sidebar(page).get_by_role("button", name="🔄 Reset", exact=True).click()
            page.wait_for_timeout(300)
            settled(page)
            no_exception(page)
            for ticker in DEFAULTS:
                expect(sidebar(page).get_by_text(f"{ticker}: 16.7%", exact=True)).to_be_visible()
        run("Reset restores default holdings and equal allocations", reset)

        def comparison_valid(page):
            submit_comparison(page, "  googl, aapl  ")
            settled(page)
            no_exception(page)
            expect(page.get_by_test_id("stPlotlyChart")).to_have_count(6)
            expect(page.get_by_test_id("stDataFrame")).to_have_count(2)
        run("Portfolio B accepts another valid portfolio", comparison_valid)

        def comparison_blank(page):
            submit_comparison(page, " , , ")
            settled(page)
            no_exception(page)
            expect(page.get_by_test_id("stPlotlyChart")).to_have_count(5)
            expect(page.get_by_test_id("stDataFrame")).to_have_count(1)
        run("Blank Portfolio B safely hides comparison", comparison_blank)

        def comparison_bad(page):
            submit_comparison(page, "ZZZZINVALID123")
            no_exception(page)
            expect(page.get_by_text(re.compile("invalid|unable|no data", re.I)).first).to_be_visible()
        run("Invalid Portfolio B gives a friendly validation message", comparison_bad)

        def comparison_duplicate(page):
            submit_comparison(page, "AAPL, AAPL")
            no_exception(page)
            settled(page)
        run("Duplicate Portfolio B tickers are handled safely", comparison_duplicate)

        def stock_weight_accuracy(page):
            assert reference, "Independent price data unavailable; cannot verify weighted result"
            for ticker in DEFAULTS:
                change_slider(page, ticker, "Home")
            change_slider(page, "MSFT", "End")
            settled(page)
            no_exception(page)
            actual = float(value(page, "Portfolio Return").rstrip("%")) / 100
            expected = reference["MSFT"]
            assert abs(actual - expected) < 0.001, (
                f"100% MSFT displays {actual:.2%}; MSFT reference is {expected:.2%}. "
                "Weights may be applied to price columns in a different ticker order.")
        run("A 100 percent MSFT allocation matches MSFT actual returns", stock_weight_accuracy)

        def mobile(page):
            page.set_viewport_size({"width": 390, "height": 844})
            page.reload(wait_until="domcontentloaded")
            expect(page.get_by_role("heading", name="Portfolio Risk Dashboard", exact=True)).to_be_visible(timeout=30000)
            settled(page)
            no_exception(page)
            overflow = page.evaluate("document.documentElement.scrollWidth > window.innerWidth")
            assert not overflow, "Page overflows the mobile viewport horizontally"
        run("Mobile viewport renders without horizontal page overflow", mobile)
        browser.close()

    passed = sum(result["status"] == "PASS" for result in results)
    print(f"\nRESULT: {passed}/{len(results)} passed; {len(results) - passed} failed.", flush=True)
    print(f"Evidence: {output}", flush=True)
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
