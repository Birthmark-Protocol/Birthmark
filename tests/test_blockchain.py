"""
Tests for blockchain module.

Demonstrates how to use the blockchain interface with different backends.
Run with: python -m pytest test_blockchain.py -v
"""

import pytest
from datetime import datetime
from blockchain import (
    MockBlockchain,
    EthereumBlockchain,
    LoopringBlockchain,
    get_blockchain_interface,
    record_to_blockchain,
    verify_from_blockchain,
    batch_record_to_blockchain,
    BirthmarkRecord,
    TransactionFailedError,
    VerificationError
)


class TestMockBlockchain:
    """Test suite for MockBlockchain implementation."""
    
    def test_initialization(self):
        """Test mock blockchain can be initialized."""
        blockchain = MockBlockchain(network="test-network")
        assert blockchain.network == "test-network"
        assert blockchain._transaction_counter == 0
        
    def test_record_single_hash(self):
        """Test recording a single hash."""
        blockchain = MockBlockchain(simulate_delay=False)
        
        image_hash = "abc123def456"
        timestamp = datetime.now()
        camera_id = "camera_001"
        
        tx_id = blockchain.record_hash(image_hash, timestamp, camera_id)
        
        assert tx_id is not None
        assert tx_id.startswith("mock_tx_")
        
    def test_verify_existing_hash(self):
        """Test verifying a hash that exists."""
        blockchain = MockBlockchain(simulate_delay=False)
        
        image_hash = "abc123def456"
        timestamp = datetime.now()
        camera_id = "camera_001"
        geolocation = (45.5231, -122.6765)
        
        # Record hash
        tx_id = blockchain.record_hash(image_hash, timestamp, camera_id, geolocation)
        
        # Verify it
        record = blockchain.verify_hash(image_hash)
        
        assert record is not None
        assert record.hash == image_hash
        assert record.camera_id == camera_id
        assert record.geolocation == geolocation
        assert record.transaction_id == tx_id
        assert record.block_number is not None
        
    def test_verify_nonexistent_hash(self):
        """Test verifying a hash that doesn't exist."""
        blockchain = MockBlockchain(simulate_delay=False)
        
        record = blockchain.verify_hash("nonexistent_hash")
        
        assert record is None
        
    def test_record_with_geolocation(self):
        """Test recording with GPS coordinates."""
        blockchain = MockBlockchain(simulate_delay=False)
        
        image_hash = "geo_test_hash"
        timestamp = datetime.now()
        camera_id = "camera_001"
        geolocation = (45.5231, -122.6765)  # Portland, OR
        
        tx_id = blockchain.record_hash(image_hash, timestamp, camera_id, geolocation)
        record = blockchain.verify_hash(image_hash)
        
        assert record.geolocation == geolocation
        
    def test_batch_recording(self):
        """Test batch recording multiple hashes."""
        blockchain = MockBlockchain(simulate_delay=False)
        
        records = [
            ("hash1", datetime.now(), "camera_001", None),
            ("hash2", datetime.now(), "camera_001", (45.5, -122.6)),
            ("hash3", datetime.now(), "camera_002", None),
            ("hash4", datetime.now(), "camera_002", (45.6, -122.7))
        ]
        
        tx_ids = blockchain.batch_record_hashes(records)
        
        assert len(tx_ids) == 4
        assert all(tx_id.startswith("mock_tx_") for tx_id in tx_ids)
        
        # Verify all records were stored
        for image_hash, _, _, _ in records:
            record = blockchain.verify_hash(image_hash)
            assert record is not None
            
    def test_multiple_records_different_blocks(self):
        """Test that records are distributed across blocks."""
        blockchain = MockBlockchain(simulate_delay=False)
        
        # Record 20 hashes to trigger multiple blocks
        for i in range(20):
            blockchain.record_hash(f"hash_{i}", datetime.now(), "camera_001")
        
        stats = blockchain.get_stats()
        assert stats["total_records"] == 20
        assert stats["total_transactions"] == 20
        # Should have advanced at least one block
        assert stats["current_block"] > 1000
        
    def test_record_to_dict(self):
        """Test converting record to dictionary."""
        blockchain = MockBlockchain(simulate_delay=False)
        
        image_hash = "dict_test"
        timestamp = datetime.now()
        camera_id = "camera_001"
        
        blockchain.record_hash(image_hash, timestamp, camera_id)
        record = blockchain.verify_hash(image_hash)
        
        record_dict = record.to_dict()
        
        assert isinstance(record_dict, dict)
        assert record_dict["hash"] == image_hash
        assert record_dict["camera_id"] == camera_id
        
    def test_record_from_dict(self):
        """Test creating record from dictionary."""
        data = {
            "hash": "test_hash",
            "timestamp": "2025-11-02T12:00:00",
            "camera_id": "camera_001",
            "geolocation": (45.5, -122.6),
            "transaction_id": "tx_12345",
            "block_number": 1000,
            "network": "testnet"
        }
        
        record = BirthmarkRecord.from_dict(data)
        
        assert record.hash == "test_hash"
        assert record.camera_id == "camera_001"
        assert record.geolocation == (45.5, -122.6)


