import zipfile

def zip_files(file_paths, zip_name, file_names):
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for i, file in enumerate(file_paths):
            zipf.write(file, file_names[i])

#Zip files for the stravaWebhook cloud function
files_to_zip = ['config.py', 'main_stravaWebhook.py', 'requirements.txt', 'data/firebaseServiceAccountKey.json']
archive_file_names = ['config.py', 'main.py', 'requirements.txt', 'data/firebaseServiceAccountKey.json']
zip_file_name = 'zipped/stravaWebhook.zip'
zip_files(files_to_zip, zip_file_name, archive_file_names)

#Zip files for the processActivity cloud function
files_to_zip = ['activityFunctions.py', 'config.py', 'googleSheetsAPI.py', 'main_processActivity.py', 'requirements.txt', 'StravaAPI.py', 'data/firebaseServiceAccountKey.json', 'Email2.html', 'smtp.py']
archive_file_names = ['activityFunctions.py', 'config.py', 'googleSheetsAPI.py', 'main.py', 'requirements.txt', 'StravaAPI.py', 'data/firebaseServiceAccountKey.json', 'Email2.html', 'smtp.py']
zip_file_name = 'zipped/processActivity.zip'
zip_files(files_to_zip, zip_file_name, archive_file_names)

#Zip files for the processLatestActivity cloud function
files_to_zip = ['activityFunctions.py', 'config.py', 'googleSheetsAPI.py', 'main_processLatestActivity.py', 'requirements.txt', 'StravaAPI.py', 'data/firebaseServiceAccountKey.json', 'Email2.html', 'smtp.py']
archive_file_names = ['activityFunctions.py', 'config.py', 'googleSheetsAPI.py', 'main.py', 'requirements.txt', 'StravaAPI.py', 'data/firebaseServiceAccountKey.json', 'Email2.html', 'smtp.py']
zip_file_name = 'zipped/processLatestActivity.zip'
zip_files(files_to_zip, zip_file_name, archive_file_names)
