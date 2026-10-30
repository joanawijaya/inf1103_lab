import json
import os
from product import Product
from inventory import Inventory 

FILENAME = "inventory.json"

def load_inventory(): 
    inventory = Inventory()
    if os.path.exists(FILENAME):
        try:
            with open(FILENAME, "r") as file:
                data = json.load(file)
            print("Inventory loaded successfully.")
            for item in data:
                product = Product(item["id"], item["name"], item["price"], item["stock"])
                inventory.add_product(product)
        except json.JSONDecodeError:
            print("inventory.json was empty or corrupted. Starting with an empty inventory.")
    else:
                print("inventory.json not found. Starting with an empty inventory.")
    return inventory  

def save_inventory(inventory): 
     with open(FILENAME, "w") as file:
         json.dump(inventory.to_dict_list(), file, indent=4)
     print("Inventory saved successfully.")

def add_product_menu(inventory):
    print("\nAdd New Product")
    prod_id = input("Product ID: ").strip()
    name = input("Product Name: ").strip()

    try:
        price = float(input("Price: "))
        stock = int(input("Stock Quantity: "))
    except ValueError:
        print("Error: Invalid price or stock quantity entered.")
        return

    product = Product(prod_id, name, price, stock)
    inventory.add_product(product)

def update_stock_menu(inventory):
    print("\nUpdate Stock")
    product_id = input("Enter Product ID to update: ").strip()

    product = inventory.find_product(product_id)
    if product is None:
        print("Product not found.")
        return

    try:
        new_stock = int(input("Enter new stock quantity: "))
    except ValueError:
        print("Error: Stock must be a valid integer.")
        return
    product.update_stock(new_stock)
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
            inventory.display_all()
        elif choice == '2':
            add_product_menu(inventory)
        elif choice == '3':
            update_stock_menu(inventory)
        elif choice == '4':
            search_menu(inventory)
        elif choice == '5':
            save_inventory(inventory)
        elif choice == '6':
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid option. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main()