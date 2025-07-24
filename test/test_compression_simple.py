"""
Simple compression library test with built-in libraries only.
"""

import json
import gzip
import time
from faker import Faker


def test_gzip_compression():
    """Test GZIP compression with sample data."""
    # Generate sample data
    faker = Faker("ko_KR")
    sample_data = json.dumps([{
        "name": faker.name(),
        "email": faker.email(),
        "address": faker.address(),
        "text": faker.text()
    } for _ in range(100)], ensure_ascii=False).encode("utf-8")
    
    print(f"Original size: {len(sample_data)} bytes")
    
    # Test compression
    start_time = time.time()
    compressed_data = gzip.compress(sample_data, compresslevel=6)
    compression_time = time.time() - start_time
    
    print(f"Compressed size: {len(compressed_data)} bytes")
    compression_ratio = len(sample_data) / len(compressed_data)
    print(f"Compression ratio: {compression_ratio:.2f}x")
    print(f"Compression time: {compression_time:.4f}s")
    
    # Test decompression
    start_time = time.time()
    decompressed_data = gzip.decompress(compressed_data)
    decompression_time = time.time() - start_time
    
    print(f"Decompression time: {decompression_time:.4f}s")
    
    # Verify data integrity
    assert sample_data == decompressed_data, "Data integrity check failed!"
    print("✅ Data integrity verified!")
    
    return {
        "algorithm": "GZIP",
        "original_size": len(sample_data),
        "compressed_size": len(compressed_data),
        "compression_ratio": compression_ratio,
        "compression_time": compression_time,
        "decompression_time": decompression_time
    }


if __name__ == "__main__":
    print("Testing GZIP compression...")
    result = test_gzip_compression()
    print("\nTest completed successfully! 🎉")