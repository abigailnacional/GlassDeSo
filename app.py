import requests
from typing import Optional
from xmlrpc.client import boolean
from flask import Flask, flash, redirect, render_template, request, \
    url_for, session  # pragma: no cover
from BitcloutIdentity import BitcloutIdentity
import BitcloutAPI
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__) 
app.secret_key = "super secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

#Function that grabs the most recent post made using a DeSo username and post hash
#The DeSo API automatically grabs the most recent post because I haven't provided a LastPostHashHex.
def get_recent_post(username):
 url = 'https://bitclout.com/api/v0/get-posts-for-public-key'
 data = {
   "PublicKeyBase58Check": "",
   "Username": username,
   "ReaderPublicKeyBase58Check": "",
   "NumToFetch": 1,
   "MediaRequired": False
 }
 response = requests.post(url,  json=data)
 response_json = response.json()

 #Get only the message content
 ret = response_json['Posts'][0]['Body']

 return ret

#Class for posts made for GlassDeSo, offer_stat is offer status. Either they 
# received an offer or they didn't. The post_ID is to keep track of posts in
# this SQLAlchemy database, while the hashVal keeps track of what post it is
# in the actual DeSo blockchain.
class GDSPosts(db.Model):
    post_ID = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(100))
    company = db.Column(db.String(100))
    job = db.Column(db.String(100))
    offer_stat = db.Column(db.Boolean)
    hashVal = db.Column(db.String(100), nullable=True)

    def __init__(self, post_ID, author, company, job, offer_stat, hashVal: Optional[str] = ""):
        self.post_ID = post_ID
        self.author = author
        self.company = company
        self.job = job
        self.offer_stat = offer_stat
        self.hashVal = hashVal

@app.route("/")
def hello(): 
    return redirect('/home')

# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    jwt='';
    pubkey='';
    if request.method == 'POST':
        print(request.form['jwt']);
        if request.form['jwt'] == None:
            error = 'Invalid Credentials. Please try again.'
        else:
            jwt = request.form['jwt']
            pubkey = request.form['pubkey']
            identity = BitcloutIdentity(pubkey)
            if(not identity.validateJWT(jwt)):
                error = "Could not login"
            else:
                session['pubkey'] = pubkey
                return redirect('/home')

    return render_template('login.html', test='this is a test', pubkey=pubkey, jwt=jwt, error=error)

# Route for handling the login page logic
@app.route('/home')
def home():
    if('pubkey' in session and session['pubkey'] != None):
        if(not 'userinfo' in session or session['userinfo'] == None):
            userinfo = BitcloutAPI.getUserInfo(session['pubkey'])
            session['userinfo'] = userinfo
            print('retrieved userinfo:', userinfo)

            #I'm going to print the posts for a random user
            get_recent_post("Krassenstein")
        return render_template('home.html', pubkey=session['pubkey'], userinfo=session['userinfo'])
    return redirect('/login')

#Page where user creates a new post
@app.route('/newpost', methods = ['GET', 'POST'])
def newpost():
    #If the form was just submitted:
    if request.method == 'POST':
        #Change offer status value to string
        offerVar = "False"
        if request.form.get('offer_stat', False):
            offerVar = "True"

        #Construct the message string
        message = 'Company: ' + request.form['company'] + "\nJob: " + request.form['job'] + "\nReceived Offer: " + offerVar + "\nReview: " + request.form['review'] + "\nInterview Questions: " + request.form['questions']
        print(message)
        return redirect(url_for('postsuccess'))
    else:
        return render_template('newPost.html')

@app.route('/postsuccess', methods = ['GET', 'POST'])
def postsuccess():
    return render_template('postSuccess.html')

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/login')

if __name__ == "__main__": 
    app.run(debug=True, host='0.0.0.0')
