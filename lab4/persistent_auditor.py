import os

FILENAME = "inventory.txt"

# 1. Load existing orders safely from file
def load_inventory(filename=FILENAME):
    orders = []
    if not os.path.exists(filename):
        return orders

    try:
        with open(filename, "r") as file:
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split(",")
                    if len(parts) == 3:
                        order_id = int(parts[0].strip())
                        product = parts[1].strip()
                        qty = int(parts[2].strip())
                        orders.append([order_id, product, qty])
    except (FileNotFoundError, ValueError):
        pass
        
    return orders


# 2. Save consolidated orders back to orders.txt
def save_inventory(orders, filename=FILENAME):
    with open(filename, "w") as file:
        for order in orders:
            file.write(f"{order[0]},{order[1]},{order[2]}\n")
    print(f"\nOrder successfully saved to {filename}")


# 3. Print full inventory report
def display_inventory(orders):
    print("\n--- Current Inventory List ---")
    if not orders:
        print("(No inventory items stored)")
    else:
        for order in orders:
            print(f"{order[0]}, {order[1]}, {order[2]}")
    print("------------------------------\n")
def main():
    orders = load_inventory()

    # Show initial state when program starts
    print("Current Orders:\n")
    if not orders:
        print("(No existing orders found)")
    else:
        for order in orders:
            print(f"{order[0]}, {order[1]}, {order[2]}")
    print()

    # Continuous loop to accept multiple inputs
    while True:
        product_name = input("Enter Product Name (or type 'quit' to save & exit): ").strip()

        if product_name.lower() == "quit":
            break

        if not product_name:
            print("Error: Product name cannot be empty. Try again.\n")
            continue

        qty_input = input("Enter Quantity: ").strip()

        if not qty_input.isdigit():
            print("Error: Invalid quantity. Please enter a positive integer.\n")
            continue

        quantity = int(qty_input)

        # Check if product already exists for consolidation
        existing_order = None
        for order in orders:
            if order[1].lower() == product_name.lower():
                existing_order = order
                break

        if existing_order:
            existing_order[2] += quantity
            print(f"\nUpdated Existing Order: {existing_order[0]},{existing_order[1]},{existing_order[2]}")
        else:
            next_id = 1001 if not orders else max(o[0] for o in orders) + 1
            new_order = [next_id, product_name, quantity]
            orders.append(new_order)
            print(f"\nNew Order Added: {new_order[0]},{new_order[1]},{new_order[2]}")

        # Show updated total list after every valid entry
        display_inventory(orders)

    # Save data upon exiting the loop
    save_inventory(orders)
    display_inventory(orders)


if __name__ == "__main__":
    main()