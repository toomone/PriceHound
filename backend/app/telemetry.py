"""
Telemetry configuration for agentless log, trace, and metric shipping to Datadog.

This module provides:
- OTLP-based log export to Datadog (via OpenTelemetry)
- OTLP-based metrics export to Datadog (via OpenTelemetry)
- APM tracing via ddtrace in agentless mode

Both work without requiring a local Datadog Agent - data is sent directly
to Datadog's HTTP intake APIs.

Usage:
    Set environment variables:
        DD_API_KEY: Your Datadog API key (required)
        DD_SITE: Datadog site (default: datadoghq.com)
        DD_SERVICE: Service name (default: pricehound)
        DD_ENV: Environment (default: production)
        DD_VERSION: Version (default: APP_VERSION from version.py)
"""
import os
import logging
from typing import Optional, Dict, Any

from .version import APP_VERSION

logger = logging.getLogger("pricehound.telemetry")

# Track if telemetry is initialized
_telemetry_initialized = False
_tracing_initialized = False
_metrics_initialized = False
_logger_provider = None
_meter_provider = None
_meter = None

# Metric counters
_counters: Dict[str, Any] = {}


class DatadogLogProcessor:
    """Custom processor to normalize log levels for Datadog (lowercase).
    
    Datadog expects log levels like 'info', 'warning', 'error' (lowercase),
    but OpenTelemetry sends 'INFO', 'WARNING', 'ERROR' (uppercase).
    This processor normalizes them before export.
    """
    
    def __init__(self, next_processor):
        self._next_processor = next_processor
    
    def on_emit(self, log_data):
        # Convert severity text to lowercase for Datadog
        if hasattr(log_data, 'severity_text') and log_data.severity_text:
            # Modify the severity_text attribute directly
            log_data.severity_text = log_data.severity_text.lower()
        self._next_processor.on_emit(log_data)
    
    def shutdown(self):
        self._next_processor.shutdown()
    
    def force_flush(self, timeout_millis=30000):
        return self._next_processor.force_flush(timeout_millis)


def setup_otlp_logging() -> bool:
    """Configure OpenTelemetry to ship logs to Datadog via OTLP.
    
    Returns:
        True if OTLP logging was successfully configured, False otherwise.
    """
    global _telemetry_initialized, _logger_provider
    
    if _telemetry_initialized:
        logger.debug("OTLP logging already initialized")
        return True
    
    dd_api_key = os.getenv("DD_API_KEY")
    dd_site = os.getenv("DD_SITE", "datadoghq.com")
    
    if not dd_api_key:
        logger.warning("⚠️ DD_API_KEY not set - OTLP logging disabled (logs will only go to console)")
        return False
    
    try:
        # Import OpenTelemetry components (only when needed)
        from opentelemetry import _logs
        from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
        from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
        from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
        from opentelemetry.sdk.resources import Resource
        
        # Service metadata from environment
        service_name = os.getenv("DD_SERVICE", "pricehound")
        service_version = os.getenv("DD_VERSION", APP_VERSION)
        environment = os.getenv("DD_ENV", "production")
        hostname = os.getenv("RENDER_SERVICE_NAME", os.getenv("HOSTNAME", "local"))
        
        # Define resource attributes (service metadata)
        resource = Resource.create({
            "service.name": service_name,
            "service.version": service_version,
            "deployment.environment": environment,
            "host.name": hostname,
        })
        
        # Datadog OTLP intake endpoint for logs
        # Format: https://otlp.{site}/v1/logs
        otlp_endpoint = f"https://otlp.{dd_site}/v1/logs"
        
        logger.info(f"🔗 OTLP endpoint: {otlp_endpoint}")
        
        # Create OTLP exporter with Datadog API key header
        exporter = OTLPLogExporter(
            endpoint=otlp_endpoint,
            headers={
                "DD-API-KEY": dd_api_key,
            }
        )
        
        # Set up logger provider with batch processing
        _logger_provider = LoggerProvider(resource=resource)
        
        # Wrap batch processor with Datadog normalizer (lowercase log levels)
        batch_processor = BatchLogRecordProcessor(exporter)
        datadog_processor = DatadogLogProcessor(batch_processor)
        _logger_provider.add_log_record_processor(datadog_processor)
        
        _logs.set_logger_provider(_logger_provider)
        
        # Create handler and attach to root logger
        otlp_handler = LoggingHandler(
            level=logging.INFO,
            logger_provider=_logger_provider
        )
        
        # Add handler to root logger so all loggers inherit it
        logging.getLogger().addHandler(otlp_handler)
        
        _telemetry_initialized = True
        logger.info(f"✅ OTLP logging enabled → {dd_site} (service: {service_name}, env: {environment})")
        return True
        
    except ImportError as e:
        logger.error(f"❌ OpenTelemetry packages not installed: {e}")
        logger.error("   Install with: pip install opentelemetry-sdk opentelemetry-exporter-otlp-proto-http")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to setup OTLP logging: {e}")
        return False


