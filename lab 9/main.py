import json
import os
import csv
from product import Product
from physical_product import PhysicalProduct
from DigitalProduct import DigitalProduct
from product_factory import ProductFactory
from inventory import Inventory
from supplier import Supplier

FILENAME = "inventory.json"
PRODUCTS_CSV = "products.csv"

def get_positive_float(prompt: str) -> float:
    """Keep asking until the user enters a number greater than zero."""
    while True:
        try:
            value = float(input(prompt))
            if value <= 0:
                print("Please enter a number greater than zero.")
                continue
            return value
        except ValueError:
            print("Please enter a valid number, e.g. 12.50") 

def get_or_create_supplier(data: dict, suppliers: dict[str, Supplier]) -> Supplier:
    """Reuse one Supplier object for every product that shares the same supplier_id."""
    supplier_id = data["supplier_id"]
    if supplier_id not in suppliers:
        suppliers[supplier_id] = Supplier(supplier_id, data["name"], data["contact_email"])
    return suppliers[supplier_id]


def create_product_from_dict(item: dict, suppliers: dict[str, Supplier]) -> Product:
    """Build a product from saved JSON data. Creation goes through the factory.
    Raises ValueError for an unknown type or invalid values."""
    supplier = get_or_create_supplier(item["supplier"], suppliers)
    return ProductFactory.create(
        item["type"], item["id"], item["name"], item["price"], item["stock"], supplier,
        weight=item.get("weight", 0.0),
        download_size=item.get("download_size", 0.0),
    )


def load_inventory() -> tuple[Inventory, dict[str, Supplier]]:
    inventory = Inventory()
    suppliers: dict[str, Supplier] = {}
    if os.path.exists(FILENAME):
        try:
            with open(FILENAME, "r") as file:
                data = json.load(file)
        except json.JSONDecodeError:
            print("inventory.json was empty or corrupted. Starting with an empty inventory.")
            return inventory, suppliers

        print("Inventory loaded successfully.")
        for item in data:
            try:
                inventory.add_product(create_product_from_dict(item, suppliers))
            except (KeyError, ValueError) as error:
                print(f"Skipping a bad inventory.json entry: {error!r}")
    else:
        print("inventory.json not found. Starting with an empty inventory.")
    return inventory, suppliers


def save_inventory(inventory):
    with open(FILENAME, "w") as file:
        json.dump(inventory.to_dict_list(), file, indent=4)
    print("Inventory saved successfully.")


def load_products(path: str, inventory: Inventory, supplier: Supplier) -> None:
    """Load products from a CSV file using the ProductFactory.

    try    -> open the file
    except -> FileNotFoundError: friendly message, no crash
    else   -> file opened: read rows; a bad row is reported and skipped
    finally-> always runs
    """
    try:
        file = open(path, newline="")
    except FileNotFoundError:
        print(f"Products file not found: {path}")
    else:
        loaded = 0
        with file:
            reader = csv.reader(file)
            next(reader, None)  
            for row in reader:
                if not row:  
                    continue
                try:
                    product_type, product_id, name, price, stock = row
                    product = ProductFactory.create(
                        product_type.strip(), product_id.strip(), name.strip(),
                        float(price), int(stock), supplier,
                    )
                    if inventory.add_product(product):
                        loaded += 1
                    else:
                        print(f"Skipping line {reader.line_num}: duplicate product ID {product_id}")
                except ValueError as error:
                    print(f"Skipping line {reader.line_num}: {error}")
        print(f"{loaded} products loaded.")
    finally:
        print("Load attempt finished.")

def choose_supplier(suppliers: dict[str, Supplier]) -> Supplier | None:
    """Pick an existing supplier by ID, or create a new one independently of any product."""
    supplier_id = input("Supplier ID: ").strip()
    if supplier_id in suppliers:
        return suppliers[supplier_id]
    name = input("New supplier name: ").strip()
    email = input("Supplier contact email: ").strip()
    if not supplier_id or not name:
        print("Supplier ID and name are required.")
        return None
    suppliers[supplier_id] = Supplier(supplier_id, name, email)
    return suppliers[supplier_id]


def add_product_menu(inventory, suppliers):
    print("\nAdd New Product")
    print("1. Physical Product")
    print("2. Digital Product")
    kind = input("Choose type (1/2): ").strip()
    if kind not in ("1", "2"):
        print("Invalid type.")
        return

    prod_id = input("Product ID: ").strip()
    name = input("Product Name: ").strip()
    supplier = choose_supplier(suppliers)
    if supplier is None:
        return

    price = get_positive_float("Price: ")  # asks again until valid
    try:
        stock = int(input("Stock Quantity: "))
        if kind == "1":
            weight = float(input("Weight (kg): "))
            product = ProductFactory.create("physical", prod_id, name, price, stock,
                                            supplier, weight=weight)
        else:
            size = float(input("Download size (MB): "))
            product = ProductFactory.create("digital", prod_id, name, price, stock,
                                            supplier, download_size=size)
    except ValueError as error:
        # Covers both bad numbers (int()/float()) and our own validation errors.
        print(f"Error: {error}")
        return

    if inventory.add_product(product):
        print("Product added successfully!")
    else:
        print("Error: Product ID already exists!")


def update_stock_menu(inventory):
    print("\nUpdate Stock")
    product_id = input("Enter Product ID to update: ").strip()

    product = inventory.find_product(product_id)
    if product is None:
        print("Product not found.")
        return

    try:
        new_stock = int(input("Enter new stock quantity: "))
        product.update_stock(new_stock)  # raises ValueError if negative
    except ValueError as error:
        print(f"Error: {error}")
        return

    print("Stock updated successfully!")


def search_menu(inventory):
    print("\nSearch Product")
    query = input("Enter Product ID or Name to search: ").strip()

    results = inventory.search_product(query)

    if results:
        print("\nSearch Results:")
        for item in results:
            item.display_information()
    else:
        print("No matching product found.")


def load_csv_menu(inventory, suppliers):
    print("\nLoad Products from CSV")
    path = input(f"File path (press Enter for {PRODUCTS_CSV}): ").strip() or PRODUCTS_CSV
    supplier = choose_supplier(suppliers)
    if supplier is None:
        return
    load_products(path, inventory, supplier)


def main():
    print("=========================================")
    print("INVENTORY MANAGEMENT SYSTEM")
    print("=========================================")

    inventory, suppliers = load_inventory()

    while True:
        print("\n---------- MENU ----------")
        print("1. Display All Products")
        print("2. Add Product")
        print("3. Update Stock")
        print("4. Search Product")
        print("5. Save Inventory")
        print("6. Load Products from CSV")
        print("7. Exit")
        print("--------------------------")

        choice = input("Enter option: ").strip()

        if choice == '1':
            inventory.display_all()
        elif choice == '2':
            add_product_menu(inventory, suppliers)
        elif choice == '3':
            update_stock_menu(inventory)
        elif choice == '4':
            search_menu(inventory)
        elif choice == '5':
            save_inventory(inventory)
        elif choice == '6':
            load_csv_menu(inventory, suppliers)
        elif choice == '7':
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid option. Please enter a number between 1 and 7.")


if __name__ == "__main__":
    main()
