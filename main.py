from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room

app = Flask(__name__)
socketio = SocketIO(app)

# Chatroom state
chat_room = {}


@app.route("/test")
def test():
    return render_template("index.html")


@app.route("/")
def login():
    return render_template("login.html")

@app.route("/chatroom/<room>")
def enter_chatroom(room):
    # Check if the 'nickname' is provided in the URL parameters
    nickname = request.args.get('nickname', None)

    if not nickname:
        # Redirect to a page to enter nickname if 'nickname' is not provided
        return render_template("enter_nickname.html", room=room)

    # Check if the nickname is already in use
    if is_nickname_taken(room, nickname):
        # If the nickname is already taken, change it to "joker"
        nickname = "NameWasAlreadyTaken"

    return render_template("chatroom.html", room=room, nickname=nickname)

@app.route("/chatroom/<room>/<nickname>")
def chatroom(room, nickname):
    return render_template("chatroom.html", room=room, nickname=nickname)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join')
def handle_join(data):
    room = data['room']
    nickname = data['nickname']
    join_room(room)
    chat_room[room] = chat_room.get(room, [])
    chat_room[room].append(nickname)
    socketio.emit('user_joined', {'nickname': nickname}, room=room)

@socketio.on('message')
def handle_message(data):
    room = data['room']
    nickname = data['nickname']
    message = data['message']
    socketio.emit('message', {'nickname': nickname, 'message': message}, room=room)

@socketio.on('leave')
def handle_leave(data):
    room = data['room']
    nickname = data['nickname']
    leave_room(room)
    chat_room[room].remove(nickname)
    socketio.emit('user_left', {'nickname': nickname}, room=room)

def is_nickname_taken(room, nickname):
    return nickname in chat_room.get(room, [])

if __name__ == "__main__":
    socketio.run(app, host='127.0.0.1', port=5000)
