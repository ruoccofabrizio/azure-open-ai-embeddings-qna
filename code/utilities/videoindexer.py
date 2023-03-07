import pandas as pd
import os, json, re, io, requests
from os import path
from utilities.utils import add_embeddings

videoaccountid=os.getenv("VIDEO_ACCOUNT_ID")
videolocation=os.getenv("VIDEO_LOCATION")
clientid= os.getenv("CLIENT_ID")
clientsecret= os.getenv("CLIENT_SECRET")
tenantid= os.getenv("TENANT_ID")
subsid= os.getenv("SUBSCRIPTION_ID")
rg= os.getenv("RG")
videoaccountname= os.getenv("VIDEO_ACCOUNT_NAME")

video_index = {}

def getAADtoken(clientid, clientsecret, tenantid, subsid, rg, videoaccountname):
    url = 'https://login.microsoftonline.com/'+tenantid+'/oauth2/v2.0/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'client_id': clientid,
        'grant_type': 'client_credentials',
        'scope': 'https://management.azure.com/.default',
        'client_secret': clientsecret
    }
    response = requests.request("POST", url, headers=headers, data=data)
    bearertoken = response.json()['access_token']
    
    url = 'https://management.azure.com/subscriptions/'+ subsid + '/resourceGroups/' + rg + '/providers/Microsoft.VideoIndexer/accounts/' + videoaccountname + '/generateAccessToken?api-version=2022-07-20-preview'
    data = "{\r\n\tpermissionType: \"Contributor\",\r\n\tscope: \"Account\"\r\n}"
    headers = {
        'Authorization': 'Bearer  '+ bearertoken,
        'Content-type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=data)
    return response.json()['accessToken']

def getplayertoken(clientid, clientsecret, tenantid, subsid, rg, videoaccountname, scope, videoid=None):
    url = 'https://login.microsoftonline.com/'+tenantid+'/oauth2/v2.0/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'client_id': clientid,
        'grant_type': 'client_credentials',
        'scope': 'https://management.azure.com/.default',
        'client_secret': clientsecret
    }
    response = requests.request("POST", url, headers=headers, data=data)
    bearertoken = response.json()['access_token']
    
    url = 'https://management.azure.com/subscriptions/'+ subsid + '/resourceGroups/' + rg + '/providers/Microsoft.VideoIndexer/accounts/' + videoaccountname + '/generateAccessToken?api-version=2022-07-20-preview'
    data = "{\r\n\tpermissionType: \"Reader\",\r\n\tscope: \"Video\"\r\n, videoId: \""+videoid+"\"\r\n}"
    headers = {
        'Authorization': 'Bearer  '+ bearertoken,
        'Content-type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=data)
    return response.json()['accessToken']

def getallvideos(token, location, accountid):
    url = f"https://api.videoindexer.ai/{location}/Accounts/{accountid}/Videos?accessToken={token}"
    response = requests.request("GET", url)
    return response.json()

def getvideoindexerresults(token, location, accountid, allvideos):
    videotranscripts = pd.DataFrame(columns=['videoName', 'transcript','time'])
    print('about to process all videos')
    try:
        for ids in allvideos['results']:
            if (ids['state'] == 'Processed'):
                tempdf = pd.DataFrame(columns=['videoName', 'transcript','time'])
                tempdf = getonevideo(token, location, accountid, ids['id'])
                videotranscripts= tempdf.append(videotranscripts, ignore_index=True)
        return videotranscripts
    except Exception as e:
        print(e)


def getonevideo(token, location, accountid, videoid):
    url = f"https://api.videoindexer.ai/{location}/Accounts/{accountid}/Videos/{videoid}/Index?accessToken={token}"
    response = requests.request("GET", url)
    newvideotranscripts = pd.DataFrame(columns=['videoName','transcript','time'])
    timeoffset = ''
    videotranscript = ''
    for index, transcript in enumerate(response.json()['videos'][0]['insights']['transcript']): #response.json()['videos'][0]['insights']['transcript']:
        videotranscript = videotranscript + transcript['text'] + ' '
        if index % 10 == 0 or index == (len(response.json()['videos'][0]['insights']['transcript'])-1):
            timeoffset = transcript['instances'][0]['adjustedStart']
            newvideotranscripts = newvideotranscripts.append({'videoName': str(videoid+'_'+str(index)), 'transcript': videotranscript, 'time':timeoffset}, ignore_index=True)
            videotranscript = ''
    return newvideotranscripts


def ingestvideos():
    videotoken = getAADtoken(clientid, clientsecret, tenantid, subsid, rg, videoaccountname)
    result_all_videos = getallvideos(videotoken, videolocation, videoaccountid)
    video_index = getvideoindexerresults(videotoken, videolocation, videoaccountid, result_all_videos)
    for index, row in video_index.iterrows():
        try:
            add_embeddings(row['transcript'], row['videoName'], row['time'], os.getenv('OPENAI_EMBEDDINGS_ENGINE_DOC', 'text-search-davinci-doc-001'))
        except Exception as e:
            print(e)
    print ('All videos done')

def getplayertoken(clientid, clientsecret, tenantid, subsid, rg, videoaccountname, videoid):
    print('videoid is: ', videoid)
    url = 'https://login.microsoftonline.com/'+tenantid+'/oauth2/v2.0/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'client_id': clientid,
        'grant_type': 'client_credentials',
        'scope': 'https://management.azure.com/.default',
        'client_secret': clientsecret
    }
    response = requests.request("POST", url, headers=headers, data=data)
    bearertoken = response.json()['access_token']
    
    url = 'https://management.azure.com/subscriptions/'+ subsid + '/resourceGroups/' + rg + '/providers/Microsoft.VideoIndexer/accounts/' + videoaccountname + '/generateAccessToken?api-version=2022-07-20-preview'
    data={
        'permissionType': 'Reader',
        'scope': 'Video',
        'videoId': ''
    }
    if videoid:
        data['videoId']=videoid
    headers = {
        'Authorization': 'Bearer  '+ bearertoken,
        'Content-type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=str(data))
    return response.json()['accessToken']

def createvideolink(videoid,timestamp):
    videoid = videoid.split('_')[0]
    videotoken = getplayertoken(clientid, clientsecret, tenantid, subsid, rg, videoaccountname, videoid)
    # videoid has a name with underscores and a number, e.g. 123456789_0 remove the number
    timestamp = int(timestamp.split(':')[0])*3600 + int(timestamp.split(':')[1])*60 + int(timestamp.split(':')[2].split('.')[0]) + int(timestamp.split(':')[2].split('.')[1])/1000
    timestamp = int(timestamp)
    url= 'https://www.videoindexer.ai/embed/player/'+videoaccountid+'/'+videoid+'/?accessToken='+videotoken+'&locale=en&location='+videolocation+'&t='+str(timestamp)
    return url
