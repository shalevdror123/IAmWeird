from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
from models import db, User, Message

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'

db.init_app(app)
with app.app_context():
    db.create_all()

socketio = SocketIO(app)


def create_tables():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if user:
            session['username'] = username
            return redirect(url_for('chat'))
        else:
            return redirect(url_for('register'))
    return render_template('index.html')


@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('index'))
    
    # Retrieve all messages from the database
    messages = Message.query.order_by(Message.timestamp.asc()).all()
    
    return render_template('chat.html', username=session['username'], messages=messages)


@app.route('/logout')
def logout():
    # Clear the session
    session.pop('username', None)
    
    # Redirect to the homepage
    return redirect(url_for('index'))


@app.route('/shalevisweird')
def shalev():
    return render_template('shalev.html')

@socketio.on('send_message')
def handle_send_message(json):
    username = json['username']
    message_content = json['message']
    user = User.query.filter_by(username=username).first()
    new_message = Message(content=message_content, user_id=user.id)
    db.session.add(new_message)
    db.session.commit()
    emit('receive_message', {'username': username, 'message': message_content}, broadcast=True)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        
        if User.query.filter_by(username=username).first():
            return redirect(url_for('register'))

        new_user = User(username=username)
        db.session.add(new_user)
        db.session.commit()

        session['username'] = username
        
        return redirect(url_for('chat'))

    return render_template('register.html')



if __name__ == '__main__':
    socketio.run(app, debug=True)
