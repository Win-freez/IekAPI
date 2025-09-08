import argparse
import asyncio

import httpx

from src.config import settings
from src.logging_config import setup_logging
from src.services.ExcelService import ExcelPriceService
from src.services.IekService import IekAPI


async def main(file_path: str):
    setup_logging()

    async with httpx.AsyncClient() as client:
        api = IekAPI(client=client, max_concurrent=100)

        await api.login(
            username=settings.IEK.username,
            password=settings.IEK.password)

        checker = ExcelPriceService(api=api)

        await checker.process_excel_file(
            file_path=file_path,
            output_path=file_path,
            article_column="Артикул",
            header_row=1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Проверка цен в Excel по артикулу через API IEK"
    )
    parser.add_argument(
        "file",
        help="Путь к Excel-файлу (.xlsx), который нужно обработать"
    )
    args = parser.parse_args()

    asyncio.run(main(args.file))