from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException

from src.dependencies import get_dataset_manager
from src.settings import settings
from src.services.dataset_manager import DatasetManager
from src.services.exceptions import BaseServiceException
from src.schemas.statistical_summary import StatisticalSummaryRequest, ColumnStatistics, FilterConditions


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    DatasetManager.load_dataset(settings.dataset_file_name)
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/summary/")
def count_dataset_summary(
        input_data: StatisticalSummaryRequest,
        dataset_manager: DatasetManager = Depends(get_dataset_manager)
) -> dict[str, ColumnStatistics]:
    if not dataset_manager.dataset_available:
        raise HTTPException(status_code=503, detail="Dataset was not loaded, service unavailable")
    try:
        return dataset_manager.compute_summary_statistics(
            columns=[column_name.value for column_name in input_data.columns],
            filter_conditions=input_data.filters.model_dump() if input_data.filters else None,
        )
    except BaseServiceException as e:
        raise HTTPException(status_code=500, detail=str(e))
