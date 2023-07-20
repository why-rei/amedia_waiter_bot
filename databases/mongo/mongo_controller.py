from pymongo import MongoClient

client = MongoClient('localhost', 27017)

if __name__ == '__main__':
    db = client.mongo
    res = db.notice.find()

    for i in res:
        print(i['anime_id'])
