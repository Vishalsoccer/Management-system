"""
Library Management System
--------------------------
A console-based application to manage a library's books.
Data is persisted in a JSON file (library.json) so it survives restarts.

Features:
1. Add book
2. Issue book
3. Return book
4. Search book
5. View all books
"""

import json
import os
from datetime import date

DATA_FILE = "library.json"


class LibraryManagementSystem:
    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
        self.books = self.load_data()

    # ---------- Persistence ----------
    def load_data(self):
        """Load book data from the JSON file, or start empty if none exists."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                print("Warning: could not read existing data file. Starting fresh.")
                return {}
        return {}

    def save_data(self):
        """Save the current book dictionary to the JSON file."""
        with open(self.data_file, "w") as f:
            json.dump(self.books, f, indent=4)

    # ---------- Core Features ----------
    def add_book(self, book_id, title, author, copies=1):
        """Add a new book, or increase copies if the ID already exists."""
        book_id = str(book_id)
        copies = int(copies)

        if book_id in self.books:
            self.books[book_id]["total_copies"] += copies
            self.books[book_id]["available_copies"] += copies
            print(f"Added {copies} more copies of '{self.books[book_id]['title']}' "
                  f"(ID: {book_id}).")
        else:
            self.books[book_id] = {
                "title": title,
                "author": author,
                "total_copies": copies,
                "available_copies": copies,
                "issued_to": {},  # borrower_name -> issue_date
            }
            print(f"Book '{title}' by {author} added (ID: {book_id}, Copies: {copies}).")

        self.save_data()
        return True

    def issue_book(self, book_id, borrower):
        """Issue a copy of the book to a borrower, if available."""
        book_id = str(book_id)
        if book_id not in self.books:
            print(f"Error: Book ID '{book_id}' not found.")
            return False

        book = self.books[book_id]
        if book["available_copies"] <= 0:
            print(f"Error: No available copies of '{book['title']}' to issue.")
            return False

        book["available_copies"] -= 1
        book["issued_to"][borrower] = str(date.today())
        self.save_data()
        print(f"Book '{book['title']}' issued to {borrower}.")
        return True

    def return_book(self, book_id, borrower):
        """Return a previously issued book copy."""
        book_id = str(book_id)
        if book_id not in self.books:
            print(f"Error: Book ID '{book_id}' not found.")
            return False

        book = self.books[book_id]
        if borrower not in book["issued_to"]:
            print(f"Error: No record of '{borrower}' having borrowed '{book['title']}'.")
            return False

        del book["issued_to"][borrower]
        book["available_copies"] += 1
        self.save_data()
        print(f"Book '{book['title']}' returned by {borrower}.")
        return True

    def search_book(self, title=None, author=None, book_id=None):
        """Search by title (partial), author (partial), or exact ID."""
        results = {}

        if book_id is not None:
            book_id = str(book_id)
            if book_id in self.books:
                results[book_id] = self.books[book_id]
        else:
            for bid, info in self.books.items():
                title_match = title and title.lower() in info["title"].lower()
                author_match = author and author.lower() in info["author"].lower()
                if title_match or author_match:
                    results[bid] = info

        if results:
            print(f"\nFound {len(results)} book(s):")
            self._print_books(results)
        else:
            print("No matching book found.")

        return results

    def view_all_books(self):
        """Display all books in a formatted table."""
        if not self.books:
            print("No books found in the library.")
            return
        print(f"\nTotal Titles: {len(self.books)}")
        self._print_books(self.books)

    # ---------- Helper ----------
    @staticmethod
    def _print_books(books_dict):
        header = f"{'ID':<8}{'Title':<25}{'Author':<20}{'Available':<12}{'Total':<8}"
        print(header)
        print("-" * len(header))
        for bid, info in books_dict.items():
            print(
                f"{bid:<8}{info.get('title', ''):<25}{info.get('author', ''):<20}"
                f"{info.get('available_copies', 0):<12}{info.get('total_copies', 0):<8}"
            )
            if info.get("issued_to"):
                borrowers = ", ".join(
                    f"{name} ({d})" for name, d in info["issued_to"].items()
                )
                print(f"    Issued to: {borrowers}")
        print()


# ---------------- CLI Menu ----------------
def get_input(prompt, required=True):
    """Get input from the user; loop until non-empty if required."""
    while True:
        value = input(prompt).strip()
        if value or not required:
            return value
        print("This field is required. Please try again.")


def main_menu():
    lms = LibraryManagementSystem()

    menu = """
========== Library Management System ==========
1. Add Book
2. Issue Book
3. Return Book
4. Search Book
5. View All Books
6. Exit
=================================================
"""

    while True:
        print(menu)
        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            print("\n-- Add Book --")
            book_id = get_input("Book ID: ")
            title = get_input("Title: ")
            author = get_input("Author: ")
            copies = get_input("Number of Copies: ")
            try:
                copies = int(copies)
            except ValueError:
                print("Invalid number, defaulting to 1 copy.")
                copies = 1
            lms.add_book(book_id, title, author, copies)

        elif choice == "2":
            print("\n-- Issue Book --")
            book_id = get_input("Book ID: ")
            borrower = get_input("Borrower Name: ")
            lms.issue_book(book_id, borrower)

        elif choice == "3":
            print("\n-- Return Book --")
            book_id = get_input("Book ID: ")
            borrower = get_input("Borrower Name: ")
            lms.return_book(book_id, borrower)

        elif choice == "4":
            print("\n-- Search Book --")
            print("Search by: 1) Title   2) Author   3) Book ID")
            sub_choice = input("Choose (1/2/3): ").strip()
            if sub_choice == "1":
                title = get_input("Enter Title (or part of it): ")
                lms.search_book(title=title)
            elif sub_choice == "2":
                author = get_input("Enter Author (or part of it): ")
                lms.search_book(author=author)
            elif sub_choice == "3":
                book_id = get_input("Enter Book ID: ")
                lms.search_book(book_id=book_id)
            else:
                print("Invalid choice.")

        elif choice == "5":
            print("\n-- All Books --")
            lms.view_all_books()

        elif choice == "6":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main_menu()
