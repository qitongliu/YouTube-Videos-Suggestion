#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import text
from flask import Flask, request, render_template, g, redirect, Response, send_from_directory
from datetime import datetime
import time

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir,static_url_path='')
app.debug = True
# PROPAGATE_EXCEPTIONS = True

#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@w4111a.eastus.cloudapp.azure.com/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@w4111a.eastus.cloudapp.azure.com/proj1part2"
#
DATABASEURI = "postgresql://ql2257:3368@w4111a.eastus.cloudapp.azure.com/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args


  #
  # example of a database query
  #
  # cursor = g.conn.execute("SELECT name FROM test")
  # names = []
  # for result in cursor:
    # names.append(result['name'])  # can also be accessed using result[0]
  # cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = {})


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

@app.route('/static/css/<path:path>')
def send_css(path):
  return send_from_directory('/static/css',path)


#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/another')
def another():
  return render_template("another.html")


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test VALUES (NULL, ?)', name)
  return redirect('/')


@app.route('/<userId>/video/<videoId>')
def video(userId, videoId):
  s = text("SELECT * FROM video WHERE video_id = :x")
  cursor = g.conn.execute(s,x=videoId)
  vidobj = list(cursor)[0]
  vidtitle = vidobj['title']
  embed = vidobj['embed_code']
  numlikes = vidobj['like_count']
  numdislikes = vidobj['dislike_count']
  views = vidobj["view_count"]
  desc = vidobj["description"]
  date = vidobj["date"]
  cid = vidobj["channel_id"]
  cursor.close()
  s2 = text("SELECT * FROM comment WHERE video_id = :x")
  cursor = g.conn.execute(s2,x=videoId)
  allcomms = []
  for comment in cursor:
    comdict = dict(text=comment['text'],name=comment['display_name'],
      date =comment["com_date"],likes = comment['like_count'])
    allcomms.append(comdict)
  cursor.close()
  
  try:
    s4 = text("SELECT * FROM channel WHERE c_id = :x")
    cursor = g.conn.execute(s4,x=cid)
    cha = list(cursor)[0]
    cname = cha['c_title']
  except IndexError:
    cname = []

  context = dict(title=vidtitle,embhtml=embed,likes=numlikes,
    dislikes = numdislikes,comments = allcomms,views = views,
    desc = desc, date = date, cid = "../channel/" + cid, cname = cname)
  curtime = datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S")
  s3 = text("UPDATE watched SET watch_time=:z WHERE user_id=:x AND video_id=:y; \
    INSERT INTO watched (user_id, video_id, watch_time) \
    SELECT :x, :y, :z \
    WHERE NOT EXISTS (SELECT 1 FROM watched WHERE user_id = :x AND video_id = :y)")
  cursor = g.conn.execute(s3,x=userId,y=videoId,z=curtime)
  return render_template("video.html", **context)


@app.route('/<userId>/video/<videoId>/like',methods=['POST'])
def likevid(userId,videoId):
  s = text("INSERT INTO likes_1 (user_id, video_id) SELECT :x, :y WHERE NOT EXISTS (SELECT 1 FROM likes_1 WHERE user_id = :x AND video_id = :y)")
  cursor = g.conn.execute(s,x=userId,y=videoId)
  return "", 200, {'Content-Type': 'text/plain'}

