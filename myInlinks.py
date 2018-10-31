import math
import operator
from elasticsearch import Elasticsearch
import random

LINKGRAPH = '/Users/vishruthkrishnaprasad/Downloads/IR/ASSGN4/LinkGraph.txt'
RESULT = '/Users/vishruthkrishnaprasad/Downloads/IR/ASSGN4/elastitest.txt'
OUTPUT = '/Users/vishruthkrishnaprasad/Downloads/IR/ASSGN4/hubscore2.txt'
OUTPUT2 = '/Users/vishruthkrishnaprasad/Downloads/IR/ASSGN4/authorities2.txt'

INDEX = 'crawler'
DOC_TYPE = 'document'

inlinks = dict()
outlinks = dict()
hubperplexity = list()
autperplexity = list()
authority = dict()
hub_scores = dict()
root_set = set()
base_set = set()


def main():
    getAllInlinks()
    buildBase()
    calcHits()
    writeFile()


def getAllInlinks():
    global inlinks
    global outlinks

    f = open(LINKGRAPH, "r")
    alllines = f.readlines()

    for eachlinewithend in alllines:
        eachline = eachlinewithend.replace("\n", "")
        links = eachline.split(" ")
        setoflinks = set(links[1:])
        inlinks[links[0]] = set([link for link in links[1:] if link is not ""])

        for link in setoflinks:
            if link is "":
                continue
            else:
                if link not in outlinks:
                    outlinks[link] = {links[0]}
                else:
                    outlinks[link].add(links[0])

def buildBase():
    global inlinks
    global root_set
    global base_set

    es = Elasticsearch()
    action = {
        "query": {
            "match": {
                "TEXT": "BASKETBALL STARS AND RECORDS"
            }
        }
        , "_source": ["OUTLINKS", "INLINKS"]
        , "size": 1000
    }

    top1000 = es.search(index=INDEX, doc_type=DOC_TYPE, body=action)["hits"]["hits"]

    for doc in top1000:
        root_set.add(doc["_id"])
        root_set | set([val for val in doc["_source"]["OUTLINKS"].split(" ") if val is not ""])

    base_set = root_set.copy()
    memorydic = dict()

    while len(base_set) < 10000:
        for id in root_set:
            if len(base_set) > 10000:
                break
            memorydic[id] = set()
            if id not in inlinks:
                continue
            else:
                realinlinks = list(inlinks[id])
                length = len(realinlinks)
                if length > 200:
                    i = 0
                    memory = memorydic[id]

                    while i < length and i < 201:
                        num = random.randint(0, length - 1)
                        if num not in memorydic[id]:
                            memory.add(num)
                            base_set.add(realinlinks[num])
                            i += 1
                        elif len(memory) is length:
                            i = length
                    memorydic[id] = memory
                else:
                    base_set = base_set | set(realinlinks)
                print(len(base_set))

        root_set = base_set


# -----------


    # datacollected = {}
    # for doc in top1000:
    #     realinlinks = [val for val in doc["_source"]["INLINKS"].split("\n") if val is not ""]
    #     realoutlinks = [val for val in doc["_source"]["OUTLINKS"].split(" ") if val is not ""]
    #
    #     length = len(realinlinks) - 1
    #     if length > 200:
    #         links200 = []
    #         for i in range(201):
    #             links200.append(realinlinks[random.randint(0, length)])
    #         realinlinks = links200
    #
    #     length = len(realoutlinks) - 1
    #     if length > 200:
    #         links200 = []
    #         for i in range(201):
    #             links200.append(realoutlinks[random.randint(0, length)])
    #         realoutlinks = links200
    #
    #     inlinks[doc["_id"]] = {"INLINKS": realinlinks}
    #     outlinks[doc["_id"]] = {"OUTLINKS": realoutlinks}
    #     datacollected[doc["_id"]] = {"INLINKS": realinlinks, "OUTLINKS": realoutlinks}
    #
    #     authority[doc["_id"]] = 1
    #     hub_scores[doc["_id"]] = 1

    # print(len(datacollected))

def calcHits():
    global base_set
    global hub_scores
    global authority

    for p in base_set:
        authority[p] = 1
        hub_scores[p] = 1
    hubsAndAuthorities()

