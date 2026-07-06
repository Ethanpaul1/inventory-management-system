import pytest
from unittest.mock import patch
import app as app_module
import api_client
import cli


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    # Reset inventory before each test so tests don't leak into each other
    app_module.inventory.clear()
    app_module.inventory.append({
        "id": 1, "name": "Test Item", "barcode": "123",
        "price": 5.0, "stock": 10, "brand": "TestBrand", "category": "Test"
    })
    app_module.next_id = 2
    with app_module.app.test_client() as c:
        yield c


# ============================================================
# SECTION 1: API ENDPOINT TESTS (Flask routes / CRUD)
# ============================================================

def test_get_all_items(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_get_single_item(client):
    response = client.get("/inventory/1")
    assert response.status_code == 200
    assert response.get_json()["name"] == "Test Item"


def test_get_item_not_found(client):
    response = client.get("/inventory/999")
    assert response.status_code == 404


def test_add_item(client):
    response = client.post("/inventory", json={"name": "New Item", "price": 3.0, "stock": 5})
    assert response.status_code == 201
    assert response.get_json()["name"] == "New Item"


def test_add_item_missing_name(client):
    response = client.post("/inventory", json={"price": 3.0})
    assert response.status_code == 400


def test_update_item(client):
    response = client.patch("/inventory/1", json={"stock": 50})
    assert response.status_code == 200
    assert response.get_json()["stock"] == 50


def test_update_item_not_found(client):
    response = client.patch("/inventory/999", json={"stock": 50})
    assert response.status_code == 404


def test_delete_item(client):
    response = client.delete("/inventory/1")
    assert response.status_code == 204
    assert app_module.find_item(1) is None


def test_delete_item_not_found(client):
    response = client.delete("/inventory/999")
    assert response.status_code == 404


def test_lookup_missing_query_param(client):
    response = client.get("/inventory/lookup")
    assert response.status_code == 400


@patch("app.fetch_product_by_barcode")
def test_lookup_by_barcode(mock_fetch, client):
    mock_fetch.return_value = {"name": "Mock Soup", "barcode": "111", "brand": "X", "category": "Y"}
    response = client.get("/inventory/lookup?barcode=111")
    assert response.status_code == 200
    assert response.get_json()["name"] == "Mock Soup"


@patch("app.fetch_product_by_barcode")
def test_import_product(mock_fetch, client):
    mock_fetch.return_value = {"name": "Mock Soup", "barcode": "111", "brand": "X", "category": "Y"}
    response = client.post("/inventory/import?barcode=111")
    assert response.status_code == 201
    assert response.get_json()["name"] == "Mock Soup"
    # confirm it actually landed in the inventory list
    assert len(app_module.inventory) == 2


@patch("app.fetch_product_by_name")
def test_import_product_by_name(mock_fetch, client):
    mock_fetch.return_value = {"name": "Mock Cereal", "barcode": "222", "brand": "X", "category": "Y"}
    response = client.post("/inventory/import?name=cereal")
    assert response.status_code == 201
    assert response.get_json()["barcode"] == "222"
    assert len(app_module.inventory) == 2


# ============================================================
# SECTION 2: HELPER / EXTERNAL API TESTS (api_client.py, mocked)
# ============================================================

@patch("api_client.requests.get")
def test_fetch_product_by_barcode_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "status": 1,
        "product": {"product_name": "Mock Soup", "brands": "MockBrand", "categories": "Soups"}
    }
    result = api_client.fetch_product_by_barcode("111111")
    assert result["name"] == "Mock Soup"
    assert result["barcode"] == "111111"


@patch("api_client.requests.get")
def test_fetch_product_by_barcode_not_found(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"status": 0}
    result = api_client.fetch_product_by_barcode("000000")
    assert result is None


@patch("api_client.requests.get")
def test_fetch_product_by_barcode_bad_status(mock_get):
    mock_get.return_value.status_code = 500
    result = api_client.fetch_product_by_barcode("000000")
    assert result is None


@patch("api_client.requests.get")
def test_fetch_product_by_name_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "hits": [{"product_name": "Mock Cereal", "code": "222", "brands": "X", "categories": "Y"}]
    }
    result = api_client.fetch_product_by_name("cereal")
    assert result["name"] == "Mock Cereal"


@patch("api_client.requests.get")
def test_fetch_product_by_name_no_results(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"hits": []}
    result = api_client.fetch_product_by_name("doesnotexist")
    assert result is None


# ============================================================
# SECTION 3: CLI TESTS (cli.py, mocked HTTP calls)
# ============================================================

@patch("cli.requests.get")
def test_cli_list_items(mock_get, capsys):
    mock_get.return_value.json.return_value = [
        {"id": 1, "name": "CLI Item", "price": 2.5, "stock": 4}
    ]
    cli.list_items()
    captured = capsys.readouterr()
    assert "CLI Item" in captured.out


@patch("cli.requests.get")
def test_cli_view_item_found(mock_get, capsys):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"id": 1, "name": "CLI Item"}
    cli.view_item(1)
    captured = capsys.readouterr()
    assert "CLI Item" in captured.out


@patch("cli.requests.get")
def test_cli_view_item_not_found(mock_get, capsys):
    mock_get.return_value.status_code = 404
    cli.view_item(999)
    captured = capsys.readouterr()
    assert "not found" in captured.out.lower()


@patch("cli.requests.post")
def test_cli_add_item(mock_post, capsys):
    mock_post.return_value.status_code = 201
    mock_post.return_value.json.return_value = {"id": 2, "name": "New CLI Item"}
    cli.add_item("New CLI Item", 4.0, 3)
    captured = capsys.readouterr()
    assert "Added" in captured.out


@patch("cli.requests.patch")
def test_cli_update_item(mock_patch, capsys):
    mock_patch.return_value.status_code = 200
    mock_patch.return_value.json.return_value = {"id": 1, "stock": 99}
    cli.update_item(1, stock=99)
    captured = capsys.readouterr()
    assert "Updated" in captured.out


@patch("cli.requests.delete")
def test_cli_delete_item(mock_delete, capsys):
    mock_delete.return_value.status_code = 204
    cli.delete_item(1)
    captured = capsys.readouterr()
    assert "deleted" in captured.out


@patch("cli.requests.delete")
def test_cli_delete_item_not_found(mock_delete, capsys):
    mock_delete.return_value.status_code = 404
    cli.delete_item(999)
    captured = capsys.readouterr()
    assert "not found" in captured.out.lower()


@patch("cli.requests.get")
def test_cli_find_on_api_by_name(mock_get, capsys):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"name": "Found Item"}
    cli.find_on_api("something", by="name")
    captured = capsys.readouterr()
    assert "Found Item" in captured.out


@patch("cli.requests.get")
def test_cli_find_on_api_not_found(mock_get, capsys):
    mock_get.return_value.status_code = 404
    cli.find_on_api("nothing", by="name")
    captured = capsys.readouterr()
    assert "not found" in captured.out.lower()


@patch("cli.requests.post")
def test_cli_import_from_api(mock_post, capsys):
    mock_post.return_value.status_code = 201
    mock_post.return_value.json.return_value = {"id": 2, "name": "Imported Item"}
    cli.import_from_api("0016000275867", by="barcode")
    captured = capsys.readouterr()
    assert "Imported" in captured.out


@patch("cli.requests.post")
def test_cli_import_from_api_not_found(mock_post, capsys):
    mock_post.return_value.status_code = 404
    cli.import_from_api("missing", by="name")
    captured = capsys.readouterr()
    assert "not found" in captured.out.lower()
