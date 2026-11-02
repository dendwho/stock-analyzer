import copy
import csv
from datetime import date, timedelta
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/india-research-core/scripts/research.py'
spec = importlib.util.spec_from_file_location('research', SCRIPT)
research = importlib.util.module_from_spec(spec)
spec.loader.exec_module(research)


def bars(closes, volumes=None):
    result = []
    for i, close in enumerate(closes):
        result.append({'date': (date(2024, 1, 1) + timedelta(days=i)).isoformat(),
                       'open': close, 'high': close + 1, 'low': close - 1,
                       'close': close, 'volume': volumes[i] if volumes else 10000})
    return result


class ValuationTests(unittest.TestCase):
    def test_perpetuity_and_equity_bridge(self):
        result = research.dcf({'fcff_crore': [100] * 5, 'wacc': .1, 'terminal_growth': 0,
                               'shares_crore': 10, 'net_debt_crore': 100,
                               'nci_crore': 20, 'nonoperating_assets_crore': 50})
        self.assertAlmostEqual(result['enterprise_value_crore'], 1000)
        self.assertAlmostEqual(result['fair_value_rupees'], 93)

    def test_more_debt_lowers_equity_not_enterprise_value(self):
        args = {'fcff_crore': [100], 'wacc': .12, 'terminal_growth': .04, 'shares_crore': 10}
        a = research.dcf(args)
        b = research.dcf({**args, 'net_debt_crore': 50})
        self.assertEqual(a['enterprise_value_crore'], b['enterprise_value_crore'])
        self.assertAlmostEqual(a['fair_value_rupees'] - b['fair_value_rupees'], 5)

    def test_invalid_terminal_assumptions(self):
        for g in (.12, .2):
            with self.assertRaises(ValueError):
                research.dcf({'fcff_crore': [100], 'wacc': .12, 'terminal_growth': g, 'shares_crore': 10})

    def test_negative_terminal_cashflow_rejected(self):
        with self.assertRaises(ValueError):
            research.dcf({'fcff_crore': [-100], 'wacc': .12, 'terminal_growth': .04, 'shares_crore': 10})

    def test_nonfinite_and_boolean_numbers_rejected(self):
        for value in (float('nan'), float('inf'), True):
            with self.assertRaises(ValueError):
                research.number(value, 'test')

    def test_pe_and_ev_bridge(self):
        self.assertEqual(research.multiple({'kind': 'pe', 'metric_crore': 100, 'multiple': 20, 'shares_crore': 10})['fair_value_rupees'], 200)
        self.assertEqual(research.multiple({'kind': 'ev-ebitda', 'metric_crore': 100, 'multiple': 10, 'shares_crore': 10, 'net_debt_crore': 200})['fair_value_rupees'], 80)

    def test_negative_earnings_no_pe(self):
        with self.assertRaises(ValueError):
            research.multiple({'kind': 'pe', 'metric_crore': -10, 'multiple': 20, 'shares_crore': 10})

    def test_scenario_horizon_and_dividends(self):
        result = research.scenario_return({'entry_price': 100, 'exit_price': 144, 'years': 2})
        self.assertAlmostEqual(result['annualized_wealth_return_pct'], 20)
        self.assertAlmostEqual(research.scenario_return({'entry_price': 100, 'exit_price': 0, 'years': 5})['total_return_pct'], -100)
        self.assertAlmostEqual(research.scenario_return({'entry_price': 100, 'exit_price': 100, 'cash_dividends': 10, 'years': 1})['total_return_pct'], 10)


