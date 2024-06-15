import sqlite3
import hashlib
import secrets
import os
import random
import string


class Model:
    absolute_path = "C:\\Users\\admin\\PycharmProjects\\pythonProject\\true\\first\\backend\\app_db.db"
    TABLE_NAMES = ["Users", "Info", "Books", "Preference", "Borrowed", "Directory"]

    def __init__(self) -> None:
        if os.path.exists(Model.absolute_path):
            self.db_conn = sqlite3.connect(Model.absolute_path)
            self.db_cursor = self.db_conn.cursor()
            self.create_users_table()
            self.create_info_table()
            self.create_books_table()
            self.create_preferences()
        else:
            # Create the file if it doesn't exist
            self.create_db_file()
            self.db_conn = sqlite3.connect(Model.absolute_path)
            self.db_cursor = self.db_conn.cursor()
            self.create_users_table()
            self.create_info_table()
            self.create_books_table()
            self.create_preferences()

    def create_db_file(self):
        # Create an empty database file
        with open(Model.absolute_path, 'w') as f:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.db_cursor:
            self.db_cursor.close()
        if self.db_conn:
            self.db_conn.close()

    def create_users_table(self) -> None:
        self.db_cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {Model.TABLE_NAMES[0]} (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            USERNAME TEXT NOT NULL,
            PASSWORD TEXT NOT NULL,
            TAIL TEXT NOT NULL
            )
            """)
        self.db_conn.commit()

    def create_info_table(self) -> None:
        self.db_cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {Model.TABLE_NAMES[1]} (
            ID INTEGER PRIMARY KEY,
            FIRST_NAME TEXT NOT NULL,
            LAST_NAME TEXT NOT NULL,
            AGE INTEGER NOT NULL,
            GENDER TEXT NOT NULL,
            EMAIL TEXT NOT NULL,
            USER_ID INTEGER NOT NULL,
            FOREIGN KEY (USER_ID) REFERENCES Users(ID)
            )
            """)
        self.db_conn.commit()

    def create_books_table(self):
        self.db_cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {Model.TABLE_NAMES[2]} (
            BOOK_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            TITLE TEXT NOT NULL,
            AUTHOR TEXT NOT NULL,
            SUBJECT TEXT NOT NULL,
            DATE_ADDED DATETIME DEFAULT CURRENT_TIMESTAMP,
            FILE_NAME TEXT NOT NULL, 
            PATH TEXT NOT NULL,
            COVER TEXT NOT NULL
            )
            """
        )
        self.db_conn.commit()

    def create_preferences(self):
        self.db_cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {Model.TABLE_NAMES[3]} (
            USER TEXT PRIMARY KEY,
            STATION TEXT
            )
            """
        )
        self.db_cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {Model.TABLE_NAMES[4]} (
            USER TEXT,
            BOOKS TEXT,
            FOREIGN KEY (USER) REFERENCES {Model.TABLE_NAMES[3]}(USER)
            )  
            """
        )
        self.db_conn.commit()

        self.db_cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {Model.TABLE_NAMES[5]} (
            USER TEXT, 
            DIR TEXT,
            FOREIGN KEY (USER) REFERENCES {Model.TABLE_NAMES[3]}(USER)
            )
            """
        )

    def create_user_account(self, username: str, passcode: str, tail: str) -> bool:
        self.db_cursor.execute("""
    SELECT * FROM Users WHERE USERNAME = ?
    """, (username,)
                               )
        if not self.db_cursor.fetchone():
            self.db_cursor.execute("""
        INSERT INTO Users (USERNAME, PASSWORD, TAIL) VALUES (?,?,?)
        """, (username, passcode, tail,)
                                   )
            self.db_conn.commit()
            return True
        return False

    def store_info(self, first_name: str, last_name: str, age: int, gender: str, email: str, identifier: str):
        id_only = self.find_this("ID", "Users", "Username", identifier)
        user_id = id_only[0]
        self.db_cursor.execute("""
    INSERT INTO Info (FIRST_NAME, LAST_NAME, AGE, GENDER, EMAIL, USER_ID) VALUES (?, ?, ?, ?, ?, ?)
    """,
                               (first_name, last_name, age, gender, email, user_id)
                               )
        self.db_conn.commit()

    def verify_user(self, username: str, passcode: str) -> bool:
        # For Log-in UI
        # Check if the username is in the database after attempting the log-in button
        username_check = self.db_cursor.execute(
            """
            SELECT Password, Tail FROM Users WHERE Username = ?
            """,
            (username,)
        )
        result = username_check.fetchone()
        if result:
            existing_pass, tail = result
            passcode = hashlib.sha256((passcode + tail).encode('utf-8')).hexdigest()
            if passcode == existing_pass:
                self.db_conn.commit()
                return True
        return False

    def hash_this(self, password):
        tail = secrets.token_hex(16)
        password = hashlib.sha256((password + tail).encode("utf-8")).hexdigest()
        return password, tail

    def find_this(self, column_name="*", table_name=None, con_column=None, data_information=None):
        table_name = table_name.capitalize()
        if table_name not in Model.TABLE_NAMES:
            return
        self.db_cursor.execute(
            f"""
            SELECT {column_name} FROM {table_name} WHERE {con_column} = ?
            """,
            (data_information,)
        )
        result = self.db_cursor.fetchone()
        return result

    def add_book(self, title="", author="", subject="", file_name="", file_path="", cover=""):
        if title == "" or author == "" or subject == "" or file_name == "" or file_path == "" or cover == "":
            return False
        title = title.upper()
        author = author.upper()
        subject = subject.capitalize()
        self.db_cursor.execute("""
        INSERT INTO BOOKS (TITLE, AUTHOR, SUBJECT, FILE_NAME, PATH, COVER) VALUES (?,?,?,?,?,?)
        """, (title, author, subject, file_name, file_path, cover)
                               )
        self.db_conn.commit()
        return True

    def retrieve(self, table_name):
        table_name = table_name.capitalize()
        if table_name not in Model.TABLE_NAMES:
            return False
        else:
            self.db_cursor.execute(
                """
                SELECT * FROM {}
                """.format(table_name)
            )
            result = self.db_cursor.fetchall()
            return result

    def delete_this(self, table_name, data_information):
        table_name = table_name.capitalize()
        # data_information is either username if table name is Users or first name if Info
        if table_name not in Model.TABLE_NAMES:
            return
        if not data_information:
            return

        if table_name == Model.TABLE_NAMES[0]:
            self.db_cursor.execute(
                """
                DELETE FROM {} WHERE USERNAME = ?
                """.format(table_name),
                (data_information,)  # Provide the value as a parameter to avoid SQL injection
            )
            self.db_conn.commit()
            return True
        elif table_name == Model.TABLE_NAMES[1]:
            self.db_cursor.execute(
                """
                DELETE FROM {} WHERE FIRST_NAME = ?
                """.format(table_name),
                (data_information,)  # Provide the value as a parameter to avoid SQL injection
            )
            self.db_conn.commit()
            return True
        else:
            return False

    def query(self, columns, table, con_column="TITLE", value=None):
        if not con_column:
            return
        if not value:
            return
        if len(columns) == 1:
            columns_string = columns[0]
        else:
            columns_string = ", ".join(columns)
        try:
            self.db_cursor.execute(
                f"""
                SELECT {columns_string} FROM {table} WHERE {con_column} = ?
                """, (value,)
            )
            result = self.db_cursor.fetchall()
            return result
        except sqlite3.OperationalError as e:
            return f"{str(e)}"

    def store_book(self, username, book_title):
        if not username or not book_title:
            return False
        # Check if the user exists
        check_x = self.find_this("USER", "Borrowed", "USER", username)
        if check_x:  # They exist
            # Check the books they want to borrow
            check_b = self.db_cursor.execute(
                f"""
                SELECT USER, BOOKS FROM Borrowed WHERE USER = '{username}' and BOOKS = '{book_title}'
                 """
            )
            if not check_b.fetchall():  # The book does not exist as borrowed
                self.db_cursor.execute(
                    f"""
                    INSERT INTO Borrowed (USER, BOOKS) VALUES (?,?)
                    """, (username, book_title)
                )
                self.db_conn.commit()
                return True
            else:
                return False
        else:  # User does not exist as borrower
            self.db_cursor.execute(
                f"""
                INSERT INTO Borrowed (USER, BOOKS) VALUES (?,?)
                    """, (username, book_title)
            )
            self.db_conn.commit()
            return True

    def store_pref(self, new_name, current_user):
        if not new_name or not current_user:
            return False
        check_current_x = self.find_this("USER", "Preference", "USER", current_user)
        if not check_current_x:
            self.db_cursor.execute(
                """
                INSERT INTO Preference (USER, STATION) VALUES (?, ?)
                """, (current_user, new_name)
            )
            self.db_conn.commit()
            return True
        self.db_cursor.execute(
            """
            UPDATE Preference SET STATION = ? WHERE USER = ?
            """, (new_name, current_user)
        )
        self.db_conn.commit()
        return True

    def store_dir(self, new_dir, current_x):
        if not new_dir or not current_x:
            return False
        check_current_x = self.find_this("USER", "Directory", "USER", current_x)
        if not check_current_x:
            self.db_cursor.execute(
                """
                INSERT INTO Directory (USER, DIR) VALUES (?,?)
                """, (current_x, new_dir)
            )
            self.db_conn.commit()
            return True
        self.db_cursor.execute(
            """
            UPDATE Directory SET DIR = ? WHERE USER = ?
            """, (new_dir, current_x)
        )
        self.db_conn.commit()
        return True

    @staticmethod
    def generate_string(length=8):
        character = string.ascii_uppercase + string.digits
        randomize = ""
        for i in range(length):
            randomize += random.choice(character)
        return randomize


if __name__ == "__main__":
    dm = Model()


