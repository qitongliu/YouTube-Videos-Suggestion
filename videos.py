import pandas
from sqlalchemy import create_engine
from apiclient.discovery import build

execfile("../creds.py")

DEVELOPER_KEY = devkey
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

engine = create_engine("postgresql://ql2257:3368@w4111a.eastus.cloudapp.azure.com/proj1part2")

cur = engine.connect()

df = pandas.read_sql("SELECT * FROM channel",con=engine.raw_connection())

c_id = df["c_id"]

for ch in c_id:
	results = youtube.channels().list(part="contentDetails",id=ch).execute()
	playlistId = results["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
	results = youtube.playlistItems().list(part="snippet",playlistId=playlistId).execute()
	for item in results["items"]:
		# insert into video table
		video_id = item["snippet"]["resourceId"]["videoId"]
		results = youtube.videos().list(part="snippet,contentDetails,player,statistics",id=video_id).execute()
		results = results["items"][0]
		title = results["snippet"]["title"].replace("'","").replace("%","").encode('utf-8')
		description = results["snippet"]["description"].replace("'","").replace("%","").encode('utf-8')
		publishedAt = results["snippet"]["publishedAt"]
		length = results["contentDetails"]["duration"]
		embed_code = results["player"]["embedHtml"]
		view_count = results["statistics"]["viewCount"]
		like_count = results["statistics"]["likeCount"]
		dislike_count = results["statistics"]["dislikeCount"]
		q = "INSERT INTO Video SELECT '{0}','{1}','{2}','{3}','{4}','{5}','{6}',{7},{8},{9} WHERE NOT EXISTS (SELECT 1 FROM Video WHERE video_id = '{0}')".format(video_id,ch,title,description,publishedAt,length,embed_code,str(view_count),str(like_count),str(dislike_count)) 
		#(video_id,channel_id,title,description,date,length,embed_code,view_count,like_count,dislike_count)
		cur.execute(q)

		# insert into comment table
		results = youtube.commentThreads().list(part="snippet",maxResults=10,videoId=video_id).execute()
		for comm in results["items"]:
			commentId = comm["snippet"]["topLevelComment"]["id"]
			commentLikes = comm["snippet"]["topLevelComment"]["snippet"]["likeCount"]
			commentorImage = comm["snippet"]["topLevelComment"]["snippet"]["authorProfileImageUrl"]
			commentDate = comm["snippet"]["topLevelComment"]["snippet"]["updatedAt"]
			commentText = comm["snippet"]["topLevelComment"]["snippet"]["textDisplay"].encode("ascii","ignore").replace("'","").replace("%","")
			commentorName = comm["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"].encode("ascii","ignore").replace("'","").replace("%","")
			q = "INSERT INTO comment (com_id,video_id,text,com_date,display_name, profile_img,like_count) SELECT '{0}','{1}','{2}','{3}','{4}','{5}',{6} WHERE NOT EXISTS (SELECT 1 FROM comment WHERE com_id = '{0}')".format(commentId,video_id,commentText,commentDate,commentorName,commentorImage,str(commentLikes))
			cur.execute(q)
