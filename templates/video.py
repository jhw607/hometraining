from gettext import find
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.week00
datas = list(db.video.find({}))

# print(datas)/

uri = "mongodb+srv://cluster0.ctkbc.mongodb.net/myFirstDatabase?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
client = MongoClient(uri,tls=True, tlsCertificateKeyFile='X509-cert-6481087293358866486.pem')
db2 = client.data

db2.video.insert_many(datas)