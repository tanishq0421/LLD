"""
Test contract for the Inventory Management system.

Your `solution.py` must define `Inventory` and an `InventoryError` exception.

    class Inventory:
        def add_product(self, sku: str, quantity: int) -> None:
            # Register a product with initial on-hand stock.

        def restock(self, sku: str, qty: int) -> None:
            # Increase on-hand stock. Raise InventoryError if the sku is unknown.

        def available(self, sku: str) -> int:
            # on_hand - reserved. Raise InventoryError if the sku is unknown.

        def reserve(self, sku: str, qty: int) -> str:
            # Hold `qty` (increase reserved). Return a unique reservation_id.
            # Raise InventoryError if unknown sku or available < qty.
            # MUST be safe under concurrency: total reservations never exceed available stock.

        def confirm(self, reservation_id: str) -> None:
            # Commit the reservation: reduce on_hand by the reserved qty; the reservation is done.
            # Raise InventoryError if unknown or already confirmed/released.

        def release(self, reservation_id: str) -> None:
            # Cancel the reservation: return the qty to available; the reservation is done.
            # Raise InventoryError if unknown or already confirmed/released.
"""
