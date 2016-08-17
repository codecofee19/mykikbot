from flask import Flask, request, Response
import os 
from kik import KikApi, Configuration
from kik.messages import messages_from_json, TextMessage

app = Flask(__name__)
BOT_USERNAME = os.environ['BOT_USERNAME'] 
BOT_API_KEY= os.environ['BOT_API_KEY']
kik = KikApi(BOT_USERNAME, BOT_API_KEY)
kik.set_configuration(Configuration(webhook='https://intense-beyond-98266.herokuapp.com/incoming'))
@app.route('/incoming', methods=['POST'])
def incoming():
    if not kik.verify_signature(request.headers.get('X-Kik-Signature'), request.get_data()):
        return Response(status=403) 

    messages = messages_from_json(request.json['messages'])

    for message in messages:
        if isinstance(message, TextMessage):
            kik.send_messages([
                TextMessage(
                    to=message.from_user,
                    chat_id=message.chat_id,
                    body=message.body
                )
            ])

    return Response(status=200)

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    print('HI') 
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)