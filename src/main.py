import asyncio
from pprint import pprint

import httpx

from src.config import settings
from src.services.IekService import IekAPI
from src.schemas.product import ProductResponse
from src.services.ExcelService import ExcelPriceCheckerOpenpyxl


async def main():
    async with httpx.AsyncClient() as client:
        api = IekAPI(client=client)
        cookies = await api.login(
            username=settings.IEK.username,
            password=settings.IEK.password)
        checker = ExcelPriceCheckerOpenpyxl(api=api)
        await checker.process_excel_file(
            file_path=r"C:\Users\tdrubin.com\Desktop\Справочник по iek.xlsx",
            output_path=r"C:\Users\tdrubin.com\Desktop\Справочник по iek.xlsx",
            article_column="Артикул",  # или "Артикул"
            header_row=1
        )


asyncio.run(main())
