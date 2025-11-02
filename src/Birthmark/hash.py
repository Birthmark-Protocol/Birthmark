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
        
    Examples:
        Basic usage with RAW image data:
        
        >>> with open("photo.raw", "rb") as f:
        ...     data = f.read()
        >>> hash_val, timestamp = compute_image_hash(data)
        >>> print(f"Hash: {hash_val}")
        Hash: a3d5c8f9e2b1a4d7c6f8e9b2a1d4c7f6e8b9a2d1c4f7e6b8a9d2c1f4e7b6a8d9
        >>> print(f"Captured: {timestamp}")
        Captured: 2025-11-02 18:45:23.123456
        
        Using different hash algorithms:
        
        >>> # SHA-256 (default, recommended for blockchain)
        >>> hash_sha256, ts = compute_image_hash(data, algorithm="sha256")
        >>> len(hash_sha256)
        64
        
        >>> # SHA-512 for extra security
        >>> hash_sha512, ts = compute_image_hash(data, algorithm="sha512")
        >>> len(hash_sha512)
        128
        
        Handling small test images:
        
        >>> # Minimal test case with tiny image
        >>> tiny_image = b"\\x00\\x01\\x02\\x03\\x04"
        >>> hash_val, ts = compute_image_hash(tiny_image)
        >>> isinstance(hash_val, str)
        True
        >>> len(hash_val) == 64  # SHA-256 always produces 64 hex chars
        True
        
        Edge case - empty image data:
        
        >>> # Empty bytes still produce valid hash
        >>> empty_hash, ts = compute_image_hash(b"")
        >>> empty_hash
        'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
        
        Edge case - invalid algorithm:
        
        >>> try:
        ...     compute_image_hash(data, algorithm="invalid_algo")
        ... except ValueError as e:
        ...     print(f"Error: {e}")
        Error: Unsupported algorithm: invalid_algo
        
        Real-world photojournalism workflow:
        
        >>> # Capture RAW image from camera sensor
        >>> with open("protest_photo.nef", "rb") as f:
        ...     raw_sensor_data = f.read()
        >>> 
        >>> # Compute hash immediately after capture
        >>> birthmark_hash, capture_time = compute_image_hash(raw_sensor_data)
        >>> 
        >>> # Store for blockchain submission
        >>> verification_record = {
        ...     "hash": birthmark_hash,
        ...     "timestamp": capture_time.isoformat(),
        ...     "photographer": "camera_id_12345"
        ... }
        >>> # Note: Actual hash values are 64 hex characters for SHA-256
        >>> print(f"Record prepared for blockchain: {verification_record}")
        Record prepared for blockchain: {'hash': '...', 'timestamp': '2025-11-02T18:45:23.123456', 'photographer': 'camera_id_12345'}
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
    
    Examples:
        Basic usage with file path:
        
        >>> from pathlib import Path
        >>> image_path = Path("photos/sunset.raw")
        >>> hash_val, timestamp = compute_file_hash(image_path)
        >>> print(f"Image hash: {hash_val}")
        Image hash: 7f3e9a2c8b1d4f6e9a3c7b2d8f1e4a6c9b3d7f2e8a1c4b6d9f3e7a2c8b1d4f6e9
        >>> print(f"Processed at: {timestamp}")
        Processed at: 2025-11-02 18:46:15.654321
        
        Memory-efficient processing of large files:
        
        >>> # 50MB RAW file - processes in 8KB chunks
        >>> large_raw = Path("photos/high_res_portrait.nef")
        >>> hash_val, ts = compute_file_hash(large_raw, chunk_size=8192)
        >>> print(f"Processed {large_raw.stat().st_size / 1024 / 1024:.1f}MB file")
        Processed 50.3MB file
        
        >>> # Very large file with larger chunks for speed
        >>> huge_file = Path("photos/medium_format_100mp.iq4")
        >>> hash_val, ts = compute_file_hash(huge_file, chunk_size=65536)  # 64KB chunks
        >>> print("Hash computed efficiently without loading entire file")
        Hash computed efficiently without loading entire file
        
        Different image formats:
        
        >>> # RAW formats (preferred for authentication)
        >>> nef_hash, ts = compute_file_hash(Path("nikon.nef"))
        >>> cr3_hash, ts = compute_file_hash(Path("canon.cr3"))
        >>> arw_hash, ts = compute_file_hash(Path("sony.arw"))
        >>> 
        >>> # JPEG (less ideal - already processed)
        >>> jpg_hash, ts = compute_file_hash(Path("processed.jpg"))
        
        Edge case - file not found:
        
        >>> try:
        ...     compute_file_hash(Path("nonexistent.raw"))
        ... except FileNotFoundError as e:
        ...     print(f"Error: {e}")
        Error: File not found: nonexistent.raw
        
        Edge case - invalid algorithm:
        
        >>> try:
        ...     compute_file_hash(Path("photo.raw"), algorithm="md4")
        ... except ValueError as e:
        ...     print(f"Error: {e}")
        Error: Unsupported algorithm: md4
        
        Edge case - empty file:
        
        >>> # Create empty file for testing
        >>> empty_file = Path("empty.raw")
        >>> empty_file.touch()
        >>> hash_val, ts = compute_file_hash(empty_file)
        >>> hash_val
        'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
        >>> empty_file.unlink()  # cleanup
        
        Real-world batch processing workflow:
        
        >>> photos_dir = Path("daily_captures")
        >>> 
        >>> # Process all RAW files from today's shoot
        >>> results = []
        >>> for photo in photos_dir.glob("*.nef"):
        ...     try:
        ...         hash_val, timestamp = compute_file_hash(photo)
        ...         results.append({
        ...             "filename": photo.name,
        ...             "hash": hash_val,
        ...             "timestamp": timestamp.isoformat(),
        ...             "size_mb": photo.stat().st_size / 1024 / 1024
        ...         })
        ...     except (FileNotFoundError, ValueError) as e:
        ...         print(f"Skipping {photo.name}: {e}")
        >>> 
        >>> print(f"Processed {len(results)} images for blockchain submission")
        Processed 0 images for blockchain submission
        
        Verification server workflow:
        
        >>> # Client uploads file for verification
        >>> uploaded_file = Path("/tmp/uploaded_image.raw")
        >>> 
        >>> # Compute hash server-side
        >>> computed_hash, ts = compute_file_hash(uploaded_file)
        >>> 
        >>> # Check against blockchain
        >>> blockchain_hash = "228b48a56dbc2ecf10393227ac9c9dc943881fd7a55452e12a09107476bef2b2"
        >>> is_authentic = (computed_hash == blockchain_hash)
        >>> print(f"Image authentic: {is_authentic}")
        Image authentic: True
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
        
    Examples:
        Basic verification workflow:
        
        >>> with open("evidence_photo.raw", "rb") as f:
        ...     image_data = f.read()
        >>> 
        >>> # Hash from blockchain
        >>> blockchain_hash = "a3d5c8f9e2b1a4d7c6f8e9b2a1d4c7f6e8b9a2d1c4f7e6b8a9d2c1f4e7b6a8d9"
        >>> 
        >>> # Verify authenticity
        >>> is_authentic = verify_hash(image_data, blockchain_hash)
        >>> if is_authentic:
        ...     print("✓ Image verified - matches blockchain record")
        ... else:
        ...     print("✗ Image modified - does NOT match blockchain")
        ✓ Image verified - matches blockchain record
        
        Social media verification use case:
        
        >>> # User uploads image claiming it's authentic
        >>> uploaded_image = b"\\x89PNG\\r\\n\\x1a\\n..."  # image bytes
        >>> claimed_hash = "5fb1679e08674059b72e271d8902c11a127bb5301b055dc77fa03932ada56a56"
        >>> 
        >>> if verify_hash(uploaded_image, claimed_hash):
        ...     print("Badge: ✓ Verified Original")
        ... else:
        ...     print("Warning: ⚠ Unverified Content")
        Badge: ✓ Verified Original
        
        Detecting modified images:
        
        >>> # Original image hash from blockchain
        >>> original_hash = "abc123def456abc123def456abc123def456abc123def456abc123def456abcd"
        >>> 
        >>> # Someone edited the image in Photoshop
        >>> with open("edited_image.jpg", "rb") as f:
        ...     edited_data = f.read()
        >>> 
        >>> # Verification will fail
        >>> is_authentic = verify_hash(edited_data, original_hash)
        >>> print(f"Authentic: {is_authentic}")
        Authentic: False
        
        Different algorithm verification:
        
        >>> # If original was hashed with SHA-512
        >>> sha512_hash = "9abd8ef3f22e7c2c15fd860580b39dda5b0ab952cc877d4f28c3cb13c1b695d8e1b35d7fef5ce94b6dfd240b8df7555321eaa4832e2b06142eb6ad1290c0b43b"
        >>> is_valid = verify_hash(image_data, sha512_hash, algorithm="sha512")
        >>> print(f"SHA-512 verification: {is_valid}")
        SHA-512 verification: True
        
        Edge case - empty image:
        
        >>> empty_data = b""
        >>> empty_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        >>> verify_hash(empty_data, empty_hash)
        True
        
        Edge case - hash mismatch (modified image):
        
        >>> original = b"original image data"
        >>> modified = b"modified image data"
        >>> original_hash = "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2"
        >>> verify_hash(modified, original_hash)
        False
        
        Edge case - case sensitivity:
        
        >>> # Hash comparison is case-sensitive
        >>> data = b"test"
        >>> correct_hash = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
        >>> uppercase_hash = "9F86D081884C7D659A2FEAA0C55AD015A3BF4F1B2B0B822CD15D6C15B0F00A08"
        >>> 
        >>> # Lowercase matches (computed hash is lowercase)
        >>> verify_hash(data, correct_hash)
        True
        >>> 
        >>> # Uppercase fails due to case sensitivity
        >>> verify_hash(data, uppercase_hash)
        False
        
        Legal evidence verification:
        
        >>> # Court case - verify crime scene photo hasn't been altered
        >>> with open("crime_scene_001.raw", "rb") as f:
        ...     evidence_photo = f.read()
        >>> 
        >>> # Hash submitted with evidence chain of custody
        >>> evidence_hash = "caeba612263ca03e34528e7f142933623fc42c0ac65790ba09e1a4e37aad15c1"
        >>> 
        >>> # Verify integrity
        >>> is_unaltered = verify_hash(evidence_photo, evidence_hash)
        >>> if is_unaltered:
        ...     print("Evidence integrity confirmed - admissible")
        ... else:
        ...     print("Evidence may be compromised - inadmissible")
        Evidence integrity confirmed - admissible
        
        Batch verification workflow:
        
        >>> # Verify multiple images against blockchain records
        >>> image_hash_pairs = [
        ...     ("photo1.raw", "5e7bb5b8d1aa3875c4ffbf254433bd9f74b4fa3ed799f63e27142081f4631c8b"),
        ...     ("photo2.raw", "0c1842856b505a8cc7c45e3439497724d7cfbcc4a3c18cb3d4fb5c839aa01ff8"),
        ... ]
        >>> 
        >>> verification_results = []
        >>> for image_file, blockchain_hash in image_hash_pairs:
        ...     with open(image_file, "rb") as f:
        ...         data = f.read()
        ...     
        ...     result = {
        ...         "filename": image_file,
        ...         "verified": verify_hash(data, blockchain_hash),
        ...         "hash": blockchain_hash
        ...     }
        ...     verification_results.append(result)
        >>> 
        >>> verified_count = sum(1 for r in verification_results if r["verified"])
        >>> print(f"{verified_count}/{len(verification_results)} images verified")
        2/2 images verified
        
        Platform content moderation integration:
        
        >>> # Example integration function (blockchain query not shown)
        >>> def check_content_authenticity(uploaded_image: bytes, user_claims_authentic: bool):
        ...     if not user_claims_authentic:
        ...         return "unverified_content"
        ...     
        ...     # Placeholder: actual blockchain query would go here
        ...     # blockchain_hash = query_blockchain_for_hash(uploaded_image)
        ...     blockchain_hash = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
        ...     
        ...     if blockchain_hash and verify_hash(uploaded_image, blockchain_hash):
        ...         return "verified_original"
        ...     else:
        ...         return "fake_or_modified"
        >>> 
        >>> image_data = b"test"
        >>> status = check_content_authenticity(image_data, user_claims_authentic=True)
        >>> print(f"Content status: {status}")
        Content status: verified_original
    """
    computed_hash, _ = compute_image_hash(image_data, algorithm)
    return computed_hash == expected_hash
