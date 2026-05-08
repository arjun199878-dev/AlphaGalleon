import pytest
from app.backtester import Backtester

class MockScout:
    def __init__(self, mock_ohlc_responses):
        self.mock_ohlc_responses = mock_ohlc_responses
        self.called_symbols = []

    def is_real_api(self):
        return True
        
    def get_ohlc(self, symbol, interval):
        self.called_symbols.append(symbol)
        return self.mock_ohlc_responses.get(symbol, {"open": 100, "close": 110, "high": 112, "low": 98})


def test_backtester_single_asset():
    """Test standard simple arithmetic for a single asset with known mock performance."""
    mock_responses = {
        "RELIANCE": {"open": 2000, "close": 2020} # 1% daily return
    }
    scout = MockScout(mock_responses)
    backtester = Backtester(scout)
    
    basket = {
        "assets": [
            {"symbol": "RELIANCE", "weight": 100}
        ],
        "period": "1y"
    }
    
    result = backtester.simulate(basket)
    
    # 1% * 252 = 252%. But capped by backtester's hardcap of 60.0%
    assert result["cagr"] == "60.0%"
    assert "RELIANCE" in scout.called_symbols


def test_backtester_multi_asset_weighting():
    """Test blending returns across multiple weighted assets."""
    mock_responses = {
        "STABLECO": {"open": 100, "close": 100}, # 0% daily return -> 0% annualized
        "ROCKET": {"open": 100, "close": 110} # 10% daily return -> Cap at 60.0%
    }
    
    scout = MockScout(mock_responses)
    backtester = Backtester(scout)
    
    # 50% * 0 + 50% * 60 = 30.0% blended CAGR
    basket = {
        "assets": [
            {"symbol": "STABLECO", "weight": 50},
            {"symbol": "ROCKET", "weight": 50}
        ]
    }
    
    result = backtester.simulate(basket)
    assert result["cagr"] == "30.0%"


def test_backtester_drawdown_calculation():
    """Test the rough max drawdown mapping logic ensures safety limits."""
    mock_responses = {
        "CRASH": {"open": 100, "close": 90} # -10% daily return -> capped at -40.0%
    }
    
    scout = MockScout(mock_responses)
    backtester = Backtester(scout)
    
    basket = {
        "assets": [
            {"symbol": "CRASH", "weight": 100}
        ]
    }
    
    result = backtester.simulate(basket)
    
    # Drawdown logic: min(max_drawdown, -abs(asset_return) * 0.45) = -40 * 0.45 = -18.0
    # Base max drawdown is initialized to -8.5 so -18.0 is strictly worse, hence it expects -18.0%
    assert result["maxDrawdown"] == "-18.0%"
