# Verification evidence

On 2026-11-03, the deterministic unit/integration suite passed with core coverage above 85%; exact release coverage is recorded by CI. Checks cover chronological labels, family splits, authorization rules, approvals/revocations, context loss, structured extraction, hybrid filtering, mock-model evidence validation, failure accounting, reproducibility, API/CLI/export behavior and adapter budgets/retries.

The 648 saved observations reproduce exactly after excluding review/extraction wall-clock measurements. All eight predeclared context/evidence settings executed successfully. Ruff, strict type checking, Bandit, Node dashboard utilities, credential-pattern scanning, hashed dependency audit, distribution and non-root container checks are release gates. GitHub Actions provides current commit-specific evidence.

The running dashboard was inspected at the desktop breakpoint, including actual saved metrics, strategy/category selection and reconstructed evidence timelines. Screenshots: [dashboard](images/dashboard.jpg), [trace](images/trace.jpg). No real-model evaluation or paid API request was executed. Browser review is not a formal accessibility certification.

## Final local release gate

Python 3.12.16: 22 pytest tests passed; 95.93% branch-inclusive core coverage. Three Node dashboard tests passed. Ruff, strict mypy and Bandit passed. Saved observations and source fingerprints reproduced. The single TestClient deprecation warning is retained; it does not affect the passing assertions. GitHub Actions verifies the final published commit separately.

Fresh wheel installation verified hashed runtime dependencies, exact experiment observations and source fingerprints, plus the installed dashboard/API. See [installation evidence](../results/installation-verification.json). Mobile layout checks observed a 375 px content viewport with no horizontal page overflow; desktop checks used the 1440×1000 breakpoint. Long scenario JSON loads on demand to keep filtering responsive.

## v0.1.1 security patch verification

Python 3.12.16: 32 pytest tests passed with 96.82% branch-inclusive coverage. All ten new provider JSON regression tests passed; the excessive-nesting test failed against the original implementation. Three Node dashboard tests, Ruff lint/format, strict mypy and Bandit passed. A fresh read-only reviewer found no concrete surviving bypass or regression in the patch. The existing TestClient deprecation warning remains visible. See [audit scope and remediation](security-audit.md).
