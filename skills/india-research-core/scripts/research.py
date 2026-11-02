#!/usr/bin/env python3
"""Deterministic research calculations. Inputs are evidence, not verified by this tool."""
from __future__ import annotations

import argparse
import csv
from datetime import date, datetime
import json
import math
from pathlib import Path
import statistics
import sys


def number(value, name, minimum=None, maximum=None):
    if isinstance(value, bool):
        raise ValueError(f'{name}: expected a finite number, not a boolean')
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f'{name}: expected a finite number') from exc
    if not math.isfinite(result):
        raise ValueError(f'{name}: expected a finite number')
    if minimum is not None and result < minimum:
        raise ValueError(f'{name}: must be >= {minimum}')
    if maximum is not None and result > maximum:
        raise ValueError(f'{name}: must be <= {maximum}')
    return result


def positive(value, name):
    value = number(value, name)
    if value <= 0:
        raise ValueError(f'{name}: must be positive')
    return value


def integer(value, name, minimum=1):
    value = number(value, name, minimum)
    if not value.is_integer():
        raise ValueError(f'{name}: expected a whole number')
    return int(value)


def timestamp(value, name):
    if not isinstance(value, str):
        raise ValueError(f'{name}: expected ISO timestamp with timezone')
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as exc:
        raise ValueError(f'{name}: expected ISO timestamp with timezone') from exc
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError(f'{name}: timezone is required')
    return result


def dcf(data):
    """FCFF, annual end-period discounting; totals and shares both in crore."""
    flows = data['fcff_crore']
    if not isinstance(flows, list) or not flows:
        raise ValueError('fcff_crore: supply at least one explicit annual forecast')
    flows = [number(x, 'fcff_crore') for x in flows]
    positive(flows[-1], 'terminal base FCFF')
    wacc = positive(data['wacc'], 'wacc')
    growth = number(data['terminal_growth'], 'terminal_growth', -0.99)
    if wacc <= growth:
        raise ValueError('wacc must exceed terminal_growth')
    shares = positive(data['shares_crore'], 'shares_crore')
    pv = [value / (1 + wacc) ** year for year, value in enumerate(flows, 1)]
    terminal = flows[-1] * (1 + growth) / (wacc - growth)
    terminal_pv = terminal / (1 + wacc) ** len(flows)
    ev = sum(pv) + terminal_pv
    net_debt = number(data.get('net_debt_crore', 0), 'net_debt_crore')
    nci = number(data.get('nci_crore', 0), 'nci_crore', 0)
    investments = number(data.get('nonoperating_assets_crore', 0), 'nonoperating_assets_crore', 0)
    equity = ev - net_debt - nci + investments
    return {'method': 'FCFF / WACC; annual end-period; no terminal multiple',
            'pv_forecasts_crore': pv, 'terminal_value_crore': terminal,
            'terminal_pv_crore': terminal_pv, 'enterprise_value_crore': ev,
            'equity_value_crore': equity, 'fair_value_rupees': equity / shares,
            'terminal_share_of_ev': terminal_pv / ev if ev else None}


def multiple(data):
    kind = data['kind']
    if kind not in ('pe', 'ev-ebitda'):
        raise ValueError('kind must be pe or ev-ebitda')
    metric = positive(data['metric_crore'], 'metric_crore')
    multiple_value = positive(data['multiple'], 'multiple')
    shares = positive(data['shares_crore'], 'shares_crore')
    value = metric * multiple_value
    equity = value
    if kind == 'ev-ebitda':
        equity -= number(data.get('net_debt_crore', 0), 'net_debt_crore')
        equity -= number(data.get('nci_crore', 0), 'nci_crore', 0)
        equity += number(data.get('nonoperating_assets_crore', 0), 'nonoperating_assets_crore', 0)
    return {'kind': kind, 'metric_crore': metric, 'multiple': multiple_value,
            'equity_value_crore': equity, 'fair_value_rupees': equity / shares}


