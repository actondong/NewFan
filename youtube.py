import requests
def search(url):
    conststr = "https://www.youtube.com/watch?v="
    index = len(conststr);
    retrieveurl = "https://www.googleapis.com/youtube/v3/videos?part=id%2C+snippet&id="+url[index:]+"&key=AIzaSyDj3cwMmkyIoWuiGP9UBGGSKplnKcazeMM"
    response_dict = requests.get(retrieveurl).json()
    return response_dict["items"][0]["snippet"]["title"]