import os
from struct import pack  # Fetch credentials from the environment
import sys
from sys import argv
from urllib import response # Print errors to stderr
from flask import Flask, json, request  # The framework for backend & dev server
from flask_cors import CORS, cross_origin
from gevent.pywsgi import WSGIServer  # The production server for backend
import re # Regular expression for validation of input
import hashlib  # For hashing passwords
from psycopg2 import errors
try:
    from backend.database_man import DatabaseConnection
except ModuleNotFoundError:
    from database_man import DatabaseConnection



app = Flask(__name__)  # Create the flask app
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True  # Pretty print json with newlines
cors = CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})


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
        try:
            self.db_key = os.environ["DATABASE_KEY"]
        except KeyError:
            print("== MISSING ENV VAR FOR DATABASE_KEY ==\n\tSet environment variable DATABASE_KEY")
            self.db_key = ""
        
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

        @app.before_request
        def before_request():
            # Require authentication header
            if self.db_key == "":
                return json.jsonify({"error": "No database key set"}), 500
            if request.headers.get('Authentication') is None:
                return json.jsonify({'error': 'No authentication header'}), 401
            # Check if the authentication header is valid
            if request.headers.get('Authentication') != self.db_key:
                return json.jsonify({'error': 'Invalid authentication header'}), 401


        @app.route("/", methods=["GET", "POST"])
        def index():
            if len(self.pepper) > 0: # If pepper is set, then we are in production
                header, res = self.db_connection.execute_query(
                    "SELECT * FROM rev2.users", include_headers=True)
                return pack_header_to_result_obj(header, res)
            else:
                return json.jsonify({"error": "This path is not allowed on production builds"}), 401

        @app.route("/q/<query>", methods=["GET", "POST"])
        def query(query):
            header, res = self.db_connection.execute_query(query, include_headers=True)
            return pack_header_to_result_obj(header, res)
            # return json.jsonify({"header": header, "results": res})
        

        #Re-written to work now
        @app.route("/i", methods=["POST"])
        @cross_origin()
        def insert():
            body = request.get_json()#Get the values from the request body
            table_name = body["table_name"]
            num_columns = body["num_columns"]
            columns = body["columns"]
            values = body["values"]

            query_columns = ""
            query_values = ""
            for i in range(len(columns) - 1): #converts the arrays into strings for the query
                query_columns += (str(columns[i]) + ",")
                query_values += ("%" + "s" + ",")

            query_columns += str(columns[len(columns)-1])
            query_values += ("%" + "s")
            #Builds the query string:
            query = "INSERT INTO " + str(table_name) + " (" + str(query_columns) + ") VALUES (" + query_values + ")"

            print("Got INSERT query: " + str(query))
            user_input = values#Get the values to pass to the request
            res = self.db_connection.execute_insert(query, user_input)
            return json.jsonify({"result": res})
            # return json.jsonify({"header": header, "results": res})
        

        @app.route("/ig/<query>/<csv_values>", methods=["GET", "POST"]) # this broke
        def insert_from_get(query, csv_values):
            user_input = csv_values.split(',')
            for i in range(len(user_input)):
                user_input[i] = user_input[i].replace('@@', ',')
            try:
                res = self.db_connection.execute_insert(query, user_input)
            except errors.SyntaxError:
                return json.jsonify({"error": "Syntax Error"}), 400
            if res == "success":
                return json.jsonify({"result": res})
            else:
                return json.jsonify({"error": res}), 500
            # return json.jsonify({"header": header, "results": res})

        @app.route("/q/<query>/<user_input>", methods=["GET", "POST"])
        def query_with_input(query, user_input):
            header, res = self.db_connection.execute_query(query, user_input, include_headers=True)
            return pack_header_to_result_obj(header, res)
            # return json.jsonify({"header": header, "results": res})
        
        @app.route("/u/login", methods=["POST"])
        def login():
            # Validate the login
            # re.match(r"\$a-zA-Z0-9_]{1,20}", request.form["username"])
            # re.match(r"\$a-zA-Z0-9_]{1,20}", request.form["password"])
            body = request.get_json()
            try:
                un = body["username"]
                pw = body["password"]
                # un = request.form["username"]
                # pw = request.form["password"]
            except KeyError:
                return json.jsonify({"error": "Poorly formatted request"}), 400
            # Execute the query
            password_hash, real_name, user_level = self.db_connection.get_password_hash(un)
            print(password_hash)
            if password_hash is None:
                return json.jsonify({"error": "Incorrect password or username"}), 401
            print("nice")
            try:
                salt, hashed_password = password_hash.split("$")
                hash_val = hashlib.sha256((self.pepper + salt + pw).encode()).hexdigest()
                if hash_val == hashed_password:
                    return json.jsonify({
                        "success": True,
                        "real_name": real_name,
                        "user_level": user_level
                    }), 200
            except:
                pass
            return json.jsonify({"success": False}), 401

        @app.route("/u/register", methods=["POST"])
        def register():
            try:
                body = request.get_json()
                print(body)
                # Validate the registration
                if not re.fullmatch(r"([a-zA-Z0-9_]{1,20}$)", body["username"]):
                    return json.jsonify({"error": "Invalid char or length in username"}), 400
                if not re.fullmatch(r"([a-zA-Z0-9_]{1,20}$)", body["password"]):
                    return json.jsonify({"error": "Invalid char or length in password"}), 400
                if not re.fullmatch( r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", body["email"]):
                    return json.jsonify({"error": "Bad email"}), 400

                """everything below this is super gross
                please make sure to include these fields in your form
                and post requests so i can delete this """
                try:
                    body["name"]
                except:
                    return json.jsonify({"error": "No name provided"})
                try:
                    bio = body["bio"]
                except:
                    bio = ""
                try:
                    phone = body["phone_number"]
                except:
                    phone = "0"
                try:
                    website = body["website"]
                except:
                    website = ""
                try:
                    # role_type = body["user_role_type"]
                    """ 0 = unapproved, 1 = standard user, 2 = admin """
                    role_type = 0 
                except:
                    role_type = "0"
                
                # Create the salt
                salt = os.urandom(16).hex()
                # Hash the password
                hash_val = hashlib.sha256((self.pepper + salt + body["password"]).encode()).hexdigest()
                password_hash = salt + "$" + hash_val
                # Execute the query
                success = self.db_connection.execute_insert("INSERT INTO rev2.users\
                            (user_name,                bio, email,                 phone_number, website, name,                 user_role_type, password_hash) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",
                            (body["username"], bio, body["email"], phone,        website, body["name"], role_type,      password_hash))
                print("success=", success)
                if success == "success":
                    return json.jsonify({"success": True}), 201
                elif "pk_users_user_id" in str(success):
                    return json.jsonify({"error": "Username already exists"}), 400
                else:
                    return json.jsonify({"error": str(success)}), 500
            except KeyError:
                return json.jsonify({"error": "Missing required key in request", "body": body}), 400

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
                
        @app.route("/collector/add-osb", methods=["POST"])
        def add_OSB_Managed_Meadow_Habitat():
            try:
                DatabaseConnection.execute_insert("""INSERT INTO rev2.OSB_Managed_Meadow_Habitat
                    (FID, OBJECTID, Occupancy, Region, Owner, Manager, Meadow_Nam, Prop_Type, Acres,Note,Complex_Na,GlobalID)
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)""", (grab_val(request, "speciescode"), grab_val(request, "collected_date"), grab_val(request, "collection_provenance"), grab_val(request, "id_method"), grab_val(request, "id_person"), grab_val(request, "id_confidence"), grab_val(request, "cleaning_effectiveness"), grab_val(request, "cleaned_weight"), grab_val(request, "collection_history_ref")))
                return json.jsonify({"success": True})
            except:
                self.db_connection.rollback()
                print("error in add collection:", sys.exc_info())
                return json.jsonify({"success": False})

        @app.route("/osb", methods=["GET"])    
        def query_OSB_Managed_Meadow_Habitat():
            res1 = self.db_connection.execute_query("""SELECT a.genus,a.species,a.common_name,b.plant_species_code,c.point_of_collection,d.stand_type,e.owner_username,e.collection_site_name,f.collected_date,g.storage_type,a.species_code,e.collection_site_lat_long,e.region_code,e.accession_code 
                FROM rev2.plant a left join rev2.stand_to_plant_mapping b ON a.species_code = b.plant_species_code left join rev2.stand_collection_history c ON c.stand_plant_map_id = b.stand_plant_id 
                left join rev2.stand d ON b.stand_id = d.stand_id_num left join rev2.site e ON e.site_id = d.encompassing_site_id left join rev2.seed_collection f ON f.col_provenance = e.site_id 
                left join rev2.storage_history g ON g.stored_collection = f.collection_id""", include_headers=False)

            return pack_result_obj(res1)
            
        def pack_result_obj(res1):
     
            features = []
            for i, row in enumerate(res1):
                genus = row[0]
                species = row[1]
                common_name = row[2]
                plant_species_code = row[3]
                point_of_collection = row[4]
                stand_type = row[5]
                owner_username = row[6]
                collection_site_name = row[7]
                collected_date = row[8]
                storage_type = row[9]
                species_code = row[10]
                collection_site_lat_long = row[11]
                region_code = row[12]
                accession_code = row[13]
                
                geometry = {'type':'Point','coordinates':point_of_collection}
                properties = {'FID':i,'genus':genus,'species':species,'stand_type':stand_type,'species_code':species_code,'owner_username':owner_username,'collection_site_name':collection_site_name,'collected_date':collected_date,'storage_type':storage_type,'collection_site_lat_long':collection_site_lat_long,'region_code':region_code,'accession_code':accession_code}
                features.append({'type':'Feature','id':i,'geometry':geometry,'properties':properties})
            # print convert_to_json_string1(features)
            data = {'type':'FeatureCollection','crs':'{"type": "name","properties": {"name": "EPSG:4326"}}','features':features}
            # with codecs.open("C:\\Users\\User\\Desktop\\OSB_Managed_Meadow_Habitat.json","a+",encoding='utf-8') as f:
            #  json.dump(data,f,indent=4,encoding='utf-8',ensure_ascii=False)

            print(data)
            return json.jsonify(data)



        @app.errorhandler(404)
        def not_found(error):
            return json.jsonify({"error": "Not found"}), 404
        @app.errorhandler(500)
        def internal_error(error):
            self.db_connection.rollback() # rollback the transaction
            return json.jsonify({"error": "Internal error"}), 500

        @app.after_request
        def add_header(response):
            """ response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization, Origin, X-Requested-With, Accept'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, PUT, PATCH' """
            print("Authentication:", request.headers.get("Authentication"))
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
