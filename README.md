# Inventory Management System

A Python Flask REST API for managing inventory items. The project includes CRUD endpoints, helper routes for OpenFoodFacts product lookup/import, a command-line interface, and a pytest suite covering the API, external API helpers, and CLI behavior.

## Features

- Flask routes for inventory CRUD operations.
- External API integration with OpenFoodFacts.
- CLI commands for listing, viewing, creating, updating, deleting, searching, and importing products.
- Mocked pytest coverage for the Flask app, API client, and CLI.
- Git-ready structure with Python cache files, virtual environments, and local environment files ignored.

## Installation and Setup

1. Clone the repository:

   ```bash
   git clone <your-github-repo-url>
   cd inventory-management-system
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   On macOS/Linux:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the Flask API:

   ```bash
   python app.py
   ```

   The API runs at `http://127.0.0.1:5000`.

5. Run the test suite:

   ```bash
   pytest
   ```

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/inventory` | List all inventory items. |
| `GET` | `/inventory/<item_id>` | Get one item by ID. |
| `POST` | `/inventory` | Create a new inventory item. |
| `PATCH` | `/inventory/<item_id>` | Update selected fields for an item. |
| `DELETE` | `/inventory/<item_id>` | Delete an item. |
| `GET` | `/inventory/lookup?barcode=<barcode>` | Search OpenFoodFacts by barcode. |
| `GET` | `/inventory/lookup?name=<name>` | Search OpenFoodFacts by product name. |
| `POST` | `/inventory/import?barcode=<barcode>` | Import a product from OpenFoodFacts by barcode. |
| `POST` | `/inventory/import?name=<name>` | Import a product from OpenFoodFacts by name. |

### Create Item Example

```bash
curl -X POST http://127.0.0.1:5000/inventory ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Rice\",\"price\":3.99,\"stock\":12,\"brand\":\"Store Brand\",\"category\":\"Pantry\"}"
```

### Update Item Example

```bash
curl -X PATCH http://127.0.0.1:5000/inventory/1 ^
  -H "Content-Type: application/json" ^
  -d "{\"stock\":25}"
```

## CLI Usage

Start the Flask server in one terminal before running CLI commands in another terminal.

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

## Project Structure

```text
inventory-management-system/
  app.py              # Flask routes and in-memory inventory data
  api_client.py       # OpenFoodFacts integration helpers
  cli.py              # Command-line interface for the API
  tests/test_app.py   # API, external API helper, and CLI tests
  requirements.txt    # Python dependencies
  README.md           # Project documentation
```

## Git Workflow Evidence

For the Git Management rubric, use a feature branch for new work, open a pull request on GitHub, merge it into `main`, and delete the branch after merge.

Recommended workflow for this README/docs feature:

```bash
git switch -c feature/readme-docs
git add README.md cli.py api_client.py tests/test_app.py .gitignore
git commit -m "Add README documentation and CLI import command"
git push -u origin feature/readme-docs
```

Then open a pull request from `feature/readme-docs` into `main`, merge it, and delete the feature branch on GitHub.

## Maintainability Notes

- Route functions keep validation close to the endpoint that needs it.
- `api_client.py` normalizes OpenFoodFacts responses so the Flask routes do not depend on the external API's full response shape.
- Tests mock external HTTP calls, keeping the suite fast and reliable.