@app.route('/<userId>/video/<videoId>/skip',methods=['POST'])
def skipvid(userId,videoId):
  print userId
  print videoId
  s = text("INSERT INTO skips (user_id, video_id) SELECT :x, :y WHERE NOT EXISTS (SELECT 1 FROM skips WHERE user_id = :x AND video_id = :y)")
  cursor = g.conn.execute(s,x=userId,y=videoId)

  s2 = text("(SELECT v1.video_id, v1.title, v1.dislike_count, v1.like_count, v1.view_count, v1.like_count/(1 + v1.dislike_count) AS ratio \
FROM uploaded_by ub1, video v1 \
WHERE v1.video_id = ub1.video_id AND ub1.c_id IN (SELECT st1.c_id \
FROM subscribes_to st1 \
WHERE st1.user_id = :x) AND v1.video_id NOT IN \
  (select watched.video_id from watched where watched.watch_time > (SELECT CURRENT_TIMESTAMP - INTERVAL '1 day') AND watched.user_id = :x)) \
UNION \
(SELECT v.video_id, v.title, v.dislike_count, v.like_count, v.view_count, v.like_count/(1 + v.dislike_count) AS ratio \
FROM likes_2 ub, video v \
WHERE v.video_id = ub.video_id AND ub.c_id IN (SELECT st.c_id \
FROM subscribes_to st \
WHERE st.user_id = :x) AND v.video_id NOT IN \
  (select watched.video_id from watched where watched.watch_time > (SELECT CURRENT_TIMESTAMP - INTERVAL '1 day') AND watched.user_id = :x)) \
ORDER BY ratio DESC \
LIMIT 1;")
  # print s2
  cursor = g.conn.execute(s2,x=userId)
  vidobj = list(cursor)[0]
  newvidid = vidobj["video_id"]
  print newvidid
  return redirect('/' + userId + '/video/' + newvidid)
  # return "", 200, {'Content-Type': 'text/plain'}





@app.route('/<userId>/channel/')
def channels(userId):
  s = text("SELECT * FROM channel c, subscribes_to st WHERE c.c_id = st.c_id and st.user_id = :x")
  cursor = g.conn.execute(s,x=userId)
  allch = []
  for ch in cursor:
    allch.append(dict(cid =  ch["c_id"],ctitle = ch["c_title"],
      cdesc = ch["c_description"],cviews = ch["c_view_count"],
      subs = ch["c_sub_count"]))
  cursor.close()
  for ch in allch:
    s = text("SELECT * FROM thumbnail t where t.t_url in (select ht2.t_url from has_thumb_2 ht2 where c_id = :x)")
    cursor = g.conn.execute(s,x=ch['cid'])
    thumbnail = list(cursor)[0]
    ch['thumb'] = thumbnail['t_url']
    cursor.close()

  s = text("SELECT * FROM users WHERE user_id = :x")
  cursor = g.conn.execute(s,x=userId)
  userobj = list(cursor)[0]
  username = userobj['username']
  cursor.close()

  context = dict(username = username, allch = allch)
  return render_template("channels.html", **context)









@app.route('/<userId>/channel/<channelId>')
def channel(userId, channelId):

  s = text("SELECT * FROM channel WHERE c_id = :x")
  cursor = g.conn.execute(s,x=channelId)
  chobj = list(cursor)[0]

  chtitle = chobj['c_title']
  desc = chobj['c_description']
  views = chobj['c_view_count']
  subs = chobj['c_sub_count']
  cursor.close()

  s2 = text("select * from thumbnail t where t.t_url in (select ht2.t_url from has_thumb_2 ht2 where c_id = :x)" )
  cursor = g.conn.execute(s2,x=channelId)
  thumbs = []
  for thumb in cursor:
    thumbs.append(thumb['t_url'])
  cursor.close()

  s3 = text("SELECT SUM(like_count) AS total_likes FROM video v, uploaded_by ub WHERE v.video_id = ub.video_id AND ub.c_id = :x GROUP BY ub.c_id")
  cursor = g.conn.execute(s3,x=channelId)
  likes = list(cursor)[0][0]
  cursor.close()

  s4 = text("select v.video_id, v.title from uploaded_by ub, video v where ub.video_id = v.video_id and ub.c_id = :x order by v.view_count desc limit 5")
  cursor = g.conn.execute(s4,x=channelId)
  # top_vids = [i[0] for i in list(cursor)]
  top_vids = []
  for vid in cursor:
    top_vids.append(dict(vid = "../video/" + vid["video_id"],title = vid["title"]))
  cursor.close()
  context = dict(title=chtitle,views=views,subs = subs,desc = desc,thumbs = thumbs,likes = likes,top = top_vids )
  return render_template("channel.html", **context)