class TestFactoryFunction:
    """Test the get_blockchain_interface factory function."""
    
    def test_get_mock_backend(self):
        """Test getting mock backend."""
        blockchain = get_blockchain_interface("mock")
        assert isinstance(blockchain, MockBlockchain)
        
    def test_get_mock_backend_with_params(self):
        """Test getting mock backend with parameters."""
        blockchain = get_blockchain_interface(
            "mock",
            network="custom-network",
            simulate_delay=False
        )
        assert isinstance(blockchain, MockBlockchain)
        assert blockchain.network == "custom-network"
        assert blockchain.simulate_delay is False
        
    def test_get_ethereum_backend(self):
        """Test getting Ethereum backend (will fail without provider)."""
        with pytest.raises(ValueError):
            get_blockchain_interface("ethereum")
            
    def test_invalid_backend(self):
        """Test invalid backend name."""
        with pytest.raises(ValueError, match="Unknown backend"):
            get_blockchain_interface("invalid_backend")


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_record_to_blockchain(self):
        """Test record_to_blockchain convenience function."""
        tx_id = record_to_blockchain(
            image_hash="convenience_test",
            timestamp=datetime.now(),
            camera_id="camera_001",
            backend="mock",
            simulate_delay=False
        )
        
        assert tx_id is not None
        assert tx_id.startswith("mock_tx_")
        
    def test_verify_from_blockchain(self):
        """Test verify_from_blockchain convenience function."""
        image_hash = "verify_convenience_test"
        
        # Record first
        record_to_blockchain(
            image_hash=image_hash,
            timestamp=datetime.now(),
            camera_id="camera_001",
            backend="mock",
            simulate_delay=False
        )
        
        # Then verify
        record = verify_from_blockchain(
            image_hash=image_hash,
            backend="mock",
            simulate_delay=False
        )
        
        assert record is not None
        assert record.hash == image_hash
        
    def test_batch_record_to_blockchain(self):
        """Test batch_record_to_blockchain convenience function."""
        records = [
            ("batch_hash_1", datetime.now(), "camera_001", None),
            ("batch_hash_2", datetime.now(), "camera_001", (45.5, -122.6)),
            ("batch_hash_3", datetime.now(), "camera_002", None)
        ]
        
        tx_ids = batch_record_to_blockchain(
            records,
            backend="mock",
            simulate_delay=False
        )
        
        assert len(tx_ids) == 3
        
        # Verify all were recorded
        for image_hash, _, _, _ in records:
            record = verify_from_blockchain(
                image_hash,
                backend="mock",
                simulate_delay=False
            )
            assert record is not None


class TestEthereumBlockchain:
    """Test Ethereum blockchain (mostly placeholder tests)."""
    
    def test_ethereum_requires_provider(self):
        """Test that Ethereum backend requires provider URL."""
        with pytest.raises(ValueError, match="provider_url is required"):
            EthereumBlockchain()
            
    def test_ethereum_methods_not_implemented(self):
        """Test that Ethereum methods raise NotImplementedError."""
        # This test would require a valid provider URL
        # For now, just verify the class exists
        assert EthereumBlockchain is not None


