from api_client import fetch_product_by_barcode, fetch_product_by_name
from flask import Flask, jsonify, request

app = Flask(__name__)

# Mock "database" — a list of dicts. Each item MUST have an id.
inventory = [
    {
        "id": 1,
        "name": "Peanut Butter",
        "barcode": "0016000275867",
        "price": 4.99,
        "stock": 20,
        "brand": "Jif",
        "category": "Pantry"
    }
]

next_id = 2  # simple counter to hand out new ids


def find_item(item_id):
    """Helper: returns the item dict with this id, or None."""
    for item in inventory:
        if item["id"] == item_id:
            return item
    return None


@app.route("/inventory", methods=["GET"])
def get_all_items():
    return jsonify(inventory), 200


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200


@app.route("/inventory", methods=["POST"])
def add_item():
    global next_id
    data = request.get_json()

    if not data or "name" not in data:
        return jsonify({"error": "Name is required"}), 400

    new_item = {
        "id": next_id,
        "name": data.get("name"),
        "barcode": data.get("barcode", ""),
        "price": data.get("price", 0.0),
        "stock": data.get("stock", 0),
        "brand": data.get("brand", ""),
        "category": data.get("category", "")
    }
    inventory.append(new_item)
    next_id += 1
    return jsonify(new_item), 201


@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No update data provided"}), 400

    # Only update fields that were actually sent
    for key in ["name", "barcode", "price", "stock", "brand", "category"]:
        if key in data:
            item[key] = data[key]

    return jsonify(item), 200


@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    inventory.remove(item)
    return "", 204


@app.route("/inventory/lookup", methods=["GET"])
def lookup_product():
    barcode = request.args.get("barcode")
    name = request.args.get("name")

    if barcode:
        product = fetch_product_by_barcode(barcode)
    elif name:
        product = fetch_product_by_name(name)
    else:
        return jsonify({"error": "Provide a barcode or name query param"}), 400

    if product is None:
        return jsonify({"error": "Product not found"}), 404

    return jsonify(product), 200


@app.route("/inventory/import", methods=["POST"])
def import_product():
    global next_id
    barcode = request.args.get("barcode")
    name = request.args.get("name")

    if barcode:
        product = fetch_product_by_barcode(barcode)
    elif name:
        product = fetch_product_by_name(name)
    else:
        return jsonify({"error": "Provide a barcode or name query param"}), 400

    if product is None:
        return jsonify({"error": "Product not found"}), 404

    new_item = {
        "id": next_id,
        "name": product["name"],
        "barcode": product["barcode"],
        "price": 0.0,
        "stock": 0,
        "brand": product["brand"],
        "category": product["category"]
    }
    inventory.append(new_item)
    next_id += 1
    return jsonify(new_item), 201

if __name__ == "__main__":
    app.run(debug=True)