def scenario_return(data):
    current = positive(data['entry_price'], 'entry_price')
    future = number(data['exit_price'], 'exit_price', 0)
    years = positive(data['years'], 'years')
    dividends = number(data.get('cash_dividends', 0), 'cash_dividends', 0)
    wealth = (future + dividends) / current
    return {'price_return_pct': (future / current - 1) * 100,
            'total_return_pct': (wealth - 1) * 100,
            'annualized_wealth_return_pct': (wealth ** (1 / years) - 1) * 100,
            'years': years,
            'basis': 'Gross; cumulative cash dividends, no reinvestment or timing; not IRR'}


def ipo_capitalization(data):
    price = positive(data['issue_price'], 'issue_price')
    pre = integer(data['pre_shares'], 'pre_shares')
    extra = integer(data.get('additional_dilution_shares', 0), 'additional_dilution_shares', 0)
    ofs = integer(data.get('ofs_shares', 0), 'ofs_shares', 0)
    if ofs > pre:
        raise ValueError('ofs_shares cannot exceed pre_shares')
    if ('fresh_shares' in data) == ('fresh_amount_rupees' in data):
        raise ValueError('provide exactly one of fresh_shares or fresh_amount_rupees')
    if 'fresh_shares' in data:
        fresh = integer(data['fresh_shares'], 'fresh_shares', 0)
        remainder = 0
    else:
        budget = number(data['fresh_amount_rupees'], 'fresh_amount_rupees', 0)
        fresh = math.floor(budget / price)
        remainder = budget - fresh * price
    proceeds = fresh * price
    expenses = number(data.get('issuer_expenses_rupees', 0), 'issuer_expenses_rupees', 0)
    if expenses > proceeds:
        raise ValueError('issuer expenses exceed gross fresh proceeds')
    net_proceeds = proceeds - expenses
    post = pre + fresh + extra
    market_cap = post * price
    net_debt = number(data.get('pre_net_debt_rupees', 0), 'pre_net_debt_rupees')
    deployment = number(data.get('non_debt_deployment_rupees', 0), 'non_debt_deployment_rupees', 0)
    if deployment > net_proceeds:
        raise ValueError('non_debt_deployment exceeds net fresh proceeds')
    post_net_debt = net_debt - net_proceeds + deployment
    earnings = number(data['attributable_pat_rupees'], 'attributable_pat_rupees')
    eps = earnings / post
    return {'post_diluted_shares': post, 'fresh_shares': fresh,
            'fresh_gross_rupees': proceeds, 'net_fresh_proceeds_rupees': net_proceeds,
            'ofs_proceeds_to_sellers_rupees': ofs * price,
            'unallocated_fresh_budget_rupees': remainder,
            'market_cap_rupees': market_cap, 'market_cap_crore': market_cap / 10_000_000,
            'post_net_debt_rupees': post_net_debt,
            'enterprise_value_rupees': market_cap + post_net_debt,
            'proforma_eps_rupees': eps, 'pe': price / eps if eps > 0 else None,
            'basis': 'Pro forma post-issue diluted shares; OFS adds no shares; debt repayment is net-debt neutral'}


