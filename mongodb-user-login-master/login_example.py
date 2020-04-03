from flask import Flask, render_template, url_for, request, session, redirect
from pymongo import MongoClient
import bcrypt
import re
from flask import flash

app=Flask(__name__)

app.config['MONGO_DBNAME']='mongologin'
app.config['MONGO_URI']='localhost:27017'

client = MongoClient()

@app.route('/',methods=['GET'])
def start():
    session['username'] = None
    return redirect('/index')

@app.route('/index',methods = ['POST', 'GET'])
def index():
    return render_template('index.html')

@app.route('/logout',methods=['POST','GET'])

def logout():
    s=session['username']
    session['username']=None
    s1= s + " has succesfully logged out"       
    return render_template('index.html',send=s1)

@app.route('/valid_user',methods = ['POST', 'GET'])
def valid_user(): 
    if request.method == 'POST':
        return render_template('logout.html')
    if request.method == 'GET':
        s1="logged in as " + session['username'] 
        return render_template("valid_user.html",s=s1)

@app.route('/login', methods = ['POST'])
def login():
    users = client.db.users
    login_user=users.find_one({'name': request.form['username']})

    if login_user:
        if request.form['pass'] == login_user['password'] :
            session['username'] = request.form['username']
            return redirect('/valid_user')
    return 'INVALID USERNAME PASSWORD COMBO'

def validate(s,u):
    e=0
    print(e)
    #check password
    regex = re.compile('[@_!#$%^&*()<>?/\\|}{~:]')   
    if u=='' :
        e+=1
        return False
    if u[0].isdigit() :
        e+=1
    if(regex.search(s) == None): 
        e+=1   
    if not any(x.isupper() for x in s):
        e+=1   
    if not any(x.isdigit() for x in s):
        e+=1
    
    print(e)
    if e==0:
        return True
    else:
        return False

@app.route('/register', methods = ['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = client.db.users
        existing_user = users.find_one({'name' : request.form['username']})
        if existing_user is None :
            s=request.form['pass']
            u=request.form['username']
            if validate(s,u):
                hashpass = request.form['pass']
                users.insert({'name':request.form['username'] , 'password': hashpass})
                s1=request.form['username'] + " has succesfully been registered"
                return render_template('index.html',send=s1)
            else:
                s1="CHECK IF THE FOLLOWING CONDITIONS ARE MET\n "
                sp="PASSWORD\n"
                s2="1. Password should contain a special character\n"
                s3="2. Password should contain atleast one UpperCase letter\n"
                s4="3. Password should contain atleast one number"
                su="USERNAME\n"
                su1="1. Username cant be empty\n"
                su2="2. Username cant start with a Number "
                s1+=sp+s2+s3+s4+su+su1+su2
                return render_template('register.html',send=s1)
        return 'Username aldready exists'    
    return render_template('register.html')



if __name__ == '__main__' :
    app.secret_key = 'mysecret'
    app.run(debug=True)



