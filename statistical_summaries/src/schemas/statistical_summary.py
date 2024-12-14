from datetime import date
from enum import Enum

from pydantic import BaseModel, PositiveInt, model_validator



class NumericalColumnEnum(Enum):
    quantity_sold = "quantity_sold"
    price_per_unit = "price_per_unit"


class DateRange(BaseModel):
    start_date: date
    end_date: date

    @model_validator(mode='after')
    def check_start_date_before_end_date(self):
        if not self.start_date <= self.end_date:
            raise ValueError("start_date must not be later than end_date")
        return self

class FilterConditions(BaseModel):
    date_range: DateRange = None
    category: list[str] = None
    product_ids: list[PositiveInt] = None


class StatisticalSummaryRequest(BaseModel):
    columns: list[NumericalColumnEnum] = [NumericalColumnEnum.quantity_sold, NumericalColumnEnum.price_per_unit]
    filters: FilterConditions = None


class ColumnStatistics(BaseModel):
    mean: float | None
    median: float | None
    mode: float | None
    std_dev: float | None
    percentile_25: float | None
    percentile_75: float | None
