from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    dataset_file_name: str = "sales_data.csv"
    dataset_expected_columns: set = {
        'date', 'product_id', 'product_name', 'category', 'quantity_sold', 'price_per_unit'
    }


settings = Settings()