def gmp(data):
    price = positive(data['issue_price'], 'issue_price')
    as_of = timestamp(data['as_of'], 'as_of')
    max_age = number(data.get('max_age_hours', 24), 'max_age_hours', 0)
    quotes = data.get('quotes', [])
    if not isinstance(quotes, list):
        raise ValueError('quotes must be a list')
    result = []
    for quote in quotes:
        if not quote.get('source'):
            raise ValueError('each GMP quote requires an attributable source')
        observed = quote.get('observed_at')
        age = None
        if observed:
            precision = quote.get('time_precision', 'timestamp')
            if precision == 'date':
                observed_date = date.fromisoformat(observed)
                # Date-only observations never receive an invented intraday time.
                if observed_date > as_of.date():
                    raise ValueError('GMP observation is after the research cutoff')
                freshness = 'date-only-unverified' if observed_date == as_of.date() else 'stale'
            elif precision == 'timestamp':
                age = (as_of - timestamp(observed, 'observed_at')).total_seconds() / 3600
                if age < 0:
                    raise ValueError('GMP observation is after the research cutoff')
                freshness = 'within-age-limit' if age <= max_age else 'stale'
            else:
                raise ValueError('time_precision must be date or timestamp')
        else:
            freshness = 'unknown'
        premium = quote.get('premium_rupees')
        if premium is not None:
            premium = number(premium, 'premium_rupees')
            if premium < -price:
                raise ValueError('premium implies a negative share price')
        result.append({**quote, 'premium_rupees': premium,
                       'gmp_pct': premium / price * 100 if premium is not None else None,
                       'illustrative_implied_price': price + premium if premium is not None else None,
                       'freshness': freshness, 'age_hours': age})
    known = [q['premium_rupees'] for q in result if q['premium_rupees'] is not None]
    return {'issue_price': price, 'price_basis': data.get('price_basis', 'unspecified; verify'),
            'as_of': data['as_of'], 'quotes': result,
            'availability': 'quoted' if known else 'unavailable',
            'conflicting_quotes': len(set(known)) > 1,
            'caveat': 'Unofficial attributed quotes; no averaging and no listing-price forecast'}


def position_size(data):
    capital = positive(data['account_equity'], 'account_equity')
    entry = positive(data['entry'], 'entry')
    stop = positive(data['stop'], 'stop')
    if stop >= entry:
        raise ValueError('long position requires stop below entry')
    risk = number(data['risk_fraction'], 'risk_fraction', 0, 1)
    lot = integer(data.get('lot_size', 1), 'lot_size')
    fees = number(data.get('round_trip_cost_bps', 0), 'round_trip_cost_bps', 0)
    buy_cost = number(data.get('buy_cost_bps', 0), 'buy_cost_bps', 0)
    slip = number(data.get('adverse_slippage_per_share', 0), 'adverse_slippage_per_share', 0)
    # Cost/slippage included in risk; buy fees also constrain cash spent.
    per_share_risk = entry - stop + entry * fees / 10000 + slip
    max_position = number(data['max_position_fraction'], 'max_position_fraction', 0, 1)
    current_position = number(data.get('current_position_value', 0), 'current_position_value', 0)
    cash = number(data['available_cash'], 'available_cash', 0)
    budgets = [cash, max(0, capital * max_position - current_position)]
    sector_keys = ('max_sector_fraction', 'current_sector_value')
    if any(k in data for k in sector_keys):
        if not all(k in data for k in sector_keys):
            raise ValueError('sector cap requires max_sector_fraction and current_sector_value')
        sector_cap = number(data['max_sector_fraction'], 'max_sector_fraction', 0, 1)
        current_sector = number(data['current_sector_value'], 'current_sector_value', 0)
        budgets.append(max(0, capital * sector_cap - current_sector))
    remaining_risk = max(0, capital * risk - number(data.get('existing_planned_risk', 0), 'existing_planned_risk', 0))
    qty = math.floor(min(remaining_risk / per_share_risk,
                         min(budgets) / (entry * (1 + buy_cost / 10000))) / lot) * lot
    return {'quantity': qty, 'lot_size': lot, 'position_value': qty * entry,
            'cash_required': qty * entry * (1 + buy_cost / 10000),
            'modeled_stop_loss_with_costs': qty * per_share_risk,
            'remaining_risk_budget': remaining_risk,
            'caveat': 'Gaps, illiquidity and execution failure can exceed modeled stop loss'}


