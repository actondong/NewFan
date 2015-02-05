
from flask import Flask, jsonify,render_template,request,session,redirect
from random import randint
import requests
import sys
from flask.ext.socketio import join_room, leave_room
from flask.ext.socketio import SocketIO, emit,send
import db
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
roomCurrTime={}
@app.errorhandler(404)
def page_not_found(error):
	return "Sorry, this page was not found.", 404

@app.route("/index")
def hello():
	if 'username' in session:
    		return render_template("cinema.html",myUserName=session['username'])
	else:
		return render_template("cinema.html",myUserName='Guest')

@app.route("/")
def home():
	if 'username' in session:
    		return render_template("cinema.html",myUserName=session['username'])
	else:
		return render_template("homepage.html")


@app.route('/login',  methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if db.check_user_password_right(request.form['username'],
                       request.form['password']):
			session['username']=request.form['username']
			session['logged_in']=True
			return redirect('/')
        else:
            error = 'Invalid username/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return redirect('/index')

@app.route('/signup',  methods=['POST', 'GET'])
def signup():
    error = None
    if request.method == 'POST':
        if db.add_user(request.form['username'],
                       request.form['password']):
			session['username']=request.form['username']
			session['logged_in']=True
			return redirect('/')
        else:
            error = 'Invalid username/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return redirect('/index')


@app.route('/logout',  methods=['POST', 'GET'])
def logout():
	error = None
	session.clear()
	return redirect('/')

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

@socketio.on('request host', namespace='/test')
def test_message(message):
    room = str(randint(1,1000))
    emit('host confirm', {'data':room})
    join_room(room)
    print('request host')

@socketio.on('request join', namespace='/test')
def test_message(message):
    room = message['data']
    join_room(room)
    emit('join confirm', {'data': room})
    emit('pause for new',{'data': 'pause'},room=room)
    print('request join')

@socketio.on('video status change', namespace='/test')
def video_change(message):
    currTime = message['currTime']
    room = message['room']
    roomCurrTime[room]=currTime
    stop = message['stop']
    currTime = message['currTime']
    print(message['identifier']);
    emit('change video', {'stop': stop,'currTime': currTime, 'identifier': message['identifier']}, room=room)

@socketio.on('room chat', namespace='/test')
def room_chat(message):
    room = message['room']
    data = message['data']
    print(room)
    emit('test Only', {'data': 'sds'}, room=room)

@socketio.on('chat broadcast', namespace='/test')
def room_chat(message):
    room = message['room']
    data = message['data']
    emit('chat message receive', {'data': data}, room=room)

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

#    app.run(host="0.0.0.0")

