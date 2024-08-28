import mysql.connector
from mysql.connector import Error
import re
from datetime import datetime, timedelta
import bcrypt


# Predefined admin credentials
ADMIN_USERID = 'admin'
ADMIN_PASSWORD = 'admin123'


def db_connect():
    return mysql.connector.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='faith',
        database='LMS'
    )


def create_tables():
    table_creation_statements = [
        '''
        CREATE TABLE IF NOT EXISTS register (
        id INT AUTO_INCREMENT PRIMARY KEY,
        firstname VARCHAR(50),
        lastname VARCHAR(50),
        number VARCHAR(15),
        mailid VARCHAR(50),
        userid VARCHAR(50) UNIQUE,
        password VARCHAR(50)
        )
        ''',
        # '''
        # CREATE TABLE IF NOT EXISTS Userlist (
        #     first_name VARCHAR(50),
        #     last_name VARCHAR(50),
        #     mobile_no VARCHAR(15),
        #     email_id VARCHAR(50),
        #     subscription_plan VARCHAR(50),
        #     status VARCHAR(20)
        # )
        # ''',
        '''
        CREATE TABLE IF NOT EXISTS Books (
            bookid INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            author VARCHAR(100),
            genre VARCHAR(50),
            rent_rate VARCHAR(10),
            status VARCHAR(20),
            startdate DATE,
            enddate DATE
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS genre (
            genre_id INT AUTO_INCREMENT PRIMARY KEY,
            genre_name VARCHAR(50),
            book_name VARCHAR(100)
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS author (
            author_id INT AUTO_INCREMENT PRIMARY KEY,
            author_name VARCHAR(50),
            authbook_name VARCHAR(50)
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS SubscriptionPlan (
            id INT AUTO_INCREMENT PRIMARY KEY,
            userid VARCHAR(50),
            plan VARCHAR(50),
            amount VARCHAR(10),
            payment_method VARCHAR(50),
            payment_details VARCHAR(100),
            status VARCHAR(20),
            start_date DATE,
            end_date DATE,
            FOREIGN KEY (userid) REFERENCES register(userid)
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS rent_book (
            rent_id INT AUTO_INCREMENT PRIMARY KEY,
            bookid INT NOT NULL,
            userid varchar(50),
            title VARCHAR(255),
            author VARCHAR(255),
            genre VARCHAR(100),
            price VARCHAR(10),
            startdate DATE,
            enddate DATE,
            FOREIGN KEY (bookid) REFERENCES Books(bookid)
        )
        '''
    ]

    try:
        # Connect to the database
        conn = db_connect()
        cursor = conn.cursor()

        # Execute each table creation statement separately
        for statement in table_creation_statements:
            cursor.execute(statement)

        # Commit changes
        conn.commit()
        print("Tables created successfully")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            print('MySQL connection successfull')

def admin_login():
    userid = input("Enter admin userid: ")
    password = input("Enter admin password: ")

    if userid == ADMIN_USERID and password == ADMIN_PASSWORD:
        print("Login successful")
        admin_page()
    else:
        print("Invalid credentials or not an admin")


def admin_page():
    while True:
        print("\nAdmin Page")
        print("1. Add Book")
        print("2. View Book Details")
        print("3. View User Details")
        print("4. Manage Overdue Books")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            add_book()
        elif choice == '2':
            view_books()
        elif choice == '3':
            view_users()
        elif choice == '4':
            overdue_book()
        elif choice == '5':
            print("Exiting the system....")
            break
        else:
            print("Invalid choice")


