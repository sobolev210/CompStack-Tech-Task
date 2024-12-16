# Statistical summaries app

This repository contains results of performing Interview Task for 
"Python Application Engineer" position

## Assumptions made
- Each row in a dataset contains data for one sale
- The dataset is relatively small, and can fit into RAM. There is no huge increase in amount of data 
expected within 1-2 years. For a bigger dataset, chunk-based approach can be used, or saving dataset to DB can be considered
- The RPS limit is relatively small, e.g. 10 RPS/second. For bigger RPS, gunicorn with Uvicorn workers can be considered


## How to run


### Without Docker
1. Install the dependencies

```
cd statistical_summaries
pip install -r requirements.txt
```

2. Add your dataset file to "_statistical_summaries_" folder

You can name your file _sales_data.csv_ and just put it to the mentioned folder.
Alternatively, if your file is named differently, you can change `dataset_file_name` in 
_src/settings.py_ module, or set your dataset file name via env variables
(e.g. on Ubuntu `export dataset_file_name="my_file_name.csv"`)

3. Run the application

```
uvicorn src.main:app
```

### With Docker

1. Build docker image
```
cd statistical_summaries
docker build -t statistical_summaries .
```

2. Add your dataset file to "_statistical_summaries_" folder


3. Run the application

Here, you would need to mount your dataset file, so it's available
inside docker container - it can be done with `-v` flag.
Full command example:
```
docker run -p 8000:8000 -v ./sales_data.csv:/app/sales_data.csv statistical_summaries
```
Here, in value for `-v` flag, part before ":" is path to the dataset on the local machine. 
You can leave part on the right unchanged


## Reasoning behind counting statistics summary with current approach

For _price_per_unit_, I decided to count statistics taking into account _quantity_sold_, i.e. counting weighted mean, 
median, etc. with _quantity_sold_ values being the weights. 
This statistics seems to be more valuable, comparing to approach with not taking _quantity_sold_ into account - business can get the average price of sold units and understand if people buy expensive units or not.

For _quantity_sold_, I decided to count statistics, e.g. mean, per sale. This way, e.g., we know the average price of unit sold,
we know the average quantity sold, and we can predict our revenue based on predicted amount of sales


## Examples of requests and responses

_Columns provided, no filters provided_

Request
```json
{
  "columns": [
    "quantity_sold",
    "price_per_unit"
  ]
}
```

Response
```json
{
  "quantity_sold": {
    "mean": 25.81,
    "median": 25,
    "mode": 19,
    "std_dev": 14.08,
    "percentile_25": 14,
    "percentile_75": 38.25
  },
  "price_per_unit": {
    "mean": 66.8,
    "median": 39.99,
    "mode": 49.99,
    "std_dev": 65.57,
    "percentile_25": 25.99,
    "percentile_75": 89.99
  }
}
```

_Filtering by dates and categories_

Request
```json
{
  "columns": [
    "quantity_sold",
    "price_per_unit"
  ],
  "filters": {
    "date_range": {
      "start_date": "2023-03-17",
      "end_date": "2023-04-03"
    },
    "category": [
      "Health & Beauty", "Stationery", "Accessories"
    ]
  }
}
```



Response
```json
{
  "quantity_sold": {
    "mean": 24.76,
    "median": 25,
    "mode": 2,
    "std_dev": 14.97,
    "percentile_25": 10,
    "percentile_75": 38
  },
  "price_per_unit": {
    "mean": 30.49,
    "median": 34.99,
    "mode": 49.99,
    "std_dev": 18.01,
    "percentile_25": 12.99,
    "percentile_75": 49.99
  }
}
```

_Filtering, no rows match to given criteria_

Request
```json
{
  "columns": [
    "quantity_sold"
  ],
  "filters": {
    "date_range": {
      "start_date": "2023-03-17",
      "end_date": "2023-04-03"
    },
    "category": [
      "Health & Beauty", "Stationery", "Accessories"
    ],
    "product_ids": [1020]

  }
}
```

Response
```json
{
  "quantity_sold": {
    "mean": null,
    "median": null,
    "mode": null,
    "std_dev": null,
    "percentile_25": null,
    "percentile_75": null
  }
}
```