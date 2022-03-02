import os
from struct import pack  # Fetch credentials from the environment
import sys
from sys import argv
from urllib import response # Print errors to stderr
from flask import Flask, json, request  # The framework for backend & dev server
from gevent.pywsgi import WSGIServer  # The production server for backend
import re # Regular expression for validation of input
import hashlib  # For hashing passwords
from psycopg2 import errors
try:
    from backend.database_man import DatabaseConnection
except ModuleNotFoundError:
    from database_man import DatabaseConnection



app = Flask(__name__)  # Create the flask app
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True  # Pretty print json with newlines


def grab_val(request, value):
    try:
        return request.form[value]
    except KeyError:
        return None

class BackendRESTAPI():
    def __init__(self, port_num=5440, norun=False):
        self.db_connection = DatabaseConnection()
        self.port_number    = port_num
        self.host           = "localhost"
        self.devenv         = True
        try:
            self.pepper = os.environ["PEPPER"]
        except KeyError:
            print("== MISSING ENV VAR FOR PEPPER ==\n\tSet environment variable PEPPER")
            self.pepper = ""
        
        def pack_header_to_result_obj(headers, result_lsit):
            res_obj = {'headers': headers}
            res_obj['data'] = []
            for i in range(len(result_lsit)):
                res_obj['data'].append({})
                if type(result_lsit) is not str:
                    for j in range(len(result_lsit[i])):
                        res_obj['data'][i][headers[j]] = result_lsit[i][j]
                else:
                    res_obj['error'] = result_lsit
                    del res_obj['data']
                    break
            print(res_obj)
            return json.jsonify(res_obj)

        @app.route("/", methods=["GET"])
        def index():
            header, res = self.db_connection.execute_query(
                "SELECT * FROM rev2.users", include_headers=True)
            return pack_header_to_result_obj(header, res)

        @app.route("/q/<query>", methods=["GET"])
        def query(query):
            header, res = self.db_connection.execute_query(query, include_headers=True)
            return pack_header_to_result_obj(header, res)
            # return json.jsonify({"header": header, "results": res})
        
        @app.route("/i/<query>", methods=["POST"]) # this broke
        def insert(query):
            header, res = self.db_connection.execute_insert(query, '')
            return pack_header_to_result_obj(header, res)
            # return json.jsonify({"header": header, "results": res})
        
        @app.route("/i/<query>/<csv_values>", methods=["POST"])
        def insert_with_input(query, csv_values):
            user_input = csv_values.split(',')
            res = self.db_connection.execute_insert(query, user_input)
            return json.jsonify({"success": res })
            # return json.jsonify({"header": header, "results": res})

        @app.route("/q/<query>/<user_input>", methods=["GET"])
        def query_with_input(query, user_input):
            header, res = self.db_connection.execute_query(query, user_input, include_headers=True)
            return pack_header_to_result_obj(header, res)
            # return json.jsonify({"header": header, "results": res})
        
        @app.route("/u/login", methods=["POST"])
        def login():
            # Validate the login
            re.match(r"\$a-zA-Z0-9_]{1,20}", request.form["username"])
            re.match(r"\$a-zA-Z0-9_]{1,20}", request.form["password"])
            un = request.form["username"]
            pw = request.form["password"]
            # Execute the query
            password_hash = self.db_connection.get_password_hash(un)
            if password_hash is None:
                return json.jsonify({"error": "Incorrect password or username"})
            print("nice")
            try:
                salt, hashed_password = password_hash.split("$")
                hash_val = hashlib.sha256((self.pepper + salt + pw).encode()).hexdigest()
                if hash_val == hashed_password:
                    return json.jsonify({"success": True})
            except:
                pass
            return json.jsonify({"success": False})

        @app.route("/u/register", methods=["POST"])
        def register():
            try:
                print(request.form)
                # Validate the registration
                if not re.fullmatch(r"([a-zA-Z0-9_]{1,20}$)", request.form["username"]):
                    return json.jsonify({"error": "Invalid char or length in username"})
                if not re.fullmatch(r"([a-zA-Z0-9_]{1,20}$)", request.form["password"]):
                    return json.jsonify({"error": "Invalid char or length in password"})
                if not re.fullmatch( r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", request.form["email"]):
                    return json.jsonify({"error": "Bad email"})

                """everything below this is super gross
                please make sure to include these fields in your form
                and post requests so i can delete this """
                try:
                    request.form["name"]
                except:
                    return json.jsonify({"error": "No name provided"})
                try:
                    bio = request.form["bio"]
                except:
                    bio = ""
                try:
                    phone = request.form["phone_number"]
                except:
                    phone = "0"
                try:
                    website = request.form["website"]
                except:
                    website = ""
                try:
                    # role_type = request.form["user_role_type"]
                    """ 0 = unapproved, 1 = standard user, 2 = admin """
                    role_type = 0 
                except:
                    role_type = "0"
                
                # Create the salt
                salt = os.urandom(16).hex()
                # Hash the password
                hash_val = hashlib.sha256((self.pepper + salt + request.form["password"]).encode()).hexdigest()
                password_hash = salt + "$" + hash_val
                # Execute the query
                success = self.db_connection.execute_insert("INSERT INTO rev2.users\
                            (user_name,                bio, email,                 phone_number, website, name,                 user_role_type, password_hash) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",
                            (request.form["username"], bio, request.form["email"], phone,        website, request.form["name"], role_type,      password_hash))
                if success:
                    return json.jsonify({"success": True})
                else:
                    return json.jsonify({"error": "Username already exists"})
            except KeyError:
                return json.jsonify({"error": "Missing required key in request"})

        @app.route("/add/farm", methods=["POST"])
        def add_farm():
            print(request.headers)

            try:
                farm_name = request.form["farm_name"]
            except KeyError:
                return json.jsonify({"error": "No farm name provided"})
            try:
                farm_location = request.form["farm_location"]
            except KeyError:
                farm_location = ""
            try:
                contact_email = request.form["contact_email"]
            except KeyError:
                contact_email = ""
            try:
                contact_phone = request.form["contact_phone_number"]
            except KeyError:
                contact_phone = ""
                
            try: 
                success = self.db_connection.execute_insert("INSERT INTO rev2.farms (farm_name,  contact_email, contact_phone_number) VALUES (%s, %s, %s)",
                                                                          (farm_name, contact_email, contact_phone))
                if success:
                    return json.jsonify({"success": True})
                else:
                    return json.jsonify({"error": "Farm name already exists"})
            except:
                self.db_connection.connection.rollback()
                print("error in add farm: ", sys.exc_info())
                return json.jsonify({"error": "Internal error occured"})

        @app.route("/collector/add-collection", methods=["POST"])
        def add_collection():
            try:
                DatabaseConnection.execute_insert("""INSERT INTO rev2.seed_collection
                    (col_species_code, col_collected_date, col_provenance, id_method, id_person_name, id_confidence, cleaning_effectiveness, cleaned_weight, collection_history_reference)
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)""", (grab_val(request, "speciescode"), grab_val(request, "collected_date"), grab_val(request, "collection_provenance"), grab_val(request, "id_method"), grab_val(request, "id_person"), grab_val(request, "id_confidence"), grab_val(request, "cleaning_effectiveness"), grab_val(request, "cleaned_weight"), grab_val(request, "collection_history_ref")))
                return json.jsonify({"success": True})
            except:
                self.db_connection.rollback()
                print("error in add collection:", sys.exc_info())
                return json.jsonify({"success": False})

        @app.after_request
        def add_header(response):
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization, Origin, X-Requested-With, Accept'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, PUT, PATCH'
            return response


        # Start the server
        if not norun:
            if self.devenv:
                # Development server
                app.run(host=self.host, port=self.port_number, debug=True, use_reloader=True)
            else:
                # Production server
                http_server = WSGIServer((self.host, self.port_number), app)
                http_server.serve_forever()


def get_app(port):
    return BackendRESTAPI(port_num=int(port), norun=True)

try: 
    application = get_app(os.environ['PORT'])
except KeyError:
    application = get_app(8080)

if __name__ == "__main__":
    app.run(host=application.host, port=application.port_number, debug=True, use_reloader=True)
