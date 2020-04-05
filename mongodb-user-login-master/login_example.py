from flask import Flask, render_template, url_for, request, session, redirect
from pymongo import MongoClient
import bcrypt
import re
import pytz
from datetime import datetime
from datetime import timedelta

app=Flask(__name__)

app.config['MONGO_DBNAME']='mongologin'
app.config['MONGO_URI']='localhost:27017'

client = MongoClient()
client.db.temp.drop()

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
        s1="logged in as " + session['username'] 
        return render_template("valid_user.html",s=s1)
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
            address=request.form['address']
            email= request.form['email']
            if validate(s,u):
                hashpass = request.form['pass']
                users.insert({'name':request.form['username'] , 'password': hashpass , 'credits':1000, 'address':address, 'email':email})
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

@app.route('/credit', methods = ['POST', 'GET'])
def credit():
        return render_template('credits.html')

@app.route('/updatemsg', methods = ['POST', 'GET'])
def updatemsg():
    if request.method == 'POST' :
        x= request.form["r"]
        try:
            val = int(x)
        except ValueError:
            return render_template('credits.html',msg="ENTER VALID RECHARGE AMOUNT")
        updatecredits(val)
        msg="SUCCESFULLY RECHARGED"
        return render_template('credits.html',msg=msg) 

@app.route('/book',methods = ['POST', 'GET'])
def book():
    india = pytz.timezone('Asia/Kolkata')
    t1 = datetime.now(india)
    t2= t1 + timedelta(days=1)
    t3 = t1 + timedelta(days=2)
    return render_template("book.html",s1=t1, s2=t2, s3=t3)

@app.route('/confirmbook',methods = ['POST', 'GET'])
def confirmbook():
    if request.method=='POST': 
        slot=(request.form['slot'])
        day=int(request.form['day'])
        month=int(request.form['month'])
        year=int(request.form['year'])

        book = client.db.book
        
        status=book.find_one({'slot': slot,'day':day,'month':month,'year':year})
        if status:
            s="THE SLOT YOU HAVE PICKED IS ALDREADY BOOKED, PLEASE CHOOSE A DIFFERENT SLOT!"
            return render_template('confirmbooking.html',s=s)
        else :
            india = pytz.timezone('Asia/Kolkata')
            tnow = datetime.now(india)
            a= int(tnow.year) <= year
            b = int(tnow.month) <= month
            c = int(tnow.day) <= day
            hour = (int(slot[0]) + 12)%24
            d = int(tnow.hour) < hour

            if a and b and c and d :
                temp_obj={"username":session['username'],"slot": slot,"day":day,"month":month,"year":year}
                temp = client.db.temp
                temp.insert({'store':temp_obj})
                return redirect('/ask')
            else :
                s="You have booked too late. please choose a different slot!"
                return render_template('confirmbooking.html',s=s,a=a,b=b,c=c,d=d)

@app.route('/previous_bookings',methods = ['POST', 'GET'])
def previous_bookings():
       book=client.db.user_book
       l=[]
       for document in book.find():
            if document['username'] == session['username'] :
                l.append({'slot': document['slot'],'day':document['day'],'month':document['month'],'year':document['year']})

       return render_template("previous_bookings.html",list=l,s=session['username'])

@app.route('/ask',methods = ['POST', 'GET'])
def ask():
       return render_template("ask.html")
    
@app.route('/successbook',methods = ['POST', 'GET'])
def successbook():
       temp = client.db.temp
       for l in temp.find():
           l1=l['store']
           l2=l1['username']
           if l2 == session["username"] :
                temp_obj=l1
                break
       client.db.temp.drop()
       slot=temp_obj["slot"]
       day=int(temp_obj['day'])
       month=int(temp_obj['month'])
       year=int(temp_obj['year'])

       x= -1000
       success = updatecredits(x)
       if success == 1 :
            book = client.db.book
            user_book=client.db.user_book
            book.insert({'slot': slot,'day':day,'month':month,'year':year}) 
            user_book.insert({'username':session['username'],'slot': slot,'day':day,'month':month,'year':year}) 
            s="SUCCESFULLY BOOKED"
       else :
            s="INSUFFECIENT CREDIT BALANCE, PLEASE RECHARGE AND BOOK"
       return render_template('confirmbooking.html',s=s)

def updatecredits(x):
    u=client.db.users
    for i in u.find({'name': session['username']}):
        temp=i
        break
    x=int(x)
    new_credits = temp["credits"] + x
    if new_credits < 0 :
         return 2
    else :
        u.update({"_id" : temp["_id"]},
        {"credits" : temp["credits"] + x,"name":temp["name"],"password":temp["password"],"email":temp["email"],"address":temp["address"]})
        return 1

@app.route('/user_details',methods = ['POST', 'GET'])
def user_details():
    u=client.db.users
    for i in u.find({'name': session['username']}):
        temp=i
        break
    return render_template("user_details.html",t=temp)


if __name__ == '__main__' :
    app.secret_key = 'mysecret'
    app.run(debug=True)



