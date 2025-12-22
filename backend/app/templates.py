"""
Template management for PriceHound.
Handles storage and retrieval of quote templates from Redis.
"""

import json
import uuid
import logging
from datetime import datetime
from typing import Optional

from .models import Template, TemplateItem
from .redis_client import get_redis, is_redis_available, RedisKeys

logger = logging.getLogger("pricehound.templates")


# Default templates to seed on startup
DEFAULT_TEMPLATES = [
    {
        "id": "website-fullstack",
        "name": "Full Stack Website",
        "description": "Complete observability for a web application with frontend, backend, database, and logs",
        "icon": "🌐",
        "region": "us",
        "items": [
            {"product_name": "APM Hosts", "quantity": 2},
            {"product_name": "Infrastructure Hosts", "quantity": 3},
            {"product_name": "RUM Sessions", "quantity": 100000},
            {"product_name": "Database Hosts", "quantity": 1},
            {"product_name": "Logs Ingested", "quantity": 10},
            {"product_name": "Logs Indexed (15-day Retention)", "quantity": 5},
        ]
    },
    {
        "id": "iot-infrastructure",
        "name": "IoT Project",
        "description": "Monitor IoT devices with metrics, logs, and incident management",
        "icon": "📡",
        "region": "us",
        "items": [
            {"product_name": "Custom Metrics", "quantity": 500},
            {"product_name": "Infrastructure Hosts", "quantity": 5},
            {"product_name": "Logs Ingested", "quantity": 50},
            {"product_name": "Logs Indexed (3-day Retention)", "quantity": 10},
            {"product_name": "Incident Management (Per User)", "quantity": 5},
            {"product_name": "On-Call", "quantity": 5},
        ]
    },
    {
        "id": "kubernetes-aws",
        "name": "Kubernetes on AWS",
        "description": "Full K8s cluster monitoring with containers, cloud costs, and log management",
        "icon": "☸️",
        "region": "us",
        "items": [
            {"product_name": "Infrastructure Hosts", "quantity": 10},
            {"product_name": "Containers", "quantity": 100},
            {"product_name": "APM Hosts", "quantity": 5},
            {"product_name": "Cloud Cost Management", "quantity": 1},
            {"product_name": "Logs Ingested", "quantity": 100},
            {"product_name": "Logs Indexed (7-day Retention)", "quantity": 30},
        ]
    }
]


def get_all_templates() -> list[Template]:
    """Get all templates from Redis."""
    redis_client = get_redis()
    
    if not redis_client or not is_redis_available():
        logger.warning("Redis not available, returning default templates")
        return _get_default_templates()
    
    try:
        # Get all template IDs from index
        template_ids = redis_client.get_index(RedisKeys.TEMPLATES_INDEX)
        
        if not template_ids:
            # No templates in Redis, seed defaults
            logger.info("No templates found, seeding defaults...")
            seed_default_templates()
            template_ids = redis_client.get_index(RedisKeys.TEMPLATES_INDEX)
        
        templates = []
        for template_id in template_ids:
            template_data = redis_client.get_json(RedisKeys.template(template_id))
            if template_data:
                templates.append(Template(**template_data))
        
        # Sort by name for consistent ordering
        templates.sort(key=lambda t: t.name)
        return templates
        
    except Exception as e:
        logger.error(f"Failed to get templates from Redis: {e}")
        return _get_default_templates()


def get_template(template_id: str) -> Optional[Template]:
    """Get a single template by ID."""
    redis_client = get_redis()
    
    if not redis_client or not is_redis_available():
        # Return from defaults if Redis not available
        for tmpl in DEFAULT_TEMPLATES:
            if tmpl["id"] == template_id:
                return _dict_to_template(tmpl)
        return None
    
    try:
        template_data = redis_client.get_json(RedisKeys.template(template_id))
        if template_data:
            return Template(**template_data)
        return None
    except Exception as e:
        logger.error(f"Failed to get template {template_id}: {e}")
        return None


def create_template(
    name: str,
    description: str,
    icon: str,
    items: list[dict],
    region: str = "us"
) -> Template:
    """Create a new template."""
    redis_client = get_redis()
    
    template_id = str(uuid.uuid4())[:8]  # Short ID for templates
    now = datetime.utcnow().isoformat()
    
    template = Template(
        id=template_id,
        name=name,
        description=description,
        icon=icon,
        region=region,
        items=[TemplateItem(**item) for item in items],
        created_at=now
    )
    
    if redis_client and is_redis_available():
        try:
            # Store template
            redis_client.set_json(
                RedisKeys.template(template_id),
                template.model_dump()
            )
            # Add to index
            redis_client.add_to_index(RedisKeys.TEMPLATES_INDEX, template_id)
            logger.info(f"Created template: {name} ({template_id})")
        except Exception as e:
            logger.error(f"Failed to store template in Redis: {e}")
    
    return template


def seed_default_templates() -> int:
    """Seed the default templates into Redis. Returns count of templates seeded."""
    redis_client = get_redis()
    
    if not redis_client or not is_redis_available():
        logger.warning("Redis not available, cannot seed templates")
        return 0
    
    count = 0
    for tmpl_data in DEFAULT_TEMPLATES:
        try:
            template = _dict_to_template(tmpl_data)
            
            # Store template
            redis_client.set_json(
                RedisKeys.template(template.id),
                template.model_dump()
            )
            # Add to index
            redis_client.add_to_index(RedisKeys.TEMPLATES_INDEX, template.id)
            count += 1
            logger.info(f"Seeded template: {template.name}")
            
        except Exception as e:
            logger.error(f"Failed to seed template {tmpl_data.get('name')}: {e}")
    
    return count


def _dict_to_template(data: dict) -> Template:
    """Convert a dict to a Template model."""
    return Template(
        id=data["id"],
        name=data["name"],
        description=data["description"],
        icon=data["icon"],
        region=data.get("region", "us"),
        items=[TemplateItem(**item) for item in data["items"]],
        created_at=data.get("created_at", datetime.utcnow().isoformat())
    )


def _get_default_templates() -> list[Template]:
    """Get default templates as Template objects."""
    return [_dict_to_template(tmpl) for tmpl in DEFAULT_TEMPLATES]

