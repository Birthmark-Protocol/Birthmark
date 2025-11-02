"""
Camera interface for capturing and authenticating images.

This module provides the interface between camera hardware/software
and the Birthmark Protocol authentication system.
"""

from typing import Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

from .hash import compute_image_hash
from .blockchain import record_to_blockchain, BirthmarkRecord


@dataclass
class CaptureResult:
    """
    Result of authenticated image capture.
    
    Attributes:
        image_path: Where image was saved
        hash: Computed hash of image
        timestamp: Capture timestamp
        transaction_id: Blockchain transaction ID
        camera_id: Camera identifier used
    """
    image_path: Path
    hash: str
    timestamp: datetime
    transaction_id: str
    camera_id: str


class CameraInterface:
    """
    Interface for camera capture with Birthmark authentication.
    
    This class handles:
    - Image capture (simulated for now)
    - Hash computation
    - Blockchain recording
    - Local storage with metadata
    """
    
    def __init__(
        self,
        camera_id: str,
        network: str = "testnet",
        auto_record: bool = True
    ):
        """
        Initialize camera interface.
        
        Args:
            camera_id: Unique identifier for this camera
            network: Blockchain network to use
            auto_record: Automatically record to blockchain
        """
        self.camera_id = camera_id
        self.network = network
        self.auto_record = auto_record
        
    def capture_authenticated(
        self,
        output_path: Path,
        geolocation: Optional[Tuple[float, float]] = None
    ) -> CaptureResult:
        """
        Capture image with authentication.
        
        This is the main workflow:
        1. Capture image data from camera
        2. Compute hash immediately
        3. Record to blockchain
        4. Save image locally with metadata
        
        Args:
            output_path: Where to save image
            geolocation: Optional GPS coordinates
            
        Returns:
            CaptureResult with all authentication details
            
        Raises:
            CameraError: If capture fails
            BlockchainError: If recording fails (if auto_record=True)
        """
        # TODO: Replace with actual camera capture
        # For now, this is a placeholder showing the workflow
        
        # Step 1: Capture raw image data
        image_data = self._capture_raw_data()
        
        # Step 2: Compute hash immediately (before any processing)
        image_hash, timestamp = compute_image_hash(image_data)
        
        # Step 3: Record to blockchain (if enabled)
        transaction_id = None
        if self.auto_record:
            transaction_id = record_to_blockchain(
                image_hash=image_hash,
                timestamp=timestamp,
                camera_id=self.camera_id,
                geolocation=geolocation,
                network=self.network
            )
        
        # Step 4: Save image with metadata
        self._save_with_metadata(
            image_data=image_data,
            output_path=output_path,
            hash=image_hash,
            timestamp=timestamp,
            transaction_id=transaction_id
        )
        
        return CaptureResult(
            image_path=output_path,
            hash=image_hash,
            timestamp=timestamp,
            transaction_id=transaction_id,
            camera_id=self.camera_id
        )
    
    def _capture_raw_data(self) -> bytes:
        """
        Capture raw image data from camera sensor.
        
        TODO: Implement actual camera interface.
        This will need platform-specific code:
        - iOS: AVFoundation
        - Android: Camera2 API
        - Desktop: OpenCV or similar
        """
        raise NotImplementedError("Camera capture not yet implemented")
    
    def _save_with_metadata(
        self,
        image_data: bytes,
        output_path: Path,
        hash: str,
        timestamp: datetime,
        transaction_id: Optional[str]
    ) -> None:
        """
        Save image file with Birthmark metadata.
        
        Metadata includes:
        - Birthmark hash
        - Blockchain transaction ID
        - Timestamp
        - Camera ID
        
        This can be embedded in EXIF or as sidecar file.
        """
        # TODO: Implement metadata embedding
        # Can use Pillow for EXIF, or save separate JSON sidecar
        raise NotImplementedError("Metadata embedding not yet implemented")
    
    def verify_image(
        self,
        image_path: Path
    ) -> Tuple[bool, Optional[BirthmarkRecord]]:
        """
        Verify an image's authenticity.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Tuple of (is_authentic, blockchain_record)
            
        Example:
            >>> camera = CameraInterface("camera_001")
            >>> is_authentic, record = camera.verify_image("photo.jpg")
            >>> if is_authentic:
            ...     print(f"Authentic! Captured at {record.timestamp}")
        """
        # TODO: Implement verification
        # 1. Read image file
        # 2. Compute current hash
        # 3. Check blockchain for original hash
        # 4. Compare and return results
        raise NotImplementedError("Image verification not yet implemented")
