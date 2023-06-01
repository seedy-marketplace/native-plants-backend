import psycopg2 as db_con  # Manage the connection to databse
import os
from sys import stderr
from flask import json
from decimal import Decimal  # Allow override for decimal type in json serialization


class DatabaseConnection():
    def __init__(self):
        try:
            # Fetch credentials from the environment
            """ self.host_name = os.environ["DB_HOST_NAME"]
            self.db_user   = os.environ["DB_USER"]
            self.db_pass   = os.environ["DB_PASS"]
            self.db_name   = os.environ["DB_NAME"] """

            self.DATABASE_URL = os.environ['DATABASE_URL']
        except KeyError:
            # If >= 1 of the credentials are missing,
            print("Set environment variables DB_HOST_NAME, DB_USER, DB_PASS, DB_NAME", file=stderr)
            exit(1)
        
        # Connect to the database
        """ self.connection = db_con.connect(
            host=self.host_name, 
            user=self.db_user, 
            password=self.db_pass, 
            database=self.db_name) """
        self.connection = db_con.connect(self.DATABASE_URL, sslmode='require')
        self.cursor = self.connection.cursor()
        # Set the override for decimal type (maybe datetimes in future?)
        json.JSONEncoder.default = self.default
    def execute_query(self, query, user_input="", include_headers=False):
        # Execute the query and return the results
        try:
            user_input = [self.clean_query(i) for i in user_input]    
            self.connection = db_con.connect(self.DATABASE_URL, sslmode='require')
            self.cursor = self.connection.cursor()        
            self.cursor.execute(query, user_input)
            if include_headers:
                columns = [column[0] for column in self.cursor.description]
                res = columns, self.cursor.fetchall()
            else:
                res = self.cursor.fetchall()
            self.connection.rollback()
            return res
        except db_con.Error as e:
            print(f'Error {e}')
            self.connection.rollback()
            return "error", str(e)
    def execute_insert(self, query : str, user_input : list):
        # Execute the query and return the results
        print("Executing query: ", query)
        print("With user input: ", user_input)
        if type(user_input) is not list and type(user_input) is not tuple:
            print("Invalid type given to execute_insert!")
            return "Invalid type given to execute_insert"
        try:
            # user_input = [self.clean_query(i) for i in user_input] # This was bad anyways
            if (len(user_input) > 0):
                self.connection = db_con.connect(self.DATABASE_URL, sslmode='require')
                self.cursor = self.connection.cursor()  
                self.cursor.execute(query, user_input)
            else:
                print(f'query={query}')
                self.connection = db_con.connect(self.DATABASE_URL, sslmode='require')
                self.cursor = self.connection.cursor()  
                self.cursor.execute(query)
            self.connection.commit()
            return "success"
        except db_con.errors.UniqueViolation as e:
            print(f'Error {e}')
            self.connection.rollback()
            return e
        except Exception as e:
            print(f'Error {e}')
            print(e)
            self.connection.rollback()
            return "Syntax error. Query unable to be executed."
        
    #new database delete method
    def execute_delete(self, query : str):
        try:
            print(f'query={query}')
            self.connection = db_con.connect(self.DATABASE_URL, sslmode='require')
            self.cursor = self.connection.cursor()  
            self.cursor.execute(query)
            self.connection.commit()
            return "success"
        except db_con.errors.UniqueViolation as e:
            print(f'Error {e}')
            self.connection.rollback()
            return e
        except Exception as e:
            print(f'Error {e}')
            print(e)
            self.connection.rollback()
            return "Syntax error. Query unable to be executed"
        
        
    #new database update method
    def execute_update(self, query : str):
        try:
            print(f'query={query}')
            self.connection = db_con.connect(self.DATABASE_URL, sslmode='require')
            self.cursor = self.connection.cursor()  
            self.cursor.execute(query)
            self.connection.commit()
            return "success"
        except db_con.errors.UniqueViolation as e:
            print(f'Error {e}')
            self.connection.rollback()
            return e
        except Exception as e:
            print(f'Error {e}')
            print(e)
            self.connection.rollback()
            return "Syntax error. Query unable to be executed"
        
    def get_password_hash(self, username):
        # Get the password hash for a user
        username = self.clean_query(username)
        print(f'username={username}')
        self.connection = db_con.connect(self.DATABASE_URL, sslmode='require')
        self.cursor = self.connection.cursor()  
        self.cursor.execute("SELECT password_hash, name, user_role_type, related_org_id FROM rev2.users WHERE user_name = %s", [username])
        res = self.cursor.fetchone()
        print(f'res={res}')
        try:
           return res[0], res[1], res[2]
        except TypeError:
            return None, None, None
    def close_connection(self):
        self.connection.close()
    def clean_query(self, query):
        # Very basic attempt at cleaning up the query
        # I believe psycopg2 does a fair bit of protection
        # but I'm sure it's not 100%
        if isinstance(query, str):
            return query.replace("'", "''")
        return query
    def rollback(self):
        self.connection.rollback()
    def default(self, o):
        # Override the default json serialization for decimal type
        if isinstance(o, Decimal):
            return float(o)
