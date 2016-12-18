from flask import Flask, jsonify, render_template, request, session, redirect
from random import randint
from youtube import searchID
import requests
import sys
from flask.ext.socketio import join_room, leave_room
from flask.ext.socketio import SocketIO, emit, send
from twilio.rest import TwilioRestClient
import db
import twilio.twiml

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
roomCurrTime = {}
targetUrl = 'ec2-52-0-171-169.compute-1.amazonaws.com:8080'


@app.errorhandler(404)
def page_not_found(error):
    return "Sorry, this page was not found.", 404


@app.route("/index")
def hello():
    if 'username' in session:
        name = db.get_user_name(session['username'])
        return render_template("cinema.html", myUserName=name, myPhoneNumber=session['username'])
    else:
        return render_template("cinema.html", myUserName='Guest', myPhoneNumber='11111')


@app.route('/confirmInvitation/<info>', methods=['POST', 'GET'])
def confirm(info):
    phoneNumber, room = info.split('+')
    socketio.emit('commit join', {'username': phoneNumber, 'room': room}, namespace='/test')
    return "You have successfully joined room " + room


@app.route("/")
def home():
    if 'username' in session:
        name = db.get_user_name(session['username'])
        return render_template("cinema.html", myUserName=name, myPhoneNumber=session['username'])
    else:
        resp = twilio.twiml.Response()
        resp.message("Hello, Mobile Monkey")
        return render_template("homepage.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if db.check_user_password_right(request.json['username'],
                                        request.json['password']):
            session['username'] = request.json['username']
            session['logged_in'] = True
            return jsonify(success=True)
        else:
            return jsonify(success=False)
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return redirect('/index')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    error = None
    if request.method == 'POST':
        if db.add_user(request.json['username'],
                       request.json['password'],
                       request.json['name']):
            return jsonify(success=True)
        else:
            return jsonify(success=False)
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return redirect('/index')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    error = None
    session.clear()
    return redirect('/')


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        url = "https://api.github.com/search/repositories?q=" + request.form["user_search"]
        response_dict = requests.get(url).json()
        return render_template("results.html", api_data=response_dict)
    else:  # request.method == "GET"
        return render_template("search.html")


@socketio.on('my event', namespace='/test')
def test_message(message):
    emit('rome', {'data': 'romeeeee'}, broadcast=True)


@socketio.on('waiting for invitation', namespace='/test')
def invitation(message):
    number = message['number']
    room = message['room']
    twilioID = 'AC336052c209d59ff6da54f40127b309c0'
    token = '403e4ce7e10d41559201cfdb973997f3'
    client = TwilioRestClient(twilioID, token)
    message = client.messages.create(
        body="click on the following link to join the room:\nhttp://" + targetUrl + "/confirmInvitation/" + number + "+" + room,
        to="+1" + number,
        from_="+18628998914")
    print message.sid


@socketio.on('URL query', namespace='/test')
def query(message):
    room = message['room']
    URL = message['url']
    item = searchID(URL)
    if item:
        if room:
            emit('get video ID', {'ID': item["id"], 'title': item["snippet"]["title"]}, room=room)
        else:
            emit('get video ID', {'ID': item["id"], 'title': item["snippet"]["title"]})
    else:
        emit('get video ID', {'ID': item, 'title': item})


@socketio.on('request host', namespace='/test')
def test_message(message):
    room = str(randint(1, 1000))
    emit('host confirm', {'data': room})
    join_room(room)


@socketio.on('request join', namespace='/test')
def test_message(message):
    room = message['data']
    join_room(room)
    emit('join confirm', {'data': room})
    emit('pause for new', {'data': 'pause'}, room=room)


@socketio.on('broadcast ID', namespace='/test')
def broadcastID(message):
    room = message['room']
    currVideo = message['ID']
    startTime = message['startTime']
    emit('wait for video ID', {'currVideo': currVideo, "startTime": startTime}, room=room)


@socketio.on('video status change', namespace='/test')
def video_change(message):
    currTime = message['currTime']
    room = message['room']
    roomCurrTime[room] = currTime
    stop = message['stop']
    currTime = message['currTime']
    emit('change video', {'stop': stop, 'currTime': currTime, 'identifier': message['identifier']}, room=room)


@socketio.on('room chat', namespace='/test')
def room_chat(message):
    room = message['room']
    data = message['data']
    emit('test Only', {'data': 'sds'}, room=room)


@socketio.on('chat broadcast', namespace='/test')
def room_chat(message):
    room = message['room']
    data = message['data']
    emit('chat message receive', {'data': data}, room=room)


@socketio.on('chat broadcast flying', namespace='/test')
def room_chat(message):
    room = message['room']
    data = message['data']
    emit('flying message receive', {'data': data}, room=room)


@socketio.on('my broadcast event', namespace='/test')
def test_message(message):
    emit('my response', {'data': message['data']}, broadcast=True)


@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected'})


@socketio.on('join', namespace='/test')
def on_join(data):
    room = data['room']
    join_room(room)
    #   emit('my response',{'data':' He has entered the room.'}, room=room)
    print('join')


@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    send(data['username'] + ' has left the room.', room=room)
    print('leave')


if __name__ == "__main__":
    socketio.run(app, '127.0.0.1', 5050)

# app.run(host="0.0.0.0")