def load_ohlcv(path, mapping=None):
    mapping = mapping or {key: key for key in ('date', 'open', 'high', 'low', 'close', 'volume')}
    rows = []
    with open(path, newline='', encoding='utf-8-sig') as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or any(mapping.get(k) not in reader.fieldnames for k in ('date', 'open', 'high', 'low', 'close', 'volume')):
            raise ValueError('CSV needs mapped date, open, high, low, close, volume columns')
        for line, raw in enumerate(reader, 2):
            day = date.fromisoformat(raw[mapping['date']].strip())
            if rows and day.isoformat() <= rows[-1]['date']:
                raise ValueError(f'line {line}: dates must be ascending and unique')
            row = {'date': day.isoformat()}
            for key in ('open', 'high', 'low', 'close'):
                row[key] = positive(raw[mapping[key]], f'line {line} {key}')
            row['volume'] = number(raw[mapping['volume']], f'line {line} volume', 0)
            if not (row['low'] <= min(row['open'], row['close']) <= max(row['open'], row['close']) <= row['high']):
                raise ValueError(f'line {line}: invalid OHLC range')
            rows.append(row)
    if not rows:
        raise ValueError('empty price history')
    return rows


def ema(values, period):
    if len(values) < period:
        return [None] * len(values)
    result = [None] * (period - 1) + [statistics.mean(values[:period])]
    alpha = 2 / (period + 1)
    for value in values[period:]:
        result.append(alpha * value + (1 - alpha) * result[-1])
    return result


def wilder(values, period):
    if len(values) < period:
        return None
    avg = statistics.mean(values[:period])
    for value in values[period:]:
        avg = (avg * (period - 1) + value) / period
    return avg


def drawdown(values):
    peak = values[0]
    worst = 0
    for value in values:
        peak = max(peak, value)
        worst = min(worst, value / peak - 1)
    return worst


def indicators(rows):
    closes = [r['close'] for r in rows]
    changes = [b - a for a, b in zip(closes, closes[1:])]
    up = wilder([max(c, 0) for c in changes], 14)
    down = wilder([max(-c, 0) for c in changes], 14)
    rsi = None
    if up is not None:
        rsi = 50 if up == down == 0 else (100 if down == 0 else 100 - 100 / (1 + up / down))
    tr = [max(row['high'] - row['low'], abs(row['high'] - prev['close']), abs(row['low'] - prev['close']))
          for prev, row in zip(rows, rows[1:])]
    e12, e26 = ema(closes, 12), ema(closes, 26)
    macd_values = [a - b for a, b in zip(e12, e26) if a is not None and b is not None]
    signal = ema(macd_values, 9)[-1] if macd_values else None
    returns = [math.log(b / a) for a, b in zip(closes, closes[1:])]
    result = {'as_of_date': rows[-1]['date'], 'observations': len(rows), 'close': closes[-1],
              'sma': {str(p): statistics.mean(closes[-p:]) if len(closes) >= p else None for p in (20, 50, 200)},
              'ema_20': ema(closes, 20)[-1], 'wilder_rsi_14': rsi,
              'wilder_atr_14': wilder(tr, 14),
              'macd_12_26': macd_values[-1] if macd_values else None,
              'macd_signal_9': signal,
              'macd_histogram': macd_values[-1] - signal if signal is not None else None,
              'annualized_log_volatility_pct': statistics.stdev(returns) * math.sqrt(252) * 100 if len(returns) >= 2 else None,
              'maximum_close_drawdown_pct': drawdown(closes) * 100,
              'volume_vs_prior_20_mean': None,
              'bollinger_20_2': None,
              'conventions': 'SMA-seeded EMA; Wilder initialized on first 14 changes/TR excluding first bar; 252-session volatility; close drawdown; short history needs warm-up review'}
    if len(rows) >= 21:
        base_volume = statistics.mean(r['volume'] for r in rows[-21:-1])
        result['volume_vs_prior_20_mean'] = rows[-1]['volume'] / base_volume if base_volume else None
    if len(closes) >= 20:
        mean, dev = statistics.mean(closes[-20:]), statistics.pstdev(closes[-20:])
        result['bollinger_20_2'] = {'lower': mean - 2 * dev, 'middle': mean, 'upper': mean + 2 * dev}
    return result


def percentile(values, fraction):
    values = sorted(values)
    rank = (len(values) - 1) * fraction
    lower = math.floor(rank)
    upper = math.ceil(rank)
    return values[lower] + (values[upper] - values[lower]) * (rank - lower)


