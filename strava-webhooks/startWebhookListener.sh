#kill existing listeners / ngrok urls
for pid in $(ps aux | grep "index.js" | grep -v grep | awk '{print $2}'); do sudo kill -9 $pid; done
for pid in $(ps aux | grep "ngrok http 1000" | grep -v grep | awk '{print $2}'); do kill -9 $pid; done

#delete old log files
rm logs/ngrok.txt
rm logs/nodejs.txt

#Start nodejs listener
sudo nohup node index.js > logs/nodejs.txt &

#Start ngrok tunnel
domain=$(jq .webhook_callback_url ../data/config.json)
nohup ngrok http --domain=${domain:8} 1000 --log=stdout > logs/ngrok.txt &

#Create event subscription
python setNewEventSubscription.py