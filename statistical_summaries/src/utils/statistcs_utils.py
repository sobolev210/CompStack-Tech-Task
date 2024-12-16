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
    if len(values) % 2 == 0:
        right_border = df.loc[df['cum_weight'] == median_weight, 'value']
        if right_border.empty:
            weighted_median_value = df.loc[df['cum_weight'] >= median_weight, 'value'].iloc[0]
        else:
            right_border_value = right_border.iloc[0]
            left_border_value = df.loc[df['cum_weight'] > median_weight, 'value'].iloc[0]
            weighted_median_value = (right_border_value + left_border_value) / 2
    else:
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


def count_weighted_std(values, weights) -> float | None:
    if (len(values) == 1 and len(weights) == 1 and weights.iloc[0] == 1) or len(values) == 0:
        return None
    average = np.average(values, weights=weights)

    # Fast and numerically precise:
    variance = np.average((values-average)**2, weights=weights)

    return math.sqrt(variance)
