"""
Storage layer abstractions.
File systems, databases, and media asset management.
"""

from .assets import save_bytes, save_file, read_file, get_asset_path, hash_bytes

__all__ = ["save_bytes", "save_file", "read_file", "get_asset_path", "hash_bytes"]