def setup_otlp_metrics() -> bool:
    """Configure OpenTelemetry to ship metrics to Datadog via OTLP.
    
    Returns:
        True if OTLP metrics was successfully configured, False otherwise.
    """
    global _metrics_initialized, _meter_provider, _meter, _counters
    
    if _metrics_initialized:
        logger.debug("OTLP metrics already initialized")
        return True
    
    dd_api_key = os.getenv("DD_API_KEY")
    dd_site = os.getenv("DD_SITE", "datadoghq.com")
    
    if not dd_api_key:
        logger.warning("⚠️ DD_API_KEY not set - OTLP metrics disabled")
        return False
    
    try:
        from opentelemetry import metrics
        from opentelemetry.sdk.metrics import MeterProvider, Counter, UpDownCounter, Histogram, ObservableCounter, ObservableUpDownCounter, ObservableGauge
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, AggregationTemporality
        from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
        from opentelemetry.sdk.resources import Resource
        
        # Service metadata from environment
        service_name = os.getenv("DD_SERVICE", "pricehound")
        service_version = os.getenv("DD_VERSION", APP_VERSION)
        environment = os.getenv("DD_ENV", "production")
        
        # Define resource attributes (service metadata)
        resource = Resource.create({
            "service.name": service_name,
            "service.version": service_version,
            "deployment.environment": environment,
        })
        
        # Datadog OTLP intake endpoint for metrics
        otlp_endpoint = f"https://otlp.{dd_site}/v1/metrics"
        
        logger.info(f"🔗 OTLP metrics endpoint: {otlp_endpoint}")
        
        # Datadog requires Delta temporality for counters (not Cumulative)
        temporality_delta = {
            Counter: AggregationTemporality.DELTA,
            UpDownCounter: AggregationTemporality.DELTA,
            Histogram: AggregationTemporality.DELTA,
            ObservableCounter: AggregationTemporality.DELTA,
            ObservableUpDownCounter: AggregationTemporality.DELTA,
            ObservableGauge: AggregationTemporality.DELTA,
        }
        
        # Create OTLP exporter with Datadog API key header and Delta temporality
        exporter = OTLPMetricExporter(
            endpoint=otlp_endpoint,
            headers={"DD-API-KEY": dd_api_key},
            preferred_temporality=temporality_delta
        )
        
        # Export metrics every 60 seconds
        reader = PeriodicExportingMetricReader(exporter, export_interval_millis=60000)
        _meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
        metrics.set_meter_provider(_meter_provider)
        _meter = metrics.get_meter("pricehound")
        
        # Create counters for various events
        _counters["quotes_created"] = _meter.create_counter(
            "pricehound.quotes.created",
            description="Number of quotes created (public URLs)"
        )
        _counters["quotes_viewed"] = _meter.create_counter(
            "pricehound.quotes.viewed",
            description="Number of times shared quotes are viewed"
        )
        _counters["pricing_sync"] = _meter.create_counter(
            "pricehound.sync.pricing",
            description="Number of pricing sync operations"
        )
        
        _metrics_initialized = True
        logger.info(f"✅ OTLP metrics enabled → {dd_site} (service: {service_name}, env: {environment})")
        return True
        
    except ImportError as e:
        logger.error(f"❌ OpenTelemetry metrics packages not installed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to setup OTLP metrics: {e}")
        return False


def record_quote_created(region: str, protected: bool = False) -> None:
    """Record a quote creation metric."""
    if _metrics_initialized and "quotes_created" in _counters:
        _counters["quotes_created"].add(1, {
            "region": region,
            "protected": str(protected).lower()
        })


def record_quote_viewed(region: str) -> None:
    """Record a quote view metric."""
    if _metrics_initialized and "quotes_viewed" in _counters:
        _counters["quotes_viewed"].add(1, {"region": region})