@app.route('/<int:userId>/')
def users(userId):
  # print request.args
  # print userId
  # print type(userId)
  #
  # example of a database query
  #
  # cursor = g.conn.execute("SELECT name FROM test")
  # try:  
  # cursor = g.conn.execute("SELECT * FROM video WHERE video_id = '3dhKRWB1_IA'")
  # cursor = g.conn.execute("SELECT * FROM video WHERE video_id = '{0}'".format(videoId))
  # print "SELECT * FROM video WHERE video_id = '{0}'".format(videoId)
  # cursor = g.conn.execute("SELECT * FROM video limit 5")
  s = text("SELECT * FROM users WHERE user_id = :x")
  cursor = g.conn.execute(s,x=userId)
  userobj = list(cursor)[0]
  # print "197"
  # for result in cursor:
  #   names.append(result['video_id'])  # can also be accessed using result[0]
  username = userobj['username']
  cursor.close()
  # print username

  prof_pic = text("SELECT * FROM prof_pic WHERE user_id = :x")
  cursor = g.conn.execute(prof_pic, x=userId)
  prof_obj = list(cursor)[0]
  prof_url = prof_obj['t_url']
  cursor.close()

  likes_1 = text("SELECT * FROM likes_1 WHERE user_id = :x")
  cursor = g.conn.execute(likes_1, x=userId)
  likevidobjs = list(cursor)
  likevid = []
  for likevidobj in likevidobjs:
    likevid.append(likevidobj['video_id'])
  cursor.close()
  #print likevid

  likevideos = []
  for vid in likevid:
    like_vtab = text("SELECT * FROM video WHERE video_id = :x")
    cursor = g.conn.execute(like_vtab, x=vid)
    like_vtabobj = list(cursor)[0]
    likevideos.append(dict(vid = "video/" + vid, title = like_vtabobj['title']))
    cursor.close()

  skips = text("SELECT * FROM skips WHERE user_id = :x")
  cursor = g.conn.execute(skips, x=userId)
  skipvidobjs = list(cursor)
  skipvid = []
  for skipvidobj in skipvidobjs:
    skipvid.append(skipvidobj['video_id'])
  cursor.close()
  #print skipvid

  skipvideos = []
  for vid in skipvid:
    skip_vtab = text("SELECT * FROM video WHERE video_id = :x")
    cursor = g.conn.execute(skip_vtab, x=vid)
    skip_vtabobj = list(cursor)[0]
    skipvideos.append(dict(vid = "video/" + vid, title = skip_vtabobj['title']))
    cursor.close()

  watched = text("SELECT * FROM watched WHERE user_id = :x")
  cursor = g.conn.execute(watched, x=userId)
  watvidobjs = list(cursor)
  watvid = []
  for watvidobj in watvidobjs:
    watvid.append(watvidobj['video_id'])
  cursor.close()
  #print watvid

  watvideos = []
  for vid in watvid:
    wat_vtab = text("SELECT * FROM video WHERE video_id = :x")
    cursor = g.conn.execute(wat_vtab, x=vid)
    wat_vtabobj = list(cursor)[0]
    watvideos.append(dict(vid = "video/" + vid, title = wat_vtabobj['title']))
    cursor.close()

  #context = dict(username=username, userid=userId, likevid=likevid, skipvid=skipvid, watvid=watvid)
  context = dict(username=username, profurl=prof_url, userid=userId, likevideos=likevideos, skipvideos=skipvideos, watvideos=watvideos, cid= "../"+str(userId)+"/channel/")
  return render_template("user.html", **context)



@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=5001, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.debug=True
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
