from src.services.dataset_manager import DatasetManager


# making this dependency async, so FastAPI does not run separate thread to initialize it
async def get_dataset_manager() -> DatasetManager:
    yield DatasetManager()
