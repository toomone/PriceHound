"""
Telemetry configuration for agentless log and trace shipping to Datadog.

This module provides:
- OTLP-based log export to Datadog (via OpenTelemetry)
- APM tracing via ddtrace in agentless mode

Both work without requiring a local Datadog Agent - data is sent directly
to Datadog's HTTP intake APIs.

Usage:
    Set environment variables:
        DD_API_KEY: Your Datadog API key (required)
        DD_SITE: Datadog site (default: datadoghq.com)
        DD_SERVICE: Service name (default: pricehound)
        DD_ENV: Environment (default: production)
        DD_VERSION: Version (default: 1.0.0)
"""
import os
import logging
from typing import Optional

logger = logging.getLogger("pricehound.telemetry")

# Track if telemetry is initialized
_telemetry_initialized = False
_tracing_initialized = False
_logger_provider = None


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
        service_version = os.getenv("DD_VERSION", "1.0.0")
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
        _logger_provider.add_log_record_processor(
            BatchLogRecordProcessor(exporter)
        )
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
    service_version = os.getenv("DD_VERSION", "1.0.0")
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
    all buffered logs and traces are flushed to Datadog.
    """
    global _telemetry_initialized, _tracing_initialized, _logger_provider
    
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
    """Check if OTLP telemetry is currently enabled."""
    return _telemetry_initialized


def is_tracing_enabled() -> bool:
    """Check if ddtrace tracing is currently enabled."""
    return _tracing_initialized

