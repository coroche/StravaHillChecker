@echo off

REM Read variables from file
for /F "delims=" %%i in (zipped\deploymentConfig.ini) do set %%i

REM Set root for python tests
set PYTHONPATH=%CD%

echo Running tests...
REM loop over all test files
pytest Tests -x
if %ERRORLEVEL% NEQ 0 (
    pause
    exit /b
    )

echo All tests passed! Proceeding with deployment.

echo Zipping files...
REM Create zip files from source code
python zipped/ZipFiles.py

echo Uploading files to bucket...
REM Upload source code
cmd /c gsutil cp zipped/stravaWebhook.zip 			gs://%GCP_Bucket%/stravaWebhook/
cmd /c gsutil cp zipped/processActivity.zip 		gs://%GCP_Bucket%/processActivity/
cmd /c gsutil cp zipped/sendReminders.zip 			gs://%GCP_Bucket%/sendReminders/
cmd /c gsutil cp zipped/subscribe.zip 			    gs://%GCP_Bucket%/subscribe/
cmd /c gsutil cp zipped/getMap.zip 			        gs://%GCP_Bucket%/getMap/
cmd /c gsutil cp zipped/getChart.zip 			    gs://%GCP_Bucket%/getChart/

echo redeploying functions...
REM Redeploy functions
start cmd /c gcloud functions deploy stravaWebhook 			--gen2 --source=gs://%GCP_Bucket%/stravaWebhook/stravaWebhook.zip 					--runtime=python311 --trigger-http 																		--region=%Region% --entry-point=hello_http
start cmd /c gcloud functions deploy processActivity 		--gen2 --source=gs://%GCP_Bucket%/processActivity/processActivity.zip 				--runtime=python311 --trigger-http 																		--region=%Region% --entry-point=hello_http
start cmd /c gcloud functions deploy sendReminders 			--gen2 --source=gs://%GCP_Bucket%/sendReminders/sendReminders.zip 					--runtime=python311 --trigger-resource sendReminderTopic --trigger-event google.pubsub.topic.publish 	--region=%Region% --entry-point main            --timeout 20s
start cmd /c gcloud functions deploy subscribe 	            --gen2 --source=gs://%GCP_Bucket%/subscribe/subscribe.zip 	                        --runtime=python311 --trigger-http 																		--region=%Region% --entry-point=gcf_entry_point
start cmd /c gcloud functions deploy getMap 	            --gen2 --source=gs://%GCP_Bucket%/getMap/getMap.zip 	                            --runtime=python311 --trigger-http 																		--region=%Region% --entry-point=gcf_entry_point
start cmd /c gcloud functions deploy getChart 	            --gen2 --source=gs://%GCP_Bucket%/getChart/getChart.zip 	                        --runtime=python311 --trigger-http 																		--region=%Region% --entry-point=gcf_entry_point
