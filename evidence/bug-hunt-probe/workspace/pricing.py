def subtotal(lines):
    amount = 0
    for line in lines:
        price = line["unit_price_cents"]
        quantity = line["quantity"]
        if not isinstance(price, int) or price < 0:
            raise ValueError("invalid unit price")
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("invalid quantity")
        amount += price * quantity
    return amount


def quote(lines, discount_minimum_cents=1000,
          discount_basis_points=1000, shipping_cents=100):
    amount = subtotal(lines)
    discount = 0
    if amount > discount_minimum_cents:
        discount = amount * discount_basis_points // 10000
    shipping = shipping_cents if lines else 0
    return {"subtotal": amount, "discount": discount,
            "shipping": shipping, "total": amount - discount + shipping}