class IPOTests(unittest.TestCase):
    def test_capitalization_example(self):
        data = json.loads((ROOT / 'examples/ipo-capitalization.json').read_text())
        result = research.ipo_capitalization(data)
        self.assertEqual(result['post_diluted_shares'], 12_000_000)
        self.assertEqual(result['market_cap_crore'], 120)
        self.assertEqual(result['post_net_debt_rupees'], -40_000_000)
        self.assertEqual(result['enterprise_value_rupees'], 1_160_000_000)
        self.assertEqual(result['proforma_eps_rupees'], 5)
        self.assertEqual(result['pe'], 20)

    def test_ofs_does_not_dilute(self):
        result = research.ipo_capitalization({'issue_price': 100, 'pre_shares': 1000,
             'fresh_shares': 0, 'ofs_shares': 500, 'attributable_pat_rupees': -100})
        self.assertEqual(result['post_diluted_shares'], 1000)
        self.assertEqual(result['net_fresh_proceeds_rupees'], 0)
        self.assertIsNone(result['pe'])

    def test_fresh_amount_rounding_disclosed(self):
        result = research.ipo_capitalization({'issue_price': 3, 'pre_shares': 1000,
                    'fresh_amount_rupees': 10, 'attributable_pat_rupees': 100})
        self.assertEqual(result['fresh_shares'], 3)
        self.assertEqual(result['unallocated_fresh_budget_rupees'], 1)

    def test_invalid_capitalization_inputs(self):
        base = {'issue_price': 100, 'pre_shares': 1000, 'fresh_shares': 100, 'attributable_pat_rupees': 10}
        for changes in ({'ofs_shares': 1001}, {'fresh_amount_rupees': 100},
                        {'issuer_expenses_rupees': 10001}, {'non_debt_deployment_rupees': 10001}, {'fresh_shares': 0.5}):
            with self.assertRaises(ValueError):
                research.ipo_capitalization({**base, **changes})

    def test_gmp_preserves_conflicts_negative_and_missing(self):
        data = json.loads((ROOT / 'examples/gmp.json').read_text())
        result = research.gmp(data)
        self.assertTrue(result['conflicting_quotes'])
        self.assertEqual(result['quotes'][1]['gmp_pct'], -5)
        self.assertEqual(result['quotes'][1]['freshness'], 'stale')
        self.assertIsNone(result['quotes'][2]['gmp_pct'])
        self.assertNotIn('average', result)

    def test_gmp_zero_is_quote(self):
        result = research.gmp({'issue_price': 100, 'as_of': '2026-11-02T15:00:00+05:30',
                              'quotes': [{'source': 'fixture', 'premium_rupees': 0}]})
        self.assertEqual(result['availability'], 'quoted')
        self.assertEqual(result['quotes'][0]['gmp_pct'], 0)
        self.assertEqual(result['quotes'][0]['freshness'], 'unknown')

    def test_gmp_date_precision_not_invented(self):
        result = research.gmp({'issue_price': 100, 'as_of': '2026-11-02T15:00:00+05:30',
             'quotes': [{'source': 'fixture', 'premium_rupees': 10, 'observed_at': '2026-11-02', 'time_precision': 'date'}]})
        self.assertEqual(result['quotes'][0]['freshness'], 'date-only-unverified')
        self.assertIsNone(result['quotes'][0]['age_hours'])

    def test_gmp_no_quotes_is_unavailable(self):
        self.assertEqual(research.gmp({'issue_price': 100, 'as_of': '2026-11-02T15:00:00+05:30'})['availability'], 'unavailable')

    def test_gmp_future_or_naive_time_rejected(self):
        for time in ('2026-11-03T15:00:00+05:30', '2026-11-02T14:00:00'):
            with self.assertRaises(ValueError):
                research.gmp({'issue_price': 100, 'as_of': '2026-11-02T15:00:00+05:30',
                              'quotes': [{'source': 'fixture', 'premium_rupees': 10, 'observed_at': time}]})


