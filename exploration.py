import pprint

def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db

if __name__ == '__main__':
    db = get_db('udacity')
    # Number of documents
    db.barcelona.find().count() #890632

    # Number of unique users
    len(db.barcelona.aggregate([{
        "$group":{
            "_id":"$created.user",
            "count":{
                "$sum":1
            }
        }
    }])['result']) #1486

    #Top 1 contributing user
    db.barcelona.aggregate([{
        "$group":{
            "_id":"$created.user",
            "count":{
                "$sum":1
            }
        }
    },{"$sort":{"count":-1}},
    {"$limit":3}])['result']
    # [{u'count': 98459, u'_id': u'josepmunoz'}]}

    # Street types after cleaning
    pprint.pprint(db.barcelona.aggregate([{
        "$group" : {
            "_id" : "$address.st_type",
            "count" : { "$sum" : 1 }
        },
    }])['result'])
    '''
    [{u'_id': u'Cami', u'count': 3},
     {u'_id': u'Rambleta', u'count': 1},
     {u'_id': u'Autovia', u'count': 2},
     {u'_id': u'Gran', u'count': 104},
     {u'_id': u'Passatge', u'count': 298},
     {u'_id': u'Avinguda', u'count': 1033},
     {u'_id': u'Autopista', u'count': 4},
     {u'_id': u'Carrer', u'count': 7982},
     {u'_id': u'Via', u'count': 15},
     {u'_id': u'Placeta', u'count': 3},
     {u'_id': u'Rambla', u'count': 165},
     {u'_id': u'Travessera', u'count': 81},
     {u'_id': u'Carretera', u'count': 88},
     {u'_id': u'Placa', u'count': 36},
     {u'_id': u'Passeig', u'count': 141},
     {u'_id': u'Ronda', u'count': 114},
     {u'_id': None, u'count': 880562}]
    '''
