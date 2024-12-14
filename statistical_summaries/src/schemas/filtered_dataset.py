import datetime

from pydantic import BaseModel


class FilteredDatasetEntry(BaseModel):
    date: datetime.date
    product_id: int
    product_name: str
    category: str
    quantity_sold: int
    price_per_unit: float
