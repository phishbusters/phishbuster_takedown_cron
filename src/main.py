import os
import requests
import check_install
import uuid

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
COMPLAINT_COLLECTION = 'complaints'
PHISHING_STATS_COLLECTION = 'phishingstats'

MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

users = db[USERS_COLLECTION]
analyzed_profiles = db[ANALYZED_PROFILE_COLLECTION]
complaints = db[COMPLAINT_COLLECTION]
phishing_stats = db[PHISHING_STATS_COLLECTION]


def get_stat_by_date(date):
    start_of_day = datetime(date.year, date.month, date.day, 0, 0, 0)
    end_of_day = datetime(date.year, date.month, date.day, 23, 59, 59)

    existing_stat = phishing_stats.find_one({
        'date': {
            '$gte': start_of_day,
            '$lte': end_of_day
        }
    })

    return existing_stat


def create_or_update_stat(date, field_to_update):
    existing_stat = get_stat_by_date(date)

    if existing_stat:
        print('Updating existing stat')
        phishing_stats.update_one(
            {'_id': existing_stat['_id']},
            {'$inc': {field_to_update: 1}}
        )
        return phishing_stats.find_one({'_id': existing_stat['_id']})
    else:
        print('Creating new stat')
        new_stat = {
            'date': date,
            'phishingChatsDetected': 0,
            'fakeProfilesDetected': 0,
            'complaintsClosed': 0,
            'complaintsCreated': 0,
            'complaintsInProgress': 0,
            field_to_update: 1
        }
        phishing_stats.insert_one(new_stat)
        return new_stat


def start_process():
    print('Starting process')
    complaints_to_process = complaints.find({"status": "Created"})

    print('Complaints found: ', complaints.count_documents(
        {"status": "Created"}))
    for complaint in complaints_to_process:
        complaint_id = complaint.get('_id', None)
        if complaint_id is None:
            print('Complaint without complaintId')
            continue

        current_status = complaint.get('status', 'Created')
        if current_status == 'Created':
            profiles = analyzed_profiles.find({'complaintId': complaint_id})
            profiles_count = analyzed_profiles.count_documents(
                {'complaintId': complaint_id})
            if profiles_count == 0:
                print('No profile ids found')
                continue

            for profile in profiles:
                print('Next profile id: ', profile.get('profileId', ''))
                related_company_name = profile.get('relatedCompanyName', '')
                if not related_company_name or related_company_name == '':
                    print('No company name found')
                    continue

                user_data = users.find_one({
                    "$and": [
                        {"company.companyName": {"$exists": True}},
                        {"company.companyName": related_company_name},
                        {"company.authorizationStatus": "accepted"}
                    ]
                })
                pdf_url = user_data.get('company', {}).get(
                    'authorizationDocument', {}).get('url', '') if user_data else ''
                if pdf_url == '':
                    print('No pdf url found')
                    continue

                pdf_directory = 'pdfs/'
                pdf_filename = uuid.uuid4().hex + '.pdf'
                pdf_path = os.path.join(pdf_directory, pdf_filename)
                if not os.path.exists(pdf_directory):
                    os.makedirs(pdf_directory)

                print('Downloading PDF')
                response = requests.get(pdf_url)
                if response.status_code != 200:
                    continue

                with open(pdf_path, 'wb') as f:
                    f.write(response.content)
                print('PDF downloaded and wrote to disk')
                completed = complete_impersonation_form(
                    FORM_URL, profile.get('profileId', ''), related_company_name, pdf_path)
                if completed:
                    print('Updating complaint status')
                    complaints.update_one(
                        {'_id': complaint_id},
                        {'$set': {'status': 'Open', 'updatedAt': datetime.now()}}
                    )
                    print('Updating stats database')
                    create_or_update_stat(
                        datetime.now(), 'complaintsInProgress')


if __name__ == '__main__':
    start_process()
