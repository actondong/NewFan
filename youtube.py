import requests
def searchID(url):
    if url.startswith("https://www.youtube.com/watch?v="):
        conststr = "https://www.youtube.com/watch?v="
        index = len(conststr);
        retrieveurl = "https://www.googleapis.com/youtube/v3/videos?part=id%2C+snippet&id="+url[index:]+"&key=AIzaSyAk3oNS-F8xuLs5G55nJQAxgTBxjMbIEz0"
        response_dict = requests.get(retrieveurl).json()
        if response_dict["items"]:
            return response_dict["items"][0]
    return None