def add_book():
    print("-----------ADD BOOK____________")
    name = input("Enter book name: ")
    author = input("Enter book author: ")

    print("Select genre:")
    print("1. Romance")
    print("2. Horror")
    print("3. Comic")
    print("4. Research")

    genre_choice = input("Enter the number corresponding to the genre: ")

    genre_map = {
        '1': 'Romance',
        '2': 'Horror',
        '3': 'Comic',
        '4': 'Research'
    }

    genre = genre_map.get(genre_choice, 'Unknown')

    rent_rate = input("Enter rent rate: ")
    print("Choose the status of book")
    print("1. Available")
    print("2. UnAvailable")
    status_choice = input("Enter the number corresponding to the book status: ")

    status_map = {
        '1': 'Available',
        '2': 'UnAvailable'
    }

    status = status_map.get(status_choice, 'Unknown')

    # Get rental dates
    startdate = input("Enter rental start date (YYYY-MM-DD): ")
    enddate = input("Enter rental end date (YYYY-MM-DD): ")

    conn = db_connect()
    cursor = conn.cursor()

    query = '''
    INSERT INTO Books (name, author, genre, rent_rate, status, startdate, enddate)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    '''
    cursor.execute(query, (name, author, genre, rent_rate, status, startdate, enddate))

    conn.commit()
    print("Book added successfully")

    cursor.close()
    conn.close()


# def view_books():
#     conn = db_connect()
#     cursor = conn.cursor()
#
#     print("----------------------")
#     print("LIST OF BOOKS")
#     print("----------------------")
#     cursor.execute("SELECT * FROM Books")
#     books = cursor.fetchall()
#
#     for book in books:
#         # print(book)
#         print(f"bookid: {book[0]}, bookname: {book[1]}, author: {book[2]}, genre: {book[3]}, rate: Rs{book[4]}, status: {book[5]}, startdate: {book[6]}, enddate: {book[7]}")
#
#     cursor.close()
#     conn.close()

def view_books():
    conn = db_connect()
    cursor = conn.cursor()

    print("----------------------")
    print("LIST OF BOOKS")
    print("----------------------")
    cursor.execute("SELECT * FROM Books")
    books = cursor.fetchall()

    for book in books:
        print(
            f"bookid: {book[0]}, bookname: {book[1]}, author: {book[2]}, genre: {book[3]}, rate: Rs{book[4]}, status: {book[5]}, startdate: {book[6]}, enddate: {book[7]}")
    while True:
        print("\nOptions:")
        print("1. Update a book")
        print("2. Delete a book")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            update_book(conn, cursor)
        elif choice == '2':
            delete_book(conn, cursor)
        elif choice == '3':
            # admin_page()
            break
        else:
            print("Invalid choice!")

    cursor.close()
    conn.close()


def update_book(conn, cursor):
    book_name = input("Enter the name of the book you want to update: ")

    # Check if the book exists
    cursor.execute("SELECT * FROM Books WHERE name = %s", (book_name,))
    book = cursor.fetchone()

    if book:
        print("Current details:")
        print(f"Book Name: {book[1]}")
        print(f"Author: {book[2]}")
        print(f"Genre: {book[3]}")
        print(f"Rent Rate: Rs{book[4]}")
        print(f"Status: {book[5]}")
        print(f"Start Date: {book[6]}")
        print(f"End Date: {book[7]}")

        new_name = input("Enter new book name (or press Enter to keep unchanged): ") or book[1]
        new_author = input("Enter new author name (or press Enter to keep unchanged): ") or book[2]
        new_genre = input("Enter new genre (or press Enter to keep unchanged): ") or book[3]
        new_rate = input("Enter new rent rate (or press Enter to keep unchanged): ") or book[4]
        new_status = input("Enter new status (or press Enter to keep unchanged): ") or book[5]
        new_startdate = input("Enter new start date (YYYY-MM-DD) (or press Enter to keep unchanged): ") or book[6]
        new_enddate = input("Enter new end date (YYYY-MM-DD) (or press Enter to keep unchanged): ") or book[7]

        cursor.execute("""
            UPDATE Books 
            SET name = %s, author = %s, genre = %s, rent_rate = %s, status = %s, startdate = %s, enddate = %s
            WHERE name = %s
        """, (new_name, new_author, new_genre, new_rate, new_status, new_startdate, new_enddate, book_name))

        conn.commit()
        print(f"Book '{book_name}' updated successfully!")
    else:
        print("Book not found!")


