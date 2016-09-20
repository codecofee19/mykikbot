from flask import Flask, request, Response
import os
from kik import KikApi, Configuration
from kik.messages import messages_from_json, TextMessage, PictureMessage, StartChattingMessage
from clarifai.client import ClarifaiApi 
KIK_USERNAME = os.environ['KIK_USERNAME'] 
KIK_API_KEY = os.environ['KIK_API_KEY'] 
WEBHOOK =  os.environ['WEBHOOK']
app = Flask(__name__)
kik = KikApi(KIK_USERNAME, KIK_API_KEY)
kik.set_configuration(Configuration(webhook=WEBHOOK))
clarifai_api = ClarifaiApi() 

@app.route('/', methods=['POST'])
def incoming():
    if not kik.verify_signature(request.headers.get('X-Kik-Signature'), request.get_data()):
        return Response(status=403) 

    messages = messages_from_json(request.json['messages'])
    for message in messages:
        if isinstance(message, StartChattingMessage):
            kik.send_messages([
            TextMessage(
            to=message.from_user,
            chat_id = message.chat_id,
            body='Hello Im the Mad Lib Bot! Send me pictures and Ill tell a wacky random story based on the tags of the image'
            ),
            ])  

        elif isinstance(message, PictureMessage):
            result = clarifai_api.tag_image_urls(message.pic_url)
            one = result["results"]
            two = one[0]
            three = two['result']
            four = three['tag']
            five = four['classes']
	    kik.send_messages([
	    TextMessage(
	    to=message.from_user,
	    chat_id=message.chat_id,
	    body=five[1]
	    ),

	   ])

    return Response(status=200)

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
