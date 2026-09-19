# Llama 4 Maverick v2 result - Isha Kirti Ghia

- Trials: 60
- Passed: 10
- Overall pass rate: 16.7%
- Negative trials passed: 9/30
- Negative pass rate: 30.0%
- Measured provider cost: US$0.14812621
- Frozen commit: `42253ad28fc58b36b9014808f9d8e3fd523c01ed`

The most important behaviour was that the model often reached a final
conclusion without successfully invoking the gated decision action. This
caused repeated action-integrity failures. Several request-document cases
also failed because the supplied line dispositions or totals did not satisfy
the tool schema. Two trials encountered backend read timeouts.

At approximately US$0.15, the battery was inexpensive, but the quality was
not worth the measured cost for operational use. A 16.7% pass rate and 30.0%
negative-case pass rate are too low for reliable health-insurance
first-response processing.

**Isha Kirti Ghia - 19 September 2026**