from __future__ import annotations

from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider

_metrics_reader: PrometheusMetricReader | None = None


def configure_metrics() -> None:
    global _metrics_reader
    _metrics_reader = PrometheusMetricReader()
    provider = MeterProvider(metric_readers=[_metrics_reader])
    metrics.set_meter_provider(provider)
