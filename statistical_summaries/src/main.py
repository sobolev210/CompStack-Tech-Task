import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException

from src.dependencies import get_statistics_counter
from src.settings import settings
from src.services.statistics_counter import StatisticsCounter
from src.services.exceptions import BaseServiceException
from src.schemas.statistical_summary import StatisticalSummaryRequest, ColumnStatistics


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    StatisticsCounter.load_dataset(settings.dataset_file_name)
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/summary/")
def count_dataset_summary(
        input_data: StatisticalSummaryRequest,
        statistics_counter: StatisticsCounter = Depends(get_statistics_counter)
) -> dict[str, ColumnStatistics]:
    if not statistics_counter.dataset_available:
        raise HTTPException(status_code=503, detail="Dataset was not loaded, service unavailable")
    try:
        res= statistics_counter.compute_summary_statistics(
            columns=[column_name.value for column_name in input_data.columns],
            filter_conditions=input_data.filters.model_dump() if input_data.filters else None,
        )
        return res
    except BaseServiceException as e:
        raise HTTPException(status_code=500, detail=str(e))
