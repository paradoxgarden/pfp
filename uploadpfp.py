import atproto
from atproto_client.models import blob_ref
import requests
import base64
#from tls_client import Session
import tomllib
from atproto import Client, client_utils, models

image_file = "pfp.png"
with open("config.toml", "rb") as f:
    config = tomllib.load(f)
# Discord
# 
def discord_upload()->requests.Response:
    with open(image_file, "rb") as f:
        payload = {
            "avatar": f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode()}"
        }
        # this is a bunch of nonsense to get discord to think we're a browser
        headers = {
                "authority": "discord.com",
                "method": "PATCH",
                "scheme": "https",
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "en-US",
                "authorization": config["discord"]["token"],
                "origin": "https://discord.com",
                "sec-ch-ua": '"Not/A)Brand";v="99", "Brave";v="115", "Chromium";v="115"',
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9020 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "X-Debug-Options": "bugReporterEnabled",
                "X-Discord-Locale": "en-US",
                "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDIwIiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDUiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMjAgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMjYgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMjYiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNDAyMzcsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM4NTE3LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsLCJkZXNpZ25faWQiOjB9"
            }
        r = requests.patch("https://discord.com/api/v9/users/@me", json=payload, headers=headers)
        return r


# steam:
# https://steamcommunity.com/id/ParadoxGarden/minimaledit
# https://steam.readthedocs.io/en/stable/api/steam.webauth.html
# after some consideration steam auth thru web requires 2fa
# so some manual intervention may be required


# bsky
# https://atproto.blue/en/latest/
# 
def bsky_upload()->atproto.models.ComAtprotoRepoPutRecord.Response:
    pfp_collection:str="app.bsky.actor.profile"
    login:dict[str, str] = config["bsky"]
    client = Client(base_url=login["baseurl"])
    _ = client.login(login["user"],login["pass"])
    with open(image_file, "rb") as f:
        blob: atproto.models.ComAtprotoRepoUploadBlob.Data = atproto.models.ComAtprotoRepoUploadBlob.Data(f.read())
        blobresp:atproto.models.ComAtprotoRepoUploadBlob.Response = client.com.atproto.repo.upload_blob(blob)
        blobref: blob_ref.BlobRef = blobresp.blob

        getparams: atproto.models.ComAtprotoRepoGetRecord.Params = atproto.models.ComAtprotoRepoGetRecord.Params(collection=pfp_collection,repo=client.me.did,rkey="self") 
        profile: atproto.models.ComAtprotoRepoGetRecord.Response = client.com.atproto.repo.get_record(params=getparams)
        
        putrecord: atproto.models.AppBskyActorProfile.Record = profile.value
        putrecord.avatar = blobref

        putdata: atproto.models.ComAtprotoRepoPutRecord.Data = \
            atproto.models.ComAtprotoRepoPutRecord.Data(collection=pfp_collection,record=putrecord,repo=client.me.did,rkey="self")
        putresp = client.com.atproto.repo.put_record(putdata)
        return putresp

if __name__ == '__main__':
    #r = discord_upload()
    r = bsky_upload()

