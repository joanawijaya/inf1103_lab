from product import Product 
class Inventory: 
    def __init__(self):
        self.__products = []
    
    def add_product(self, product):
        for item in self.__products:
            if item.get_id().lower() == product.get_id().lower():
                return False
        self.__products.append(product)
        return True
    
    def find_product(self, product_id):
        for item in self.__products:
            if item.get_id().lower() == product_id.lower():
                return item
        return None 

    def search_product(self, query):
        results = []
        for item in self.__products:
            if query.lower() in item.get_id().lower() or query.lower() in item.get_name().lower():
                results.append(item)
        return results
    
    def display_all(self):
        print("\nCurrent Inventory")
        print("--------------------------")
        if not self.__products:
            print("No products oops!")
        else:
            for item in self.__products:
                item.display_information()
        print("--------------------------")        

    def to_dict_list(self):
        result = []
        for item in self.__products:
            result.append(item.to_dict())
        return result 
         
      
