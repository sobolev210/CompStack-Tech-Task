import math

import pandas as pd
import numpy as np


def count_weighted_median(values: pd.Series, weights: pd.Series) -> float:
    # Combine the data into a DataFrame for convenience
    df = pd.DataFrame({'value': values, 'weight': weights})

    # Sort the DataFrame by values
    df = df.sort_values(by='value').reset_index(drop=True)

    # Calculate the cumulative weight
    df['cum_weight'] = df['weight'].cumsum()

    # Find the total weight
    total_weight = df['weight'].sum()

    # Find the median weight position
    median_weight = total_weight / 2

    # Identify the weighted median
    weighted_median_value = df.loc[df['cum_weight'] >= median_weight, 'value'].iloc[0]

    return weighted_median_value


def count_weighted_mode(values, weights):
    # Combine values and weights into a DataFrame
    df = pd.DataFrame({'value': values, 'weight': weights})

    # Group by value and sum weights
    weight_sums = df.groupby('value')['weight'].sum()

    # Find the maximum weight(s)
    max_weight = weight_sums.max()

    # Find the value(s) corresponding to the maximum weight
    mode_values = weight_sums[weight_sums == max_weight].index.tolist()

    return min(mode_values)


def count_weighted_std(values, weights):
    average = np.average(values, weights=weights)

    # Fast and numerically precise:
    variance = np.average((values-average)**2, weights=weights)

    return math.sqrt(variance)
