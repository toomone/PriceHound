#!/usr/bin/env python3
"""
Redis backup script for PriceHound.
Exports all Redis keys to JSON files for disaster recovery.

Usage:
    REDIS_URL=redis://... python backup_redis.py
    
Or with restore:
    REDIS_URL=redis://... python backup_redis.py --restore backups/redis_backup_20240101_120000.json
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Optional

try:
    import redis
except ImportError:
    print("❌ Redis package not installed. Run: pip install redis")
    sys.exit(1)


def get_redis_client() -> redis.Redis:
    """Create Redis client from environment variable."""
    redis_url = os.environ.get("REDIS_URL")
    if not redis_url:
        print("❌ REDIS_URL environment variable not set")
        sys.exit(1)
    
    return redis.from_url(redis_url, decode_responses=True)


def backup_redis(output_dir: str = "backups") -> Optional[str]:
    """
    Backup all Redis keys to a JSON file.
    
    Args:
        output_dir: Directory to save backup files
        
    Returns:
        Path to the backup file, or None on failure
    """
    try:
        client = get_redis_client()
        client.ping()
        print("✅ Connected to Redis")
    except redis.ConnectionError as e:
        print(f"❌ Failed to connect to Redis: {e}")
        return None
    
    # Get all keys
    keys = client.keys("*")
    print(f"📦 Found {len(keys)} keys to backup")
    
    if not keys:
        print("⚠️ No keys found in Redis, nothing to backup")
        return None
    
    backup_data = {
        "metadata": {
            "created_at": datetime.utcnow().isoformat(),
            "key_count": len(keys),
            "version": "1.0"
        },
        "keys": {}
    }
    
    for key in keys:
        try:
            key_type = client.type(key)
            
            if key_type == "string":
                value = client.get(key)
                # Try to parse as JSON for cleaner storage
                try:
                    parsed_value = json.loads(value)
                    backup_data["keys"][key] = {
                        "type": "string",
                        "is_json": True,
                        "value": parsed_value
                    }
                except (json.JSONDecodeError, TypeError):
                    backup_data["keys"][key] = {
                        "type": "string",
                        "is_json": False,
                        "value": value
                    }
            
            elif key_type == "zset":
                # Sorted set (used for indexes like quotes:index)
                members = client.zrange(key, 0, -1, withscores=True)
                backup_data["keys"][key] = {
                    "type": "zset",
                    "value": [[m, s] for m, s in members]
                }
            
            elif key_type == "hash":
                backup_data["keys"][key] = {
                    "type": "hash",
                    "value": client.hgetall(key)
                }
            
            elif key_type == "list":
                backup_data["keys"][key] = {
                    "type": "list",
                    "value": client.lrange(key, 0, -1)
                }
            
            elif key_type == "set":
                backup_data["keys"][key] = {
                    "type": "set",
                    "value": list(client.smembers(key))
                }
            
            else:
                print(f"⚠️ Skipping key '{key}' with unsupported type: {key_type}")
                
        except Exception as e:
            print(f"⚠️ Error backing up key '{key}': {e}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Save backup with timestamp
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_dir, f"redis_backup_{timestamp}.json")
    
    with open(filename, "w") as f:
        json.dump(backup_data, f, indent=2, default=str)
    
    # Calculate file size
    file_size = os.path.getsize(filename)
    size_str = f"{file_size / 1024:.1f} KB" if file_size > 1024 else f"{file_size} bytes"
    
    print(f"✅ Backup saved to {filename} ({size_str})")
    print(f"   Keys backed up: {len(backup_data['keys'])}")
    
    return filename


def restore_redis(backup_file: str, dry_run: bool = False) -> bool:
    """
    Restore Redis keys from a backup file.
    
    Args:
        backup_file: Path to the backup JSON file
        dry_run: If True, only simulate the restore
        
    Returns:
        True on success, False on failure
    """
    if not os.path.exists(backup_file):
        print(f"❌ Backup file not found: {backup_file}")
        return False
    
    with open(backup_file, "r") as f:
        backup_data = json.load(f)
    
    print(f"📂 Loading backup from {backup_file}")
    print(f"   Created: {backup_data['metadata']['created_at']}")
    print(f"   Keys: {backup_data['metadata']['key_count']}")
    
    if dry_run:
        print("\n🔍 DRY RUN - No changes will be made")
        for key, data in backup_data["keys"].items():
            print(f"   Would restore: {key} ({data['type']})")
        return True
    
    try:
        client = get_redis_client()
        client.ping()
        print("✅ Connected to Redis")
    except redis.ConnectionError as e:
        print(f"❌ Failed to connect to Redis: {e}")
        return False
    
    restored = 0
    errors = 0
    
    for key, data in backup_data["keys"].items():
        try:
            key_type = data["type"]
            value = data["value"]
            
            if key_type == "string":
                if data.get("is_json", False):
                    client.set(key, json.dumps(value))
                else:
                    client.set(key, value)
            
            elif key_type == "zset":
                client.delete(key)  # Clear existing
                for member, score in value:
                    client.zadd(key, {member: score})
            
            elif key_type == "hash":
                client.delete(key)
                if value:
                    client.hset(key, mapping=value)
            
            elif key_type == "list":
                client.delete(key)
                if value:
                    client.rpush(key, *value)
            
            elif key_type == "set":
                client.delete(key)
                if value:
                    client.sadd(key, *value)
            
            restored += 1
            
        except Exception as e:
            print(f"⚠️ Error restoring key '{key}': {e}")
            errors += 1
    
    print(f"\n✅ Restore complete: {restored} keys restored, {errors} errors")
    return errors == 0


def main():
    parser = argparse.ArgumentParser(
        description="Backup and restore Redis database for PriceHound"
    )
    parser.add_argument(
        "--restore",
        metavar="FILE",
        help="Restore from a backup file instead of creating a backup"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate restore without making changes"
    )
    parser.add_argument(
        "--output-dir",
        default="backups",
        help="Directory for backup files (default: backups)"
    )
    
    args = parser.parse_args()
    
    if args.restore:
        success = restore_redis(args.restore, dry_run=args.dry_run)
        sys.exit(0 if success else 1)
    else:
        result = backup_redis(output_dir=args.output_dir)
        sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()

