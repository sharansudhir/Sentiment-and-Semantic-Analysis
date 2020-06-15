import json
from datetime import datetime
import re
from prettytable import PrettyTable

print("***** Starting Program *****")
x = PrettyTable()

x.field_names = ["Tweet ID", "Tweet Message", "Matched Keywords", "Positive Count", "Negative Count", "Polarity"]
x.align = "l"

all_positive_tweets = []
all_negative_tweets = []
final_data = {}
query_keywords_list = ['Canada', 'University', 'Dalhousie University', 'Halifax', 'Canada Education']


def get_data_from_file(filename):
    existing_data = []
    with open(filename, 'r') as content_file:
        content = content_file.read()

    if content != '':
        if filename.endswith(".json"):
            existing_data = json.loads(content)
        else:
            existing_data = content.splitlines()
    return existing_data


def data_transformation_process(filename) -> []:
    file_data = get_data_from_file(filename)
    selected_data = []
    counter = 0
    for d in file_data:
        if counter < 550:
            datetime_object = datetime.strptime(d['created_at'], '%a %b %d  %H:%M:%S %z %Y')
            data_obj = {
                'date_time': datetime_object.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'tweet_id': 'tweet_' + str(counter)
            }
            counter = counter + 1
            if 'location' in d:
                data_obj['location'] = d['location']
            else:
                data_obj['location'] = ''
            if d['truncated'] and 'extended_tweet' in d:
                data_obj['content'] = re.sub('\W+', ' ', d['extended_tweet']['full_text'])
            else:
                data_obj['content'] = re.sub('\W+', ' ', d['text'])
            selected_data.append(data_obj)
    return selected_data


twitter_data = data_transformation_process('tweets_data.json')
tweets_list = []
for i in twitter_data:
    splitted_tweet = i['content'].split(" ")
    tweet_bag = {}
    for key in splitted_tweet:
        if key in tweet_bag:
            c = tweet_bag[key];
            tweet_bag[key] = c + 1
        else:
            tweet_bag[key] = 1
    tweet_bag['tweet_message'] = i
    tweet_bag['tweet_id'] = i['tweet_id']
    tweets_list.append(tweet_bag)

positive_words_list = get_data_from_file("positiveWords.txt")
negative_words_list = get_data_from_file("negativeWords.txt")


def tag_tweet_with_polarity(sentiment_type):
    list_type = []

    if sentiment_type == "positive":
        list_type = positive_words_list
    else:
        list_type = negative_words_list
    for word in list_type:
        for i in range(len(tweets_list)):
            tweet = tweets_list[i]
            for key in list(tweet):
                if key == word:
                    tweet_obj = {
                        'tweet_message': tweet['tweet_message']['content']
                    }
                    if sentiment_type == "positive":
                        pos_wrd_lst = []
                        if tweet['tweet_id'] in final_data:
                            tmp_tweet_obj = final_data[tweet['tweet_id']]
                            pos_wrd_lst = tmp_tweet_obj['pos_wrd_lst']
                            pos_wrd_lst.append(word)
                            tmp_tweet_obj['pos_wrd_lst'] = pos_wrd_lst
                            final_data[tweet['tweet_id']] = tmp_tweet_obj
                        else:
                            pos_wrd_lst.append(word)
                            tweet_obj['pos_wrd_lst'] = pos_wrd_lst
                            final_data[tweet['tweet_id']] = tweet_obj
                    if sentiment_type == "negative":
                        neg_wrd_lst = []
                        if tweet['tweet_id'] in final_data:
                            tmp_tweet_obj = final_data[tweet['tweet_id']]
                            if 'neg_wrd_lst' in tmp_tweet_obj:
                                neg_wrd_lst = tmp_tweet_obj['neg_wrd_lst']
                                neg_wrd_lst.append(word)
                                tmp_tweet_obj['neg_wrd_lst'] = neg_wrd_lst
                                final_data[tweet['tweet_id']] = tmp_tweet_obj
                            else:
                                neg_wrd_lst.append(word)
                                tmp_tweet_obj['neg_wrd_lst'] = neg_wrd_lst
                                final_data[tweet['tweet_id']] = tmp_tweet_obj
                        else:
                            neg_wrd_lst.append(word)
                            tweet_obj['neg_wrd_lst'] = neg_wrd_lst
                            final_data[tweet['tweet_id']] = tweet_obj


def merge_all_sentiments():
    for tweet in tweets_list:
        if "positive_tag_data" in tweet:
            for word_obj in tweet['positive_tag_data']:
                all_positive_tweets.append(word_obj)
        if "negative_tag_data" in tweet:
            for word_obj in tweet['negative_tag_data']:
                all_negative_tweets.append(word_obj)


tag_tweet_with_polarity("positive")
tag_tweet_with_polarity("negative")

for key in final_data:
    tweet_msg = final_data[key]['tweet_message']
    pos_wrd_lst = []
    neg_wrd_lst = []
    if "pos_wrd_lst" in final_data[key]:
        pos_wrd_lst = final_data[key]['pos_wrd_lst']
    if "neg_wrd_lst" in final_data[key]:
        neg_wrd_lst = final_data[key]['neg_wrd_lst']

    polarity = ""
    if len(pos_wrd_lst) > len(neg_wrd_lst):
        polarity = "Positive"
    elif len(pos_wrd_lst) < len(neg_wrd_lst):
        polarity = "Negative"
    else:
        polarity = "Neutral"
    x.add_row([key, tweet_msg, "1158259", len(pos_wrd_lst), len(neg_wrd_lst), polarity])

data_str = x.print_html(attributes={"name":"my_table", "class":"red_table"})
text_file = open("sample.html", "w")
n = text_file.write(data_str)
text_file.close()
print("***** Program Completed *****")
