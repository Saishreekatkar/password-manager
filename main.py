import pymysql.cursors
import hashlib

def create_connection():
    """ Create a connection to the MySQL database """
    connection = pymysql.connect(
        host='localhost',  
        user='surkee',  
        password='myfoobar',  
        database='manager',
        cursorclass=pymysql.cursors.DictCursor
    )
    print("Connected to MySQL database")
    return connection

def create_table(connection):
    """ Create a table to store user credentials """
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_credentials (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                password_plain VARCHAR(255) NOT NULL,
                website VARCHAR(255) NOT NULL
            )
        """)
    print("Table 'user_credentials' created successfully.")

def create_master_password_table(connection):
    """ Create a table to store the master password """
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS master_password (
                id INT AUTO_INCREMENT PRIMARY KEY,
                password VARCHAR(255) NOT NULL
            )
        """)
    print("Table 'master_password' created successfully.")

def hash_password(password):
    """ Hash a password using SHA-256 """
    return hashlib.sha256(password.encode()).hexdigest()

def insert_user(connection, name, email, password, website):
    """ Insert a new user into the database """
    hashed_password = hash_password(password)
    with connection.cursor() as cursor:
        sql = "INSERT INTO user_credentials (name, email, password_hash, password_plain, website) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (name, email, hashed_password, password, website))
    connection.commit()
    print("User inserted successfully.")

def get_master_password(connection):
    """ Get the master password from the database """
    with connection.cursor() as cursor:
        cursor.execute("SELECT password FROM master_password")
        result = cursor.fetchone()
        if result:
            return result['password']
        else:
            return None

def set_master_password(connection):
    """ Set the master password """
    while True:
        master_password = input("Set master password: ")
        confirm_password = input("Confirm master password: ")
        if master_password == confirm_password:
            hashed_password = hash_password(master_password)
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO master_password (password) VALUES (%s)", (hashed_password,))
            connection.commit()
            print("Master password set successfully.")
            break
        else:
            print("Passwords do not match. Please try again.")

def add_new_entry(connection):
    """ Function to add a new entry """
    name = input("Enter your name: ")
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    website = input("Enter the website: ")
    insert_user(connection, name, email, password, website)

def access_existing_entries(connection):
    """ Function to access existing entries """
    print("Accessing existing entries...")
    website = input("Enter the website: ")
    with connection.cursor() as cursor:
        sql = "SELECT * FROM user_credentials WHERE website = %s"
        cursor.execute(sql, (website,))
        result = cursor.fetchone()
        if result:
            print("User found:")
            print(f"Name: {result['name']}")
            print(f"Email: {result['email']}")
            print(f"Password: {result['password_plain']}")
            print(f"Website: {result['website']}")
        else:
            print("No entry found for the provided website.")

def main():
    connection = None
    try:
        connection = create_connection()
        create_table(connection)
        create_master_password_table(connection)
        
        # Check if the master password is set
        master_password = get_master_password(connection)
        if master_password is None:
            set_master_password(connection)

        # Prompt for the master password
        while True:
            input_password = input("Provide master password: ").strip()  # Strip leading and trailing whitespaces
            input_password_hash = hash_password(input_password)
            if input_password_hash == master_password.strip():  # Strip leading and trailing whitespaces
                print("Master password verified.")
                break
            else:
                print("Incorrect master password. Try again.")

        # Display menu options
        while True:
            print("\nMenu:")
            print("1. Add a new entry")
            print("2. Access existing entries")
            print("3. Exit")
            choice = input("Enter your choice (1/2/3): ")
            if choice == '1':
                add_new_entry(connection)
            elif choice == '2':
                access_existing_entries(connection)
            elif choice == '3':
                print("Exiting program.")
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection:
            connection.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    main()
