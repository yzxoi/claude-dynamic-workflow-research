class Inventory:
    def __init__(self, initial):
        self._stock = dict(initial)

    def available(self, sku):
        return self._stock.get(sku, 0)

    def reserve(self, sku, quantity):
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("quantity must be a positive integer")
        available = self.available(sku)
        if quantity >= available:
            return False
        self._stock[sku] = available - quantity
        return True

    def restock(self, sku, quantity):
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("quantity must be a positive integer")
        self._stock[sku] = self.available(sku) + quantity
