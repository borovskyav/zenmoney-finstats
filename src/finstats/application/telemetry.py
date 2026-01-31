from __future__ import annotations

from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider


def configure_metrics() -> None:
    metrics_reader = PrometheusMetricReader()
    provider = MeterProvider(metric_readers=[metrics_reader])
    metrics.set_meter_provider(provider)
