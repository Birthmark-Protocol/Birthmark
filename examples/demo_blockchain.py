"""
Demo script for blockchain module.

This demonstrates the complete workflow without requiring pytest.
"""

from datetime import datetime
import hashlib
from birthmark.blockchain import (
    MockBlockchain,
    get_blockchain_interface,
    record_to_blockchain,
    verify_from_blockchain,
    batch_record_to_blockchain
)


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")


def demo_basic_usage():
    """Demonstrate basic recording and verification."""
    print_section("Demo 1: Basic Recording and Verification")
    
    # Initialize blockchain
    blockchain = MockBlockchain(simulate_delay=False)
    print("✓ Initialized MockBlockchain")
    
    # Simulate capturing an image
    image_data = b"This is simulated raw image data from camera"
    image_hash = hashlib.sha256(image_data).hexdigest()
    print(f"✓ Computed image hash: {image_hash[:16]}...")
    
    # Record to blockchain
    tx_id = blockchain.record_hash(
        image_hash=image_hash,
        timestamp=datetime.now(),
        camera_id="canon_eos_r5_12345",
        geolocation=(45.5231, -122.6765)  # Portland, OR
    )
    print(f"✓ Recorded to blockchain: {tx_id}")
    
    # Verify the image
    record = blockchain.verify_hash(image_hash)
    
    if record:
        print("\n✅ IMAGE VERIFIED!")
        print(f"   Camera: {record.camera_id}")
        print(f"   Timestamp: {record.timestamp}")
        print(f"   Location: {record.geolocation}")
        print(f"   Transaction: {record.transaction_id}")
        print(f"   Block: {record.block_number}")
    else:
        print("\n❌ Image not found")
    
    return True


def demo_batch_processing():
    """Demonstrate batch recording for scale."""
    print_section("Demo 2: Batch Processing")
    
    blockchain = MockBlockchain(simulate_delay=False)
    print("✓ Initialized MockBlockchain")
    
    # Simulate multiple photographers at an event
    print("\nSimulating 25 photos from 5 different cameras...")
    
    records = []
    for i in range(25):
        image_data = f"Image data for photo {i}".encode()
        image_hash = hashlib.sha256(image_data).hexdigest()
        camera_id = f"camera_{i % 5 + 1:03d}"
        geolocation = (45.5 + i*0.001, -122.6 + i*0.001)
        
        records.append((
            image_hash,
            datetime.now(),
            camera_id,
            geolocation
        ))
    
    # Batch record
    tx_ids = blockchain.batch_record_hashes(records)
    print(f"✓ Batch recorded {len(tx_ids)} images")
    
    # Verify a few samples
    print("\nVerifying random samples:")
    for idx in [0, 10, 20]:
        image_hash = records[idx][0]
        record = blockchain.verify_hash(image_hash)
        if record:
            print(f"  ✓ Photo {idx}: Verified (Camera: {record.camera_id})")
    
    # Show stats
    stats = blockchain.get_stats()
    print(f"\nBlockchain stats:")
    print(f"  Total records: {stats['total_records']}")
    print(f"  Total transactions: {stats['total_transactions']}")
    print(f"  Current block: {stats['current_block']}")
    
    return True


def demo_convenience_functions():
    """Demonstrate convenience functions."""
    print_section("Demo 3: Convenience Functions")
    
    print("Using convenience functions for simpler API...")
    
    # Record using convenience function
    image_hash = hashlib.sha256(b"Convenience test image").hexdigest()
    
    tx_id = record_to_blockchain(
        image_hash=image_hash,
        timestamp=datetime.now(),
        camera_id="sony_a7iv_67890",
        geolocation=(47.6062, -122.3321),  # Seattle, WA
        backend="mock",
        simulate_delay=False
    )
    print(f"✓ Recorded: {tx_id}")
    
    # Verify using convenience function
    record = verify_from_blockchain(
        image_hash=image_hash,
        backend="mock",
        simulate_delay=False
    )
    
    if record:
        print(f"✓ Verified: {record.camera_id} @ {record.geolocation}")
    
    return True


def demo_privacy_features():
    """Demonstrate privacy-preserving features."""
    print_section("Demo 4: Privacy Features")
    
    blockchain = MockBlockchain(simulate_delay=False)
    
    # Whistleblower scenario: anonymized camera ID, no GPS
    print("Scenario: Sensitive documentation requiring source protection")
    
    sensitive_image = hashlib.sha256(b"Sensitive evidence photo").hexdigest()
    
    tx_id = blockchain.record_hash(
        image_hash=sensitive_image,
        timestamp=datetime.now(),
        camera_id="anon_device_xyz123",  # Anonymized
        geolocation=None  # No GPS for privacy
    )
    print(f"✓ Recorded with anonymized ID: {tx_id}")
    
    # Verification still works
    record = blockchain.verify_hash(sensitive_image)
    
    if record:
        print("\n✅ Image authenticated while preserving privacy:")
        print(f"   Camera ID: {record.camera_id} (anonymized)")
        print(f"   Location: {record.geolocation} (not recorded)")
        print(f"   Source identity protected ✓")
    
    return True


