# Independent evidence notes — 19 October 2026

These sources provide reasons to investigate momentum, not validation of our bot.
This pass reviewed the linked primary-source abstracts/metadata, not a full
replication or systematic literature review.

- Liu and Tsyvinski, *Risks and Returns of Cryptocurrency*, NBER Working Paper
  24877, August 2018; published in Review of Financial Studies (2021). The study
  reports time-series momentum in Bitcoin, Ripple and Ethereum and prediction
  associated with investor attention. It does not establish our 17-pair,
  four-hour, long-only spot system's profitability under present fees.
  https://www.nber.org/papers/w24877
- Liu, Tsyvinski and Wu, *Common Risk Factors in Cryptocurrency*, NBER Working
  Paper 25882, May 2019; published in Journal of Finance (2022). The abstract
  identifies market, size and momentum factors and describes long-short factor
  strategies. A long-short factor result is not directly transferable to our
  unleveraged long-only rules, universe or execution costs.
  https://www.nber.org/papers/w25882
- Freqtrade official lookahead-analysis documentation says its verification
  assumes single-pair and full-pairlist equivalence. Our ranking depends on all
  17 markets. Therefore do not claim a routine single-pair lookahead pass proves
  this cross-sectional implementation is causal; use full-universe prefix tests
  and additional engine-specific review.
  https://www.freqtrade.io/en/stable/lookahead-analysis/

Interpretation: momentum has primary research support as a broad phenomenon.
There is no source here validating our five-day versus twenty-day horizon,
SMA conditions, top-five/top-nine cutoffs, a dependable income stream, or regional
exchange eligibility. No new strategy parameters were inferred from abstracts.
Our historical results remain selected-universe-biased and already inspected.
