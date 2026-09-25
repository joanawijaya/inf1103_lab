# PART 1 : Handles the prompt, input validation, and returns a valid integer or "quit" signal
def get_valid_input():
    user_input = input("Enter stock quantity (or type 'quit' to exit): ").strip()

    if user_input.lower() == "quit":
        return "quit"

    if not user_input.isdigit():
        print("Error: Invalid input. Please enter a positive whole number.")
        return None  

    quantity = int(user_input)

    if quantity < 0:
        print("Error: Negative values are not allowed.")
        return None  
    return quantity


# PART 2 : Calculates and returns the new total
def process_delivery(current_total, new_value):
    return current_total + new_value


# PART 3 : Calculates 10% tax for a single delivery
def calculate_tax(amount):
    return amount * 0.10


# PART 4 : Prints the final summary report
def generate_report(total_units, failed_attempts, total_tax):
    print("\n--- Audit Summary ---")
    print(f"Total Deliveries Processed: {total_units}")
    print(f"Number of Failed/Rejected Entries: {failed_attempts}")
    print(f"Total Tax Accumulated: ${total_tax:.2f}")


def main():
    inventory = 0
    failed_entries = 0
    total_tax = 0.0

    while True:
        result = get_valid_input()

        if result == "quit":
            break

        if result is None:
            failed_entries += 1
            continue

        delivery_amount = result
        inventory = process_delivery(inventory, delivery_amount)

        tax = calculate_tax(delivery_amount)
        total_tax += tax

        print(
            f"Delivery Accepted: {delivery_amount} units | Current Total: {inventory} units"
        )

       
        if inventory > 500:
            print(
                "OVERSTOCK ALERT: Total inventory exceeds 500 units. Terminating audit."
            )
            break

  
    generate_report(inventory, failed_entries, total_tax)


if __name__ == "__main__":
    main()

# self reflection
# answer : Keeping calculation separate from printing makes your code much cleaner and more flexible. 
# If your boss later wants to save tax data to a file, database, or app interface, you won't need to rewrite the math function. You just pass the returned number wherever it needs to go.
# A returned number can be used in other math calculations—like calculating total price, If a function only prints the tax, that value is stuck on the screen and lost to the rest of your code.