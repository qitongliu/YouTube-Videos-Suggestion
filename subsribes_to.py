import pandas
from sqlalchemy import create_engine

engine = create_engine("postgresql://ql2257:3368@w4111a.eastus.cloudapp.azure.com/proj1part2")

cur = engine.connect()

df = pandas.read_sql("SELECT * FROM channel",con=engine.raw_connection())

user_id = [0,1] * 5
c_id = df["c_id"]

for i, item in enumerate(user_id):
	q = "INSERT INTO subscribes_to VALUES (" + str(user_id[i]) + ",'" + c_id[i] + "')" 
	cur.execute(q)
