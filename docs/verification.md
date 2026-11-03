# Verification evidence

On 2026-11-03, the deterministic unit/integration suite passed with core coverage above 85%; exact release coverage is recorded by CI. Checks cover chronological labels, family splits, authorization rules, approvals/revocations, context loss, structured extraction, hybrid filtering, mock-model evidence validation, failure accounting, reproducibility, API/CLI/export behavior and adapter budgets/retries.

The 648 saved observations reproduce exactly after excluding review/extraction wall-clock measurements. All eight predeclared context/evidence settings executed successfully. Ruff, strict type checking, Bandit, Node dashboard utilities, credential-pattern scanning, hashed dependency audit, distribution and non-root container checks are release gates. GitHub Actions provides current commit-specific evidence.

The running dashboard was inspected at the desktop breakpoint, including actual saved metrics, strategy/category selection and reconstructed evidence timelines. Screenshots: [dashboard](images/dashboard.jpg), [trace](images/trace.jpg). No real-model evaluation or paid API request was executed. Browser review is not a formal accessibility certification.
