"""
Student Management System
--------------------------
A simple console-based CRUD application to manage student records.
Data is persisted in a JSON file (students.json) so it survives restarts.

Features:
1. Add student
2. Delete student
3. Search student
4. Update student
5. Display all students
"""

import json
import os

DATA_FILE = "students.json"


class StudentManagementSystem:
    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
        self.students = self.load_data()

    # ---------- Persistence ----------
    def load_data(self):
        """Load student data from the JSON file, or start empty if none exists."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                print("Warning: could not read existing data file. Starting fresh.")
                return {}
        return {}

    def save_data(self):
        """Save the current student dictionary to the JSON file."""
        with open(self.data_file, "w") as f:
            json.dump(self.students, f, indent=4)

    # ---------- Core Features ----------
    def add_student(self, student_id, name, age, grade, email=""):
        """Add a new student. student_id must be unique."""
        student_id = str(student_id)
        if student_id in self.students:
            print(f"Error: Student ID '{student_id}' already exists.")
            return False

        self.students[student_id] = {
            "name": name,
            "age": age,
            "grade": grade,
            "email": email,
        }
        self.save_data()
        print(f"Student '{name}' (ID: {student_id}) added successfully.")
        return True

    def delete_student(self, student_id):
        """Delete a student by ID."""
        student_id = str(student_id)
        if student_id not in self.students:
            print(f"Error: Student ID '{student_id}' not found.")
            return False

        removed = self.students.pop(student_id)
        self.save_data()
        print(f"Student '{removed['name']}' (ID: {student_id}) deleted successfully.")
        return True

    def search_student(self, student_id=None, name=None):
        """Search by ID (exact) or by name (partial, case-insensitive)."""
        results = {}

        if student_id is not None:
            student_id = str(student_id)
            if student_id in self.students:
                results[student_id] = self.students[student_id]

        elif name is not None:
            name_lower = name.lower()
            results = {
                sid: info
                for sid, info in self.students.items()
                if name_lower in info["name"].lower()
            }

        if results:
            print(f"\nFound {len(results)} student(s):")
            self._print_students(results)
        else:
            print("No matching student found.")

        return results

    def update_student(self, student_id, **fields):
        """Update one or more fields (name, age, grade, email) for a student."""
        student_id = str(student_id)
        if student_id not in self.students:
            print(f"Error: Student ID '{student_id}' not found.")
            return False

        valid_fields = {"name", "age", "grade", "email"}
        updated_any = False

        for key, value in fields.items():
            if key in valid_fields and value not in (None, ""):
                self.students[student_id][key] = value
                updated_any = True

        if updated_any:
            self.save_data()
            print(f"Student ID '{student_id}' updated successfully.")
        else:
            print("No valid fields provided to update.")

        return updated_any

    def display_all_students(self):
        """Display all students in a formatted table."""
        if not self.students:
            print("No students found in the system.")
            return
        print(f"\nTotal Students: {len(self.students)}")
        self._print_students(self.students)

    # ---------- Helper ----------
    @staticmethod
    def _print_students(students_dict):
        header = f"{'ID':<8}{'Name':<20}{'Age':<6}{'Grade':<10}{'Email':<25}"
        print(header)
        print("-" * len(header))
        for sid, info in students_dict.items():
            print(
                f"{sid:<8}{info.get('name', ''):<20}{str(info.get('age', '')):<6}"
                f"{info.get('grade', ''):<10}{info.get('email', ''):<25}"
            )
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
    sms = StudentManagementSystem()

    menu = """
========== Student Management System ===============
1. Add Student
2. Delete Student
3. Search Student
4. Update Student
5. Display All Students
6. Exit 
====================================================
"""

    while True:
        print(menu)
        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            print("\n-- Add Student --")
            student_id = get_input("Student ID: ")
            name = get_input("Name: ")
            age = get_input("Age: ")
            grade = get_input("Grade/Class: ")
            email = get_input("Email (optional): ", required=False)
            sms.add_student(student_id, name, age, grade, email)

        elif choice == "2":
            print("\n-- Delete Student --")
            student_id = get_input("Student ID to delete: ")
            sms.delete_student(student_id)

        elif choice == "3":
            print("\n-- Search Student --")
            print("Search by: 1) ID   2) Name")
            sub_choice = input("Choose (1/2): ").strip()
            if sub_choice == "1":
                student_id = get_input("Enter Student ID: ")
                sms.search_student(student_id=student_id)
            elif sub_choice == "2":
                name = get_input("Enter Name (or part of it): ")
                sms.search_student(name=name)
            else:
                print("Invalid choice.")

        elif choice == "4":
            print("\n-- Update Student --")
            student_id = get_input("Student ID to update: ")
            if str(student_id) not in sms.students:
                print(f"Error: Student ID '{student_id}' not found.")
                continue
            print("Leave a field blank to keep it unchanged.")
            name = get_input("New Name: ", required=False)
            age = get_input("New Age: ", required=False)
            grade = get_input("New Grade/Class: ", required=False)
            email = get_input("New Email: ", required=False)
            sms.update_student(student_id, name=name, age=age, grade=grade, email=email)

        elif choice == "5":
            print("\n-- All Students --")
            sms.display_all_students()

        elif choice == "6":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main_menu()
