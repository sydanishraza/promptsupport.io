"""
KE-PR3: Asset storage abstraction with content-hash deduplication
Handles file I/O for media assets with consistent hashing and path management.
"""

import os
import hashlib
import shutil
from typing import Tuple, Optional, Union
from pathlib import Path


def hash_bytes(data: bytes) -> str:
    """Generate consistent SHA256 hash for content deduplication"""
    return hashlib.sha256(data).hexdigest()[:16]


def _ensure_upload_dir(upload_dir: str) -> None:
    """Ensure upload directory exists"""
    os.makedirs(upload_dir, exist_ok=True)


def get_asset_path(filename_or_hash: str, upload_dir: str = "static/uploads") -> str:
    """Get full path for an asset file"""
    return os.path.join(upload_dir, filename_or_hash)


def save_bytes(data: bytes, filename: str, upload_dir: str = "static/uploads") -> Tuple[str, str]:
    """
    Save bytes to disk with content-hash deduplication
    
    Args:
        data: Raw bytes to save
        filename: Original filename (used for extension)
        upload_dir: Target directory
        
    Returns:
        Tuple of (hash, relative_path)
    """
    try:
        # Generate content hash for deduplication
        content_hash = hash_bytes(data)
        
        # Preserve file extension
        ext = os.path.splitext(filename)[1].lower()
        hashed_filename = f"{content_hash}{ext}"
        
        # Create full path
        _ensure_upload_dir(upload_dir)
        full_path = os.path.join(upload_dir, hashed_filename)
        
        # Check if file already exists (deduplication)
        if os.path.exists(full_path):
            print(f"🔄 KE-PR3: File already exists (deduplicated): {hashed_filename}")
            return content_hash, hashed_filename
        
        # Write new file
        with open(full_path, "wb") as f:
            f.write(data)
        
        print(f"💾 KE-PR3: Saved asset {hashed_filename} ({len(data)} bytes) -> {upload_dir}")
        return content_hash, hashed_filename
        
    except Exception as e:
        print(f"❌ KE-PR3: Error saving bytes: {e}")
        raise


def save_file(temp_path: str, upload_dir: str = "static/uploads") -> Tuple[str, str]:
    """
    Move/copy a temporary file to assets directory with content hashing
    
    Args:
        temp_path: Path to temporary file
        upload_dir: Target directory
        
    Returns:
        Tuple of (hash, relative_path)
    """
    try:
        # Read file data for hashing
        with open(temp_path, "rb") as f:
            data = f.read()
        
        # Use save_bytes to handle deduplication
        original_filename = os.path.basename(temp_path)
        content_hash, relative_path = save_bytes(data, original_filename, upload_dir)
        
        # Clean up temporary file
        try:
            os.remove(temp_path)
            print(f"🗑️ KE-PR3: Cleaned up temporary file: {temp_path}")
        except FileNotFoundError:
            print(f"⚠️ KE-PR3: Temporary file already removed: {temp_path}")
        
        return content_hash, relative_path
        
    except Exception as e:
        print(f"❌ KE-PR3: Error saving file {temp_path}: {e}")
        raise


def read_file(asset_path: str) -> bytes:
    """
    Read asset file as bytes
    
    Args:
        asset_path: Full or relative path to asset
        
    Returns:
        File content as bytes
    """
    try:
        with open(asset_path, "rb") as f:
            data = f.read()
        
        print(f"📖 KE-PR3: Read asset {asset_path} ({len(data)} bytes)")
        return data
        
    except Exception as e:
        print(f"❌ KE-PR3: Error reading file {asset_path}: {e}")
        raise


def copy_asset(source_path: str, target_dir: str, new_filename: str = None) -> Tuple[str, str]:
    """
    Copy an existing asset to target directory with optional renaming
    
    Args:
        source_path: Source file path
        target_dir: Target directory
        new_filename: Optional new filename (uses original if not provided)
        
    Returns:
        Tuple of (hash, relative_path)
    """
    try:
        # Read source file
        data = read_file(source_path)
        
        # Use original filename if new one not provided
        filename = new_filename or os.path.basename(source_path)
        
        # Save with deduplication
        return save_bytes(data, filename, target_dir)
        
    except Exception as e:
        print(f"❌ KE-PR3: Error copying asset {source_path}: {e}")
        raise


def list_assets(upload_dir: str = "static/uploads", extension_filter: str = None) -> list:
    """
    List all assets in upload directory
    
    Args:
        upload_dir: Directory to scan
        extension_filter: Optional extension filter (e.g., '.png')
        
    Returns:
        List of asset filenames
    """
    try:
        if not os.path.exists(upload_dir):
            return []
        
        assets = []
        for filename in os.listdir(upload_dir):
            if extension_filter and not filename.lower().endswith(extension_filter.lower()):
                continue
            assets.append(filename)
        
        print(f"📋 KE-PR3: Listed {len(assets)} assets in {upload_dir}")
        return assets
        
    except Exception as e:
        print(f"❌ KE-PR3: Error listing assets: {e}")
        return []


def get_file_info(asset_path: str) -> dict:
    """
    Get file information including size, hash, and metadata
    
    Args:
        asset_path: Path to asset file
        
    Returns:
        Dictionary with file information
    """
    try:
        if not os.path.exists(asset_path):
            return {"exists": False}
        
        stat = os.stat(asset_path)
        data = read_file(asset_path)
        
        return {
            "exists": True,
            "size": stat.st_size,
            "hash": hash_bytes(data),
            "filename": os.path.basename(asset_path),
            "extension": os.path.splitext(asset_path)[1],
            "modified": stat.st_mtime
        }
        
    except Exception as e:
        print(f"❌ KE-PR3: Error getting file info for {asset_path}: {e}")
        return {"exists": False, "error": str(e)}