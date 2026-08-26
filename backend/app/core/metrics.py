from prometheus_client import Counter, Histogram

ASSESSMENTS_TOTAL = Counter(
    "trustops_assessments_total",
    "Assessments completed, by final status and certification level",
    ["status", "certification_level"],
)

ASSESSMENT_DURATION = Histogram(
    "trustops_assessment_duration_seconds",
    "Total wall-clock time of an assessment run, end to end",
)

SCANNER_DURATION = Histogram(
    "trustops_scanner_duration_seconds",
    "Wall-clock time of a single scanner run",
    ["tool"],
)

SCANNER_ERRORS_TOTAL = Counter(
    "trustops_scanner_errors_total",
    "Scanner runs that raised an exception (isolated failure, not a full assessment failure)",
    ["tool"],
)
