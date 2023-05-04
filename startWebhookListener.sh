#kill existing listeners / ngrok urls
for pid in $(ps aux | grep "strava-webhooks/index.js" | grep -v grep | awk '{print $2}'); do sudo kill -9 $pid; done
for pid in $(ps aux | grep "ngrok http 1000" | grep -v grep | awk '{print $2}'); do kill -9 $pid; done

#delete old log files
rm logs/ngrok.txt
rm logs/nodejs.txt

#Start nodejs listener
sudo nohup node strava-webhooks/index.js > logs/nodejs.txt &

#Start ngrok tunnel
nohup ngrok http 1000 --log=stdout > logs/ngrok.txt &

#Grab public ngrok URL
python updateCallbackUrl.py

#Wait until Strava app is updated
domain=$(jq .webhook_callback_url config.json)
domain="\"""${domain:9}"
printf "\nUpdate your Strava app with the new authorization domain\n"
printf "https://www.strava.com/settings/api\n"
printf "Auth domain: $domain\n"
read -p "Once updated, press enter to continue"

#Create event subscription
python setNewEventSubscription.py