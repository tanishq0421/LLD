class Movie:
    def __init__(self, movie_name: str, total_seats: int, ticket_price: float, booked_seats: int = 0):
        self.movie_name = movie_name
        self.total_seats = total_seats
        self.ticket_price = ticket_price
        self.booked_seats = booked_seats

    def book_ticket(self, number_of_tickets: int) -> None:
        if number_of_tickets <= self.total_seats:
            self.booked_seats += number_of_tickets
            self.total_seats -= number_of_tickets
            total_price = number_of_tickets * self.ticket_price
            print(f"Booking Confirmed! Total price for {number_of_tickets} tickets: ${total_price:.2f}")    
        else:
            print(f"Sorry not enough seats available.")   

    def show_status(self) -> None:
        available_seats = self.total_seats - self.booked_seats
        print(f"Movie: {self.movie_name}, Total Seats: {self.total_seats}, Booked Seats: {self.booked_seats}, Available Seats: {available_seats}")

movie1 = Movie("Inception", 100, 12.5)
movie1.show_status()
movie1.book_ticket(5)
movie1.show_status()

movie1.book_ticket(96)
movie1.show_status()

movie2 = Movie("The Matrix", 50, 10.0)
movie2.show_status()
movie2.book_ticket(60)  # Attempting to book more tickets than available
movie2.show_status()