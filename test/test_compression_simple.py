"""
Simple compression tests by data size for each library.
"""

import json
import gzip
import time

try:
    import lz4.frame as lz4
except ImportError:
    lz4 = None

try:
    import zstandard as zstd
except ImportError:
    zstd = None

try:
    import snappy
except ImportError:
    snappy = None

try:
    import brotli
except ImportError:
    brotli = None


def generate_data(size_kb: int) -> bytes:
    """Generate test data of specified size in KB."""
    text = "Hello World! This is test data for compression. " * 20
    target_size = size_kb * 1024
    repeat_count = target_size // len(text.encode()) + 1
    data = (text * repeat_count).encode()[:target_size]
    return data


def test_compression(data: bytes, name: str, compress_func, decompress_func) -> dict:
    """Test single compression algorithm."""
    original_size = len(data)
    
    start = time.time()
    compressed = compress_func(data)
    compress_time = time.time() - start
    
    compressed_size = len(compressed)
    ratio = original_size / compressed_size
    
    start = time.time()
    decompressed = decompress_func(compressed)
    decompress_time = time.time() - start
    
    assert data == decompressed, f"{name} integrity check failed"
    
    return {
        "algorithm": name,
        "original_kb": original_size / 1024,
        "compressed_kb": compressed_size / 1024,
        "ratio": ratio,
        "compress_time": compress_time,
        "decompress_time": decompress_time
    }


def test_all_sizes():
    """Test all libraries with different data sizes."""
    sizes = [1, 10, 100, 1000]  # KB
    
    algorithms = [
        ("GZIP", gzip.compress, gzip.decompress),
    ]
    
    # Add optional libraries
    if lz4:
        algorithms.append(("LZ4", lz4.compress, lz4.decompress))
    
    if zstd:
        algorithms.append(("ZSTD", 
                         lambda d: zstd.ZstdCompressor().compress(d),
                         lambda d: zstd.ZstdDecompressor().decompress(d)))
    
    if snappy and hasattr(snappy, 'compress'):
        algorithms.append(("Snappy", snappy.compress, snappy.decompress))
    
    if brotli:
        algorithms.append(("Brotli", brotli.compress, brotli.decompress))
    
    print(f"{'Size(KB)':<8} {'Algorithm':<8} {'Original':<10} {'Compressed':<12} {'Ratio':<8} {'Comp(s)':<8}")
    print("-" * 65)
    
    for size_kb in sizes:
        data = generate_data(size_kb)
        print(f"{size_kb:<8}", end="")
        
        for name, compress_func, decompress_func in algorithms:
            try:
                result = test_compression(data, name, compress_func, decompress_func)
                print(f" {name:<8} {result['original_kb']:<10.1f} {result['compressed_kb']:<12.1f} "
                      f"{result['ratio']:<8.2f} {result['compress_time']:<8.4f}")
            except Exception as e:
                print(f" {name:<8} ERROR: {str(e)[:30]}")
        
        print()


if __name__ == "__main__":
    print("Compression Test by Data Size")
    print("=" * 65)
    test_all_sizes()