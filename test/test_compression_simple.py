import gzip
import time
import logging

try: import lz4.frame as lz4
except ImportError: lz4 = None

try: import zstandard as zstd
except ImportError: zstd = None

try: import snappy
except ImportError: snappy = None

try: import brotli
except ImportError: brotli = None

def generate_data(size_kb): return ("Hello World! " * 100).encode()[:size_kb * 1024]

def test_compression(data, name, compress_func, decompress_func):
    start = time.time(); compressed = compress_func(data); compress_time = time.time() - start
    start = time.time(); decompressed = decompress_func(compressed); decompress_time = time.time() - start
    assert data == decompressed
    return {"name": name, "ratio": len(data) / len(compressed), "time": compress_time, "size": len(compressed) / 1024}

def test_all_sizes():
    algorithms = [("GZIP", gzip.compress, gzip.decompress)]
    if lz4: algorithms.append(("LZ4", lz4.compress, lz4.decompress))
    if zstd: algorithms.append(("ZSTD", lambda d: zstd.ZstdCompressor().compress(d), lambda d: zstd.ZstdDecompressor().decompress(d)))
    if snappy and hasattr(snappy, 'compress'): algorithms.append(("Snappy", snappy.compress, snappy.decompress))
    if brotli: algorithms.append(("Brotli", brotli.compress, brotli.decompress))
    
    logging.info(f"{'Size':<6} {'Algo':<7} {'Ratio':<8} {'KB':<8} {'Time':<8}")
    logging.info("-" * 40)
    
    for size_kb in [1, 10, 100, 1000]:
        data = generate_data(size_kb)
        for name, compress_func, decompress_func in algorithms:
            try:
                result = test_compression(data, name, compress_func, decompress_func)
                logging.info(f"{size_kb:<6} {name:<7} {result['ratio']:<8.1f} {result['size']:<8.1f} {result['time']:<8.4f}")
            except Exception:
                logging.error(f"{size_kb:<6} {name:<7} ERROR")

if __name__ == "__main__": 
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    test_all_sizes()