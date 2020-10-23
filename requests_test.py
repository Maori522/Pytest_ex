import aiohttp
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from datetime import datetime
import json
import time
import asyncio
import numpy as np

my_key = "66efb91e-7480-4412-bc26-1f73957504c6"
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
data = []
parameters = {
    'start': '1',
    'limit': '10',
    'sort': 'volume_24h'
}
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': my_key,
}

response_timeout = 500
max_80_percentile_value = 450
max_rps_value = 5
max_response_size = 10 * 1000  # in kilobytes
current_date_conditions = []
response_time_list = []
async_request_count = 8



def is_date_valid(data):
    for tickers in data['data']:
        if datetime.strptime(tickers['last_updated'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime(
                "%Y-%m-%d") == time.strftime("%Y-%m-%d"):
            current_date_conditions.append(True)
        else:
            current_date_conditions.append(False)
    return all(current_date_conditions)


def test_response():
    session = Session()
    try:
        session.headers.update(headers)
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

    assert is_date_valid(data)
    assert response.elapsed.microseconds / 1000 < response_timeout
    assert len(response.content) < max_response_size


async def async_response(session):
    start_time = round(time.time() * 1000)
    async with session.get(url, params=parameters, headers=headers) as response:
        data = await response.read()
        end_time = round(time.time() * 1000)
        data = json.loads(data.decode("utf-8"))
        response_time = end_time - start_time
        response_time_list.append(response_time)
        assert is_date_valid(data)
        assert response_time < response_timeout
        assert response.content.total_bytes < max_response_size


async def test_async_response():
    tasks = []
    async with aiohttp.ClientSession() as session:
        for i in range(async_request_count):
            task = asyncio.create_task(async_response(session))
            tasks.append(task)

        await asyncio.gather(*tasks)
    rps = (sum(response_time_list) / 1000) / async_request_count
    percentile = np.percentile(response_time_list, 80)
    assert rps < max_rps_value
    assert percentile < max_80_percentile_value


#asyncio.run(test_async_response())
