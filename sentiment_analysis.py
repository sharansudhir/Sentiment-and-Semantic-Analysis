import json
from datetime import datetime
import re
from prettytable import PrettyTable
import csv

sentimentTable = PrettyTable(border=True)          #Pretty Table Declaration
sentimentTable.field_names = ["Tweet ID", "Tweet Message", "Matched Keywords", "Positive Count", "Negative Count", "result"] #Table Header
sentimentTable.align = "l"  #Table Alignment

finalOutput = {}

def extractData(filename):    #Function to load JSON File and Text File which contains negative and positve words
    existingData = []
    with open(filename, 'r') as contentFile:
        content = contentFile.read()

    if(content != ''):
        if(filename.endswith(".json")):
            existingData = json.loads(content)
        else:
            existingData = content.splitlines()
    return existingData

def dataClean(filename) -> []:   #Function to remove redundant data
    data = extractData(filename)
    dataOutput = []
    increementCounter = 1000
    for cursor in data:
        increementCounter = increementCounter + 1
        if(increementCounter > 1000 and increementCounter < 1650):                     #total number of tweets 550
            dateTimeObject = datetime.strptime(cursor['created_at'], '%a %b %d  %H:%M:%S %z %Y')
            dataObject = {'date_time': dateTimeObject.strftime('%Y-%m-%dT%H:%M:%SZ'),'tweet_id': 'tweet_' + str(increementCounter)}

            if('location' in cursor):    #store selected tweet location
                dataObject['location'] = cursor['location']
            else:
                dataObject['location'] = ''
            if(cursor['truncated'] and 'extended_tweet' in cursor):  #store full tweet of selected tweet
                dataObject['content'] = re.sub('\W+', ' ', cursor['extended_tweet']['full_text'])
            else:
                dataObject['content'] = re.sub('\W+', ' ', cursor['text'])

            if not(dataObject['content'].startswith("RT ")):
                dataOutput.append(dataObject)


    return dataOutput


twitterData = dataClean('tweets_data.json')   #Clean Twitter Data

tweetsList = []             #List to Store Tweet Bags



for i in twitterData:
    tweetBag = {}
    seperatedTweet = i['content'].split(" ")

    for key in seperatedTweet:
        if(key in tweetBag):
            tweetBag[key] = tweetBag[key] + 1
        else:
            tweetBag[key] = 1
    tweetBag['tweet_message'] = i
    tweetBag['tweet_id'] = i['tweet_id']
    tweetsList.append(tweetBag)

positiveWordsList = extractData("positiveWords.txt")        #laod Positive Wirds
negativeWordsList = extractData("negativeWords.txt")        #Load Negative Words


def tweetComparison(sentimentType):     #function to compare tweet bags with positive words and negative words

    if(sentimentType == "positive"):    #check for sentiment
        tweetListType = positiveWordsList
    else:
        tweetListType = negativeWordsList

    for wordInTweetBag in tweetListType:    #compare word in tweet bag with specific sentiment list type
        for i in range(len(tweetsList)):
            tweet = tweetsList[i]
            for key in list(tweet):

                if(key == wordInTweetBag):
                    tweetObject = {'tweet_message': tweet['tweet_message']['content']}

                    if(sentimentType == "positive"):
                        wordsListPositive = []


                        if(tweet['tweet_id'] in finalOutput):
                            temporaryTweetData = finalOutput[tweet['tweet_id']]
                            wordsListPositive = temporaryTweetData['wordsListPositive']
                            wordsListPositive.append(wordInTweetBag)
                            temporaryTweetData['wordsListPositive'] = wordsListPositive
                            finalOutput[tweet['tweet_id']] = temporaryTweetData

                        else:
                            wordsListPositive.append(wordInTweetBag)
                            tweetObject['wordsListPositive'] = wordsListPositive
                            finalOutput[tweet['tweet_id']] = tweetObject

                    if(sentimentType == "negative"):
                        wordsListNegative = []


                        if(tweet['tweet_id'] in finalOutput):
                            temporaryTweetData = finalOutput[tweet['tweet_id']]


                            if('wordsListNegative' in temporaryTweetData):
                                wordsListNegative = temporaryTweetData['wordsListNegative']
                                wordsListNegative.append(wordInTweetBag)
                                temporaryTweetData['wordsListNegative'] = wordsListNegative
                                finalOutput[tweet['tweet_id']] = temporaryTweetData
                            else:
                                wordsListNegative.append(wordInTweetBag)
                                temporaryTweetData['wordsListNegative'] = wordsListNegative
                                finalOutput[tweet['tweet_id']] = temporaryTweetData

                        else:
                            wordsListNegative.append(wordInTweetBag)
                            tweetObject['wordsListNegative'] = wordsListNegative
                            finalOutput[tweet['tweet_id']] = tweetObject


tweetComparison("positive")         #call comparison function
tweetComparison("negative")         #call comparison function


for key in finalOutput:  #set polarity and create each row
    wordsListPositive = []
    wordsListNegative = []
    tweetContent = finalOutput[key]['tweet_message']
    if("wordsListPositive" in finalOutput[key]):
        for word in finalOutput[key]['wordsListPositive']:
            wordsListPositive.append(word)

    if("wordsListNegative" in finalOutput[key]):
        for word in finalOutput[key]['wordsListNegative']:
            wordsListNegative.append(word)
    result = ""

    if(len(wordsListPositive) > len(wordsListNegative)):
        result = "Positive"

    elif(len(wordsListPositive) < len(wordsListNegative)):
        result = "Negative"

    else:
        result = "Neutral"
    sentimentTable.add_row([key, tweetContent, wordsListPositive + wordsListNegative, len(wordsListPositive), len(wordsListNegative), result])
wordsListPositive = []
wordsListNegative = []
for key in finalOutput:
    tweetContent = finalOutput[key]['tweet_message']

    if("wordsListPositive" in finalOutput[key]):
        for word in finalOutput[key]['wordsListPositive']:
            wordsListPositive.append(word)

    if("wordsListNegative" in finalOutput[key]):
        for word in finalOutput[key]['wordsListNegative']:
            wordsListNegative.append(word)


dataSentiment = sentimentTable.get_html_string()  #create html code for final data
totalList = wordsListPositive + wordsListNegative #combine positive and negative word list
mostOccurringWords = {}

for word in totalList:

    if(word in mostOccurringWords):
          mostOccurringWords[word] = mostOccurringWords[word] + 1
    else:
        mostOccurringWords[word] = 1

with open('mostOccurringWords.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['word', 'count'])
    w.writeheader()

    for key in mostOccurringWords:
        d = {'word': key, 'count': mostOccurringWords[key]}
        w.writerow(d)

with open("sentiment_analysis.html", "w") as textFile: #create html file
    textFile.write(dataSentiment)


