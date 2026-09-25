# auditor.py

inventory = 0
failed_entries = 0

while True:
    user_input = input("Enter stock quantity (or type 'quit' to exit): ").strip()
    if user_input.lower() == "quit":
        break
    if not user_input.isdigit():
        print("Error: Invalid input. Please enter a positive whole number.")
        failed_entries += 1
        continue

    quantity = int(user_input)

    if quantity < 0:
        print("Error: Negative values are not allowed.")
        failed_entries += 1
        continue

    inventory += quantity
    print(f"Current Total Inventory: {inventory} units")

    if inventory > 500:
        print("OVERSTOCK ALERT: Total inventory exceeds 500 units. Terminating audit.")
        break

print("\n--- Audit Summary ---")
print(f"Total Units Processed: {inventory}")
print(f"Number of Failed/Rejected Entries: {failed_entries}")