# Inventory Management System

This is a small Flask REST API for keeping track of inventory items. It stores data in a Python list, so it is meant for the lab project and testing, not for production use.

The project also has a simple command line tool and an OpenFoodFacts lookup/import feature.

## What It Does

- Lists inventory items.
- Adds new items.
- Updates item details with `PATCH`.
- Deletes items.
- Looks up products from OpenFoodFacts by barcode or name.
- Imports a product from OpenFoodFacts into the inventory list.
- Includes tests for the API routes, external API helper functions, and CLI functions.

## Setup

Clone the project and move into the folder:

```bash
git clone https://github.com/Ethanpaul1/inventory-management-system.git
cd inventory-management-system
```

Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

On macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the requirements:

```bash
pip install -r requirements.txt
```

Run the Flask app:

```bash
python app.py
```

The API runs at:

```text
http://127.0.0.1:5000
```

Run the tests:

```bash
pytest
```

## API Endpoints

| Method | Endpoint | What it does |
| --- | --- | --- |
| `GET` | `/inventory` | Gets all inventory items. |
| `GET` | `/inventory/<item_id>` | Gets one item by ID. |
| `POST` | `/inventory` | Adds a new item. |
| `PATCH` | `/inventory/<item_id>` | Updates part of an item. |
| `DELETE` | `/inventory/<item_id>` | Deletes an item. |
| `GET` | `/inventory/lookup?barcode=<barcode>` | Looks up an OpenFoodFacts product by barcode. |
| `GET` | `/inventory/lookup?name=<name>` | Looks up an OpenFoodFacts product by name. |
| `POST` | `/inventory/import?barcode=<barcode>` | Imports an OpenFoodFacts product by barcode. |
| `POST` | `/inventory/import?name=<name>` | Imports an OpenFoodFacts product by name. |

## How The Project Works

The main file is `app.py`. It creates the Flask app, stores the inventory list, and defines the routes. Each route handles one job:

- `GET` routes read data.
- `POST /inventory` adds a new item from JSON.
- `PATCH /inventory/<item_id>` changes only the fields that are sent.
- `DELETE /inventory/<item_id>` removes an item from the list.
- `/inventory/lookup` searches OpenFoodFacts but does not save the result.
- `/inventory/import` searches OpenFoodFacts and then saves the result in the inventory list.

The `api_client.py` file keeps the OpenFoodFacts code separate from the Flask routes. That makes the routes easier to read, and it also makes the external API easier to test with mocks.

The `cli.py` file is a small command line client. It does not store data by itself. It sends HTTP requests to the Flask API, so the Flask app needs to be running before the CLI commands are used.

The tests in `tests/test_app.py` use Flask's test client for the routes and `unittest.mock.patch` for external requests. This means the tests do not depend on the real OpenFoodFacts website being online.

## Example API Requests

Add an item:

```bash
curl -X POST http://127.0.0.1:5000/inventory ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Rice\",\"price\":3.99,\"stock\":12,\"brand\":\"Store Brand\",\"category\":\"Pantry\"}"
```

Update an item:

```bash
curl -X PATCH http://127.0.0.1:5000/inventory/1 ^
  -H "Content-Type: application/json" ^
  -d "{\"stock\":25}"
```

Import a product by barcode:

```bash
curl -X POST "http://127.0.0.1:5000/inventory/import?barcode=0016000275867"
```

## CLI Examples

Start the Flask app first, then run these from another terminal:

```bash
python cli.py list
python cli.py view 1
python cli.py add "Rice" 3.99 12
python cli.py update 1 stock=25 price=4.49
python cli.py delete 1
python cli.py find barcode 0016000275867
python cli.py find name "peanut butter"
python cli.py import barcode 0016000275867
python cli.py import name "peanut butter"
```

## Project Files

```text
app.py              Flask routes and inventory list
api_client.py       OpenFoodFacts helper functions
cli.py              Command line commands
tests/test_app.py   Tests for the app, API helpers, and CLI
requirements.txt    Project dependencies
README.md           Project instructions
```

## Git Workflow

For new changes, I used feature branches, opened pull requests into `main`, merged them, and deleted the feature branches after merging.

Example workflow:

```bash
git switch -c feature/readme-docs
git add README.md
git commit -m "Add README documentation"
git push -u origin feature/readme-docs
```

Then the branch can be opened as a pull request on GitHub and merged into `main`.
