import json
import os

FILENAME = "inventory.json"

# ==========================================
# 1. Data Persistence Functions from last week
# ==========================================

def load_inventory():
    """Load inventory from inventory.json if it exists; otherwise return an empty list."""
    if os.path.exists(FILENAME):
        try:
            with open(FILENAME, "r") as file:
                print("inventory.json found.")
                data = json.load(file)
                print("Inventory loaded successfully.")
                return data
        except json.JSONDecodeError:
            print("inventory.json was empty or corrupted. Starting with an empty inventory.")
            return []
    else:
        print("inventory.json not found. Starting with an empty inventory.")
        return []


def save_inventory(inventory):
    """Save the current inventory list of dictionaries to inventory.json."""
    with open(FILENAME, "w") as file:
        json.dump(inventory, file, indent=4)
    print("Inventory saved successfully.")


# ==========================================
# 2. Data Manipulation / CRUD Functions
# ==========================================

def display_all(inventory):
    """Display all items in the inventory."""
    print("\nCurrent Inventory")
    print("-----------------------------------")
    if not inventory:
        print("No products in inventory.")
    else:
        for item in inventory:
            print(
                f"ID: {item['id']} | "
                f"Name: {item['name']} | "
                f"Price: ${item['price']:.2f} | "
                f"Stock: {item['stock']}"
            )
    print("-----------------------------------")


def add_product(inventory):
    """Add a new product dictionary to the inventory."""
    print("\nAdd New Product")
    prod_id = input("Product ID: ").strip()

    # Prevent duplicate Product IDs
    for item in inventory:
        if item["id"].lower() == prod_id.lower():
            print("Error: Product ID already exists!")
            return

    name = input("Product Name: ").strip()
    
    try:
        price = float(input("Price: "))
        stock = int(input("Stock Quantity: "))
    except ValueError:
        print("Error: Invalid price or stock quantity entered.")
        return

    # Dictionary representation for individual products
    product = {
        "id": prod_id,
        "name": name,
        "price": price,
        "stock": stock
    }

    inventory.append(product)
    print("\nProduct added successfully!")


def update_stock(inventory):
    """Update stock quantity for an existing product."""
    print("\nUpdate Stock")
    prod_id = input("Enter Product ID to update: ").strip()

    for item in inventory:
        if item["id"].lower() == prod_id.lower():
            try:
                new_stock = int(input("Enter new stock quantity: "))
                item["stock"] = new_stock
                print("Stock updated successfully!")
                return
            except ValueError:
                print("Error: Stock must be a valid integer.")
                return

    print("Product not found.")


def search_product(inventory):
    """Search for products by ID or Name."""
    print("\nSearch Product")
    query = input("Enter Product ID or Name to search: ").strip().lower()

    results = [
        item for item in inventory
        if query in item["id"].lower() or query in item["name"].lower()
    ]

    if results:
        print("\nSearch Results:")
        for item in results:
            print(
                f"ID: {item['id']} | "
                f"Name: {item['name']} | "
                f"Price: ${item['price']:.2f} | "
                f"Stock: {item['stock']}"
            )
    else:
        print("No matching product found.")


# ==========================================
# 3. Main Menu System
# ==========================================

def main():
    print("=========================================")
    print("INVENTORY MANAGEMENT SYSTEM")
    print("=========================================")

    inventory = load_inventory()

    while True:
        print("\n---------- MENU ----------")
        print("1. Display All Products")
        print("2. Add Product")
        print("3. Update Stock")
        print("4. Search Product")
        print("5. Save Inventory")
        print("6. Exit")
        print("--------------------------")

        choice = input("Enter option: ").strip()

        if choice == '1':
            display_all(inventory)
        elif choice == '2':
            add_product(inventory)
        elif choice == '3':
            update_stock(inventory)
        elif choice == '4':
            search_product(inventory)
        elif choice == '5':
            save_inventory(inventory)
        elif choice == '6':
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid option. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main()
