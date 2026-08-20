class Document:
    def __init__(self, title: str, content: str, pages: int):
        self.__title = title  # private attribute
        self.__content = content  # private attribute
        self.__pages = pages  # private attribute

    def get_title(self) -> str:
        return self.__title

    def get_content(self) -> str:
        return self.__content

    def get_pages(self) -> int:
        return self.__pages


class Printer:
    def __init__(self, printer_name: str, printer_type: str):
        self.__printer_name = printer_name  # private attribute
        self.__printer_type = printer_type  # private attribute

    def get_printer_name(self) -> str:
        return self.__printer_name

    def get_printer_type(self) -> str:
        return self.__printer_type

    def print_document(self, document: Document) -> None:
        print(f"Printing Document: {document.get_title()}")
        print(f"Content: {document.get_content()}")
        print(f"Number of Pages: {document.get_pages()}")


printer = Printer("HP LaserJet", "Laser")
doc = Document("Sample Document", "This is a sample document content.", 5)
printer.print_document(doc)