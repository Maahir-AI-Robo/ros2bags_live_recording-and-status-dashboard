"""
ML Exporter

Create ML-ready dataset packages from completed ros2 bag recordings.

The exporter creates a directory for each bag under `ml_datasets/` containing:
 - raw/ (copy of the original bag files)
 - metadata.json (bag metadata: filename, filesize, duration, topics)
 - schema.json (topic -> message type mapping)
 - package.tar.gz (compressed archive of raw/)

This is intentionally lightweight and avoids heavy ML dependencies. Downstream
pipelines can convert the packaged data to TFRecord/Parquet/etc.
"""

import os
import shutil
import json
import tarfile
from datetime import datetime
from typing import Dict, Any, Optional


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def package_bag_for_ml(bag_path: str, out_root: Optional[str] = None) -> Dict[str, Any]:
    """Package a completed bag directory/file into an ML dataset package.

    Args:
        bag_path: Path to the bag file or bag directory.
        out_root: Root directory where ml_datasets will be created. Defaults to
            <cwd>/ml_datasets.

    Returns:
        A dict with package information (package_dir, metadata_path, archive_path).
    """
    if not out_root:
        out_root = os.path.join(os.getcwd(), 'ml_datasets')

    if not os.path.exists(bag_path):
        raise FileNotFoundError(f"Bag path does not exist: {bag_path}")

    bag_name = os.path.basename(bag_path.rstrip(os.sep))
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    package_dir = os.path.join(out_root, f"{bag_name}_{timestamp}")
    raw_dir = os.path.join(package_dir, 'raw')

    ensure_dir(raw_dir)

    # Copy bag contents into raw/
    if os.path.isdir(bag_path):
        # Copy directory tree
        dest_path = os.path.join(raw_dir, bag_name)
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)
        shutil.copytree(bag_path, dest_path)
    else:
        # Single file bag
        shutil.copy2(bag_path, raw_dir)

    # Build metadata
    total_size = 0
    for root, _, files in os.walk(raw_dir):
        for f in files:
            total_size += os.path.getsize(os.path.join(root, f))

    metadata = {
        'bag_name': bag_name,
        'original_path': os.path.abspath(bag_path),
        'packaged_at': datetime.now().isoformat(),
        'raw_size_bytes': total_size,
    }

    # Write metadata.json
    metadata_path = os.path.join(package_dir, 'metadata.json')
    with open(metadata_path, 'w') as fh:
        json.dump(metadata, fh, indent=2)

    # Create a lightweight schema placeholder - downstream pipelines can
    # populate with actual topic->type mapping if available.
    schema = {
        'notes': 'Topic and message type schema can be filled by ros2_manager.get_bag_info',
        'topics': {}
    }
    schema_path = os.path.join(package_dir, 'schema.json')
    with open(schema_path, 'w') as fh:
        json.dump(schema, fh, indent=2)

    # Create compressed archive of raw/
    archive_path = os.path.join(package_dir, f'{bag_name}.tar.gz')
    with tarfile.open(archive_path, 'w:gz') as tar:
        tar.add(raw_dir, arcname=os.path.basename(raw_dir))

    return {
        'package_dir': package_dir,
        'metadata_path': metadata_path,
        'schema_path': schema_path,
        'archive_path': archive_path,
    }


def populate_schema_with_bag_info(package_dir: str, bag_info: Dict[str, Any]) -> None:
    """Populate schema.json in package_dir with topic/type info from bag_info.

    This function expects bag_info to be a dict returned by ros2_manager.get_bag_info.
    """
    schema_path = os.path.join(package_dir, 'schema.json')
    if not os.path.exists(schema_path):
        # create default
        with open(schema_path, 'w') as fh:
            json.dump({'topics': {}}, fh)

    with open(schema_path, 'r') as fh:
        schema = json.load(fh)

    topics = bag_info.get('topics', []) if isinstance(bag_info, dict) else []
    for t in topics:
        name = t.get('name') or t.get('topic')
        msg_type = t.get('type') or t.get('message_type')
        if name:
            schema['topics'][name] = msg_type or 'unknown'

    with open(schema_path, 'w') as fh:
        json.dump(schema, fh, indent=2)
