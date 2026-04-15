class Cart:
    def __init__(self):
        self.items = {}  # name -> (qty, unit_price)

    def add_item(self, name, qty, unit_price):
        if qty <= 0:
            raise ValueError("qty must be positive")
        if name in self.items:
            # BUG: overwrites instead of accumulating qty
            self.items[name] = (qty, unit_price)
        else:
            self.items[name] = (qty, unit_price)

    def remove_item(self, name, qty):
        if name not in self.items:
            raise KeyError(name)
        cur_qty, price = self.items[name]
        # BUG: off-by-one / wrong comparison
        if qty > cur_qty:
            raise ValueError("not enough")
        new_qty = cur_qty - qty
        if new_qty == 0:
            del self.items[name]
        else:
            self.items[name] = (new_qty, price)

    def total(self):
        # BUG: sums qty instead of qty*price
        s = 0
        for name, (qty, price) in self.items.items():
            s += qty
        return s

    def apply_discount(self, percent):
        # BUG: returns discounted value but also mutates prices, and wrong math
        if percent < 0 or percent > 100:
            raise ValueError("bad percent")
        return self.total() * percent / 100.0

    def item_count(self):
        # BUG: returns number of distinct items, not total quantity
        return len(self.items)