def reachability(rows, data):
    horizon = integer(data['horizon_sessions'], 'horizon_sessions')
    low = positive(data['zone_low'], 'zone_low')
    high = positive(data['zone_high'], 'zone_high')
    if low > high:
        raise ValueError('zone_low exceeds zone_high')
    current = rows[-1]['close']
    # Relative zones allow historical comparison at each historical starting close.
    relative_low, relative_high = low / current - 1, high / current - 1
    nonoverlap = data.get('nonoverlapping', True)
    if not isinstance(nonoverlap, bool):
        raise ValueError('nonoverlapping must be a boolean')
    step = horizon if nonoverlap else 1
    minima, maxima, touches = [], [], []
    for start in range(0, len(rows) - horizon, step):
        reference = rows[start]['close']
        future = rows[start + 1:start + horizon + 1]
        minima.append(min(r['low'] for r in future) / reference - 1)
        maxima.append(max(r['high'] for r in future) / reference - 1)
        # At least one actual daily range intersects; don't infer fills across gaps.
        touches.append(any(r['low'] / reference - 1 <= relative_high and
                           r['high'] / reference - 1 >= relative_low for r in future))
    atr = indicators(rows)['wilder_atr_14']
    count = len(touches)
    return {'as_of_date': rows[-1]['date'], 'history_start': rows[0]['date'],
            'reference_close': current, 'zone_low': low, 'zone_high': high,
            'distance_low_pct': relative_low * 100, 'distance_high_pct': relative_high * 100,
            'distance_low_atr': (low - current) / atr if atr else None,
            'distance_high_atr': (high - current) / atr if atr else None,
            'horizon_sessions': horizon, 'complete_windows': count,
            'nonoverlapping': nonoverlap, 'diagnostic_sample_adequate': count >= 20,
            'historical_range_intersection_share': sum(touches) / count if count else None,
            'downside_excursion_pct': {str(p): percentile(minima, p) * 100 for p in (0.1, 0.5, 0.9)} if count else None,
            'upside_excursion_pct': {str(p): percentile(maxima, p) * 100 for p in (0.1, 0.5, 0.9)} if count else None,
            'caveat': 'Backward-looking sample description, not a forward probability or fill; assess current market/sector/catalysts separately'}


def portfolio(data):
    holdings = data['holdings']
    cash = number(data.get('cash', 0), 'cash', 0)
    seen, result = set(), []
    for holding in holdings:
        symbol = holding['id']
        if not symbol or symbol in seen:
            raise ValueError('portfolio holding IDs must be nonempty and unique')
        seen.add(symbol)
        value = number(holding['value'], 'holding value', 0)
        result.append({**holding, 'value': value})
    total = sum(r['value'] for r in result) + cash
    positive(total, 'portfolio total')
    sectors = {}
    for row in result:
        row['weight_pct'] = row['value'] / total * 100
        sector = row.get('sector') or 'unknown'
        sectors[sector] = sectors.get(sector, 0) + row['weight_pct']
    return {'portfolio_value': total, 'cash_weight_pct': cash / total * 100,
            'holdings': result, 'sector_weights_pct': sectors,
            'single_name_hhi': sum((r['value'] / total) ** 2 for r in result),
            'basis': 'Supplied common-date market values; no inferred correlation or look-through'}


def screen(data):
    rules, rows = data['rules'], data['rows']
    allowed = {'gte': lambda a, b: a >= b, 'lte': lambda a, b: a <= b,
               'gt': lambda a, b: a > b, 'lt': lambda a, b: a < b}
    checked = []
    for rule in rules:
        if rule['op'] not in allowed:
            raise ValueError('screen rule op must be gt, gte, lt or lte')
        checked.append((rule['field'], rule['op'], number(rule['value'], 'rule value')))
    passed, failed, missing = [], [], []
    seen = set()
    for row in rows:
        identity = row.get('id')
        if not identity or identity in seen:
            raise ValueError('screen IDs must be nonempty and unique')
        seen.add(identity)
        absent, violations = [], []
        for field, op, target in checked:
            value = row.get(field)
            if value is None:
                absent.append(field)
            elif not allowed[op](number(value, field), target):
                violations.append(field)
        if absent:
            missing.append({'id': identity, 'missing_fields': absent, 'failed_fields': violations})
        elif violations:
            failed.append({'id': identity, 'failed_fields': violations})
        else:
            passed.append(row)
    return {'passed': passed, 'failed': failed, 'excluded_missing': missing,
            'universe_count': len(rows), 'rules': rules,
            'caveat': 'Screen on supplied snapshot only; passing is not an investment recommendation'}


