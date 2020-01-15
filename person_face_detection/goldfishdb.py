#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import pymongo
import json
from bson import json_util


def save_data(data):
    connection = pymongo.MongoClient("localhost", 27017)
    db = connection.goldfish
    db.new.drop()
    result = db.new.insert_many(data)
    return 0


def merge_data(data):
    connection = pymongo.MongoClient("localhost", 27017)
    db = connection.goldfish
    db.merged.drop()
    ans = []
    aggs = [
        {"$project": {"PID": 1, "Height": 1, "Gender": 1, "Age": 1, "Time": 1, "x1": 1, "x2": 1, "y1": 1, "y2": 1}
         },
        {"$group": {"_id": "$PID", "avg_height": {"$avg": "$Height"}, "avg_gender": {"$avg": "$Gender"},
                    "avg_age": {"$avg": "$Age"}, "min_time": {"$min": "$Time"}, "max_time": {"$max": "$Time"},
                    "location": {"$push": {"x1": "$x1", "x2": "$x2", "y1": "$y1", "y2": "$y2"}
                                 }
                    }},
        {"$sort": {"_id": 1}}
    ]
    result = db.new.aggregate(pipeline=aggs)
    for c in result:
        loc = []
        loc.append(c['location'][0])
        loc.append(c['location'][-1])
        c['location'] = loc
        ans.append(c)
    result = db.merged.insert_many(ans)
    return 0


def export_json_original(path):
    connection = pymongo.MongoClient("localhost", 27017)
    db = connection.goldfish
    cursor = db.new.find()
    with open(path, 'w+') as f:
        json_docs = [json.dumps(doc, default=json_util.default) for doc in cursor]
        for json_doc in json_docs:
            f.write(json_doc)
            f.write("\n")


def export_json_merged(path):
    connection = pymongo.MongoClient("localhost", 27017)
    db = connection.goldfish
    cursor = db.merged.find()
    with open(path, 'w+') as f:
        """
        for i in db.merged.find():
            f.write(json.dumps(i))
            f.write("\n")
        """
        json_docs = [json.dumps(doc, default=json_util.default) for doc in cursor]
        for json_doc in json_docs:
            f.write(json_doc)
            f.write("\n")