import sys

import requests

BASE_URL = "http://127.0.0.1:5000/inventory"


def list_items():
    response = requests.get(BASE_URL)
    for item in response.json():
        print(f"[{item['id']}] {item['name']} - ${item['price']} (stock: {item['stock']})")


def view_item(item_id):
    response = requests.get(f"{BASE_URL}/{item_id}")
    if response.status_code == 404:
        print("Item not found.")
        return
    print(response.json())


def add_item(name, price, stock, barcode="", brand="", category=""):
    payload = {
        "name": name,
        "price": price,
        "stock": stock,
        "barcode": barcode,
        "brand": brand,
        "category": category
    }
    response = requests.post(BASE_URL, json=payload)
    if response.status_code == 201:
        print("Added:", response.json())
    else:
        print("Error:", response.json())


def update_item(item_id, **kwargs):
    response = requests.patch(f"{BASE_URL}/{item_id}", json=kwargs)
    if response.status_code == 404:
        print("Item not found.")
        return
    print("Updated:", response.json())


def delete_item(item_id):
    response = requests.delete(f"{BASE_URL}/{item_id}")
    if response.status_code == 404:
        print("Item not found.")
    else:
        print(f"Item {item_id} deleted.")


def find_on_api(query, by="name"):
    if by == "barcode":
        response = requests.get(f"{BASE_URL}/lookup", params={"barcode": query})
    else:
        response = requests.get(f"{BASE_URL}/lookup", params={"name": query})

    if response.status_code == 404:
        print("Not found on external API.")
        return
    print(response.json())


def import_from_api(query, by="name"):
    if by == "barcode":
        response = requests.post(f"{BASE_URL}/import", params={"barcode": query})
    else:
        response = requests.post(f"{BASE_URL}/import", params={"name": query})

    if response.status_code == 201:
        print("Imported:", response.json())
    elif response.status_code == 404:
        print("Not found on external API.")
    else:
        print("Error:", response.json())


def print_help():
    print("""
Commands:
  list                          - view all items
  view <id>                     - view one item
  add <name> <price> <stock>    - add a new item
  update <id> <field>=<value>   - update item field(s)
  delete <id>                   - delete an item
  find <barcode|name> <query>   - search external API
  import <barcode|name> <query> - import external API product
""")


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        print_help()
        sys.exit(0)

    command = args[0]

    try:
        if command == "list":
            list_items()
        elif command == "view":
            view_item(int(args[1]))
        elif command == "add":
            add_item(args[1], float(args[2]), int(args[3]))
        elif command == "update":
            item_id = int(args[1])
            updates = {}
            for pair in args[2:]:
                key, value = pair.split("=")
                updates[key] = value
            update_item(item_id, **updates)
        elif command == "delete":
            delete_item(int(args[1]))
        elif command == "find":
            find_on_api(args[2], by=args[1])
        elif command == "import":
            import_from_api(args[2], by=args[1])
        else:
            print("Unknown command.")
            print_help()
    except (IndexError, ValueError) as e:
        print(f"Invalid input: {e}")
        print_help()
