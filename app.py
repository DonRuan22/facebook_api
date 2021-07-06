from flask import Flask, request
import requests
import json
import config
import logging
import os



app = Flask(__name__)
SECRET_KEY = 'b8d43ce14d05828c73257013c8e67b95'
#PAGE_ACCESS_TOKEN = "EAACCGdwRfhABANBdZCtGQWTBPWLiH2wnRLreO6vZAtP6WZBvTAsmDkCVYkVD7fmUtGu5ARlGtI1tV8nhSyZCjy0sHGfKRNZAJcemHpaQ0glcfqITZBxuZA6Y6RrehcrgWvZCzAWVT9T3Rln5lOMArSy9A64HPOg19AT9T2PyWWdZAQdeFTuESLpqS"
VERIFY_TOKEN = 'rasa-don'



#Function to access the Sender API
def callSendAPI(senderPsid, response, type_response='message'):
    #PAGE_ACCESS_TOKEN = config.PAGE_ACCESS_TOKEN
    if(type_response == 'message'):
        payload = {
        'recipient': {'id': senderPsid},
        'message': response,
        'messaging_type': 'RESPONSE'
        }
    if(type_response == "sender_action"):
        payload = {
        'recipient': {'id': senderPsid},
        "sender_action": "typing_on",
        }    
    headers = {'content-type': 'application/json'}

    url = 'https://graph.facebook.com/v2.6/me/messages?access_token={}'.format(os.environ.get('PAGE_ACCESS_TOKEN'))
    r = requests.post(url, json=payload, headers=headers)
    logging.warning(r.request.headers) 
    logging.warning(r.url) 
    logging.warning(r.content) 
    logging.warning(r.__dict__) 
    print(r.text)



#Function for handling a message from MESSENGER
def handleMessage(senderPsid, receivedMessage):
    print("handle message")
    callSendAPI(senderPsid, "","sender_action")
    
    #check if received message contains text
    if 'text' in receivedMessage:
        payload = {'sender': senderPsid,'message': receivedMessage['text']}
        #payload_json = json.loads(payload)
        #print(payload)
        #response_rasa = requests.post('https://don-edml6m2f3a-uc.a.run.app/webhooks/rest/webhook', json = payload)
        #print(response_rasa.json()[0]["text"])
        response = {"text": 'You just sent: {}'.format(receivedMessage['text']) }
        #response = {"text": response_rasa.json()[0]["text"] }

        callSendAPI(senderPsid, response)
        #logging.warning(response)
    else:
        response = {"text": 'This chatbot only accepts text messages'}
        callSendAPI(senderPsid, response)




@app.route('/', methods=["GET", "POST"])
def home():

    return 'HOME'

@app.route('/webhooks/facebook/webhook', methods=["GET", "POST"])
def index():
    if request.method == 'GET':
        #do something.....
        #VERIFY_TOKEN = config.VERIFY_TOKEN

        if 'hub.mode' in request.args:
            mode = request.args.get('hub.mode')
            print(mode)
        if 'hub.verify_token' in request.args:
            token = request.args.get('hub.verify_token')
            print(token)
        if 'hub.challenge' in request.args:
            challenge = request.args.get('hub.challenge')
            print(challenge)

        if 'hub.mode' in request.args and 'hub.verify_token' in request.args:
            mode = request.args.get('hub.mode')
            token = request.args.get('hub.verify_token')

            if mode == 'subscribe' and token == VERIFY_TOKEN:
                print('WEBHOOK VERIFIED')

                challenge = request.args.get('hub.challenge')

                return challenge, 200
            else:
                return 'ERROR', 403

        return 'SOMETHING', 200


    if request.method == 'POST':
        #do something.....
        #VERIFY_TOKEN = config.VERIFY_TOKEN
        if 'hub.mode' in request.args:
            mode = request.args.get('hub.mode')
            print(mode)
        if 'hub.verify_token' in request.args:
            token = request.args.get('hub.verify_token')
            print(token)
        if 'hub.challenge' in request.args:
            challenge = request.args.get('hub.challenge')
            print(challenge)

        if 'hub.mode' in request.args and 'hub.verify_token' in request.args:
            mode = request.args.get('hub.mode')
            token = request.args.get('hub.verify_token')

            if mode == 'subscribe' and token == VERIFY_TOKEN:
                print('WEBHOOK VERIFIED')

                challenge = request.args.get('hub.challenge')

                return challenge, 200
            else:
                return 'ERROR', 403

        #do something else
        data = request.data
        body = json.loads(data.decode('utf-8'))

        if 'object' in body and body['object'] == 'page':
            entries = body['entry']
            for entry in entries:
                webhookEvent = entry['messaging'][0]
                print(webhookEvent)

                senderPsid = webhookEvent['sender']['id']
                print('Sender PSID: {}'.format(senderPsid))

                if 'message' in webhookEvent:
                    handleMessage(senderPsid, webhookEvent['message'])

                return 'EVENT_RECEIVED', 200
        else:
            return 'ERROR', 404



if __name__ == '__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get("PORT", 5005)), debug=True)
