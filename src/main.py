import os
import requests
import check_install

from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from form_handler import complete_impersonation_form

load_dotenv()

# Leer variables de entorno
MONGO_HOST = os.getenv('MONGO_HOST')
MONGO_PORT = os.getenv('MONGO_PORT')
MONGO_USER = os.getenv('MONGO_USER')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
FORM_URL = os.getenv('FORM_URL')
ANALYZED_PROFILE_COLLECTION = 'analyzedprofiles'
USERS_COLLECTION = 'users'
COMPLAINT_COLLECTION = 'complaint'

MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

users = db[USERS_COLLECTION]
analyzed_profiles = db[ANALYZED_PROFILE_COLLECTION]
complaints = db[COMPLAINT_COLLECTION]

profiles_with_no_complaints = analyzed_profiles.find(
    {"complaintId": {"$exists": False}})
for profile in profiles_with_no_complaints:
    complaint_id = profile.get('complaintId')
    if not complaint_id:
        new_complaint = {
            'status': 'Open',
            'actionRequired': False,
            'createdAt': datetime.now(),
            'updatedAt': datetime.now()
        }
        inserted_complaint = complaints.insert_one(new_complaint)
        complaint_id = inserted_complaint.inserted_id
        analyzed_profiles.update_one({'_id': profile['_id']}, {
                                     '$set': {'complaintId': complaint_id}})
    existing_complaint = complaints.find_one({'complaintId': complaint_id})
    current_status = existing_complaint.get('status', None)
    if current_status == 'Created':
        existing_complaint = complaints.update_one(
            {'complaintId': complaint_id},
            {'$set': {'status': 'Open'}}
        )
        # We need to get it twice because the update_one doesn't update pointers
        existing_complaint = complaints.find_one({'complaintId': complaint_id})

    if existing_complaint.get('status', None) == 'Open':
        profile_id = profile['profileId']
        most_similar_company = profile['relatedCompany']
        if not most_similar_company or most_similar_company == '':
            continue

        user_data = users.find_one({
            "$and": [
                {"company.companyName": {"$exists": True}},
                {"company.companyName": most_similar_company},
                {"company.authorizationStatus": "accepted"}
            ]
        })
        pdf_url = user_data.get('company', {}).get(
            'authorizationDocument', {}).get('url', '') if user_data else ''
        if pdf_url == '':
            continue

        # Download the PDF
        pdf_path = '../pdfs'
        response = requests.get(pdf_url)
        if response.status_code != 200:
            continue

        with open(pdf_path, 'wb') as f:
            f.write(response.content)

        completed = complete_impersonation_form(
            FORM_URL, profile_id, most_similar_company, pdf_path)
        if completed:
            complaints.update_one(
                {'complaintId': complaint_id},
                {'$set': {'status': 'Completed'}}
            )
