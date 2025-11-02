"""
Cryptographic hashing functionality for image data.

This module handles computing SHA-256 hashes of raw image data
at the moment of capture, before any processing or compression.
"""

import hashlib
from datetime import datetime
from typing import Tuple, Optional
from pathlib import Path


def compute_image_hash(
    image_data: bytes,
    algorithm: str = "sha256"
) -> Tuple[str, datetime]:
    """
    Compute cryptographic hash of image data.
    
    This is the core function that creates the unique "birthmark"
    for an image. The hash is computed on raw sensor data before
    any in-camera processing occurs.
    
    Args:
        image_data: Raw image bytes (preferably RAW sensor data)
        algorithm: Hash algorithm to use (default: sha256)
        
    Returns:
        Tuple of (hash_string, timestamp)
        
    Raises:
        ValueError: If algorithm is not supported
        
    Example:
        >>> with open("image.raw", "rb") as f:
        ...     data = f.read()
        >>> hash_val, timestamp = compute_image_hash(data)
        >>> print(f"Hash: {hash_val}")
        >>> print(f"Captured: {timestamp}")
    """
    if algorithm not in hashlib.algorithms_available:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    hasher = hashlib.new(algorithm)
    hasher.update(image_data)
    
    return hasher.hexdigest(), datetime.utcnow()


def compute_file_hash(
    file_path: Path,
    algorithm: str = "sha256",
    chunk_size: int = 8192
) -> Tuple[str, datetime]:
    """
    Compute hash of image file in chunks (memory efficient).
    
    For large RAW files, this avoids loading entire file into memory.
    
    Args:
        file_path: Path to image file
        algorithm: Hash algorithm to use
        chunk_size: Bytes to read at a time
        
    Returns:
        Tuple of (hash_string, timestamp)
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If algorithm not supported
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if algorithm not in hashlib.algorithms_available:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    hasher = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    
    return hasher.hexdigest(), datetime.utcnow()


def verify_hash(
    image_data: bytes,
    expected_hash: str,
    algorithm: str = "sha256"
) -> bool:
    """
    Verify that image data matches expected hash.
    
    Args:
        image_data: Image bytes to verify
        expected_hash: Hash to compare against
        algorithm: Algorithm used for original hash
        
    Returns:
        True if hashes match, False otherwise
        
    Example:
        >>> is_authentic = verify_hash(image_data, blockchain_hash)
        >>> if is_authentic:
        ...     print("Image is authentic!")
    """
    computed_hash, _ = compute_image_hash(image_data, algorithm)
    return computed_hash == expected_hash
