"""
Test contract for the Order Matching Engine (limit order book).

Your `solution.py` must define `OrderBook`. Side is the string "BUY" or "SELL".

    class OrderBook:
        def place_order(self, order_id: str, side: str, price: int, quantity: int) -> list:
            # Match the incoming order against the opposite side by PRICE-TIME priority:
            #   BUY  matches asks with ask_price <= price, lowest ask first;
            #   SELL matches bids with bid_price >= price, highest bid first;
            #   within a price level, oldest orders fill first (FIFO).
            # Trades execute at the RESTING (passive) order's price.
            # Support partial fills; any unfilled remainder rests in the book.
            # Return the list of trades generated, each a dict:
            #   {"buy_order": <id>, "sell_order": <id>, "price": <int>, "quantity": <int>}
            # (Trades in the order they occur.)

        def best_bid(self):
            # Highest resting bid price, or None if no bids.

        def best_ask(self):
            # Lowest resting ask price, or None if no asks.

        def open_quantity(self, order_id: str) -> int:
            # Quantity of that order still resting in the book (0 if fully filled, cancelled, or unknown).

        def cancel(self, order_id: str) -> None:
            # Remove a resting order from the book (no-op if unknown / already filled).

Prices and quantities are positive integers.
"""
