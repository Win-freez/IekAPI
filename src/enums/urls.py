from enum import StrEnum


class IekURL(StrEnum):
    base = r"https://bp.iek.ru"
    login = rf"{base}/oauth/login"
    product_info = rf"{base}/api/catalog/v1/client/products"
