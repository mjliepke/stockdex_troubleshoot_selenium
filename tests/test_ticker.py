import pytest

from stockdex.ticker import Ticker

import pandas as pd


@pytest.mark.parametrize(
    "ticker, expected_response",
    [
        ("AAPL", 200),
        ("GOOGL", 200),
        ("MSFT", 200),
    ],
)
def test_get_response(ticker, expected_response):
    # Create a Ticker object
    ticker = Ticker(ticker)

    # Send an HTTP GET request to the website
    response = ticker.get_response(f"https://finance.yahoo.com/quote/{ticker.ticker}")

    # Check if the response is as expected
    assert response.status_code == expected_response


@pytest.mark.parametrize(
    "ticker, expected_response",
    [
        ("AAPL", 200),
        ("GOOGL", 200),
        ("MSFT", 200),
    ],
)
def test_cash_flow(ticker, expected_response):
    ticker = Ticker(ticker)
    cash_flow_df = ticker.cash_flow()

    # Check if the response is as expected
    assert isinstance(cash_flow_df, pd.DataFrame)
    assert cash_flow_df.shape[0] > 0


@pytest.mark.parametrize(
    "ticker, expected_response",
    [
        ("AAPL", 200),
        ("GOOGL", 200),
        ("MSFT", 200),
    ],
)
def test_analysis(ticker, expected_response):
    ticker = Ticker(ticker)
    analysis_df = ticker.analysis()

    # Check if the response is as expected
    assert isinstance(analysis_df, pd.DataFrame)
    assert analysis_df.shape[0] > 0
