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

words = [] 
counter = 0 

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
            body='Hello Im the Mad Lib Bot! Send me pictures and Ill tell a wacky random story based on the tags of the image. Ill take the first 5 pics :)'
            ),
            ])  

        elif isinstance(message, PictureMessage):
            global counter
            global words
            result = clarifai_api.tag_image_urls(message.pic_url)
            one = result["results"]
            two = one[0]
            three = two['result']
            four = three['tag']
            five = four['classes']
            if counter == 5:
                poem = "Marcy had a little " + words[0] + " whose " + words[1] + " was white as " + words[2] + "  This " + words[3] +  " would follow Mary wherever she would go. Mary also like to go " + words[4]+ "ing."
	        kik.send_messages([
	        TextMessage(
	        to=message.from_user,
	        chat_id=message.chat_id,
	        body=poem 
	        ),

	       ])
            words.append(five[1])
            counter +=1
            left = 5 - counter
            mes = str(left) + " pictures left to go!"  
	    kik.send_messages([
	    TextMessage(
	    to=message.from_user,
	    chat_id=message.chat_id,
	    body=mes 
	    ),

	   ])
    return Response(status=200)

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
