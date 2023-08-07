from httpx import AsyncClient
from lxml import etree
from lxml.etree import HTMLParser


import os
import gc
import asyncio
from typing import Union
import json
from datetime import datetime


URL = "https://chudopitomets.ru"


class ParseException(Exception):
    pass


async def GetLinksFromMainPage(url = URL) -> Union[list, ParseException]:
    """
    Данная функция находит ссылки на категории из главной страницы
    """
    async with AsyncClient() as client:
        response = await client.get(url)

    if response.status_code == 200:
        tree = etree.fromstring(response.text, HTMLParser())
        category_links = tree.xpath('//ul[@class="uk-navbar-nav uk-flex-shrink visible-links"]/li/a/@href')
        return [url + link for link in category_links]

    raise ParseException(f"Неудачный запрос на главную страницу {url}")


async def GetPages(url: str) -> Union[list, ParseException]:
    """
    Данная функция находит ссылки страницы категории
    """
    try:
        async with AsyncClient() as client:
            response = await client.get(url)
    except:
        print("Error parse product")
        raise ParseException(f"Неудачный запрос на страницу товара {url}")

    if response.status_code == 200:
        tree = etree.fromstring(response.text, HTMLParser())
        pages = tree.xpath('//ul[@class="uk-pagination uk-flex-center uk-margin-top uk-margin-remove-bottom uk-padding-small"]/li/a/text()')
        
        if pages:
            return [url] + [url + f"?page={page}" for page in range(2,int(pages[-2])+1)]
        
        return [url]

    raise ParseException(f"Неудачный запрос на страницу {url}")


async def GetProducts(url: str) -> Union[list, ParseException]:
    """
    Данная функция находит ссылки страницы товаров
    """
    try:
        async with AsyncClient() as client:
            response = await client.get(url)
    except:
        print("Error parse product")
        raise ParseException(f"Неудачный запрос на страницу товара {url}")

    if response.status_code == 200:
        tree = etree.fromstring(response.text, HTMLParser())
        links = tree.xpath('//div[@class="uk-h5 product-title uk-text-center"]/a/@href')
        return [URL + link for link in links]
    
    raise ParseException(f"Неудачный запрос на страницу {url}")


async def ParseProduct(url: str) -> Union[list, ParseException]:
    """
    Данная функция находит ссылки страницы товаров
    """
    #название*, идентификатор-, артикул*, весовая и ценовая сетка*, 
    # бренд*, характеристики*, картинки*, описание*, наличие*, вложенность категорий-, рейтинг-, отзывы-.
    try:
        async with AsyncClient() as client:
            response = await client.get(url)
    except:
        print("Error parse product")
        raise ParseException(f"Неудачный запрос на страницу товара {url}")

    if response.status_code == 200:
        dump = {}
        tree = etree.fromstring(response.text, HTMLParser())

        dump["название"] = tree.xpath('//h1[@class="product-name page-name uk-text-center global-padding-vertical uk-margin-remove"]/span/text()')
        dump["артикул"] = tree.xpath('//span[@itemprop="sku"]/text()')
        dump["бренд"] = tree.xpath('//div[@class="add2cart"]/a/img/@alt')
        dump["картинки"] = [URL + url for url in tree.xpath('//div[@class="swiper-wrapper"]//img/@src')]
        dump["наличие"] = tree.xpath('//i[@class="fa fa-check-circle ratio1x"]/text()')
        dump["описание"] = '/'.join(tree.xpath('//div[@class="product-description"]//text()'))

        value = tree.xpath('//div[@itemprop="offers"]/meta[@itemprop="name"]/@content')
        price = tree.xpath('//div[@itemprop="offers"]/meta[@itemprop="price"]/@content')

        if not value:
            dump["цена"] = str(price)
        else:
            dump["цена"] = dict(zip(value, price))

        stats_name = tree.xpath('//tr[@itemprop="additionalProperty"]/span[@itemprop="name"]/text()')
        stats_value = tree.xpath('//tr[@itemprop="additionalProperty"]/span[@itemprop="value"]/text()')
        dump["характеристики"] = dict(zip(stats_name, stats_value))

        return dump 
    
    raise ParseException(f"Неудачный запрос на страницу товара {url}")


def MakeProductsDump(dump: list) -> None:
    with open("results/output.json", "w", encoding="utf-8") as f:
        json.dump(dump, f, ensure_ascii=False, indent=2)

    print("Данные записаны в results/output.json")

async def main() -> None:
    pages = []
    products = []
    dump = []

    try:
        categorys = await GetLinksFromMainPage()

        # Парсинг категорий на страницы
        for category in categorys:
            try:
                [pages.append(link) for link in await GetPages(category)]
            
            except ParseException as e:
                print(f"Ошибка: {e}")

        # Парсинг страниц на товары
        for page in pages:
            try:
                [products.append(link) for link in await GetProducts(page)]

            except ParseException as e:
                print(f"Ошибка: {e}")

        # Парсинг товаров
        for product in products:
            try:
                # [dump.append(link) for link in await ParseProduct(product)]
                dump.append(await ParseProduct(product))
            except ParseException as e:
                print(f"Ошибка: {e}")

        MakeProductsDump(dump)
    except ParseException as e:
        print(f"Ошибка: {e}")
    
    gc.collect()


# async def TestParse():
#     url = "https://chudopitomets.ru/product/excel-kaltsiy/?sku=9098"
#     async with AsyncClient() as client:
#         response = await client.get(url)

#     if response.status_code == 200:
#         tree = etree.fromstring(response.text, HTMLParser())
#         print(tree.xpath('//div[@itemprop="offers"]/meta[@itemprop="name"]/@content'))





if __name__ == "__main__":


    asyncio.run(main())

    #  time.sleep(5 * 24 * 60 * 60)
