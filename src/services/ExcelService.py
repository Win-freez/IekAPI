import logging
from contextlib import contextmanager
from typing import List, Dict, Any

from openpyxl import load_workbook
from pydantic import ValidationError

from src.schemas.product import ProductResponse
from src.services.IekService import IekAPI

logger = logging.getLogger(__name__)


class ExcelPriceService:
    PRICE_FIELDS = ["priceBase", "pricePersonal", "priceRoc", "priceRrc"]

    def __init__(self, api: IekAPI):
        self.api = api

    async def process_excel_file(
            self,
            file_path: str,
            output_path: str,
            article_column: str = "Артикул",
            header_row: int = 1,
    ) -> str:
        with self._open_sheet(file_path) as ws:
            article_col_idx = self._find_article_column(ws, article_column, header_row)
            rows_by_article = self._collect_articles(ws, article_col_idx, header_row)

            price_col_indexes = self._prepare_price_columns(ws, header_row)

            products = await self.api.get_products(list(rows_by_article.keys()))
            products_map = {p["article"]: p["result"] for p in products if isinstance(p, dict)}

            self._fill_prices(ws, rows_by_article, products_map, price_col_indexes)

            ws.parent.save(output_path)
            logger.info("Результат сохранён в %s", output_path)
        return output_path

    @staticmethod
    @contextmanager
    def _open_sheet(file_path: str):
        wb = load_workbook(filename=file_path)
        try:
            yield wb.active
        finally:
            wb.close()


    @staticmethod
    def _find_article_column(ws, article_column: str, header_row: int) -> int:
        for col in range(1, ws.max_column + 1):
            if ws.cell(row=header_row, column=col).value == article_column:
                return col
        raise ValueError(f"Колонка '{article_column}' не найдена в строке {header_row}")

    @staticmethod
    def _collect_articles(ws, article_col_idx: int, header_row: int) -> dict[str, list[int]]:
        rows: Dict[str, list[int]] = {}
        for row in range(header_row + 1, ws.max_row + 1):
            raw = ws.cell(row=row, column=article_col_idx).value
            art = str(raw).strip() if raw else ""
            rows.setdefault(art, []).append(row)
        return rows

    def _prepare_price_columns(self, ws, header_row: int) -> List[int]:
        start_col = ws.max_column + 1
        indexes = []
        for i, field in enumerate(self.PRICE_FIELDS):
            col_idx = start_col + i
            ws.cell(row=header_row, column=col_idx, value=field)
            indexes.append(col_idx)
        return indexes

    def _fill_prices(
            self,
            ws,
            rows_by_article: dict[str, list[int]],
            products: dict[str, Any | Exception],
            price_col_indexes: list[int],
    ):
        for article, rows in rows_by_article.items():
            result = products.get(article)
            product = self._validate_result(article, result)

            for row in rows:
                if product is None or isinstance(product, Exception):
                    self._write_error(ws, row, price_col_indexes)
                else:
                    self._write_product(ws, row, price_col_indexes, product)

    @staticmethod
    def _validate_result(article: str, result: Any) -> ProductResponse | None:
        if result is None or isinstance(result, Exception):
            return None
        if isinstance(result, ProductResponse):
            return result
        if isinstance(result, dict):
            try:
                return ProductResponse.model_validate(result)
            except ValidationError as e:
                logger.warning("Ошибка валидации для артикула %s: %s", article, e)
        return None

    @staticmethod
    def _safe_float(v: Any) -> float | None:
        try:
            return float(v) if v is not None else None
        except Exception:
            return None

    def _write_product(
            self, ws, row: int, price_col_indexes: list[int], product: ProductResponse
    ):
        for i, field in enumerate(self.PRICE_FIELDS):
            val = self._safe_float(getattr(product, field, None))
            ws.cell(row=row, column=price_col_indexes[i], value=val if val is not None else "НЕТ ДАННЫХ")

    @staticmethod
    def _write_error(ws, row: int, price_col_indexes: list[int]):
        for col in price_col_indexes:
            ws.cell(row=row, column=col, value="НЕТ ДАННЫХ")
