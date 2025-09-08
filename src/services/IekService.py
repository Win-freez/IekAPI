import asyncio
import logging
from typing import Any

from httpx import AsyncClient, TimeoutException, HTTPError, Cookies
from tenacity import retry, stop_after_attempt, after_log
from src.config import settings
from src.enums.urls import IekURL

logger = logging.getLogger(__name__)


class IekAPI:
    def __init__(
            self,
            client: AsyncClient,
            max_concurrent: int = 10
    ) -> None:
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.client = client
        self.cookies = None

    @retry(
        stop=stop_after_attempt(3),
        reraise=True,
        after=after_log(logger, logging.WARNING)
    )
    async def login(self, username: str, password: str) -> Cookies:
        auth_data = {
            "username": username,
            "password": password
        }

        try:
            r = await self.client.post(
                url=IekURL.login,
                data=auth_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            r.raise_for_status()
            logger.info("Успешная авторизация, cookies сохранены")
            self.cookies = r.cookies

        except Exception as e:
            logger.error(f"Ошибка авторизации: {e}")
            raise
        else:
            return r.cookies

    @retry(
        stop=stop_after_attempt(3),
        reraise=True,
        after=after_log(logger, logging.WARNING)
    )
    async def fetch(
            self,
            url: str,
            params: dict | None = None,
            delay: float = 0
    ) -> dict[str, Any] | list[dict[str, Any]] | None:
        """Асинхронный запрос с ограничением по семафору и логированием"""
        async with self.semaphore:
            try:
                r = await self.client.get(url, params=params, timeout=15)
                r.raise_for_status()
                await asyncio.sleep(delay)
                return r.json()
            except TimeoutException:
                logger.error(f"Timeout при запросе {url}")
                raise
            except HTTPError as e:
                logger.error(f"Ошибка HTTP {e} при запросе {url}")
                raise
            except Exception as e:
                logger.exception(f"Неожиданная ошибка при запросе {url}: {e}")

    async def get_product_info(self, article: str) -> dict[str, Any] | None:
        product_data = await self.fetch(
            url=f"{IekURL.product_info}/{article}",
        )
        return product_data

    async def get_products(self, articles: list[str]) -> list[dict[str, Any] | Exception]:
        tasks = [self.get_product_info(article) for article in articles]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return [
            {"article": article, "result": result}
            for article, result in zip(articles, results)
        ]
