from typing import Optional
from xmlrpc.client import boolean
from flask import Flask, flash, redirect, render_template, request, \
    url_for, session  # pragma: no cover
from BitcloutIdentity import BitcloutIdentity
import BitcloutAPI

app = Flask(__name__) 
app.secret_key = "super secret key"

#Class for posts made for GlassDeSo
class GDSPosts:
    def __init__(
            self,
            postID: int,
            author: str,
            company: str,
            job: str,
            offerStat: bool,
            #hashVal is optional because we don't know what the hash is when we
            #  post it; we have to look it up and add it later
            hashVal: Optional[str] = ""):
        self.postID = postID
        self.author = author
        self.company = company
        self.job = job
        self.offerStat = offerStat
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
                print('user holds NeonStoic. Log them in!')
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

        return render_template('home.html', pubkey=session['pubkey'], userinfo=session['userinfo'])
    return redirect('/login')

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/login')

if __name__ == "__main__": 
    app.run(debug=True, host='0.0.0.0')
