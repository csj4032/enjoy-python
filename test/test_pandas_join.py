import logging

import pytest
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from faker import Faker

engine = create_engine("mysql+pymysql://genius:genius@localhost:3306/genius")
sync_session = sessionmaker(bind=engine)()

Base = declarative_base()


class Customers(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    address = Column(String, nullable=False)
    company = Column(String, nullable=False)

    def __repr__(self):
        return f"<Customer(name='{self.name}', email='{self.email}', phone_number='{self.phone_number}', address='{self.address}')>"


def test_table_truncate():
    sync_session.execute(text("TRUNCATE TABLE customers"))
    sync_session.commit()
    assert True


def test_table_fake_insert():
    faker = Faker("ko_KR")
    data = [{"name": faker.name(), "email": faker.email(), "phone_number": faker.random_int(1, 7), "address": faker.address(), "company": faker.company()} for _ in range(1000)]
    logging.info(f"data: {data}")
    sync_session.bulk_insert_mappings(Customers, data)
    sync_session.commit()
    assert True


def test_data_():
    faker = Faker("ko_KR")
    original = pd.DataFrame(sync_session.execute(text("SELECT id, name FROM customers WHERE id >= 800")).all(), columns=["id", "name"])
    source = pd.DataFrame([{"id": _, "name": faker.name(), "email": faker.email(), "phone_number": faker.random_int(1, 7), "address": faker.address(), "company": faker.company()} for _ in range(900, 1100)])
    merged = original.merge(source, on="id", how="outer", indicator=True)
    insert = merged[merged["_merge"] == "right_only"].rename(columns={"name_y": "name"}).drop(columns=["name_x", "_merge"]).to_dict(orient="records")
    update = merged[merged["_merge"] == "both"].rename(columns={"name_y": "name"}).drop(columns=["name_x", "_merge", "email", "phone_number", "address", "company"]).to_dict(orient="records")
    logging.info(f"insert: {insert}")
    logging.info(f"update: {update}")
    sync_session.bulk_insert_mappings(Customers, insert)
    sync_session.bulk_update_mappings(Customers, update)
    sync_session.commit()
    assert True
