"""
Compression library tests for different algorithms.
Tests compression ratio, performance, and round-trip integrity.
"""

import json
import time
import tempfile
import os
from typing import NamedTuple
import pytest

try:
    import lz4.frame
    LZ4_AVAILABLE = True
except ImportError:
    LZ4_AVAILABLE = False

try:
    import zstandard as zstd
    ZSTD_AVAILABLE = True
except ImportError:
    ZSTD_AVAILABLE = False

try:
    import snappy
    # Test if snappy has the expected functions
    if hasattr(snappy, 'compress') and hasattr(snappy, 'decompress'):
        SNAPPY_AVAILABLE = True
    else:
        SNAPPY_AVAILABLE = False
except ImportError:
    SNAPPY_AVAILABLE = False

import gzip  # Built-in

try:
    import brotli
    BROTLI_AVAILABLE = True
except ImportError:
    BROTLI_AVAILABLE = False

try:
    from faker import Faker
    FAKER_AVAILABLE = True
except ImportError:
    FAKER_AVAILABLE = False


class CompressionResult(NamedTuple):
    """Result of compression test."""
    algorithm: str
    original_size: int
    compressed_size: int
    compression_ratio: float
    compression_time: float
    decompression_time: float
    data_matches: bool


class TestCompressionLibraries:
    """Test suite for various compression libraries."""
    
    @pytest.fixture
    def sample_data(self) -> bytes:
        """Generate sample data for testing."""
        if FAKER_AVAILABLE:
            faker = Faker("ko_KR")
            fake_data = [
                {
                    "birth": faker.date_of_birth().strftime("%Y-%m-%d"),
                    "name": faker.name(),
                    "email": faker.email(),
                    "phone": faker.phone_number(),
                    "address": faker.address(),
                    "job": faker.job(),
                    "company": faker.company(),
                    "sentence": faker.sentence()
                }
                for _ in range(100)
            ]
        else:
            # Fallback data without faker
            fake_data = [
                {
                    "name": f"User {i}",
                    "email": f"user{i}@example.com",
                    "text": "This is sample text for compression testing. " * 10
                }
                for i in range(100)
            ]
        
        return json.dumps(fake_data, ensure_ascii=False).encode("utf-8")
    
    @pytest.fixture
    def large_sample_data(self) -> bytes:
        """Generate larger sample data for performance testing."""
        if FAKER_AVAILABLE:
            faker = Faker("ko_KR")
            fake_data = [
                {
                    "birth": faker.date_of_birth().strftime("%Y-%m-%d"),
                    "name": faker.name(),
                    "email": faker.email(),
                    "phone": faker.phone_number(),
                    "address": faker.address(),
                    "job": faker.job(),
                    "company": faker.company(),
                    "sentence": faker.sentence(),
                    "description": faker.text(max_nb_chars=500)
                }
                for _ in range(1000)
            ]
        else:
            # Fallback data without faker
            fake_data = [
                {
                    "name": f"User {i}",
                    "email": f"user{i}@example.com",
                    "text": "This is sample text for compression testing. " * 50
                }
                for i in range(1000)
            ]
        
        return json.dumps(fake_data, ensure_ascii=False).encode("utf-8")

    def _test_compression_algorithm(self, data: bytes, compress_func, decompress_func, algorithm_name: str) -> CompressionResult:
        """Test a compression algorithm and return results."""
        original_size = len(data)
        
        # Test compression
        start_time = time.time()
        compressed_data = compress_func(data)
        compression_time = time.time() - start_time
        
        compressed_size = len(compressed_data)
        compression_ratio = original_size / compressed_size if compressed_size > 0 else 0
        
        # Test decompression
        start_time = time.time()
        decompressed_data = decompress_func(compressed_data)
        decompression_time = time.time() - start_time
        
        # Verify data integrity
        data_matches = data == decompressed_data
        
        return CompressionResult(
            algorithm=algorithm_name,
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=compression_ratio,
            compression_time=compression_time,
            decompression_time=decompression_time,
            data_matches=data_matches
        )

    @pytest.mark.skipif(not ZSTD_AVAILABLE, reason="zstandard not available")
    def test_zstd_compression(self, sample_data: bytes):
        """Test Zstandard compression."""
        def compress_zstd(data: bytes) -> bytes:
            return zstd.ZstdCompressor(level=3).compress(data)
        
        def decompress_zstd(data: bytes) -> bytes:
            return zstd.ZstdDecompressor().decompress(data)
        
        result = self._test_compression_algorithm(
            sample_data, compress_zstd, decompress_zstd, "ZSTD"
        )
        
        assert result.data_matches, "ZSTD: Decompressed data doesn't match original"
        assert result.compression_ratio > 1.0, "ZSTD: No compression achieved"
        assert result.compressed_size < result.original_size, "ZSTD: Compressed size is not smaller"

    @pytest.mark.skipif(not SNAPPY_AVAILABLE, reason="python-snappy not available")
    def test_snappy_compression(self, sample_data: bytes):
        """Test Snappy compression."""
        result = self._test_compression_algorithm(
            sample_data, snappy.compress, snappy.decompress, "Snappy"
        )
        
        assert result.data_matches, "Snappy: Decompressed data doesn't match original"
        assert result.compression_ratio > 1.0, "Snappy: No compression achieved"

    def test_gzip_compression(self, sample_data: bytes):
        """Test GZIP compression."""
        def compress_gzip(data: bytes) -> bytes:
            return gzip.compress(data, compresslevel=6)
        
        result = self._test_compression_algorithm(
            sample_data, compress_gzip, gzip.decompress, "GZIP"
        )
        
        assert result.data_matches, "GZIP: Decompressed data doesn't match original"
        assert result.compression_ratio > 1.0, "GZIP: No compression achieved"

    @pytest.mark.skipif(not BROTLI_AVAILABLE, reason="brotli not available")
    def test_brotli_compression(self, sample_data: bytes):
        """Test Brotli compression."""
        def compress_brotli(data: bytes) -> bytes:
            return brotli.compress(data, quality=6)
        
        result = self._test_compression_algorithm(
            sample_data, compress_brotli, brotli.decompress, "Brotli"
        )
        
        assert result.data_matches, "Brotli: Decompressed data doesn't match original"
        assert result.compression_ratio > 1.0, "Brotli: No compression achieved"

    @pytest.mark.skipif(not LZ4_AVAILABLE, reason="lz4 not available")
    def test_lz4_compression(self, sample_data: bytes):
        """Test LZ4 compression."""
        result = self._test_compression_algorithm(
            sample_data, lz4.frame.compress, lz4.frame.decompress, "LZ4"
        )
        
        assert result.data_matches, "LZ4: Decompressed data doesn't match original"
        assert result.compression_ratio > 1.0, "LZ4: No compression achieved"

    def test_compression_comparison(self, large_sample_data: bytes):
        """Compare all available compression algorithms."""
        algorithms = []
        
        # Add available algorithms
        if ZSTD_AVAILABLE:
            algorithms.append(("ZSTD", lambda d: zstd.ZstdCompressor(level=3).compress(d), 
                             lambda d: zstd.ZstdDecompressor().decompress(d)))
        
        if SNAPPY_AVAILABLE:
            algorithms.append(("Snappy", snappy.compress, snappy.decompress))
        
        algorithms.append(("GZIP", lambda d: gzip.compress(d, compresslevel=6), gzip.decompress))
        
        if BROTLI_AVAILABLE:
            algorithms.append(("Brotli", lambda d: brotli.compress(d, quality=6), brotli.decompress))
        
        if LZ4_AVAILABLE:
            algorithms.append(("LZ4", lz4.frame.compress, lz4.frame.decompress))
        
        if not algorithms:
            pytest.skip("No compression libraries available")
        
        results = []
        for name, compress_func, decompress_func in algorithms:
            result = self._test_compression_algorithm(
                large_sample_data, compress_func, decompress_func, name
            )
            results.append(result)
            assert result.data_matches, f"{name}: Data integrity check failed"
        
        # Print comparison table
        print("\n" + "="*80)
        print("COMPRESSION ALGORITHM COMPARISON")
        print("="*80)
        print(f"{'Algorithm':<10} {'Ratio':<8} {'Comp Time':<12} {'Decomp Time':<12} {'Size (KB)':<10}")
        print("-" * 80)
        
        for result in sorted(results, key=lambda x: x.compression_ratio, reverse=True):
            print(f"{result.algorithm:<10} "
                  f"{result.compression_ratio:<8.2f} "
                  f"{result.compression_time:<12.4f} "
                  f"{result.decompression_time:<12.4f} "
                  f"{result.compressed_size/1024:<10.1f}")
        
        print("-" * 80)
        print(f"Original size: {len(large_sample_data)/1024:.1f} KB")
        
        # Best compression ratio
        best_ratio = max(results, key=lambda x: x.compression_ratio)
        print(f"Best compression ratio: {best_ratio.algorithm} ({best_ratio.compression_ratio:.2f}x)")
        
        # Fastest compression
        fastest_comp = min(results, key=lambda x: x.compression_time)
        print(f"Fastest compression: {fastest_comp.algorithm} ({fastest_comp.compression_time:.4f}s)")
        
        # Fastest decompression
        fastest_decomp = min(results, key=lambda x: x.decompression_time)
        print(f"Fastest decompression: {fastest_decomp.algorithm} ({fastest_decomp.decompression_time:.4f}s)")

    def test_gzip_levels(self, sample_data: bytes):
        """Test different GZIP compression levels."""
        levels = [1, 6, 9]  # Fast, default, best
        results = []
        
        for level in levels:
            def compress_gzip_level(data: bytes) -> bytes:
                return gzip.compress(data, compresslevel=level)
            
            result = self._test_compression_algorithm(
                sample_data, compress_gzip_level, gzip.decompress, f"GZIP-{level}"
            )
            results.append(result)
            assert result.data_matches, f"GZIP-{level}: Data integrity check failed"
        
        print(f"\nGZIP Compression Levels Comparison:")
        print(f"{'Level':<8} {'Ratio':<8} {'Comp Time':<12} {'Size (KB)':<10}")
        print("-" * 40)
        
        for result in results:
            level = result.algorithm.split('-')[1]
            print(f"{level:<8} "
                  f"{result.compression_ratio:<8.2f} "
                  f"{result.compression_time:<12.4f} "
                  f"{result.compressed_size/1024:<10.1f}")

    def test_empty_data_compression(self):
        """Test compression of empty data."""
        empty_data = b""
        
        # Test GZIP (always available)
        assert gzip.decompress(gzip.compress(empty_data)) == empty_data
        
        # Test other algorithms if available
        if SNAPPY_AVAILABLE:
            assert snappy.decompress(snappy.compress(empty_data)) == empty_data
        
        if BROTLI_AVAILABLE:
            assert brotli.decompress(brotli.compress(empty_data)) == empty_data
        
        if LZ4_AVAILABLE:
            assert lz4.frame.decompress(lz4.frame.compress(empty_data)) == empty_data
        
        if ZSTD_AVAILABLE:
            zstd_compressor = zstd.ZstdCompressor()
            zstd_decompressor = zstd.ZstdDecompressor()
            assert zstd_decompressor.decompress(zstd_compressor.compress(empty_data)) == empty_data

    def test_text_vs_binary_compression(self):
        """Compare compression ratios for text vs binary data."""
        # Text data (highly compressible)
        text_data = "Hello World! " * 1000
        text_bytes = text_data.encode("utf-8")
        
        # Binary data (less compressible)
        binary_data = bytes(range(256)) * 50
        
        algorithms = [("GZIP", gzip.compress, gzip.decompress)]
        
        if ZSTD_AVAILABLE:
            algorithms.append(("ZSTD", lambda d: zstd.ZstdCompressor().compress(d), 
                             lambda d: zstd.ZstdDecompressor().decompress(d)))
        
        print(f"\nText vs Binary Data Compression:")
        print(f"{'Algorithm':<8} {'Text Ratio':<12} {'Binary Ratio':<12}")
        print("-" * 35)
        
        for name, compress_func, decompress_func in algorithms:
            text_result = self._test_compression_algorithm(
                text_bytes, compress_func, decompress_func, f"{name}-Text"
            )
            binary_result = self._test_compression_algorithm(
                binary_data, compress_func, decompress_func, f"{name}-Binary"
            )
            
            assert text_result.data_matches, f"{name}: Text data integrity failed"
            assert binary_result.data_matches, f"{name}: Binary data integrity failed"
            
            print(f"{name:<8} "
                  f"{text_result.compression_ratio:<12.2f} "
                  f"{binary_result.compression_ratio:<12.2f}")


if __name__ == "__main__":
    # Run a quick demo
    test_suite = TestCompressionLibraries()
    
    # Generate sample data
    if FAKER_AVAILABLE:
        faker = Faker("ko_KR")
        sample_data = json.dumps([{
            "name": faker.name(),
            "email": faker.email(),
            "address": faker.address(),
            "text": faker.text()
        } for _ in range(100)], ensure_ascii=False).encode("utf-8")
    else:
        sample_data = json.dumps([{
            "name": f"User {i}",
            "email": f"user{i}@example.com",
            "text": "Sample text " * 20
        } for i in range(100)], ensure_ascii=False).encode("utf-8")
    
    print("Running compression library comparison...")
    test_suite.test_compression_comparison(sample_data)
    test_suite.test_gzip_levels(sample_data)
    test_suite.test_text_vs_binary_compression()