import pymysql.cursors
import hashlib

def create_connection():
    """ Create a connection to the MySQL database """
    connection = pymysql.connect(
        host='localhost',
        user='surkee',  # Replace 'username' with your MySQL username
        password='myfoobar',  # Replace 'password' with your MySQL password
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
                password VARCHAR(255) NOT NULL,
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
        sql = "INSERT INTO user_credentials (name, email, password, website) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (name, email, hashed_password, website))
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
            input_password = input("Provide master password: ")
            input_password_hash = hash_password(input_password)
            if input_password_hash == master_password:
                print("Master password verified.")
                break
            else:
                print("Incorrect master password. Try again.")

        name = input("Enter your name: ")
        email = input("Enter your email: ")
        password = input("Enter your password: ")
        website = input("Enter the website: ")
        insert_user(connection, name, email, password, website)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection:
            connection.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    main()
