import json

import pandas as pd
from faker import Faker


def generate_fake_data() -> list[dict[str, str]]:
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
    with open("./fake_data.json", "w") as f: f.write(fake_data_json)

    df = pd.read_parquet("/Users/genius/Workspace/enjoy-docker/stream/warehouse/default_database/genius_departments_iceberg_sink/data/00000-0-b31a2bae-b447-4a0f-85e2-9d91cf18a61f-00001.parquet")
    print(df.head())