//src: https://developers.strava.com/docs/webhookexample/

'use strict';

// Imports dependencies and sets up http server
const
  express = require('express'),
  bodyParser = require('body-parser'),
  fs = require('fs'),
  path = require('path'),
// creates express http server
  app = express().use(bodyParser.json());


// Get the current directory of the JavaScript file
const currentDir = __dirname;

// Path to your JSON file (one folder level higher)
const filePath = path.join(currentDir, '../data/config.json');

// Sets server port and logs message on success
app.listen(process.env.PORT || 1000, () => console.log('webhook is listening'));

// Creates the endpoint for our webhook
app.post('/webhook', (req, res) => {
  console.log("webhook event received!", req.query, req.body);
  if (req.body.object_type == 'activity') {
        const spawn = require("child_process").spawn;
        const pythonProcess = spawn('python',["webhookReceiver.py", req.body.object_id]);
        
        pythonProcess.stdout.on('data', (data) => {
            console.log('' + data)
            });   
  }
  
  res.status(200).send('EVENT_RECEIVED');
});

// Adds support for GET requests to our webhook
app.get('/webhook', (req, res) => {
  // Parses the query params
  let mode = req.query['hub.mode'];
  let token = req.query['hub.verify_token'];
  let challenge = req.query['hub.challenge'];
  
  // Checks if a token and mode is in the query string of the request
  if (mode && token) {
    readTokenFromFile((err, storedToken) => {
      if (err) {
        res.status(500).send('Error reading token from file');
        return;
      }
      
      // Verifies that the mode and token sent are valid
      if (mode === 'subscribe' && token === storedToken) {     
        // Responds with the challenge token from the request
        console.log('WEBHOOK_VERIFIED');
        res.json({"hub.challenge":challenge});  
      } else {
        // Responds with '403 Forbidden' if verify tokens do not match
        res.sendStatus(403);      
      }
    }
  )}
});

function readTokenFromFile(callback) {
  
  fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) {
      callback(err, null);
      return;
    }

    try {
      const tokens = JSON.parse(data);
      const storedToken = tokens.webhook_verify_token;
      callback(null, storedToken);
    } catch (error) {
      callback(error, null);
    }
  });
}