def delete_book(conn, cursor):
    book_name = input("Enter the name of the book you want to delete: ")

    # Check if the book exists
    cursor.execute("SELECT * FROM Books WHERE name = %s", (book_name,))
    book = cursor.fetchone()

    if book:
        confirm = input(f"Are you sure you want to delete the book '{book_name}'? (yes/no): ")
        if confirm.lower() == 'yes':
            cursor.execute("DELETE FROM Books WHERE name = %s", (book_name,))
            conn.commit()
            print(f"Book '{book_name}' deleted successfully!")
        else:
            print("Delete operation canceled.")
    else:
        print("Book not found!")

def view_users():
    while True:
        print("\n--- View User Details ---")
        print("1. Subscribed Users")
        print("2. Unsubscribed Users")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            view_subscribed_users()
        elif choice == '2':
            view_unsubscribed_users()
        elif choice == '3':
            print("Exiting View User Details...")
            break
        else:
            print("Invalid choice. Please select a valid option.")

def view_subscribed_users():
    conn = db_connect()
    cursor = conn.cursor()

    try:
        # Query to get details of subscribed users
        query = '''
        SELECT r.firstname, r.lastname, r.mailid, r.number
        FROM register r
        JOIN SubscriptionPlan sp ON r.userid = sp.userid
        WHERE sp.status = 'Active'
        '''
        cursor.execute(query)
        users = cursor.fetchall()

        print("\n--- Subscribed Users ---")
        if users:
            for user in users:
                print(f"First Name: {user[0]}, Last Name: {user[1]}, Email ID: {user[2]}, Number: {user[3]}")
        else:
            print("No subscribed users found.")

    except Error as e:
        print(f"Error fetching subscribed users: {e}")

    cursor.close()
    conn.close()

def view_unsubscribed_users():
    conn = db_connect()
    cursor = conn.cursor()

    try:
        # Query to get details of unsubscribed users
        query = '''
        SELECT r.firstname, r.lastname, r.mailid, r.number
        FROM register r
        LEFT JOIN SubscriptionPlan sp ON r.userid = sp.userid
        WHERE sp.userid IS NULL OR sp.status = 'Expired'
        '''
        cursor.execute(query)
        users = cursor.fetchall()

        print("\n--- Unsubscribed Users ---")
        if users:
            for user in users:
                print(f"First Name: {user[0]}, Last Name: {user[1]}, Email ID: {user[2]}, Number: {user[3]}")
        else:
            print("No unsubscribed users found.")

    except Error as e:
        print(f"Error fetching unsubscribed users: {e}")

    cursor.close()
    conn.close()

def overdue_book():
    conn = db_connect()
    cursor = conn.cursor(dictionary=True)  # Use dictionary=True for better readability

    # Get current date
    current_date = datetime.now().date()

    try:
        # Query to get details of overdue books
        query = """
            SELECT rb.rent_id, rb.bookid, b.name, rb.startdate, rb.enddate
            FROM rent_book rb
            JOIN Books b ON rb.bookid = b.bookid
            WHERE rb.enddate < %s
        """

        cursor.execute(query, (current_date,))
        overdue_books = cursor.fetchall()

        if not overdue_books:
            print("No overdue books found.")
        else:
            print("Overdue Books:")
            for book in overdue_books:
                print(f"Rent ID: {book['rent_id']}, Book ID: {book['bookid']}, Title: {book['name']}, Start Date: {book['startdate']}, End Date: {book['enddate']}")

    except Error as e:
        print(f"Error: {e}")

    finally:
        cursor.close()
        conn.close()
def customer_menu():
    while True:
        print("\n--------------------------------")
        print("1. Login")
        print("2. Register. New user?")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            logincus()
        elif choice == '2':
            customer_register()
        elif choice == '3':
            print("System exiting...")
            break
        else:
            print("Invalid choice! Choose up to 3 only")