class PriceTests(unittest.TestCase):
    def test_flat_series(self):
        result = research.indicators(bars([100] * 250))
        self.assertEqual(result['wilder_rsi_14'], 50)
        self.assertEqual(result['maximum_close_drawdown_pct'], 0)
        self.assertEqual(result['annualized_log_volatility_pct'], 0)
        self.assertEqual(result['macd_12_26'], 0)
        self.assertEqual(result['wilder_atr_14'], 2)

    def test_rising_and_falling_rsi(self):
        self.assertEqual(research.indicators(bars(list(range(100, 130))))['wilder_rsi_14'], 100)
        self.assertEqual(research.indicators(bars(list(range(130, 100, -1))))['wilder_rsi_14'], 0)

    def test_insufficient_indicator_warmup_is_null(self):
        result = research.indicators(bars([100, 101]))
        self.assertIsNone(result['wilder_rsi_14'])
        self.assertIsNone(result['sma']['200'])
        self.assertIsNone(result['macd_signal_9'])

    def test_atr_accounts_for_gaps(self):
        rows = bars([100] + [120] * 14)
        self.assertGreater(research.indicators(rows)['wilder_atr_14'], 2)

    def test_reachability_complete_nonoverlapping_windows(self):
        result = research.reachability(bars([100] * 101), {'zone_low': 99, 'zone_high': 101, 'horizon_sessions': 5})
        self.assertEqual(result['complete_windows'], 20)
        self.assertEqual(result['historical_range_intersection_share'], 1)
        self.assertTrue(result['diagnostic_sample_adequate'])
        self.assertIn('not a forward probability', result['caveat'])

    def test_reachability_no_history_no_probability(self):
        result = research.reachability(bars([100]), {'zone_low': 90, 'zone_high': 95, 'horizon_sessions': 20})
        self.assertEqual(result['complete_windows'], 0)
        self.assertIsNone(result['historical_range_intersection_share'])

    def test_gap_does_not_infer_range_touch(self):
        rows = bars([100, 80, 100])
        result = research.reachability(rows, {'zone_low': 89, 'zone_high': 91, 'horizon_sessions': 2})
        self.assertEqual(result['historical_range_intersection_share'], 0)

    def test_csv_validation_and_mapping(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'prices.csv'
            path.write_text('Date,O,H,L,C,V\n2024-01-01,100,101,99,100,10\n')
            mapping = dict(zip(('date','open','high','low','close','volume'), ('Date','O','H','L','C','V')))
            self.assertEqual(research.load_ohlcv(path, mapping)[0]['close'], 100)
            path.write_text('date,open,high,low,close,volume\n2024-01-01,100,99,101,100,10\n')
            with self.assertRaises(ValueError):
                research.load_ohlcv(path)

    def test_duplicate_dates_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'prices.csv'
            path.write_text('date,open,high,low,close,volume\n' + '2024-01-01,100,101,99,100,10\n' * 2)
            with self.assertRaises(ValueError):
                research.load_ohlcv(path)


class RiskTests(unittest.TestCase):
    def test_sizing_cash_and_sector_caps(self):
        data = json.loads((ROOT / 'examples/position-size.json').read_text())
        result = research.position_size(data)
        self.assertEqual(result['quantity'], 699)
        self.assertLessEqual(result['cash_required'], 70_000)
        self.assertLessEqual(result['modeled_stop_loss_with_costs'], 10_000)

    def test_existing_exposure_and_risk_can_prevent_entry(self):
        base = {'account_equity': 100_000, 'entry': 100, 'stop': 90, 'risk_fraction': .01,
                'available_cash': 100_000, 'max_position_fraction': .1}
        self.assertEqual(research.position_size({**base, 'current_position_value': 10_000})['quantity'], 0)
        self.assertEqual(research.position_size({**base, 'existing_planned_risk': 1000})['quantity'], 0)

    def test_lot_rounding_and_stop_rules(self):
        base = {'account_equity': 100_000, 'entry': 100, 'stop': 90, 'risk_fraction': .01,
                'available_cash': 100_000, 'max_position_fraction': .1, 'lot_size': 30}
        self.assertEqual(research.position_size(base)['quantity'], 90)
        with self.assertRaises(ValueError):
            research.position_size({**base, 'stop': 110})

    def test_screen_missing_is_not_zero(self):
        result = research.screen(json.loads((ROOT / 'examples/screen.json').read_text()))
        self.assertEqual([r['id'] for r in result['passed']], ['SYNTHETIC-QUALITY'])
        self.assertEqual(result['excluded_missing'][0]['id'], 'SYNTHETIC-MISSING')

    def test_portfolio_cash_and_unknown_sector(self):
        result = research.portfolio({'holdings': [{'id': 'A', 'value': 60}, {'id': 'B', 'value': 20, 'sector': 'IT'}], 'cash': 20})
        self.assertEqual(result['sector_weights_pct']['unknown'], 60)
        self.assertEqual(result['cash_weight_pct'], 20)
        self.assertAlmostEqual(result['single_name_hhi'], .4)

    def test_portfolio_duplicate_identity_rejected(self):
        with self.assertRaises(ValueError):
            research.portfolio({'holdings': [{'id': 'A', 'value': 1}, {'id': 'A', 'value': 1}]})


class BacktestTests(unittest.TestCase):
    config = {'fast': 2, 'slow': 3, 'initial_cash': 10000, 'buy_cost_bps': 10,
              'sell_cost_bps': 20, 'slippage_bps': 5, 'max_volume_fraction': .1}

    def test_next_open_timing_and_costs(self):
        rows = bars([100, 101, 102, 110, 111, 112])
        result = research.backtest_sma(rows, self.config)
        self.assertEqual(result['fills'][0]['date'], rows[3]['date'])
        self.assertEqual(result['fills'][0]['signal_date'], rows[2]['date'])
        self.assertAlmostEqual(result['fills'][0]['price'], 110 * 1.0005)
        self.assertGreater(result['costs_including_modeled_slippage'], 0)

    def test_zero_volume_prevents_fill(self):
        result = research.backtest_sma(bars([100, 101, 102, 103, 104], [0] * 5), self.config)
        self.assertEqual(result['fills'], [])
        self.assertEqual(result['final_equity'], 10000)

    def test_volume_cap_and_no_short(self):
        result = research.backtest_sma(bars([100, 101, 102, 103, 104], [10] * 5), self.config)
        self.assertEqual(result['open_quantity'], 1)
        falling = research.backtest_sma(bars([104, 103, 102, 101, 100]), self.config)
        self.assertEqual(falling['fills'], [])

    def test_higher_costs_reduce_terminal_wealth(self):
        rows = bars([100, 101, 102, 103, 104, 90, 89, 88])
        low = research.backtest_sma(rows, {**self.config, 'buy_cost_bps': 0, 'sell_cost_bps': 0, 'slippage_bps': 0})
        high = research.backtest_sma(rows, {**self.config, 'buy_cost_bps': 100, 'sell_cost_bps': 100, 'slippage_bps': 100})
        self.assertLess(high['final_equity'], low['final_equity'])
        self.assertGreaterEqual(high['open_quantity'], 0)


class ReportAndCLITests(unittest.TestCase):
    def fixture(self, kind):
        return json.loads((ROOT / f'examples/{kind}-report.json').read_text())

    def test_conservative_report_examples_pass(self):
        for kind in ('stock', 'ipo'):
            self.assertTrue(research.validate_report(self.fixture(kind))['valid'])

    def test_gmp_required_without_user_prompt(self):
        data = self.fixture('ipo')
        del data['gmp']
        with self.assertRaisesRegex(ValueError, 'GMP section is mandatory'):
            research.validate_report(data)

    def test_timeframe_and_entry_assessment_required(self):
        data = self.fixture('stock')
        del data['verdict']['timeframe']
        with self.assertRaisesRegex(ValueError, 'timeframe'):
            research.validate_report(data)
        data = self.fixture('stock')
        del data['entry_assessment']
        with self.assertRaisesRegex(ValueError, 'entry'):
            research.validate_report(data)

    def test_no_current_buy_verdict_without_verified_price(self):
        data = self.fixture('stock')
        data['verdict']['status'] = 'attractive-now'
        with self.assertRaisesRegex(ValueError, 'verified reference price'):
            research.validate_report(data)

    def test_broken_source_reference_rejected(self):
        data = self.fixture('stock')
        data['verdict']['source_ids'] = ['missing-document']
        with self.assertRaisesRegex(ValueError, 'unresolved'):
            research.validate_report(data)

    def test_naive_cutoff_rejected(self):
        data = self.fixture('ipo')
        data['as_of'] = '2026-11-02T15:30:00'
        with self.assertRaisesRegex(ValueError, 'timezone'):
            research.validate_report(data)

    def test_cli_pipeline_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'result.json'
            cmd = [sys.executable, str(SCRIPT), 'dcf', '--input', str(ROOT / 'examples/dcf.json'), '--output', str(output)]
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
            saved = output.read_text()
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 2)
            self.assertEqual(output.read_text(), saved)

    def test_invalid_cli_json_returns_useful_error(self):
        run = subprocess.run([sys.executable, str(SCRIPT), 'dcf', '--input', '-'], input='{}', capture_output=True, text=True)
        self.assertEqual(run.returncode, 2)
        self.assertIn('Input error', run.stderr)


if __name__ == '__main__':
    unittest.main()
