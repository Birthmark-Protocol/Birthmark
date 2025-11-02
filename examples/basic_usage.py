"""
Example: Basic Birthmark Protocol Usage

This example demonstrates the core workflow:
1. Capture/load an image
2. Compute its cryptographic hash
3. Record to blockchain
4. Verify authenticity
"""

from pathlib import Path
from birthmark import compute_image_hash, CameraInterface


def example_hash_computation():
    """Example 1: Computing hash of existing image file."""
    print("=== Example 1: Hash Computation ===")
    
    # Load an image file (in production, this would be raw sensor data)
    image_path = Path("example_image.jpg")
    
    if not image_path.exists():
        print(f"⚠️  {image_path} not found - create a test image first")
        return
    
    # Read image data
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    # Compute hash
    image_hash, timestamp = compute_image_hash(image_data)
    
    print(f"✓ Image Hash: {image_hash}")
    print(f"✓ Timestamp: {timestamp}")
    print()


def example_authenticated_capture():
    """Example 2: Authenticated image capture (simulation)."""
    print("=== Example 2: Authenticated Capture ===")
    
    # Initialize camera interface
    camera = CameraInterface(
        camera_id="example_camera_001",
        network="testnet",
        auto_record=False  # Set False since blockchain not implemented yet
    )
    
    print(f"✓ Camera initialized: {camera.camera_id}")
    print(f"✓ Network: {camera.network}")
    print()
    
    # Note: Actual capture not implemented yet
    print("⚠️  Actual camera capture not yet implemented")
    print("    This is a placeholder showing the intended workflow")
    print()


def example_verification():
    """Example 3: Verifying image authenticity."""
    print("=== Example 3: Image Verification ===")
    
    # In production:
    # 1. Load image
    # 2. Compute current hash
    # 3. Look up original hash on blockchain
    # 4. Compare
    
    print("⚠️  Verification not yet implemented")
    print("    Will check blockchain for hash match")
    print()


if __name__ == "__main__":
    print("Birthmark Protocol - Example Usage")
    print("=" * 50)
    print()
    
    example_hash_computation()
    example_authenticated_capture()
    example_verification()
    
    print("=" * 50)
    print("✓ Examples complete!")
    print()
    print("Next steps:")
    print("  1. Implement blockchain integration (blockchain.py)")
    print("  2. Implement camera capture (camera.py)")
    print("  3. Build verification client")
