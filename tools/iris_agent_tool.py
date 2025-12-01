import json
import os
import time
from pathlib import Path

_schema_cache = None
_cache_timestamp = 0

def load_iris_schema(iris_cfg, force_refresh=False):
    global _schema_cache, _cache_timestamp
    
    cache_file = iris_cfg.schema_cache_file
    cache_ttl = iris_cfg.cache_ttl
    now = time.time()
    
    # Check memory cache first
    if _schema_cache and not force_refresh and (now - _cache_timestamp) < cache_ttl:
        logger.info("Using schema from memory cache")
        return _schema_cache
    
    # Check file cache
    if os.path.exists(cache_file) and not force_refresh:
        file_age = now - os.path.getmtime(cache_file)
        if file_age < cache_ttl:
            logger.info("Loading schema from file cache")
            with open(cache_file, 'r') as f:
                _schema_cache = json.load(f)
                _cache_timestamp = now
                return _schema_cache
    
    # Load fresh from DB
    logger.info("Loading schema from IRIS database")
    connection_string = f"iris+pyodbc://{iris_cfg.user}:{iris_cfg.password}@{iris_cfg.host}:{iris_cfg.port}/{iris_cfg.namespace}"
    db = SQLDatabase.from_uri(connection_string)
    
    tables = db.get_usable_table_names()
    schema_info = {
        "tables": tables,
        "timestamp": now,
        "connection": connection_string
    }
    
    # Save to file
    Path(cache_file).parent.mkdir(exist_ok=True)
    with open(cache_file, 'w') as f:
        json.dump(schema_info, f)
    
    _schema_cache = schema_info
    _cache_timestamp = now
    
    logger.info(f"Cached {len(tables)} tables")
    return schema_info