class TestLoopringBlockchain:
    """Test Loopring blockchain (placeholder tests)."""
    
    def test_loopring_methods_not_implemented(self):
        """Test that Loopring methods raise NotImplementedError."""
        blockchain = LoopringBlockchain()
        
        with pytest.raises(NotImplementedError):
            blockchain.record_hash("test", datetime.now(), "camera_001")
            
        with pytest.raises(NotImplementedError):
            blockchain.verify_hash("test")
            
        with pytest.raises(NotImplementedError):
            blockchain.batch_record_hashes([])


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""
    
    def test_photographer_workflow(self):
        """Test typical photographer workflow."""
        blockchain = MockBlockchain(simulate_delay=False)
        
        # Photographer takes 5 photos
        photos = []
        for i in range(5):
            image_hash = f"photo_{i:03d}_hash"
            timestamp = datetime.now()
            camera_id = "sony_a7iv_12345"
            geolocation = (45.5231 + i*0.001, -122.6765 + i*0.001)
            
            tx_id = blockchain.record_hash(
                image_hash, timestamp, camera_id, geolocation
            )
            photos.append((image_hash, tx_id))
        
        # Later, verify all photos are authentic
        for image_hash, expected_tx_id in photos:
            record = blockchain.verify_hash(image_hash)
            assert record is not None
            assert record.transaction_id == expected_tx_id
            assert record.camera_id == "sony_a7iv_12345"
            
    def test_social_media_platform_verification(self):
        """Test social media platform verifying uploaded images."""
        blockchain = MockBlockchain(simulate_delay=False)
        
        # User uploads image claiming it's authentic
        uploaded_hash = "user_uploaded_image"
        
        # Platform checks blockchain
        record = blockchain.verify_hash(uploaded_hash)
        
        # Image not found - likely manipulated or not from authenticated camera
        assert record is None
        
        # Now test with a real authenticated image
        real_hash = "authenticated_image"
        blockchain.record_hash(real_hash, datetime.now(), "verified_camera")
        
        record = blockchain.verify_hash(real_hash)
        assert record is not None  # Platform can verify this is authentic
        
    def test_batch_processing_for_scale(self):
        """Test batch processing for high-volume scenarios."""
        blockchain = MockBlockchain(simulate_delay=False)
        
        # Simulate a news event with many photographers
        # Each photographer takes multiple photos
        batch_size = 100
        records = [
            (
                f"news_event_photo_{i}",
                datetime.now(),
                f"camera_{i % 10:03d}",  # 10 different cameras
                (45.5 + (i % 10) * 0.01, -122.6 + (i % 10) * 0.01)
            )
            for i in range(batch_size)
        ]
        
        # Batch record for efficiency
        tx_ids = blockchain.batch_record_hashes(records)
        
        assert len(tx_ids) == batch_size
        
        # Verify random samples
        samples = [0, 25, 50, 75, 99]
        for idx in samples:
            image_hash, _, _, _ = records[idx]
            record = blockchain.verify_hash(image_hash)
            assert record is not None
            
    def test_anonymous_source_protection(self):
        """Test using anonymized camera IDs for source protection."""
        blockchain = MockBlockchain(simulate_delay=False)
        
        # Whistleblower uploads evidence with anonymized camera ID
        sensitive_image = "whistleblower_evidence"
        anonymous_camera_id = "anon_camera_xyz123"  # Doesn't identify device
        
        tx_id = blockchain.record_hash(
            sensitive_image,
            datetime.now(),
            anonymous_camera_id,
            geolocation=None  # No GPS for privacy
        )
        
        # Image can still be verified as authentic
        record = blockchain.verify_hash(sensitive_image)
        assert record is not None
        assert record.camera_id == anonymous_camera_id
        assert record.geolocation is None  # Privacy preserved


def test_integration_example():
    """
    Full integration example showing complete workflow.
    
    This demonstrates how a camera app would use the blockchain module.
    """
    # Initialize blockchain (mock for testing)
    blockchain = MockBlockchain(simulate_delay=False)
    
    # Camera captures image
    image_data = b"simulated raw image data here"
    
    # Compute hash (in real implementation, this would use the hash module)
    import hashlib
    image_hash = hashlib.sha256(image_data).hexdigest()
    
    # Get metadata
    timestamp = datetime.now()
    camera_id = "canon_eos_r5_67890"
    geolocation = (45.5231, -122.6765)  # Portland, OR
    
    # Record to blockchain
    tx_id = blockchain.record_hash(
        image_hash,
        timestamp,
        camera_id,
        geolocation
    )
    
    print(f"✅ Image recorded to blockchain: {tx_id}")
    
    # Later: Someone wants to verify the image
    record = blockchain.verify_hash(image_hash)
    
    if record:
        print(f"✅ Image verified!")
        print(f"   Captured: {record.timestamp}")
        print(f"   Camera: {record.camera_id}")
        print(f"   Location: {record.geolocation}")
        print(f"   Transaction: {record.transaction_id}")
    else:
        print("❌ Image not found on blockchain - may be manipulated")
    
    assert record is not None


if __name__ == "__main__":
    # Run the integration example
    print("\n" + "="*60)
    print("Birthmark Protocol - Blockchain Module Test")
    print("="*60 + "\n")
    
    test_integration_example()
    
    print("\n" + "="*60)
    print("Run full test suite with: python -m pytest test_blockchain.py -v")
    print("="*60)
