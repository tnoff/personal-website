# https://github.com/open-telemetry/opentelemetry-python/discussions/4294
import logging

from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs import LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter

class CustomLoggingHandler(LoggingHandler):
    def __init__(self, level=logging.INFO, logger_provider=None) -> None:
        logger_provider = LoggerProvider()
        set_logger_provider(logger_provider)
        logger_provider.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter()))
        super().__init__(level, logger_provider)