import bcrypt
from pymongo import MongoClient
import datetime
from getpass import getpass
from traits_gen import generate_traits_from_description

client = MongoClient("mongodb://localhost:27017/")
db = client["edgecloud_project"]

users = db["users"]

users.create_index("username", unique=True, background=True)

def create_user():
    # check if username is available
    while True:
        username = input("\nEnter username: ").strip().lower()

        if not username:
            print("Username cannot be empty.")
            continue

        if users.find_one({"username": username}):
            print("Username already in use, try another.")
        else:
            print("Username available.")
            break

    # password selection and hashing
    password = getpass("Enter a password: ")

    if len(password) < 4:
        print("Password must be at least 4 characters.")
        return

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    # ask for user description
    description = input("Describe yourself in few lines: ").strip()

    # updating user in db
    new_user = {
        "username": username,
        "password_hash": hashed_pw.decode("utf-8"),
        "raw_description": description,
        "traits": None,
        "created_at": datetime.datetime.utcnow(),
        "last_login": None
    }

    insert_result = users.insert_one(new_user)

    print(f"\n🎉 User created successfully with ID: {insert_result.inserted_id}\n")
    return insert_result.inserted_id

# -----------------------------------------------------------------------------------------

def login():

    username = input("\nEnter username: ").strip().lower()
    password = getpass("Enter password: ")

    # Look up user
    user = users.find_one({"username": username})

    if not user:
        print("No such user. Try again.")
        return None

    # Check password match
    stored_hash = user["password_hash"].encode("utf-8")

    if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
        print("Login successful!\nLoading profile...")

        # Update last login timestamp
        users.update_one(
            {"username": username},
            {"$set": {"last_login": datetime.datetime.utcnow()}}
        )

        traits = user.get("traits")
        if traits is None and user.get("raw_description"):
            print("Generating your AI profile...")
            traits = generate_traits_from_description(user["raw_description"])

            users.update_one(
                {"_id": user["_id"]},
                {"$set": {"traits": traits}}
            )

        # Return useful info (not password hash)
        return {
            "user_id": str(user["_id"]),
            "username": user["username"],
            "traits": traits,
            "raw_description": user["raw_description"]
        }

    else:
        print("Incorrect password. Try again.")
        return None

# ----------------------------------------------------------------------------

def change_password(username: str):
    user = users.find_one({"username": username.lower()})
    if not user:
        print("User not found.")
        return

    old_pw = getpass("Enter current password: ")
    if not bcrypt.checkpw(old_pw.encode("utf-8"), user["password_hash"].encode("utf-8")):
        print("Incorrect current password.")
        return

    new_pw = getpass("Enter new password: ")
    if len(new_pw) < 4:
        print("New password too short.")
        return

    new_hash = bcrypt.hashpw(new_pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    users.update_one({"_id": user["_id"]}, {"$set": {"password_hash": new_hash}})
    print("Password updated.")

# --------------------------------------------------------------------------------------------------

def login_loop():
    while True:
        result  = login()
        if result:
            return result

# -------------------------------------
