import pandas as pd
import os, json, re, io, requests
from os import path
from utilities.utils import add_embeddings
from utilities.azureblobstorage import upsert_blob_metadata
from langchain.text_splitter import CharacterTextSplitter

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
                videotext, timestart=getonevideo(token, location, accountid, ids['id'])
                print('processing video and start time: ', ids['id']+ ' ' + str(timestart))
                videotranscripts = videotranscripts.append({'videoName': ids['id'], 'transcript': videotext, 'time':timestart}, ignore_index=True)
        #print('done processing all videos')
        print('videotranscripts df: ', videotranscripts)
        return videotranscripts
    except Exception as e:
        print(e)

def getonevideo(token, location, accountid, videoid):
    url = f"https://api.videoindexer.ai/{location}/Accounts/{accountid}/Videos/{videoid}/Index?accessToken={token}"
    response = requests.request("GET", url)
    print('\n')
    videotranscript = ''    
    timeoffset = ''    
    for transcript in response.json()['videos'][0]['insights']['transcript']:
        videotranscript = videotranscript + transcript['text'] + ' '
        timeoffset = transcript['instances'][0]['adjustedStart']
        print ('videotranscript is: ', videotranscript)
        print ('timeoffset is: ', timeoffset)
    return videotranscript, timeoffset

def ingestvideos():
    videotoken = getAADtoken(clientid, clientsecret, tenantid, subsid, rg, videoaccountname)
    result_all_videos = getallvideos(videotoken, videolocation, videoaccountid)
    video_index = getvideoindexerresults(videotoken, videolocation, videoaccountid, result_all_videos)
    for index, row in video_index.iterrows():
        try:
            splitter = CharacterTextSplitter(chunk_size=1024,chunk_overlap=0, separator=' ')
            chunks = []
            chunks = splitter.split_text(row['transcript'])
            #print('transcript chunks are: ', chunks)
            for index, chunk in enumerate(chunks):
                name=row['videoName']+'_'+str(index)
                time=row['time']
                print ('time is: ',time )
                #print ('videoName is: ',name )
                add_embeddings(chunk, name, time, os.getenv('OPENAI_EMBEDDINGS_ENGINE_DOC', 'text-search-davinci-doc-001'))
        except Exception as e:
            print(e)
    print ('All videos done')