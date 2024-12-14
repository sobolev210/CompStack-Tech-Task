import os
from datetime import date

import pandas as pd
import numpy as np

from src.logger import logger
from src.settings import settings
from src.services.exceptions import BaseServiceException


class StatisticsCounter:
    _df: pd.DataFrame | None = None
    _instance = None

    @classmethod
    def load_dataset(cls, file_path: str):
        if cls._df is None:
            try:
                cls._df = pd.read_csv(file_path)
            except FileNotFoundError:
                logger.error(f"Could not load dataset by path '{file_path}'. Current workdir: {os.getcwd()}")
                return
            except ValueError as e:
                logger.error(f"Could not load dataset due to an error", exc_info=e)
                return
            missing_columns = settings.dataset_expected_columns.difference(set(cls._df.columns))
            if missing_columns:
                logger.error(f"Provided dataset is missing columns: {missing_columns}")
                cls._df = None
                return
            try:
                cls._df["date"] = pd.to_datetime(cls._df["date"], format="%Y-%m-%d")
            except ValueError as e:
                logger.error(f"Could not convert values in 'date' column to datetime", exc_info=e)
                cls._df = None
                return

    @property
    def dataset_available(self):
        return self._df is not None

    def __new__(cls, *args, **kwargs):
        # Singleton pattern
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _filter_dataset(self, filter_conditions: dict) -> pd.DataFrame:
        filters_to_apply = list()
        date_range = filter_conditions.get("date_range")
        if date_range is not None:
            start_date: date = date_range["start_date"]
            end_date: date = date_range["end_date"]
            filters_to_apply.append(self._df['date'] >= str(start_date))
            filters_to_apply.append(self._df['date'] <= str(end_date))

        product_ids = filter_conditions.get("product_ids")
        if product_ids is not None:
            filters_to_apply.append(self._df['product_id'].isin(product_ids))

        categories = filter_conditions.get("category")
        if categories is not None:
            filters_to_apply.append(self._df['category'].isin(categories))

        if filters_to_apply:
            combined_filter = filters_to_apply[0]
            for filter_to_apply in filters_to_apply[1:]:
                combined_filter &= filter_to_apply

            return self._df[combined_filter]
        else:
            # if we're going to modify the df in other operations, better to return cls._df.copy(deep=True)
            return self._df

    def _compute_statistics(self, df: pd.DataFrame, columns: list[str]) -> dict:
        result = dict()
        for column_name in columns:
            column_series = df[column_name]
            if column_series.empty:
                result[column_name] = dict.fromkeys(
                    ["mean", "median", "mode", "std_dev", "percentile_25", "percentile_75"],
                )
            elif (nan_count := column_series.isna().sum()) > 0:
                raise BaseServiceException(
                    f"Column '{column_name}' contains {nan_count} NaN values, can't compute statistics"
                )

            else:
                try:
                    result[column_name] = {
                        "mean": float(round(column_series.mean(), 2)),
                        "median": float(round(column_series.median(), 2)),
                        "mode": float(round(column_series.mode().min(), 2)),
                        "std_dev": float(round(column_series.std(), 2)),
                        "percentile_25": float(round(np.percentile(column_series, 25), 2)),
                        "percentile_75": float(round(np.percentile(column_series, 75), 2)),
                    }
                except TypeError as e:
                    logger.error(f"Could not count statistics, error: {e}", exc_info=e)
                    raise BaseServiceException(
                        "Could not count statistics - probably something is wrong with a dataset"
                    )

        return result


    # todo remove
    # @lru_cache(maxsize=64)
    # def perform_statistics_count(self, columns: tuple[str, ...], filter_conditions: dict | None = None) -> dict:
    #     print("Counting statistics")
    #     df = self._df
    #     if filter_conditions is not None:
    #         df = self._filter_dataset(filter_conditions)
    #     return self._compute_statistics(df, columns)
    #
    # def compute_summary_statistics(self, columns: list[str], filter_conditions: dict | None) -> dict:
    #     # Converting lists to tuples, so they can be cached by lru_cache
    #     columns = tuple(columns)
    #     if filter_conditions is not None:
    #         for key, value in filter_conditions.items():
    #             if isinstance(value, list):
    #                 filter_conditions[key] = tuple(value)
    #     # Here, I call the additional internal function, so results of it can be cached
    #     return self.perform_statistics_count(columns, filter_conditions)

    def compute_summary_statistics(self, columns: list[str], filter_conditions: dict | None) -> dict:
        df = self._df
        if filter_conditions is not None:
            df = self._filter_dataset(filter_conditions)
        return self._compute_statistics(df, columns)


if __name__ == "__main__":
    statistics_counter = StatisticsCounter()
    statistics_counter.load_dataset("../../sales_data.csv")
    df = statistics_counter._df
    df