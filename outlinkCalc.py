import math
import operator

RESULT = '/Users/vishruthkrishnaprasad/Downloads/IR/ASSGN4/LinkGraph.txt'
OUTPUT = '/Users/vishruthkrishnaprasad/Downloads/IR/ASSGN4/result.txt'
OUTPUT2 = '/Users/vishruthkrishnaprasad/Downloads/IR/ASSGN4/result2.txt'

P = set()
inlinks = dict()
outlinks = dict()
sinks = set()
perplexity = list()

D = 0.85

PR = dict()

def main():
    global inlinks
    global outlinks
    global sinks
    global P
    global PR

    createDicts()
    N = len(P)
    print(N)
    print(len(outlinks))
    print(len(sinks))
    iterations = 0

    for p in P:
        PR[p] = 1/N

    newPR = dict()

    while notConverged():
        iterations += 1
        print(iterations)
        sinkPR = 0
        for p in sinks:
            sinkPR += PR[p]
        for p in P:
            newPR[p] = (1 - D) / N
            newPR[p] += D * sinkPR / N
            for q in inlinks[p]:
                if q in PR:
                    newPR[p] += D * PR[q] / len(outlinks[q]) #chexk here pr n outlinks ''

        for p in P:
            PR[p] = newPR[p]

    print("Final: ", iterations)

    count = 0
    for val in sorted(PR.items(), key=operator.itemgetter(1), reverse=True):
        if count > 499:
            return


        f = open(OUTPUT, "a")
        f.write("score: " + str(PR[val[0]]) + " inlink count: " + str(len(inlinks[val[0]])) + " " + str(val[0]) + "\n")
        f.close()

        count += 1

def createDicts():
    global P
    global inlinks
    global outlinks
    global sinks

    count = set()
    f = open(RESULT, "r")
    alllines = f.readlines()

    for eachlinewithend in alllines:
        eachline = eachlinewithend.replace("\n", "")
        links = eachline.split(" ")
        setoflinks = set(links[1:])
        count.add(links[0])


        inlinks[links[0]] = set([link for link in links[1:] if link is not ""])
        P.add(links[0])


        for link in setoflinks:
            if link is "":
                continue
            else:
                if link not in outlinks:
                    outlinks[link] = {links[0]}
                else:
                    outlinks[link].add(links[0])

    setlinks = set(outlinks.keys())
    sinks = count - setlinks


def notConverged():
    global perplexity

    H = 0
    for val in PR:
        H += PR[val] * math.log(PR[val], 2)

    perplexity.append(2 ** (-H))

    print("inum: ", perplexity[-4:])
    if len(perplexity) < 5:
        return True

    count = 0
    diffelements = []

    for i in range(len(perplexity) - 5, len(perplexity) - 1):
        diffelements.append(int(perplexity[i]) - int(perplexity[i + 1]))

    print("diff: ", diffelements[-4:])
    for val in diffelements[-4:]:
        if val != 0:
            return True
        count += 1

    if count is 4:
        return False

    return True


if __name__ == '__main__':
    main()
