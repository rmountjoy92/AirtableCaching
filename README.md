# Airtable Caching
![PyPI](https://img.shields.io/pypi/v/airtable_caching)
![PyPI - Downloads](https://img.shields.io/pypi/dm/airtable_caching)
![PyPI - License](https://img.shields.io/pypi/l/airtable_caching)

Utility for caching api responses from the airtable-python-wrapper and provides an ORM style interface for querying cached records.

>Dummy api key and base keys provided below for testing. Please do not modify anything using this key, or I will have to take this option away.

## Installation
```bash
pip install airtable-caching
```

## Step 1 - Import classes
```python
from airtable_caching import Base, Table
```

## Step 2 - cache a table
```python
base = Base(base_id="appjMwyFviPaM9I0L", api_key="keyqhxncgPbSySJQN")
base.cache_table("Table 1")
```

## Step 3 - Access cached data
```python
table = Table(base_id="appjMwyFviPaM9I0L", table_name="Table 1")

# get single record by it's airtable record ID
table.get('rec4trz5QrB6aWJBw')

# get all records in the table
table.query().all()

# get all records and resolve linked fields
table.query(resolve_fields={"Table 2": "Link to Table 2"}).all()

# get the first record in table
table.query().first()

# get the last record in table
table.query().last()

# filtering records in the query
table.query().filter_by({"Name": "Data entry 1 from Table 1 from Base 1"}).all()

# ordering records in the query
table.query().order_by("Number").all()

# ordering records in the query (descending)
table.query().order_by("Number", desc=True).all()
```

## Defining a custom cache folder location
By default this stores all cached data as .json files in airtable_caching/json. You can optionally pass a custom folder location to the Base and Table classes.
```python
import os
custom_json_folder = os.path.join(os.path.dirname(__file__), "custom_json")
base = Base(
    base_id="appjMwyFviPaM9I0L",
    api_key="keyqhxncgPbSySJQN",
    json_folder=custom_json_folder,
)
table = Table(
    base_id="appjMwyFviPaM9I0L",
    table_name="Table 1",
    json_folder=self.custom_json_folder,
)
```

## Changelog
### 0.0.4
#### Updated
- README and docstrings

### 0.0.3
#### Changed
- (BREAKING) Base and Table classes no longer use base name, now they use base id (see docs)
- added option for supplying custom cache location

#### Added
- Documentation
- Tests
    
### 0.0.1 - 0.0.2
- Initial release