def hubsAndAuthorities():
    global inlinks
    global outlinks


    while autNotConverged():# or hubNotConverged():
        norm = 0
        for p in base_set:
            if p in inlinks and len(inlinks[p]) > 0:
                authority[p] = 0
            # if p not in inlinks:
            #     continue
            # else:
                for q in inlinks[p]:
                    if q not in hub_scores:
                        hub_scores[q] = 1
                    authority[p] += hub_scores[q]
                norm += authority[p] ** 2
        norm = math.sqrt(norm)
        for p in base_set:
            authority[p] = authority[p] / norm
        norm = 0
        for p in base_set:
            if p in outlinks and len(outlinks[p]) > 0:
                hub_scores[p] = 0

            # if p not in outlinks:
            #     continue
            # else:
                for r in outlinks[p]:
                    if r not in authority:
                        authority[r] = 1
                    hub_scores[p] += authority[r]
                    norm = hub_scores[p] ** 2
        norm += math.sqrt(norm)
        for p in base_set:
            hub_scores[p] = hub_scores[p] / norm


# def hubNotConverged():
#     global hub_scores
#     global perplexity
#
#     Hh = 0
#     Ha = 0
#     for val in hub_scores:
#         # if int(hub_scores[val]) is not 0:
#             Hh += hub_scores[val] * math.log(hub_scores[val], 2)
#
#     for val in authority:
#         # if int(authority[val]) is not 0:
#             Ha += authority[val] * math.log(authority[val], 2)
#
#     perplexity.append(2 ** (-Ha))
#
#     print("hub: ", perplexity[-4:])
#     if len(perplexity) < 5:
#         return True
#
#     count = 0
#     diffelements = []
#
#     for i in range(len(perplexity) - 5, len(perplexity) - 1):
#         diffelements.append(int(perplexity[i]) - int(perplexity[i + 1]))
#
#     print("hub diff: ", diffelements[-4:])
#     for val in diffelements[-4:]:
#         if val != 0:
#             return True
#         count += 1
#
#     if count is 4:
#         return False
#
#     return True


def autNotConverged():
    global hub_scores
    global hubperplexity
    global authority
    global autperplexity


    Hh = 0
    Ha = 0

    for val in hub_scores:
        if int(hub_scores[val]) is not 0:
        # print(hub_scores[val], val)
            Hh += hub_scores[val] * math.log(hub_scores[val], 2)

    hubperplexity.append(2 ** (-Hh))

    for val in authority:
        if int(authority[val]) is not 0:
        # print(hub_scores[val], val)
            Ha += authority[val] * math.log(authority[val], 2)

    autperplexity.append(2 ** (-Ha))

    print("hub: ", hubperplexity[-4:], "aut: ", autperplexity[-4:])
    if len(hubperplexity) < 5:
        return True

    count = 0
    hubdiffelements = []
    autdiffelements = []

    for i in range(len(hubperplexity) - 5, len(hubperplexity) - 1):
        hubdiffelements.append(int(hubperplexity[i]) - int(hubperplexity[i + 1]))

    for i in range(len(autperplexity) - 5, len(autperplexity) - 1):
        autdiffelements.append(int(autperplexity[i]) - int(autperplexity[i + 1]))


    print("aut diff: ", autdiffelements[-4:], "hub diff: ", hubdiffelements[-4:])
    for val in hubdiffelements[-4:]:
        if val != 0:
            return True
        count += 1

    if count is 4:
        count = 0
        for val in autdiffelements[-4:]:
            if val != 0:
                return True
            count += 1

        if count is 4:
            return False

    return True

def writeFile():
    global hub_scores
    global authority

    f = open(OUTPUT, "w")
    count = 0
    for val in sorted(hub_scores.items(), key=operator.itemgetter(1), reverse=True):
        if count > 499:
            break
        f.write(str(val[0]) + "\t" + str(round(hub_scores[val[0]], 4)) + "\n")
        count += 1
    f.close()

    f = open(OUTPUT2, "w")
    count = 0
    for val in sorted(authority.items(), key=operator.itemgetter(1), reverse=True):
        if count > 499:
            break
        f.write(str(val[0]) + "\t" + str(round(authority[val[0]], 4)) + "\n")
        count += 1
    f.close()


if __name__ == '__main__':
    main()
