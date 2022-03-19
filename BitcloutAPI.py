import requests
import json

endpoint = 'https://api.bitclout.com'
        
def getUserInfo(publicKey):
    #method gets all the details for the publickey
    data = { 'PublicKeyBase58Check':publicKey}
    response = requests.post(endpoint+"/get-single-profile", json=data)
    if response.status_code == 200:
        data = json.loads(response.text)

        ret = {}
        ret['username'] = data['Profile']['Username']
        return ret
    return None