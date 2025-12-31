"""
Configuration module for PriceHound.
Handles storage type selection and other app-wide settings.
"""

import os
from enum import Enum
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Note: ddtrace agentless mode requires a Datadog Agent or serverless environment
# For true agentless tracing without an agent, we disable ddtrace and use OTLP for logs
# If you have a Datadog Agent available, set DD_AGENT_HOST to enable traces
dd_agent_host = os.getenv("DD_AGENT_HOST")
if dd_agent_host:
    # Use local agent for traces
    os.environ.setdefault("DD_TRACE_AGENT_URL", f"http://{dd_agent_host}:8126")


class StorageType(str, Enum):
    """Storage type options."""
    REDIS = "redis"
    FILE = "file"


# Storage configuration
# Set STORAGE_TYPE environment variable to "redis" or "file"
# Default is "file" for simpler local development
STORAGE_TYPE = StorageType(os.getenv("STORAGE_TYPE", "file").lower())

# Redis configuration (only used if STORAGE_TYPE is "redis")
# Set REDIS_URL environment variable to your Redis connection string
REDIS_URL = os.getenv("REDIS_URL", "")


def is_redis_storage() -> bool:
    """Check if Redis storage is configured."""
    return STORAGE_TYPE == StorageType.REDIS


def is_file_storage() -> bool:
    """Check if file storage is configured."""
    return STORAGE_TYPE == StorageType.FILE


def get_storage_type() -> str:
    """Get the current storage type as string."""
    return STORAGE_TYPE.value

