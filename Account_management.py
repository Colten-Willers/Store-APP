from cs50 import SQL

db = SQL("sqlite:///store_database.db")

def register(username, password):
     #Errorchecking
     if not username:
         return "No Username Entered."
     if not password:
         return "No Password Entered."
     
     previous_names = db.execute("SELECT username FROM users")
     names = []
     
     for x in previous_names:
         names.append(x['username'])
     if username in names:
         return "Username Already Exists."

     #Registering. 
     db.execute("INSERT INTO users (username, password) VALUES (?, ?)", username, password)
     return "Success"
