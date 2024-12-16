import os
from datetime import date

import pandas as pd
import numpy as np

from src.logger import logger
from src.settings import settings
from src.utils.statistcs_utils import count_weighted_median, count_weighted_mode, count_weighted_std


class DatasetManager:
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

            # What can be improved:
            # - add validation that values for quantity_sold and price_per_unit are > 0
            # - convert product_id to number
            cls._df["date"] = pd.to_datetime(cls._df["date"], format="%Y-%m-%d", errors='coerce')
            cls._df["quantity_sold"] = pd.to_numeric(cls._df["quantity_sold"], errors="coerce")
            cls._df["price_per_unit"] = pd.to_numeric(cls._df["price_per_unit"], errors="coerce")


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
        filtered_df = df[df["quantity_sold"].notna() & df["price_per_unit"].notna()]
        if filtered_df.empty:
            return {column_name: dict.fromkeys(
                ["mean", "median", "mode", "std_dev", "percentile_25", "percentile_75"],
            ) for column_name in columns}
        for column_name in columns:
            column_series = filtered_df[column_name]
            if column_name == "price_per_unit":
                weights_series = filtered_df["quantity_sold"]
                std_dev = count_weighted_std(column_series, weights_series)
                result[column_name] = {
                    "mean": float(round(np.average(column_series, weights=weights_series), 2)),
                    "median": round(count_weighted_median(column_series, weights_series), 2), # assuming that there can be unnecessary level of precision
                    "mode": round(count_weighted_mode(column_series, weights_series), 2), # assuming that there can be unnecessary level of precision
                    "std_dev": round(std_dev, 2) if std_dev is not None else std_dev,
                    "percentile_25": float(
                        round(np.percentile(column_series, 25, weights=weights_series, method="inverted_cdf").min(), 2)
                    ),
                    "percentile_75": float(
                        round(np.percentile(column_series, 75, weights=weights_series, method="inverted_cdf").min(), 2)
                    ),
                }
            else:
                std_dev = column_series.std()
                result[column_name] = {
                    "mean": float(round(column_series.mean(), 2)),
                    "median": float(round(column_series.median(), 2)), # assuming that there can be unnecessary level of precision
                    "mode": float(round(column_series.mode().min(), 2)), # assuming that there can be unnecessary level of precision
                    "std_dev": float(round(std_dev, 2)) if not np.isnan(std_dev) else None,
                    "percentile_25": float(round(np.percentile(column_series, 25), 2)),
                    "percentile_75": float(round(np.percentile(column_series, 75), 2)),
                }

        return result

    def compute_summary_statistics(self, columns: list[str], filter_conditions: dict | None) -> dict:
        if not columns:
            return dict()
        df = self._df
        if filter_conditions is not None:
            df = self._filter_dataset(filter_conditions)
        return self._compute_statistics(df, columns)

