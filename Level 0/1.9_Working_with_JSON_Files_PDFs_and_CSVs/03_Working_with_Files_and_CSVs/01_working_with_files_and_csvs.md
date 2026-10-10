# Working with Files and CSVs

## Basic file handling

Backend applications often need to read and write files.

Examples:

* save uploaded documents
* read text notes
* store simple outputs
* process CSV data

## Reading a text file

```python
with open("notes.txt", "r", encoding="utf-8") as file:
    content = file.read()
```

## Writing a text file

```python
with open("output.txt", "w", encoding="utf-8") as file:
    file.write("Hello backend world")
```

Using `with` is important because it helps close the file cleanly.

## What is a CSV?

CSV stands for comma-separated values.

It is a common format for tabular data.

Example:

```text
name,score
Alice,95
Bob,88
```

## Why CSV matters

CSV files are common in:

* datasets
* reports
* analytics exports
* batch input workflows

## Reading CSV in Python

```python
import csv

with open("students.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        print(row)
```

## Writing CSV in Python

```python
import csv

rows = [
    {"name": "Alice", "score": 95},
    {"name": "Bob", "score": 88}
]

with open("students.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["name", "score"])
    writer.writeheader()
    writer.writerows(rows)
```

## Why this matters in GenAI

GenAI systems may use CSV files for:

* evaluation data
* prompt datasets
* document metadata
* batch inference inputs

## Key takeaway

Basic file and CSV handling is part of everyday backend work, especially when systems interact with real data instead of only live API requests.
