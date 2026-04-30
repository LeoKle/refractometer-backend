import os
from dotenv import load_dotenv
from pymongo import MongoClient


def connect_to_mongodb():
    try:
        load_dotenv()
        mongo_uri = os.getenv("MONGO_URI")

        client = MongoClient(mongo_uri)

        print("Connected successfully to MongoDB!")
        print("Databases:", client.list_database_names())

        return client
    except Exception as e:
        print("Could not connect to MongoDB:", e)


client = connect_to_mongodb()

# Perform operations using the client, like accessing a specific database
db = client.get_database("refractometer")

spectrums_collection = db.get_collection("spectrums")

# Iterate over all documents in the spectrums collection
for spectrum in spectrums_collection.find():
    if "wavelengths" in spectrum:
        # Multiply the wavelengths array by 1e-9
        updated_wavelengths = [w * 1e-9 for w in spectrum["wavelengths"]]

        # Update the document in the database
        spectrums_collection.update_one(
            {"_id": spectrum["_id"]},  # Match the document by its _id
            {"$set": {"wavelengths": updated_wavelengths}},  # Set the updated wavelengths array
        )
        print(f"Updated document with _id: {spectrum['_id']}")
