import json

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