def backtest_sma(rows, data):
    fast = integer(data['fast'], 'fast')
    slow = integer(data['slow'], 'slow')
    if fast >= slow:
        raise ValueError('fast must be less than slow')
    if len(rows) <= slow:
        raise ValueError('not enough observations for a next-open test')
    initial = positive(data['initial_cash'], 'initial_cash')
    lot = integer(data.get('lot_size', 1), 'lot_size')
    buy_rate = number(data['buy_cost_bps'], 'buy_cost_bps', 0, 10000) / 10000
    sell_rate = number(data['sell_cost_bps'], 'sell_cost_bps', 0, 10000) / 10000
    slip = number(data['slippage_bps'], 'slippage_bps', 0, 9999) / 10000
    participation = number(data['max_volume_fraction'], 'max_volume_fraction', 0, 1)
    cash, quantity, costs, turnover = initial, 0, 0, 0
    trades, equity = [], []
    pending = None
    closes = [r['close'] for r in rows]
    for i, row in enumerate(rows):
        if i >= slow:
            # Prior close signal; current daily volume is an ex-post fill cap,
            # not information used to decide the signal.
            cap = math.floor(row['volume'] * participation / lot) * lot
            if pending == 'buy' and quantity == 0:
                fill = row['open'] * (1 + slip)
                qty = min(math.floor(cash / (fill * (1 + buy_rate)) / lot) * lot, cap)
                if qty:
                    fees = qty * fill * buy_rate
                    cash -= qty * fill + fees
                    quantity = qty
                    costs += fees + qty * (fill - row['open'])
                    turnover += qty * fill
                    trades.append({'date': row['date'], 'side': 'buy', 'quantity': qty, 'price': fill, 'fees': fees,
                                   'signal_date': rows[i - 1]['date']})
            elif pending == 'sell' and quantity:
                qty = min(quantity, cap)
                if qty:
                    fill = row['open'] * (1 - slip)
                    fees = qty * fill * sell_rate
                    cash += qty * fill - fees
                    quantity -= qty
                    costs += fees + qty * (row['open'] - fill)
                    turnover += qty * fill
                    trades.append({'date': row['date'], 'side': 'sell', 'quantity': qty, 'price': fill, 'fees': fees,
                                   'signal_date': rows[i - 1]['date']})
        if i >= slow - 1:
            equity.append(cash + quantity * row['close'])
            above = statistics.mean(closes[i - fast + 1:i + 1]) > statistics.mean(closes[i - slow + 1:i + 1])
            pending = 'buy' if above else 'sell'
    duration = (date.fromisoformat(rows[-1]['date']) - date.fromisoformat(rows[slow - 1]['date'])).days / 365.25
    # Same executable start, sizing, fees and participation as a one-shot buy-and-hold.
    first = rows[slow]
    bench_price = first['open'] * (1 + slip)
    benchmark_qty = min(math.floor(initial / (bench_price * (1 + buy_rate)) / lot) * lot,
                        math.floor(first['volume'] * participation / lot) * lot)
    benchmark_cash = initial - benchmark_qty * bench_price * (1 + buy_rate)
    benchmark_final = benchmark_cash + benchmark_qty * rows[-1]['close']
    return {'start_signal_date': rows[slow - 1]['date'], 'end_date': rows[-1]['date'],
            'final_equity': equity[-1], 'cash': cash, 'open_quantity': quantity,
            'net_marked_return_pct': (equity[-1] / initial - 1) * 100,
            'annualized_return_pct': ((equity[-1] / initial) ** (1 / duration) - 1) * 100 if duration > 0 else None,
            'max_drawdown_pct': drawdown(equity) * 100,
            'benchmark_marked_return_pct': (benchmark_final / initial - 1) * 100,
            'costs_including_modeled_slippage': costs, 'turnover_to_initial': turnover / initial,
            'fills': trades, 'equity_curve': equity,
            'limitations': ['Single security, long only; no financing or dividends beyond supplied price basis',
                            'Marked at final close; open holdings are not liquidated and no exit cost is charged to either endpoint',
                            'Next-open fills with an ex-post daily-volume cap are simplified, not guaranteed opening liquidity',
                            'Partial entries are not topped up; unfilled entry attempts/remaining exits retry while signal persists',
                            'No point-in-time universe, tax-law engine, circuit-limit or bid/ask queue simulation']}