def customer_register():
    conn = db_connect()
    cursor = conn.cursor()

    while True:
        try:
            print("Register your details here.")
            first_name = input("Enter the first name: ")
            last_name = input("Enter the last name: ")

            while True:
                number = input("Enter the number: ")
                if re.fullmatch(r'^[6-9]\d{9}$', number):
                    break
                else:
                    print("Invalid! Number should contain 10 digits and start with 6, 7, 8, or 9")

            while True:
                email = input("Enter the email id: ")
                if re.fullmatch(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                    break
                else:
                    print("Invalid! Please enter a valid email address")

            while True:
                userid = input("Create a user ID: ")
                if re.fullmatch(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,12}$', userid):
                    break
                else:
                    print("INVALID! User ID should be alphanumeric and 6-12 characters long.")

            while True:
                password = input("Enter the password: ")
                if re.fullmatch(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@#$%^&+!_])[A-Za-z\d@#$%^&+!_]{6,12}$',
                                password):
                    break
                else:
                    print(
                        "INVALID! Password must be 6-12 characters long with 1 uppercase, 1 lowercase, 1 digit, and 1 special character.")

            insert_query = "INSERT INTO register (firstname, lastname, number, mailid, userid, password) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (first_name, last_name, number, email, userid, password))
            conn.commit()

            print("Registered successfully")
            return

        except Error as e:
            print(f"Error: {e}")
            conn.rollback()

    cursor.close()
    conn.close()

def logincus():
    conn = db_connect()
    cursor = conn.cursor()

    print("Enter your details here")
    userid = input("Enter the user id: ")
    password = input("Enter password: ")

    try:
        query = "SELECT * FROM register WHERE userid = %s AND password = %s"
        cursor.execute(query, (userid, password))
        result = cursor.fetchone()

        if result:
            print(f"Welcome, {userid}!")
            customer_page()

        else:
            print("Invalid login credentials")

    except Error as e:
        print(f"Error: {e}")

    cursor.close()
    conn.close()

def customer_page():
    while True:
        print("\n Customer Dashboard")
        print("-------------------------------")
        print("1. Genre")
        print("2. Author")
        print("3. Choose Plan")
        print("4. View Plan")
        print("5. Rent book")
        print("6. Logout")

        choice = input("enter the choice: ")
        if choice == '1':
            genre()
        elif choice == '2':
            Author()
        elif choice == '3':
            choose_plan()
        elif choice == '4':
            view_plan()
        elif choice == '5':
            choose_rent()
        elif choice == '6':
            print("loging out....")
            break
        else:
            print("Invalid choice")

def genre():
    # Establish database connection
    conn = db_connect()
    cursor = conn.cursor()

    while True:
        print("\n---------- Genre List -----------")
        print("1. Romance")
        print("2. Horror")
        print("3. Comic")
        print("4. Research")
        print("5. Exit")

        genre_choice = input("Enter the choice of genre you want to view or '5' to exit: ")

        # Genre map
        genre_map = {
            '1': 'Romance',
            '2': 'Horror',
            '3': 'Comic',
            '4': 'Research'
        }

        # Exit option
        if genre_choice == '5':
            print("Exiting Genre Menu...")
            break

        # Get the selected genre
        genre = genre_map.get(genre_choice)

        if genre:
            try:
                # Query to select books from the selected genre
                query = "SELECT name, author, rent_rate, status FROM Books WHERE genre = %s"
                cursor.execute(query, (genre,))
                books = cursor.fetchall()

                # Display books of the selected genre
                print(f"\nBooks in {genre} genre:")
                if books:
                    for book in books:
                        print(f"Name: {book[0]}, Author: {book[1]}, Rent Rate: Rs{book[2]}, Status: {book[3]}")
                else:
                    print(f"No books found in the {genre} genre.")
            except Error as e:
                print(f"Error fetching books: {e}")
        else:
            print("Invalid genre choice. Please select a valid option.")

    # Close the cursor and connection
    cursor.close()
    conn.close()

def Author():
    conn = db_connect()
    cursor = conn.cursor()

    while True:
        print("\n---------- Author List -----------")
        print("1. View Authors")
        print("2. Exit")

        choice = input("Enter your choice or '2' to exit: ")

        if choice == '2':
            print("Exiting Author Menu...")
            break

        if choice == '1':
            try:
                # Query to select all authors from the author table
                query = "SELECT author_id, author_name, authbook_name FROM author"
                cursor.execute(query)
                authors = cursor.fetchall()

                # Display authors
                print("\nList of Authors:")
                if authors:
                    for author in authors:
                        print(f"Author ID: {author[0]}, Author Name: {author[1]}, Book Name: {author[2]}")
                else:
                    print("No authors found.")
            except Error as e:
                print(f"Error fetching authors: {e}")

    cursor.close()
    conn.close()

def validate_gpay_id(gpay_id):
    # Example validation: GPay ID should be a valid email address
    return re.match(r"^[0-9A-Za-z]{2,256}@[A-Za-z]{2,64}$", gpay_id)

def validate_account_number(account_number):
    # Example validation: Bank account number should be numeric and 10-18 digits
    return re.match(r"^\d{12}$", account_number)

def validate_credit_card_details(card_number, expiry_date, cvc):
    # Example validation for credit card number (16 digits), expiry date (MM/YY), and CVC (3 digits)
    card_valid = re.match(r"^\d{12}$", card_number)
    expiry_valid = re.match(r"^(0[1-9]|1[0-2])\/([0-9]{2})$", expiry_date)
    cvc_valid = re.match(r"^\d{3}$", cvc)
    return card_valid and expiry_valid and cvc_valid

def choose_plan():
    conn = db_connect()
    cursor = conn.cursor()

    plans = {
        '1': ('6 month plan', '500'),
        '2': ('1 year plan', '1000'),
        '3': ('2 year plan', '1500')
    }

    while True:
        print("\n------- Choose Plan ---------")
        print("1. 6 month plan - Rs 500")
        print("2. 1 year plan - Rs 1000")
        print("3. 2 year plan - Rs 1500")
        print("4. Exit")

        plan_choice = input("Enter the choice of plan: ")

        if plan_choice == '4':
            break

        plan = plans.get(plan_choice)
        if not plan:
            print("Invalid choice! Please choose a valid plan.")
            continue

        plan_name, amount = plan
        payment_method = input("Enter your payment method (Credit Card, Bank Transfer, GPay): ").lower()

        payment_details = None

        if payment_method == 'gpay':
            while True:
                gpay_id = input("Enter your GPay ID: ")
                if validate_gpay_id(gpay_id):
                    payment_details = gpay_id
                    break
                else:
                    print("Invalid GPay ID. Please enter a valid UPI ID (example@okaxisbank) address.")

        elif payment_method == 'bank transfer':
            while True:
                account_number = input("Enter your Bank Account Number: ")
                if validate_account_number(account_number):
                    payment_details = account_number
                    break
                else:
                    print("Invalid account number. Please enter a numeric account number with 12 digits.")

        elif payment_method == 'credit card':
            while True:
                credit_card_number = input("Enter your Credit Card Number: ")
                expiry_date = input("Enter Expiry Date (MM/YY): ")
                cvc = input("Enter CVC: ")

                if validate_credit_card_details(credit_card_number, expiry_date, cvc):
                    payment_details = f"Card: {credit_card_number}, Expiry: {expiry_date}, CVC: {cvc}"
                    break
                else:
                    print("Invalid credit card details. Please check the card number should be 12 digits, expiry date, and CVC should be 3 digits only.")

        else:
            print("Invalid payment method! Please choose either Credit Card, Bank Transfer, or GPay.")
            continue

        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=(180 if plan_choice == '1' else 365 if plan_choice == '2' else 730))

        status = 'Active'

        try:
            # Assuming you have the `userid` stored somewhere from the login session
            userid = input("Enter your User ID: ")

            insert_query = '''
            INSERT INTO SubscriptionPlan (userid, plan, amount, payment_method, payment_details, status, start_date, end_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(insert_query, (userid, plan_name, amount, payment_method, payment_details, status, start_date, end_date))
            conn.commit()

            print(f"Plan '{plan_name}' selected successfully!")
            print(f"Subscription is valid until {end_date}")

        except Error as e:
            print(f"Error subscribing to plan: {e}")
            conn.rollback()

    cursor.close()
    conn.close()
def view_plan():
    conn = db_connect()
    cursor = conn.cursor()

    userid = input("Enter your User ID to view your plan: ")  # Replace this with actual user session ID

    try:
        # Query to get the user's active subscription plan details
        query = '''
        SELECT r.firstname, r.lastname, sp.plan, sp.amount, sp.payment_method, sp.start_date, sp.end_date, sp.status
        FROM register r
        JOIN SubscriptionPlan sp ON r.userid = sp.userid
        WHERE r.userid = %s AND sp.status = 'Active'
        '''
        cursor.execute(query, (userid,))
        subscription = cursor.fetchone()

        if subscription:
            print("\n--- Your Subscription Plan ---")
            print(f"First Name: {subscription[0]}")
            print(f"Last Name: {subscription[1]}")
            print(f"Plan: {subscription[2]}")
            print(f"Amount: Rs {subscription[3]}")
            print(f"Payment Method: {subscription[4]}")
            print(f"Start Date: {subscription[5]}")
            print(f"End Date: {subscription[6]}")
            print(f"Status: {subscription[7]}")
        else:
            print("No active subscription found for this user.")

    except Error as e:
        print(f"Error: {e}")

    cursor.close()
    conn.close()
def choose_rent():
    conn = db_connect()
    cursor = conn.cursor(dictionary=True)

    try:
        userid = input("Enter your User ID: ")

        # Check if the user has an active subscription
        check_subscription_query = """
        SELECT * FROM SubscriptionPlan 
        WHERE userid = %s AND status = 'Active'
        AND CURDATE() BETWEEN start_date AND end_date
        """
        cursor.execute(check_subscription_query, (userid,))
        active_subscription = cursor.fetchone()

        if active_subscription is None:
            print("You don't have an active subscription plan. Please subscribe to a plan to rent a book.")
            return

        # Ask for the book name
        book_name = input("Enter the name of the book you want to rent: ")

        # Query to get book details by name
        query = "SELECT * FROM Books WHERE name = %s"
        cursor.execute(query, (book_name,))
        book = cursor.fetchone()

        if book is None:
            print("No book found with that name.")
            return

        # Check if the book is available
        if book['status'] != 'Available':
            print("The book is not available at the moment. Please choose another book.")
            return

        # If the book is available, proceed with renting the book
        bookid = book['bookid']

        # Insert rent record
        rent_query = """
        INSERT INTO rent_book (bookid, title, author, genre, price, startdate, enddate, userid) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(rent_query, (bookid, book_name, book['author'], book['genre'], book['rent_rate'], book['startdate'], book['enddate'], userid))
        conn.commit()

        print("Congratulations! You've rented the book! Happy reading!")

        # Display the list of books rented by the user
        rented_books_query = """
        SELECT * FROM rent_book
        WHERE userid = %s
        """
        cursor.execute(rented_books_query, (userid,))
        rented_books = cursor.fetchall()

        print("\nList of books you have rented:")
        for rented_book in rented_books:
            print(f"Book ID: {rented_book['bookid']}, Title: {rented_book['title']}, Author: {rented_book['author']}, Genre: {rented_book['genre']}, Price: {rented_book['price']}, Start Date: {rented_book['startdate']}, End Date: {rented_book['enddate']}")

    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_tables()
    while True:
        print("--------------Welcome To Faith Library-------------")
        print("\nMain Menu")
        print("1. Admin Login")
        print("2. Customer Login")
        print("3. Exit")

        main_choice = input("Enter your choice: ")

        if main_choice == '1':
            admin_login()
        elif main_choice == '2':
            customer_menu()
        elif main_choice == '3':
            print("System exiting...Thank you for using. come back again!")
            break
        else:
            print("Invalid choice! Please select up to 3 options")