def record_pricing_sync(region: str, products_count: int, success: bool = True) -> None:
    """Record a pricing sync metric."""
    if _metrics_initialized and "pricing_sync" in _counters:
        _counters["pricing_sync"].add(1, {
            "region": region,
            "products_count": str(products_count),
            "success": str(success).lower()
        })


def setup_ddtrace() -> bool:
    """Configure ddtrace for APM tracing to Datadog.
    
    Note: ddtrace requires a Datadog Agent for trace collection.
    Set DD_AGENT_HOST to enable tracing (e.g., localhost for local agent).
    Without an agent, traces will not be sent but instrumentation still works locally.
    
    Returns:
        True if ddtrace was successfully configured, False otherwise.
    """
    global _tracing_initialized
    
    if _tracing_initialized:
        logger.debug("ddtrace already initialized")
        return True
    
    dd_agent_host = os.getenv("DD_AGENT_HOST")
    
    # Service metadata from environment
    service_name = os.getenv("DD_SERVICE", "pricehound")
    service_version = os.getenv("DD_VERSION", APP_VERSION)
    environment = os.getenv("DD_ENV", "production")
    
    if not dd_agent_host:
        logger.info("ℹ️ DD_AGENT_HOST not set - ddtrace disabled (set DD_AGENT_HOST to enable APM traces)")
        logger.info("   Logs are still sent via OTLP if DD_API_KEY is configured")
        return False
    
    # Log the trace endpoint
    trace_url = os.getenv("DD_TRACE_AGENT_URL", f"http://{dd_agent_host}:8126")
    logger.info(f"🔗 Trace endpoint: {trace_url}")
    
    try:
        import ddtrace
        from ddtrace import patch_all
        
        # Enable log injection for trace correlation (adds trace_id, span_id to logs)
        ddtrace.config.logs_injection = True
        
        # Auto-instrument supported libraries (FastAPI, requests, redis, etc.)
        patch_all()
        
        _tracing_initialized = True
        logger.info(f"✅ ddtrace enabled → agent at {dd_agent_host} (service: {service_name}, env: {environment})")
        return True
        
    except ImportError as e:
        logger.error(f"❌ ddtrace package not installed: {e}")
        logger.error("   Install with: pip install ddtrace")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to setup ddtrace: {e}")
        return False


def shutdown_telemetry() -> None:
    """Gracefully shutdown telemetry exporters.
    
    This should be called on application shutdown to ensure
    all buffered logs, metrics, and traces are flushed to Datadog.
    """
    global _telemetry_initialized, _tracing_initialized, _metrics_initialized
    global _logger_provider, _meter_provider
    
    # Shutdown OTLP logging
    if _telemetry_initialized and _logger_provider is not None:
        try:
            logger.info("🔄 Flushing remaining logs to Datadog...")
            if hasattr(_logger_provider, 'shutdown'):
                _logger_provider.shutdown()
            logger.info("✅ OTLP logging shutdown complete")
        except Exception as e:
            logger.error(f"⚠️ Error during OTLP logging shutdown: {e}")
        finally:
            _telemetry_initialized = False
            _logger_provider = None
    
    # Shutdown OTLP metrics
    if _metrics_initialized and _meter_provider is not None:
        try:
            logger.info("🔄 Flushing remaining metrics to Datadog...")
            if hasattr(_meter_provider, 'shutdown'):
                _meter_provider.shutdown()
            logger.info("✅ OTLP metrics shutdown complete")
        except Exception as e:
            logger.error(f"⚠️ Error during OTLP metrics shutdown: {e}")
        finally:
            _metrics_initialized = False
            _meter_provider = None
    
    # Shutdown ddtrace
    if _tracing_initialized:
        try:
            from ddtrace import tracer
            logger.info("🔄 Flushing remaining traces to Datadog...")
            tracer.shutdown()
            logger.info("✅ ddtrace shutdown complete")
        except Exception as e:
            logger.error(f"⚠️ Error during ddtrace shutdown: {e}")
        finally:
            _tracing_initialized = False


def is_telemetry_enabled() -> bool:
    """Check if OTLP logging is currently enabled."""
    return _telemetry_initialized


def is_metrics_enabled() -> bool:
    """Check if OTLP metrics is currently enabled."""
    return _metrics_initialized


def is_tracing_enabled() -> bool:
    """Check if ddtrace tracing is currently enabled."""
    return _tracing_initialized

