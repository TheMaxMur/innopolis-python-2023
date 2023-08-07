#!/usr/bin/python3

from httpx import AsyncClient
from lxml import etree
from lxml.etree import HTMLParser


import os
import gc
import asyncio
from typing import Union
import json
from datetime import datetime
import time
import requests


base_url = "https://zoostyle-ekb.ru/"


async def get_categories(url: str) -> list:
    async with AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        return (None)
    
    html = etree.fromstring(response.text, HTMLParser())
    categories = html.xpath('//a[@class="main_a"]/@href')

    result = []

    for i in range(len(categories)):
        result.append(base_url + categories[i][1:])

    return (result)


async def get_podcategorii(url: str) -> list:
    result = []

    async with AsyncClient() as client:
        response = await client.get(url)
    
    if response.status_code != 200:
        return (None)
    
    html = etree.fromstring(response.text, HTMLParser())
    categories = html.xpath('//div[@class="goods_all_text"]//a/@href')
    
    for i in range(len(categories)):
        result.append(base_url[:-1] + categories[i])

    return (result)


async def get_product(url: str) -> list:
    result = []

    async with AsyncClient() as client:
        response = await client.get(url)
    
    if response.status_code != 200:
        return (None)
    
    html = etree.fromstring(response.text, HTMLParser())
    categories = html.xpath('//div[@class="goods"]//a/@href')
    
    for i in range(len(categories)):
        result.append(base_url[:-1] + categories[i])

    return (result)


async def get_product_info(url: str) -> dict:
    result = {}

    async with AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        return (None)

    html = etree.fromstring(response.text, HTMLParser())
    result["Name"] = ''.join(html.xpath('//span[@class="content_title"]//h1/text()'))
    result["Article"] = ''.join(html.xpath('//span[@class="catalog_right_aticul"]/text()'))
    result["Price"] = {}
    result["Price"]["Old-Price"] = ''.join(html.xpath('//div[@class="catalog_item_price"]/span[@class="catalog_item_old_price"]/text()'))
    result["Price"]["New-Price"] = ''.join(html.xpath('//div[@class="catalog_item_price"]/span[@class="catalog_item_new_price"]/text()'))
    result["Availability"] = ''.join(html.xpath('//span[@class="point_count"]/text()'))
    result["Images"] = [base_url + image_url for image_url in html.xpath('//div[@class="catalog_all_images"]//a/@href')]
    result["Description"] = ' '.join(html.xpath('//div[@id="tab-1"]//p/text()'))

    return (result)


def write_result_to_json(result: list) -> None:
    date = str(datetime.now()).split(" ")[0]

    with open(f"{date}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Данные записаны в results/{date}.json")

    return (None)


async def main() -> int:
    categories = await get_categories(base_url)
    result = []

    for i in range(len(categories)):
        tmp = await get_podcategorii(categories[i])

        if tmp == None:
            print("Error", i)
            continue

        result.append(tmp)

    print(result)

    test = []

    for i in range(len(result)):
        if result[i][0][-4:] == ".htm":
            for j in range(len(result[i])):
                test.append(list(result[i][j]))
            continue

        for j in range(len(result[i])):
            tmp = await get_product(result[i][j])
            if tmp != []:
                test.append(tmp)

    result = []

    for i in range(len(test)):
        for j in range(len(test[i])):
            tmp = await get_product_info(test[i][j])
            result.append(tmp)

    write_result_to_json(result)

    return (0)


if __name__ == "__main__":
    asyncio.run(main())
