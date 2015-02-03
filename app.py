from flask import Flask, jsonify,render_template,request
import requests
import sys
from flask.ext.socketio import join_room, leave_room
from flask.ext.socketio import SocketIO, emit,send
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.errorhandler(404)
def page_not_found(error):
	return "Sorry, this page was not found.", 404

@app.route("/")
def hello():
	return render_template("cinema.html")
	
@app.route("/search",methods=["GET","POST"])
def search():
	if request.method == "POST":
        	url = "https://api.github.com/search/repositories?q=" + request.form["user_search"]
        	response_dict = requests.get(url).json()
        	return render_template("results.html",api_data=response_dict)
    	else: # request.method == "GET"
        	return render_template("search.html")

@socketio.on('my event', namespace='/test')
def test_message(message):
    emit('rome', {'data': 'romeeeee'},broadcast=True)

@socketio.on('my broadcast event', namespace='/test')
def test_message(message):
    emit('my response', {'data': message['data']}, broadcast=True)

@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected'})
    print('Client Connected')
@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('disconnect') 

@socketio.on('my room event',namespace='/test')
def on_join(data):
    room = data['room']
    msg=data['data']
    emit('my response',{'data':msg}, room=room)


@socketio.on('join',namespace='/test')
def on_join(data):
    room = data['room']
    join_room(room)
 #   emit('my response',{'data':' He has entered the room.'}, room=room)
    print('join')


@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', room=room)       
    print('leave')
if __name__=="__main__":
	socketio.run(app,'0.0.0.0',8080)

