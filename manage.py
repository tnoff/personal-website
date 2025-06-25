#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import logging
import os
import sys

from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter

def setup_otel():
    trace.set_tracer_provider(TracerProvider())
    span_processor = BatchSpanProcessor(OTLPSpanExporter())
    trace.get_tracer_provider().add_span_processor(span_processor)
    DjangoInstrumentor().instrument()

    logger_provider = LoggerProvider()
    set_logger_provider(logger_provider)
    log_exporter = OTLPLogExporter()
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
    handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')

    # This call is what makes the Django application be instrumented
    if 'test' not in sys.argv:
        setup_otel()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
