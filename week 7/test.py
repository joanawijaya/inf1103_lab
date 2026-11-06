from physical_product import PhysicalProduct
from DigitalProduct import DigitalProduct
from product import Product

p = PhysicalProduct("201", "guitar", 500.0, 5, 3.5)
d = DigitalProduct("301", "game", 60.0, 100, 4500)
p.display_information()
print(p.get_fulfilment_info(), p.calculate_shipping_cost())
d.display_information()
print(d.get_fulfilment_info())
Product("1", "x", 1.0, 1)   # should crash: abstract class