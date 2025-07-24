import json
import lz4.frame
import pandas as pd
import zstandard as zstd
import snappy
import gzip
import brotli
from typing import List, Dict

from faker import Faker


def generate_fake_data() -> List[Dict[str, str]]:
    faker = Faker("ko_KR")
    return [dict({
        "birth": faker.date_of_birth().strftime("%Y-%m-%d"),
        "name": faker.name(),
        "email": faker.email(),
        "phone": faker.phone_number(),
        "address": faker.address(),
        "job": faker.job(),
        "company": faker.company(),
        "sentence": faker.sentence()
    }) for _ in range(1)]


if __name__ == '__main__':
    fake_data = generate_fake_data()
    fake_data_json = json.dumps(fake_data, ensure_ascii=False)
    with open("./fake_data.json", "w") as f:
        f.write(fake_data_json)


    df = pd.read_parquet("/Users/genius/Workspace/enjoy-docker/stream/warehouse/default_database/genius_departments_iceberg_sink/data/00000-0-b31a2bae-b447-4a0f-85e2-9d91cf18a61f-00001.parquet");
    print(df.head())
    # df.to_json("./fake_data_pandas.json", orient="records", force_ascii=False)
    # df.to_csv("./fake_data_pandas.csv", index=False, header=True, encoding="utf-8")
    # df.to_parquet("./fake_data_pandas.parquet", index=False, compression="UNCOMPRESSED")
    # df.to_parquet("./fake_data_pandas.parquet.zstd", index=False, compression="ZSTD")
    # df.to_parquet("./fake_data_pandas.parquet.snappy", index=False, compression="SNAPPY")
    # df.to_parquet("./fake_data_pandas.parquet.gzip", index=False, compression="GZIP")
    # df.to_parquet("./fake_data_pandas.parquet.brotli", index=False, compression="BROTLI")
    # df.to_parquet("./fake_data_pandas.parquet.brotli", index=False, compression="LZ4")

    # with open("./fake_data.zstd", "wb") as f:
    #     f.write(zstd.ZstdCompressor(level=22).compress(fake_data_json.encode("utf-8")))
    #
    # with open("./fake_data.snappy", "wb") as f:
    #     f.write(snappy.compress(fake_data_json.encode("utf-8")))
    #
    # with open("./fake_data.gzip", 'wb') as f:
    #     f.write(gzip.compress(fake_data_json.encode('utf-8')))
    #
    # with open("./fake_data.brotli", 'wb') as f:
    #     f.write(brotli.compress(fake_data_json.encode('utf-8')))
    #
    # with open("./fake_data.lz4", 'wb') as f:
    #     f.write(lz4.frame.compress(fake_data_json.encode('utf-8')))

    # pandas는 fastparquet, pyarrow 두 라이브러리를 지원한다.
    # fastparquet + GZIP 조합이 가장 작은 파일을 생성한다.
