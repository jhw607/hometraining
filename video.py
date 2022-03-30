from gettext import find
from pymongo import MongoClient
from pymongo import MongoClient

# ec2서버
client = MongoClient('mongodb://jungle:jungle@13.125.166.86',27017)
db = client.HomeTrainingDB


# mongo atlas
uri = "mongodb+srv://cluster0.ctkbc.mongodb.net/myFirstDatabase?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
client = MongoClient(uri,tls=True, tlsCertificateKeyFile='X509-cert-6481087293358866486.pem')
db_user = client.account
db_video = client.data
db_record = client.record

users = list(db_user.user.find({'id':'qq'},{'_id':False}))
videos = list(db_video.video.find({},{'_id':False}))
# records = list(db_record.record.find())

# print(users)
# print(videos)
# print(records)

db.user.insert_many(users)
db.video.insert_many(videos)
# db.record.insert_many(records)


# db = client.week00
# datas = list(db.video.find({}))
# db2.video.insert_many(datas)
