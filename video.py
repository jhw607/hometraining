from gettext import find
from pymongo import MongoClient
from pymongo import MongoClient

# ec2서버 
client = MongoClient('mongodb://jungle:jungle@13.125.166.86',27017)
db = client.HomeTrainingDB

# 배포용 서버
# client = MongoClient('mongodb://jungle:jungle@54.180.104.183',27017)
# db_publish = client.HomeTrainingDB

client2 = MongoClient('localhost',27017)
db2 = client2.HomeTrainingDB
# mongo atlas
# uri = "mongodb+srv://cluster0.ctkbc.mongodb.net/myFirstDatabase?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
# client = MongoClient(uri,tls=True, tlsCertificateKeyFile='X509-cert-6481087293358866486.pem')
# db_user = client.account
# db_video = client.data
# db_record = client.record

users = list(db.user.find({},{'_id':False}))
videos = list(db.video.find({},{'_id':False}))
records = list(db.record.find({},{'_id':False}))

# print(users)
# print(videos)
# print(records)

db2.user.insert_many(users)
db2.video.insert_many(videos)
db2.record.insert_many(records)


# db = client.week00
# datas = list(db.video.find({}))
# db2.video.insert_many(datas)
