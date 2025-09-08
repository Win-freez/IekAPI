from datetime import datetime
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ImageVariant(BaseModel):
    ext: str
    url: str
    width: int


class Analog(BaseModel):
    article: str
    description: str
    imageUrl: str
    imageUrls: List[str]
    imageVariants: List[ImageVariant]
    isArchived: bool
    name: str
    shortName: str
    tm: str


class DesignFeature(BaseModel):
    description: str
    imageUrl: str


class EtimFeature(BaseModel):
    id: str
    name: str
    sort: int
    unit: Optional[str] = None
    value: str


class EtimClass(BaseModel):
    id: str
    name: str


class Etim(BaseModel):
    class_: EtimClass = Field(alias="class")
    features: List[EtimFeature]


class FileItem(BaseModel):
    name: str
    nameOrig: str
    size: int
    url: str


class FileCategory(BaseModel):
    files: List[FileItem]
    name: str


class DesignFileList(BaseModel):
    name: str
    nameOrig: str
    size: int
    url: str


class DesignFileType(BaseModel):
    list: List[DesignFileList]
    type: str


class DesignFilesCategory(BaseModel):
    files: List[DesignFileType]
    name: str


class IncomingItem(BaseModel):
    amount: int
    dateBegan: Optional[datetime] = None
    dateEnd: Optional[datetime] = None
    type: str


class WarehouseData(BaseModel):
    availableAmount: int
    incoming: List[IncomingItem]
    warehouseId: str
    warehouseName: str


class LogisticParamValue(BaseModel):
    group: str
    individual: str
    transport: str


class LogisticParam(BaseModel):
    name: str
    nameOrig: str
    value: LogisticParamValue


class LogisticParamsData(BaseModel):
    singlePackage: Dict[str, Any]


class Lifespan(BaseModel):
    limit: Optional[str] = None
    units: str
    value: str


class Warranty(BaseModel):
    units: str
    value: str


class LeftPeriodRaw(BaseModel):
    lifespan: Lifespan
    warranty: Warranty


class LeftPeriodItem(BaseModel):
    name: str
    value: str


class ProductResponse(BaseModel):
    article: str
    name: str
    priceBase: float | None
    pricePersonal: float | None
    priceRoc: float | None
    priceRrc: float | None

    model_config = ConfigDict(from_attributes=True, extra="ignore")
