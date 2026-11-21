import ast
import contextlib
import io
import os
import tempfile
import unittest
from unittest.mock import patch

from discount_strategy import (BulkDiscount, DiscountStrategy, NoDiscount, PercentageDiscount, StudentDiscount)
from DigitalProduct import DigitalProduct
from inventory import Inventory
from main import get_positive_float, load_products
from order import Order
from order_line import OrderLine
from physical_product import PhysicalProduct
from product import Product
from product_factory import ProductFactory
from supplier import Supplier

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CSV_TEXT = (
    "product_type,product_id,name,price,stock_quantity\n"
    "physical,P001,Desk Lamp,25.00,10\n"
    "digital,D001,Photo Editor,49.90,100\n"
    "service,S001,Installation,30.00,5\n"
    "physical,P002,Office Chair,abc,3\n"
    "physical,P003,Monitor Stand,39.50,7\n"
)


def make_supplier() -> Supplier:
    return Supplier("S1", "Acme", "acme@example.com")


def make_product(price: float = 50.0, stock: int = 10) -> Product:
    return ProductFactory.create("physical", "P1", "Widget", price, stock, make_supplier(), weight=1.0)


def make_order(discount=None) -> Order:
    """Order whose lines add up to 250 (5 x 50)."""
    order = Order("O1", discount)
    order.add_order_line(make_product(50.0), 5)
    return order


class TestStrategyPattern(unittest.TestCase):
    def test_default_is_no_discount(self):
        self.assertEqual(make_order().calculate_total(), 250)

    def test_percentage_discount(self):
        self.assertAlmostEqual(make_order(PercentageDiscount(10)).calculate_total(), 225)

    def test_bulk_discount_above_threshold(self):
        self.assertEqual(make_order(BulkDiscount(200, 20)).calculate_total(), 230)

    def test_bulk_discount_below_threshold(self):
        self.assertEqual(make_order(BulkDiscount(300, 20)).calculate_total(), 250)

    def test_set_discount_changes_strategy(self):
        order = make_order(BulkDiscount(200, 20))
        self.assertEqual(order.calculate_total(), 230)
        order.set_discount(PercentageDiscount(10))
        self.assertAlmostEqual(order.calculate_total(), 225)

    def test_fourth_strategy_needs_no_change_to_order(self):
        self.assertAlmostEqual(make_order(StudentDiscount()).calculate_total(), 237.5)

        class FlatTenOff(DiscountStrategy):  # brand-new strategy defined in the test
            def apply(self, total: float) -> float:
                return total - 10

        self.assertEqual(make_order(FlatTenOff()).calculate_total(), 240)

    def test_order_has_no_discount_if_elif_logic(self):
        with open(os.path.join(ROOT, "order.py")) as f:
            tree = ast.parse(f.read())
        order_class = next(n for n in ast.walk(tree)
                           if isinstance(n, ast.ClassDef) and n.name == "Order")
        method = next(n for n in order_class.body
                      if isinstance(n, ast.FunctionDef) and n.name == "calculate_total")
        ifs = [n for n in ast.walk(method) if isinstance(n, ast.If)]
        self.assertEqual(ifs, [], "calculate_total() must not contain if/elif logic")

    def test_strategies_are_discount_strategies(self):
        for s in (NoDiscount(), PercentageDiscount(5), BulkDiscount(1, 1), StudentDiscount()):
            self.assertIsInstance(s, DiscountStrategy)

    def test_invalid_percentage_rejected(self):
        with self.assertRaises(ValueError):
            PercentageDiscount(150)


