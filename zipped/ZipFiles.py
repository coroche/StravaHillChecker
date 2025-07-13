import zipfile

def zip_files(file_paths, zip_name, file_names):
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for i, file in enumerate(file_paths):
            zipf.write(file, file_names[i])

#Zip files for the stravaWebhook cloud function
files_to_zip = ['utils/__init__.py', 'utils/decorators.py', 'data/config.py', 'data/hillsDAO.py', 'data/userDAO.py', 'main_stravaWebhook.py', 'data/__init__.py', 'requirements.txt', 'data/firebaseServiceAccountKey.json']
archive_file_names = ['utils/__init__.py', 'utils/decorators.py', 'data/config.py', 'data/hillsDAO.py', 'data/userDAO.py', 'main.py', 'data/__init__.py', 'requirements.txt', 'data/firebaseServiceAccountKey.json']
zip_file_name = 'zipped/stravaWebhook.zip'
zip_files(files_to_zip, zip_file_name, archive_file_names)

#Zip files for the processActivity cloud function
files_to_zip = ['utils/__init__.py', 'utils/decorators.py', 'library/activityFunctions.py', 'data/config.py', 'data/hillsDAO.py', 'data/userDAO.py', 'library/googleSheetsAPI.py', 'main_processActivity.py', 'requirements.txt', 'library/StravaAPI.py', 'data/firebaseServiceAccountKey.json', 'data/html_templates/Email.html', 'library/smtp.py', 'data/__init__.py', 'library/__init__.py']
archive_file_names = ['utils/__init__.py', 'utils/decorators.py', 'library/activityFunctions.py', 'data/config.py', 'data/hillsDAO.py', 'data/userDAO.py', 'library/googleSheetsAPI.py', 'main.py', 'requirements.txt', 'library/StravaAPI.py', 'data/firebaseServiceAccountKey.json', 'data/html_templates/Email.html', 'library/smtp.py', 'data/__init__.py', 'library/__init__.py']
zip_file_name = 'zipped/processActivity.zip'
zip_files(files_to_zip, zip_file_name, archive_file_names)

#Zip files for the sendReminders cloud function
files_to_zip = ['utils/__init__.py', 'utils/decorators.py', 'library/activityFunctions.py', 'data/config.py', 'data/hillsDAO.py', 'data/userDAO.py', 'library/googleSheetsAPI.py', 'main_sendReminders.py', 'requirements.txt', 'library/StravaAPI.py', 'data/firebaseServiceAccountKey.json', 'data/html_templates/FollowUpEmail.html', 'library/smtp.py', 'data/__init__.py', 'library/__init__.py']
archive_file_names = ['utils/__init__.py', 'utils/decorators.py', 'library/activityFunctions.py', 'data/config.py', 'data/hillsDAO.py', 'data/userDAO.py', 'library/googleSheetsAPI.py', 'main.py', 'requirements.txt', 'library/StravaAPI.py', 'data/firebaseServiceAccountKey.json', 'data/html_templates/FollowUpEmail.html', 'library/smtp.py', 'data/__init__.py', 'library/__init__.py']
zip_file_name = 'zipped/sendReminders.zip'
zip_files(files_to_zip, zip_file_name, archive_file_names)

#Zip files for the subscribe cloud function
files_to_zip = ['utils/__init__.py', 'utils/decorators.py', 'data/config.py', 'main_subscribe.py', 'requirements.txt', 'data/firebaseServiceAccountKey.json', 'data/html_templates/message.html', 'data/html_templates/subscribeForm.html', 'data/html_templates/verificationEmail.html', 'library/smtp.py', 'data/__init__.py', 'library/__init__.py']
archive_file_names = ['utils/__init__.py', 'utils/decorators.py', 'data/config.py', 'main.py', 'requirements.txt', 'data/firebaseServiceAccountKey.json', 'data/html_templates/message.html', 'data/html_templates/subscribeForm.html', 'data/html_templates/verificationEmail.html', 'library/smtp.py', 'data/__init__.py', 'library/__init__.py']
zip_file_name = 'zipped/subscribe.zip'
zip_files(files_to_zip, zip_file_name, archive_file_names)

#Zip files for the getMap cloud function
files_to_zip = ['utils/__init__.py', 'utils/decorators.py', 'data/config.py', 'data/hillsDAO.py', 'data/userDAO.py', 'main_getMap.py', 'requirements.txt', 'data/firebaseServiceAccountKey.json', 'data/html_templates/map.html', 'data/html_templates/message.html', 'data/__init__.py', 'library/__init__.py', 'library/googleSheetsAPI.py']
archive_file_names = ['utils/__init__.py', 'utils/decorators.py', 'data/config.py', 'data/hillsDAO.py', 'data/userDAO.py', 'main.py', 'requirements.txt', 'data/firebaseServiceAccountKey.json', 'data/html_templates/map.html', 'data/html_templates/message.html', 'data/__init__.py', 'library/__init__.py', 'library/googleSheetsAPI.py']
zip_file_name = 'zipped/getMap.zip'
zip_files(files_to_zip, zip_file_name, archive_file_names)

#Zip files for the getChart cloud function
files_to_zip = ['utils/__init__.py', 'utils/decorators.py', 'data/config.py', 'data/hillsDAO.py', 'data/userDAO.py', 'main_getChart.py', 'requirements.txt', 'data/firebaseServiceAccountKey.json', 'data/html_templates/pieChart.html', 'data/html_templates/message.html', 'data/__init__.py', 'library/__init__.py']
archive_file_names = ['utils/__init__.py', 'utils/decorators.py', 'data/config.py', 'data/hillsDAO.py', 'data/userDAO.py', 'main.py', 'requirements.txt', 'data/firebaseServiceAccountKey.json', 'data/html_templates/pieChart.html', 'data/html_templates/message.html', 'data/__init__.py', 'library/__init__.py']
zip_file_name = 'zipped/getChart.zip'
zip_files(files_to_zip, zip_file_name, archive_file_names)

#Zip files for the stravaAuth cloud function
files_to_zip = ['main_stravaAuth.py', 'requirements.txt', 'data/firebaseServiceAccountKey.json', 'data/__init__.py', 'data/userDAO.py', 'data/config.py', 'data/hillsDAO.py', 'data/html_templates/message.html', 'library/__init__.py', 'library/StravaAPI.py', 'library/googleSheetsAPI.py', 'utils/__init__.py', 'utils/decorators.py']
archive_file_names = ['main.py', 'requirements.txt', 'data/firebaseServiceAccountKey.json', 'data/__init__.py', 'data/userDAO.py', 'data/config.py', 'data/hillsDAO.py', 'data/html_templates/message.html', 'library/__init__.py', 'library/StravaAPI.py', 'library/googleSheetsAPI.py', 'utils/__init__.py', 'utils/decorators.py']
zip_file_name = 'zipped/stravaAuth.zip'
zip_files(files_to_zip, zip_file_name, archive_file_names)