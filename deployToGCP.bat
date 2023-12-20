REM Read variables from file
for /F "delims=" %%i in (zipped\deploymentConfig.ini) do set %%i

REM Create zip files from source code
python zipped/ZipFiles.py

REM Upload source code
cmd /c gsutil cp zipped/stravaWebhook.zip 			gs://%GCP_Bucket%/stravaWebhook/
cmd /c gsutil cp zipped/processActivity.zip 		gs://%GCP_Bucket%/processActivity/
cmd /c gsutil cp zipped/processLatestActivity.zip 	gs://%GCP_Bucket%/processLatestActivity/
cmd /c gsutil cp zipped/sendReminders.zip 			gs://%GCP_Bucket%/sendReminders/

REM Redeploy functions
start cmd /c gcloud functions deploy stravaWebhook 			--gen2 --source=gs://%GCP_Bucket%/stravaWebhook/stravaWebhook.zip 					--runtime=python311 --trigger-http 																		--region=%Region% --entry-point=hello_http
start cmd /c gcloud functions deploy processActivity 		--gen2 --source=gs://%GCP_Bucket%/processActivity/processActivity.zip 				--runtime=python311 --trigger-http 																		--region=%Region% --entry-point=hello_http
start cmd /c gcloud functions deploy processLatestActivity 	--gen2 --source=gs://%GCP_Bucket%/processLatestActivity/processLatestActivity.zip 	--runtime=python311 --trigger-http 																		--region=%Region% --entry-point=hello_http
start cmd /c gcloud functions deploy sendReminders 			--gen2 --source=gs://%GCP_Bucket%/sendReminders/sendReminders.zip 					--runtime=python311 --trigger-resource sendReminderTopic --trigger-event google.pubsub.topic.publish 	--region=%Region% --entry-point main 		--timeout 20s