VERDICTS = {'attractive-now', 'attractive-below', 'watchlist', 'avoid', 'insufficient-evidence'}


def validate_report(data):
    errors = []
    def need(condition, message):
        if not condition:
            errors.append(message)
    need(data.get('schema_version') == 1, 'schema_version must be 1')
    kind = data.get('report_type')
    need(kind in ('stock', 'ipo'), 'report_type must be stock or ipo')
    need(bool(data.get('issuer', {}).get('name')), 'issuer name is required')
    try:
        timestamp(data.get('as_of'), 'as_of')
    except ValueError as exc:
        errors.append(str(exc))
    sources = data.get('sources', [])
    ids = [s.get('id') for s in sources]
    need(all(isinstance(s, str) and s for s in ids) and len(ids) == len(set(ids)), 'source IDs must be nonempty and unique')
    for source in sources:
        need(bool(source.get('url') or source.get('artifact')), 'source requires URL or artifact')
        need(bool(source.get('title')), 'source title is required')
        try:
            timestamp(source.get('retrieved_at'), 'retrieved_at')
        except ValueError as exc:
            errors.append(str(exc))
    known = set(ids)
    def refs(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == 'source_ids':
                    need(isinstance(value, list) and bool(value), 'source_ids must be a nonempty list')
                    if isinstance(value, list):
                        need(all(v in known for v in value), 'unresolved source_ids')
                else:
                    refs(value)
        elif isinstance(obj, list):
            for item in obj:
                refs(item)
    refs(data)
    verdict = data.get('verdict', {})
    need(verdict.get('status') in VERDICTS, 'investment verdict is required')
    need(bool(verdict.get('timeframe')) and bool(verdict.get('rationale')), 'verdict timeframe and rationale are required')
    need(verdict.get('confidence') in ('high', 'medium', 'low'), 'evidence confidence is required')
    need(bool(verdict.get('confidence_reason')), 'confidence_reason is required')
    need('data_gaps' in data and isinstance(data['data_gaps'], list), 'data_gaps list is required')
    price = data.get('reference_price')
    if kind == 'stock':
        entries = data.get('entry_assessment', {})
        need(bool(entries.get('horizon')) and bool(entries.get('market_context')), 'entry horizon and market context are required')
        need(isinstance(entries.get('zones'), list), 'entry zones list is required')
        if not entries.get('zones'):
            need(bool(entries.get('unavailable_reason')), 'empty entry zones need unavailable_reason')
        for zone in entries.get('zones', []):
            for key in ('rationale', 'trigger', 'invalidation', 'reachability', 'source_ids'):
                need(bool(zone.get(key)), f'entry zone requires {key}')
            try:
                low, high = positive(zone.get('low'), 'zone low'), positive(zone.get('high'), 'zone high')
                need(low <= high, 'entry zone low must not exceed high')
            except ValueError as exc:
                errors.append(str(exc))
        if verdict.get('status') in ('attractive-now', 'avoid'):
            need(isinstance(price, dict) and price.get('freshness') == 'verified', 'current-price verdict requires verified reference price')
        if price:
            try:
                positive(price.get('value'), 'reference price')
                observed = timestamp(price.get('observed_at'), 'price observed_at')
                cutoff = timestamp(data.get('as_of'), 'as_of')
                need(observed <= cutoff, 'reference price is after cutoff')
            except ValueError as exc:
                errors.append(str(exc))
            need(bool(price.get('source_ids')), 'reference price needs source_ids')
    if kind == 'ipo':
        gmp_section = data.get('gmp')
        need(isinstance(gmp_section, dict), 'GMP section is mandatory for IPO reports')
        if isinstance(gmp_section, dict):
            need(gmp_section.get('availability') in ('quoted', 'unavailable', 'historical'), 'GMP availability is required')
            need(isinstance(gmp_section.get('quotes'), list), 'GMP quotes list is required')
            if gmp_section.get('availability') == 'unavailable':
                need(bool(gmp_section.get('reason')), 'unavailable GMP needs reason')
            if gmp_section.get('availability') == 'quoted':
                need(any(q.get('premium_rupees') is not None for q in gmp_section.get('quotes', [])), 'quoted GMP needs an actual quote')
            for quote in gmp_section.get('quotes', []):
                need(bool(quote.get('source_ids')), 'GMP quote needs source_ids')
                need(quote.get('freshness') in ('within-age-limit', 'stale', 'unknown', 'date-only-unverified', 'historical'), 'GMP freshness is required')
        listing = data.get('listing_assessment', {})
        need(listing.get('status') in ('favorable', 'mixed', 'unfavorable', 'insufficient-evidence', 'historical'), 'separate listing assessment required')
        need(bool(listing.get('rationale')), 'listing rationale is required')
    if errors:
        raise ValueError('; '.join(errors))
    return {'valid': True, 'checks': 'Required decision fields, source references, entry/GMP contracts; not a financial audit'}


OPERATIONS = {'dcf': dcf, 'multiple': multiple, 'scenario-return': scenario_return,
              'ipo-capitalization': ipo_capitalization, 'gmp': gmp,
              'position-size': position_size, 'portfolio': portfolio, 'screen': screen,
              'validate-report': validate_report}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=[*OPERATIONS, 'indicators', 'reachability', 'backtest-sma', 'normalize-csv'])
    parser.add_argument('--input', help='JSON file, or - for stdin; see references/calculations.md')
    parser.add_argument('--csv', help='Normalized ascending OHLCV CSV')
    parser.add_argument('--output', help='Output file; defaults to stdout; existing files are never replaced')
    args = parser.parse_args(argv)
    try:
        data = {}
        if args.input:
            if args.input == '-':
                data = json.load(sys.stdin)
            else:
                with open(args.input, encoding='utf-8') as handle:
                    data = json.load(handle)
            if not isinstance(data, dict):
                raise ValueError('input must be a JSON object')
        if args.operation in OPERATIONS:
            if not args.input:
                raise ValueError('--input is required')
            result = OPERATIONS[args.operation](data)
        else:
            if not args.csv:
                raise ValueError('--csv is required')
            rows = load_ohlcv(args.csv, data.get('column_mapping'))
            if args.operation == 'indicators':
                result = indicators(rows)
            elif args.operation == 'reachability':
                result = reachability(rows, data)
            elif args.operation == 'backtest-sma':
                result = backtest_sma(rows, data)
            else:
                if not args.output:
                    raise ValueError('normalize-csv requires --output')
                with open(args.output, 'x', newline='', encoding='utf-8') as handle:
                    writer = csv.DictWriter(handle, fieldnames=['date', 'open', 'high', 'low', 'close', 'volume'])
                    writer.writeheader()
                    writer.writerows(rows)
                return 0
        rendered = json.dumps(result, indent=2, allow_nan=False) + '\n'
        if args.output:
            with open(args.output, 'x', encoding='utf-8') as handle:
                handle.write(rendered)
        else:
            print(rendered, end='')
        return 0
    except (ValueError, KeyError, TypeError, OSError, OverflowError) as exc:
        print(f'Input error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
