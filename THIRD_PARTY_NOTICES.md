# Reference and attribution

Upstream: https://github.com/tradermonty/claude-trading-skills
Author: TraderMonty. Reviewed on 2026-11-02.

This suite contains original Indian-market instructions and Python implementations.
Workflow concepts informed by the following reviewed upstream skills include:

- `market-news-analyst`: event collection, timestamps, impact ranking, and observed
  market reaction separated from interpretation.
- `market-breadth-analyzer`: assess participation alongside headline indices.
- `position-sizer`: risk-distance sizing constrained by capital and exposure.
- `sector-analyst`: sector participation and cycle positioning.
- `scenario-analyzer`: direct and indirect event transmission and scenario review.
- The repository index/README: explicit workflow dependencies, journaling,
  postmortems, and backtest-oriented review.

References use the upstream `main` URLs; no upstream source code has been vendored
or executed. India-specific evidence rules, valuation, GMP handling, entry
reachability methods, and calculation helpers are implemented here. If future
changes import source, record the exact upstream commit and imported files here.
The upstream license is retained below for attribution to adapted workflow ideas.

## Upstream MIT license

Copyright (c) 2026 TraderMonty

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
