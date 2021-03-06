from __future__ import absolute_import,division,print_function,unicode_literals

import logging

from builtins import str
from flask import Flask, Blueprint, request, jsonify, Response

from rasa_core.channels.channel import UserMessage, OutputChannel
from rasa_core.channels.rest import HttpInputComponent
from slackclient import SlackClient

logger = logging.getLogger(__name__)

class SlackBot(OutputChannel):
    def __init__(self,slack_verification_token,channel):
        self.slack_verification_token = slack_verification_token
        self.channel = channel
    
    def send_text_message(self,recipient_id,message):
        
        CLIENT = SlackClient(self.slack_verification_token)
        CLIENT.api_call('chat.postMessage',channel=self.channel,text = message,as_user=True)


class SlackInput(HttpInputComponent):
    def __init__(self,slack_dev_token,slack_verification_token,slack_client,debug_mode):
        self.slack_dev_token = slack_dev_token
        self.slack_client = slack_client
        self.debug_mode = debug_mode
        self.slack_verification_token = slack_verification_token

    def blueprint(self,on_new_message):
        slack_webhook = Blueprint('slack_webhook',__name__)

        @slack_webhook.route('/',methods = ['GET'])
        def health():
            return jsonify({'status':'Ok'})
        

        @slack_webhook.route('/slack/events',methods=['POST'])
        def event():
            if request.json.get('type') == 'url_verification':
                return request.json.get('challenge'),200

            if request.json.get('token') == self.slack_client and request.json.get('type') == 'event_callback':
                data = request.json
                messaging_events = data.get('event')

                channel = messaging_events.get('channel')
                user = messaging_events.get('user')
                text = messaging_events.get('text')
                bot = messaging_events.get('bot_id')
                if bot == None :
                    on_new_message(UserMessage(text,SlackBot(self.slack_verification_token,channel)))
                
            return Response(),200

        return slack_webhook