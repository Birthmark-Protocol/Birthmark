"""
Birthmark Protocol - Permanent Authentication for Digital Media

An open protocol for camera-native blockchain verification of digital images.
"""

__version__ = "0.1.0"
__author__ = "Samuel C. Ryan"
__email__ = "samryan.pdx@proton.me"

from .hash import compute_image_hash
from .blockchain import record_to_blockchain, verify_from_blockchain
from .camera import CameraInterface

__all__ = [
    "compute_image_hash",
    "record_to_blockchain",
    "verify_from_blockchain",
    "CameraInterface",
]
