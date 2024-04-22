from typing import List
from collections import UserDict
from datetime import datetime, timedelta
from tabulate import tabulate
import pickle

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return "Name not found"
        except IndexError:
            return "Not found"
        except Exception as e:
            return f"Error : {e}"

    return inner 

class Field:
    def __init__(self, value: str):
        if not value:
            raise ValueError("Field cannot be empty.")
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value: str):
        if not value.strip():
            raise ValueError("Name cannot be empty.")
        super().__init__(value)

class Phone(Field):
    def __init__(self, value: str):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Invalid phone number. Please provide a 10-digit phone number.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value: str):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Please use DD.MM.YYYY.")
        super().__init__(value)

class Record:
    def __init__(self, name: Name):
        self.name = Name(name)
        self.phones: List[Phone] = []
        self.birthday: Birthday = None
    
    @input_error
    def add_phone(self, phone_number: str):
        if any(phone.value == phone_number for phone in self.phones):
            raise ValueError("This phone number already exists for this contact.")
        self.phones.append(Phone(phone_number))


    @input_error
    def add_birthday(self, birthday: str):
        try:
            datetime.strptime(birthday, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Please use DD.MM.YYYY.")
        self.birthday = Birthday(birthday)

    def remove_phone(self, phone_number: str):
        self.phones = [phone for phone in self.phones if phone.value != phone_number]

    def edit_phone(self, old_phone_number: str, new_phone_number: str):
        if not new_phone_number.isdigit() or len(new_phone_number) != 10:
            raise ValueError("Invalid phone number. Please provide a 10-digit phone number.")
        for phone in self.phones:
            if phone.value == old_phone_number:
                phone.value = new_phone_number
                break
        else:
            raise ValueError("Phone number not found.")

    def find_phone(self, phone_number: str) -> Phone:
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None
    
    def show_birthday(self):
        if self.birthday:
            return f"{self.name.value}'s birthday is on {self.birthday.value}"
        else:
            return f"No birthday found for {self.name.value}"

    def __str__(self):
        phone_numbers = '; '.join(phone.value for phone in self.phones)
        return f"Contact name: {self.name.value}, phones: {phone_numbers}, birthday: {self.birthday}"

class AddressBook(UserDict):
    
    def save_data(book, filename="addressbook.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(book, f)

    def load_data(filename="addressbook.pkl"):
        try:
            with open(filename, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

    
    @input_error
    def add_record(self, record: Record):
            self.data[record.name.value] = record
            
    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                bdate = datetime.strptime(record.birthday.value, "%d.%m.%Y").date().replace(year=today.year)
                if 0 <= (bdate - today).days < 7:
                    if bdate.weekday() in [5]:
                        days_until_monday = (7 - bdate.weekday()) % 7
                        bdate += timedelta(days=days_until_monday)
                    elif bdate.weekday() == 6:
                        days_until_monday = 1
                        bdate += timedelta(days=days_until_monday)
                    formatted_birthday = bdate.strftime("%d %B")
                    upcoming_birthdays.append(f"{record.name.value} {formatted_birthday}")

        return upcoming_birthdays


    def find(self, name: str) -> Record:
        if name in self.data:
            return self.data.get(name)
        else:
            return None
        
    def show_all_contacts(self):
        headers = ["Name", "Phone Numbers", "Birthday"]
        data = []
        for record in self.data.values():
            phones = '; '.join(phone.value for phone in record.phones)
            birthday = record.birthday.value if record.birthday else ""
            data.append([record.name.value, phones, birthday])
        return tabulate(data, headers=headers, tablefmt="grid")

    def delete(self, name: str):
        if name in self.data:
            del self.data[name]
            return f"Contact '{name}' deleted."
        else:
            return f"Contact '{name}' not found."

@input_error
def main():
    book = AddressBook.load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ").split()
        command, args = user_input[0], user_input[1:]

        if command in ["close", "exit"]:
            print("Good bye!")
            AddressBook.save_data(book)
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            if len(args) != 2:
                print("Invalid format. Please use: add [name] [phone]")
            else:
                name, phone = args
                if not phone.isdigit() or len(phone) != 10:
                    print("Invalid phone number. Please provide a 10-digit phone number.")
                else:
                    try:
                        record = book.find(name)
                        if not record:
                            record = Record(name)
                            book.add_record(record)
                            record.add_phone(phone)
                            print("Contact added.")
                        else:
                            print("Contact with this name already exists.")
                    except ValueError as e:
                        print(e)

            
        elif command == "change":
            if len(args) != 3:
                print("Invalid format. Please use: change [name] [old phone] [new phone]")
            else:
                name, old_phone, new_phone = args
                record = book.find(name)
                if record:
                    try:
                        record.edit_phone(old_phone, new_phone)
                        print("Phone number updated.")
                    except ValueError as e:
                        print(e)
                else:
                    print("Contact not found.")

        elif command == "phone":
            if len(args) != 1:
                print("Invalid format. Please use: phone [name]")
            else:
                name = args[0]
                record = book.find(name)
                if record:
                    print(record)
                else:
                    print("Contact not found.")

        elif command == "add-birthday":
            if len(args) != 2:
                print("Invalid format. Please use: add-birthday [name] [birthday (DD.MM.YYYY)]")
            else:
                name, birthday = args
                record = book.find(name)
                if record:
                    try:
                        record.add_birthday(birthday)
                        print("Birthday added.")
                    except ValueError as e:
                        print(e)
                else:
                    print("Contact not found.")

        
        elif command == "delete":
            if len(args) == 1:
                name = args[0]
                print(book.delete(name))
            else:
                print("Invalid format. Please use: delete [name]")

        elif command == "show-birthday":
            if len(args) == 1:
                name = args[0]
                record = book.find(name)
                if record:
                    print(record.show_birthday())
                else:
                    print("Contact not found.")
            else:
                print("Invalid format. Please use: show-birthday [name]")

        elif command == "birthdays":
            upcoming_birthdays = book.get_upcoming_birthdays()
            if not upcoming_birthdays:
                print("No upcoming birthdays in the next week.")
            else:
                print("Upcoming birthdays:")
                for record in upcoming_birthdays:
                    print(record)

        elif command == "all":
            all_contacts = book.show_all_contacts()
            print(all_contacts)

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()