class TestFactory(unittest.TestCase):
    def test_creates_physical_and_digital(self):
        sup = make_supplier()
        phys = ProductFactory.create("physical", "P1", "Lamp", 25.0, 10, sup, weight=2.0)
        dig = ProductFactory.create("digital", "D1", "App", 9.9, 5, sup, download_size=100.0)
        self.assertIsInstance(phys, PhysicalProduct)
        self.assertIsInstance(dig, DigitalProduct)
        self.assertIsInstance(phys, Product)
        self.assertIsInstance(dig, Product)

    def test_unknown_type_raises_clear_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            ProductFactory.create("service", "S1", "Install", 30.0, 5, make_supplier())
        self.assertEqual(str(ctx.exception), "Unknown product type: service")

    def test_main_does_not_create_products_directly(self):
        with open(os.path.join(ROOT, "main.py")) as f:
            tree = ast.parse(f.read())
        called = {n.func.id for n in ast.walk(tree)
                  if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        self.assertNotIn("PhysicalProduct", called)
        self.assertNotIn("DigitalProduct", called)


class TestValidation(unittest.TestCase):
    def test_price_must_be_positive(self):
        for bad in (0, -1):
            with self.assertRaises(ValueError):
                make_product(price=bad)

    def test_initial_stock_cannot_be_negative(self):
        with self.assertRaises(ValueError):
            make_product(stock=-1)

    def test_update_stock_negative_rejected_and_value_unchanged(self):
        product = make_product(stock=10)
        with self.assertRaises(ValueError):
            product.update_stock(-5)
        self.assertEqual(product.get_stock(), 10)

    def test_digital_product_cannot_skip_stock_rule(self):  # LSP
        with self.assertRaises(ValueError):
            ProductFactory.create("digital", "D1", "App", 9.9, -1, make_supplier(), download_size=1.0)

    def test_order_line_quantity_must_be_positive(self):
        for bad in (0, -3):
            with self.assertRaises(ValueError):
                OrderLine(make_product(), bad)

    def test_order_add_line_rejects_bad_quantity(self):
        with self.assertRaises(ValueError):
            Order("O2").add_order_line(make_product(), 0)


class TestUserInput(unittest.TestCase):
    def test_get_positive_float_asks_again(self):
        out = io.StringIO()
        with patch("builtins.input", side_effect=["abc", "-5", "12.50"]), \
                contextlib.redirect_stdout(out):
            value = get_positive_float("Price: ")
        self.assertEqual(value, 12.5)
        self.assertEqual(out.getvalue().splitlines(), [
            "Please enter a valid number, e.g. 12.50",
            "Please enter a number greater than zero.",
        ])

    def test_zero_is_rejected(self):
        with patch("builtins.input", side_effect=["0", "3"]), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(get_positive_float("Price: "), 3.0)


class TestLoadProducts(unittest.TestCase):
    def run_load(self, path):
        inventory = Inventory()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            load_products(path, inventory, make_supplier())
        return inventory, out.getvalue().splitlines()

    def test_missing_file_handled_gracefully(self):
        inventory, lines = self.run_load("definitely_missing.csv")
        self.assertEqual(lines, [
            "Products file not found: definitely_missing.csv",
            "Load attempt finished.",
        ])
        self.assertEqual(inventory.to_dict_list(), [])

    def test_bad_rows_skipped_and_valid_rows_loaded(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "products.csv")
            with open(path, "w", newline="") as f:
                f.write(CSV_TEXT)
            inventory, lines = self.run_load(path)

        ids = [p["id"] for p in inventory.to_dict_list()]
        self.assertEqual(ids, ["P001", "D001", "P003"])
        self.assertIn("Skipping line 4: Unknown product type: service", lines)
        self.assertTrue(any(l.startswith("Skipping line 5:") for l in lines))
        self.assertEqual(lines[-2:], ["3 products loaded.", "Load attempt finished."])

    def test_negative_price_row_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "p.csv")
            with open(path, "w", newline="") as f:
                f.write("product_type,product_id,name,price,stock_quantity\n"
                        "physical,P1,Bad,-5,1\nphysical,P2,Good,5,1\n")
            inventory, lines = self.run_load(path)
        self.assertEqual([p["id"] for p in inventory.to_dict_list()], ["P2"])
        self.assertIn("1 products loaded.", lines)


class TestInventoryFindProduct(unittest.TestCase):
    def test_find_product_returns_the_product(self):  # regression test for the Lab 8 bug
        inv = Inventory()
        product = make_product()
        inv.add_product(product)
        self.assertIs(inv.find_product("p1"), product)
        self.assertIsNone(inv.find_product("nope"))


if __name__ == "__main__":
    unittest.main()
  