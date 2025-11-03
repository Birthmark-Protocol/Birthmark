// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

/**
 * @title BirthmarkRegistry
 * @dev Smart contract for storing image hash records on Ethereum
 * 
 * This contract is part of the Birthmark Protocol - an open protocol for
 * camera-native blockchain verification of digital images.
 * 
 * Features:
 * - Store SHA-256 image hashes with metadata
 * - Verify hash existence and retrieve records
 * - Batch operations for efficiency
 * - Privacy-preserving (camera IDs can be anonymized)
 * 
 * Gas Optimization Notes:
 * - Uses bytes32 for hashes (native EVM type)
 * - Packs geolocation data as scaled integers
 * - Optional geolocation to save gas when not needed
 * - Batch operations reduce per-transaction overhead
 */
contract BirthmarkRegistry {
    
    /// @dev Record structure stored on-chain
    struct BirthmarkRecord {
        bytes32 imageHash;      // SHA-256 hash of image
        uint256 timestamp;      // Unix timestamp of capture
        bytes32 cameraId;       // Camera identifier (can be anonymized)
        int256 latitude;        // Latitude * 1e6 for precision
        int256 longitude;       // Longitude * 1e6 for precision
        bool hasGeolocation;    // Whether geolocation was recorded
        uint256 blockNumber;    // Block number when recorded
    }
    
    /// @dev Mapping from image hash to record
    mapping(bytes32 => BirthmarkRecord) public records;
    
    /// @dev Track which hashes have been recorded
    mapping(bytes32 => bool) public exists;
    
    /// @dev Total number of records
    uint256 public totalRecords;
    
    /// @dev Contract owner (for future upgrades if needed)
    address public owner;
    
    /// @dev Events for off-chain indexing
    event HashRecorded(
        bytes32 indexed imageHash,
        uint256 timestamp,
        bytes32 indexed cameraId,
        bool hasGeolocation,
        uint256 blockNumber
    );
    
    event BatchHashesRecorded(
        uint256 count,
        uint256 blockNumber
    );
    
    /// @dev Constructor sets contract owner
    constructor() {
        owner = msg.sender;
    }
    
    /**
     * @dev Record a single image hash
     * @param imageHash SHA-256 hash of the image (as bytes32)
     * @param timestamp Unix timestamp when image was captured
     * @param cameraId Camera identifier (can be anonymized for privacy)
     * @param latitude Latitude * 1e6 (e.g., 45.5231 → 45523100)
     * @param longitude Longitude * 1e6 (e.g., -122.6765 → -122676500)
     * @param hasGeolocation Whether geolocation data is valid
     * @return success True if recording succeeded
     */
    function recordHash(
        bytes32 imageHash,
        uint256 timestamp,
        bytes32 cameraId,
        int256 latitude,
        int256 longitude,
        bool hasGeolocation
    ) public returns (bool success) {
        // Prevent duplicate records
        require(!exists[imageHash], "BirthmarkRegistry: Hash already recorded");
        
        // Validate timestamp is reasonable (not in far future)
        require(timestamp <= block.timestamp + 300, "BirthmarkRegistry: Timestamp too far in future");
        
        // Create record
        records[imageHash] = BirthmarkRecord({
            imageHash: imageHash,
            timestamp: timestamp,
            cameraId: cameraId,
            latitude: latitude,
            longitude: longitude,
            hasGeolocation: hasGeolocation,
            blockNumber: block.number
        });
        
        // Mark as existing
        exists[imageHash] = true;
        totalRecords++;
        
        // Emit event
        emit HashRecorded(
            imageHash,
            timestamp,
            cameraId,
            hasGeolocation,
            block.number
        );
        
        return true;
    }
    
    /**
     * @dev Verify if a hash exists and retrieve its record
     * @param imageHash Hash to look up
     * @return found Whether the hash was found
     * @return timestamp When image was captured
     * @return cameraId Camera that captured it
     * @return latitude Latitude * 1e6
     * @return longitude Longitude * 1e6
     * @return hasGeolocation Whether geolocation is valid
     * @return blockNumber Block number when recorded
     */
    function verifyHash(bytes32 imageHash) 
        public 
        view 
        returns (
            bool found,
            uint256 timestamp,
            bytes32 cameraId,
            int256 latitude,
            int256 longitude,
            bool hasGeolocation,
            uint256 blockNumber
        ) 
    {
        if (!exists[imageHash]) {
            return (false, 0, bytes32(0), 0, 0, false, 0);
        }
        
        BirthmarkRecord memory record = records[imageHash];
        return (
            true,
            record.timestamp,
            record.cameraId,
            record.latitude,
            record.longitude,
            record.hasGeolocation,
            record.blockNumber
        );
    }
    
    /**
     * @dev Batch record multiple hashes in a single transaction
     * @param imageHashes Array of image hashes
     * @param timestamps Array of timestamps
     * @param cameraIds Array of camera IDs
     * @param latitudes Array of latitudes * 1e6
     * @param longitudes Array of longitudes * 1e6
     * @param hasGeolocations Array of geolocation flags
     * @return success True if all recordings succeeded
     * 
     * Note: Arrays must all be the same length
     * Gas cost scales linearly with batch size
     */
    function batchRecordHashes(
        bytes32[] memory imageHashes,
        uint256[] memory timestamps,
        bytes32[] memory cameraIds,
        int256[] memory latitudes,
        int256[] memory longitudes,
        bool[] memory hasGeolocations
    ) public returns (bool success) {
        // Validate array lengths match
        require(
            imageHashes.length == timestamps.length &&
            timestamps.length == cameraIds.length &&
            cameraIds.length == latitudes.length &&
            latitudes.length == longitudes.length &&
            longitudes.length == hasGeolocations.length,
            "BirthmarkRegistry: Array lengths must match"
        );
        
        // Reasonable batch size limit to prevent gas issues
        require(imageHashes.length <= 100, "BirthmarkRegistry: Batch too large (max 100)");
        
        // Record each hash
        for (uint i = 0; i < imageHashes.length; i++) {
            recordHash(
                imageHashes[i],
                timestamps[i],
                cameraIds[i],
                latitudes[i],
                longitudes[i],
                hasGeolocations[i]
            );
        }
        
        emit BatchHashesRecorded(imageHashes.length, block.number);
        
        return true;
    }
    
    /**
     * @dev Check if multiple hashes exist (gas-efficient batch check)
     * @param imageHashes Array of hashes to check
     * @return results Array of booleans indicating existence
     */
    function batchVerifyExistence(bytes32[] memory imageHashes) 
        public 
        view 
        returns (bool[] memory results) 
    {
        results = new bool[](imageHashes.length);
        for (uint i = 0; i < imageHashes.length; i++) {
            results[i] = exists[imageHashes[i]];
        }
        return results;
    }
    
    /**
     * @dev Get the full record for a hash (alternative to verifyHash)
     * @param imageHash Hash to look up
     * @return record The complete record
     * @return found Whether the hash exists
     */
    function getRecord(bytes32 imageHash) 
        public 
        view 
        returns (BirthmarkRecord memory record, bool found) 
    {
        return (records[imageHash], exists[imageHash]);
    }
    
    /**
     * @dev Get contract statistics
     * @return total Total number of records
     * @return blockNum Current block number
     */
    function getStats() 
        public 
        view 
        returns (uint256 total, uint256 blockNum) 
    {
        return (totalRecords, block.number);
    }
}
