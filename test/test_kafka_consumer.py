import asyncio
import json
import logging
import ssl
import threading

import aiofiles
from aiokafka import AIOKafkaConsumer, ConsumerStoppedError
from aiokafka.errors import KafkaError, KafkaConnectionError
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

ssl_context = ssl.create_default_context(cafile='../src/security/kafka-client.pem')
ssl_context.load_cert_chain(
    certfile='../src/security/snakeoil-ca-1.crt',
    keyfile='../src/security/snakeoil-ca-1.key',
    password='genius'
)

engine = create_engine("mysql+pymysql://genius:genius@localhost:3307/genius")
async_engine = create_async_engine("mysql+asyncmy://genius:genius@localhost:3307/genius", echo=True)
sync_session = sessionmaker(bind=engine)()
async_session = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


async def kafka_consumer():
    logging.info(f"kafka_consumer started: {threading.current_thread().name}, id: {threading.current_thread().ident}")
    consumer = AIOKafkaConsumer(
        "debezium.mysql.source.genius.employees",
        group_id="kafka-consumer-group",
        bootstrap_servers="localhost:9094,localhost:9097,localhost:9910",
        security_protocol="SASL_SSL",
        sasl_mechanism="PLAIN",
        sasl_plain_username="genius",
        sasl_plain_password="genius",
        auto_offset_reset="latest",
        ssl_context=ssl_context,
        auto_commit_interval_ms=10000,
        heartbeat_interval_ms=10000,
        session_timeout_ms=30000,
        max_poll_records=100,
        max_poll_interval_ms=30000,
        enable_auto_commit=False)
    await consumer.start()

    try:
        async for message in consumer:
            try:
                logging.info(f"message: {message}")
                if message.value is not None:
                    value = json.loads(message.value.decode('utf-8'))
                    operation = value.get('op')
                    if operation == 'c':
                        logging.info(f"Create operation")
                        # write_to_file(value)
                        await async_write_to_file(value)
                    elif operation == 'u':
                        logging.info(f"Update operation")
                        # await async_write_to_file(value)
                    elif operation == 'd':
                        logging.info(f"Delete operation")
                        raise Exception("Delete operation not supported")
                else:
                    key = json.loads(message.key.decode('utf-8'))
                    logging.info(f"message key {key}, message value is None")
            except Exception as e:
                logging.error(f"Exception: {e}")
            finally:
                await consumer.commit()
                logging.info(f"Finally 1: {threading.current_thread().name}, id: {threading.current_thread().ident}")

    except ConsumerStoppedError as e:
        logging.error(e, 'ConsumerStoppedError')
    except KafkaError as e:
        logging.error(e, 'KafkaError')
    except KafkaConnectionError as e:
        logging.error(e, 'KafkaConnectionError')
    except Exception as e:
        logging.error(f"Exception 2: {e}")
    finally:
        await consumer.stop()
        logging.error(f"Finally 2: {threading.current_thread().name}, id: {threading.current_thread().ident}")


def write_to_file(value):
    employees = sync_session.execute(text("SELECT id FROM employees")).all()
    sync_session.commit()
    logging.info(f"employees size: {len(employees)}")
    with open('employees_operation.json', 'a') as f:
        f.write(json.dumps(value.get('op')) + '\n')
    with open('employees_before.json', 'a') as f:
        f.write(json.dumps(value.get('before') if value.get('before') else {}) + '\n')
    with open('employees_after.json', 'a') as f:
        f.write(json.dumps(value.get('after') if value.get('after') else {}) + '\n')


async def async_write_to_file(value):
    # async with async_session() as session:
    #     result = await session.execute(text("SELECT id FROM employees"))
    #     employees = result.fetchall()
    #     await session.commit()
    employee = value.get("after")
    sync_session.execute(text("INSERT INTO employees (id, name, department, salary) VALUES (:id, :name, :department, :salary)"),
                         {"id": employee.get("id"), "name": employee.get("name"), "department": employee.get("department"), "salary": employee.get("salary")})
    sync_session.commit()
    employees = sync_session.execute(text("SELECT id FROM employees")).all()
    logging.info(f"employees size: {len(employees)}")
    async with aiofiles.open('employees_operation.json', 'a') as f:
        await f.write(json.dumps(value.get('op')) + '\n')
    async with aiofiles.open('employees_before.json', 'a') as f:
        await f.write(json.dumps(value.get('before') if value.get('before') else {}) + '\n')
    async with aiofiles.open('employees_after.json', 'a') as f:
        await f.write(json.dumps(value.get('after') if value.get('after') else {}) + '\n')


foo_event_loop = asyncio.new_event_loop()


def run_forever(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def test_aiokafka_consumer():
    try:
        foo_event_thread = threading.Thread(target=run_forever, args=(foo_event_loop,))
        foo_event_thread.start()
        asyncio.run_coroutine_threadsafe(kafka_consumer(), foo_event_loop)
        foo_event_thread.join()
    finally:
        foo_event_loop.call_soon_threadsafe(foo_event_loop.stop)
        foo_event_loop.close()

    assert True

# def test_kafka_consumer():
#     logging.info("test_kafka_consumer")
#     consumer = KafkaConsumer(
#         "debezium.mysql.source.genius.employees",
#         bootstrap_servers=["localhost:9092"],
#         group_id="kafka-consumer-group",
#         value_deserializer=lambda x: x.decode('utf-8')
#     )
#     for message in consumer:
#         logging.info(message)
