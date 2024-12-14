from src.services.statistics_counter import StatisticsCounter


# making this dependency async, so FastAPI does not run separate thread to initialize it
async def get_statistics_counter() -> StatisticsCounter:
    yield StatisticsCounter()