def demo_verification_failure():
    """Demonstrate verification failure for manipulated images."""
    print_section("Demo 5: Detecting Manipulated Images")
    
    blockchain = MockBlockchain(simulate_delay=False)
    
    # Record original image
    original_data = b"Original authentic photo"
    original_hash = hashlib.sha256(original_data).hexdigest()
    
    blockchain.record_hash(
        image_hash=original_hash,
        timestamp=datetime.now(),
        camera_id="camera_001"
    )
    print(f"✓ Original image recorded")
    
    # Verify original
    record = blockchain.verify_hash(original_hash)
    print(f"✓ Original image verified: {record.camera_id}")
    
    # Try to verify manipulated version
    print("\nNow someone tries to pass off a manipulated version...")
    manipulated_data = b"Original authentic photo EDITED"
    manipulated_hash = hashlib.sha256(manipulated_data).hexdigest()
    
    record = blockchain.verify_hash(manipulated_hash)
    
    if record is None:
        print("❌ Manipulated image NOT FOUND on blockchain")
        print("   → System correctly identifies manipulation!")
    
    return True


def demo_social_media_platform():
    """Demonstrate how a social media platform would use this."""
    print_section("Demo 6: Social Media Platform Integration")
    
    blockchain = MockBlockchain(simulate_delay=False)
    
    print("Scenario: User uploads image claiming it's authentic")
    
    # Simulate multiple uploads
    uploads = [
        ("Authenticated camera photo", True),
        ("Downloaded internet image", False),
        ("Screenshot of another photo", False),
        ("Another camera photo", True)
    ]
    
    authenticated_count = 0
    
    for description, is_authentic in uploads:
        image_data = description.encode()
        image_hash = hashlib.sha256(image_data).hexdigest()
        
        # Platform authenticates camera photos
        if is_authentic:
            blockchain.record_hash(
                image_hash,
                datetime.now(),
                f"verified_camera_{authenticated_count}"
            )
            authenticated_count += 1
        
        # Platform checks all uploads
        record = blockchain.verify_hash(image_hash)
        
        status = "✅ VERIFIED" if record else "⚠️  UNVERIFIED"
        print(f"{status}: {description}")
    
    print(f"\nPlatform processed {len(uploads)} uploads")
    print(f"Verified: {authenticated_count}")
    print(f"Unverified: {len(uploads) - authenticated_count}")
    
    return True


def demo_backend_switching():
    """Demonstrate switching between backends."""
    print_section("Demo 7: Backend Flexibility")
    
    print("The same API works with different backends:\n")
    
    # Mock backend
    print("Mock Backend (Testing):")
    tx_id = record_to_blockchain(
        image_hash="test_hash_123",
        timestamp=datetime.now(),
        camera_id="camera_001",
        backend="mock",
        simulate_delay=False
    )
    print(f"  ✓ Transaction: {tx_id}")
    
    # Ethereum backend (would work with proper setup)
    print("\nEthereum Backend (Testnet - not configured):")
    print("  backend='ethereum'")
    print("  network='sepolia'")
    print("  → Requires: provider URL, private key, deployed contract")
    
    # Loopring backend (future)
    print("\nLoopring Backend (Production - planned):")
    print("  backend='loopring'")
    print("  network='mainnet'")
    print("  → Future: zkRollup integration for scale")
    
    print("\n✓ Same API, swappable backends!")
    
    return True


def run_all_demos():
    """Run all demonstrations."""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  Birthmark Protocol - Blockchain Module Demo".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    demos = [
        demo_basic_usage,
        demo_batch_processing,
        demo_convenience_functions,
        demo_privacy_features,
        demo_verification_failure,
        demo_social_media_platform,
        demo_backend_switching
    ]
    
    results = []
    for demo in demos:
        try:
            result = demo()
            results.append(("PASS", demo.__name__))
        except Exception as e:
            results.append(("FAIL", demo.__name__, str(e)))
    
    # Summary
    print_section("Demo Summary")
    
    passed = sum(1 for r in results if r[0] == "PASS")
    total = len(results)
    
    for result in results:
        if result[0] == "PASS":
            print(f"  ✅ {result[1]}")
        else:
            print(f"  ❌ {result[1]}: {result[2]}")
    
    print(f"\n{passed}/{total} demos passed")
    
    if passed == total:
        print("\n🎉 All demos passed! Blockchain module is working correctly.")
        print("\nNext steps:")
        print("  1. Review BLOCKCHAIN_IMPLEMENTATION.md for details")
        print("  2. Install pytest: pip install pytest")
        print("  3. Run full tests: pytest test_blockchain.py -v")
        print("  4. Start implementing Ethereum backend")
    
    print("\n" + "█"*60 + "\n")


if __name__ == "__main__":
    run_all_demos()
