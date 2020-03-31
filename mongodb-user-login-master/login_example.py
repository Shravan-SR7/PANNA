from flask import Flask, render_template, url_for, request, session, redirect
from pymongo import MongoClient
import bcrypt

app=Flask(__name__)

app.config['MONGO_DBNAME']='mongologin'
app.config['MONGO_URI']='localhost:27017'

client = MongoClient()

@app.route('/')
def index():
    print(session)
    if 'username' in session:
        return 'You are logged in as ' +session['username']
    return render_template('index.html')

@app.route('/login', methods = ['POST'])
def login():
    users = client.db.users
    login_user=users.find_one({'name': request.form['username']})

    if login_user:
        if request.form['pass'] == login_user['password'] :
            session['username'] = request.form['username']
            return redirect(url_for('index'))
    return 'INVALID USERNAME PASSWORD COMBO'

@app.route('/register', methods = ['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = client.db.users
        if request.form['username']!='' :
            existing_user = users.find_one({'name' : request.form['username']})
        else :
            return 'enter proper username'

        if existing_user is None :
            hashpass = request.form['pass']
            users.insert({'name':request.form['username'] , 'password': hashpass})
            return redirect(url_for('index'))
        return 'Username aldready exists'    
    return render_template('register.html')



if __name__ == '__main__' :
    app.secret_key = 'mysecret'
    app.run(debug=True)



