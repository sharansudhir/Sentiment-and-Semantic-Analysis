import json
import math
from prettytable import PrettyTable

with open('art.json','r') as myfile:    #load news article
     obj = json.load(myfile)

frequency = {}

y = PrettyTable(border=True)    #Pretty Table for TFIDF
y.field_names = ['Search Query','Document containing term(df)','Total Documents(N)/ number of documents term appeared (df)','Log10(N/df)']
y.align = "l"

z = PrettyTable(border=True)    #Pretty Table for frequency count
z.field_names = ['Canada word appearance','Total Words(m)','Frequency(f)']
z.align = 'l'

doc = {"Canada":0,"University":0,"Dalhousie University":0,"Halifax":0,"Canada Education":0}
dict1={}

def TFIDF(total):   #function to calculate Term Frequency-Inverse Document Frequency
    total_split = total.split(" ")

    search_query_1 = ["Canada", "University", "Dalhousie University", "Halifax", "Canada Education"] #search query
    search_query_2 = ["Dalhousie University", "Canada Education"]   #search query

    for search in search_query_1:   #start search for search_query_1
        for i in range(len(total_split)):
            if(total_split[i].lower() == search.lower() or search.lower() == total_split[i].lower()[0:len(search)]):
                doc[search] = doc[search] +1
                break

    for search in search_query_2:   #start search for search_query_2
        for i in range(len(total_split)-1):
            x=total_split[i] + " " + total_split[i+1]
            if(x.lower() == search.lower() or x.lower()[0:len(search)]==search.lower()):
                doc[search] = doc[search] +1
                break



def occurence(words):   #function to count occurence of word Canada
    list = []
    words_split = words.split(" ")
    total_words = len(words_split)
    freq = 0
    list.append(total_words)
    for i in range(total_words):
        if(words_split[i].lower() == "Canada" or words_split[i].lower() == "canada"):
            freq = freq + 1
    list.append(freq)
    return list

def calculate_relative_frequency(list):     #function to calculate relative function
    rf =round(list[1]/list[0],2)
    return rf

def log_calc(value):        #function to calculate log value
    return(math.log10(value))

for i in range(len(obj)):
    total = str(obj[i]["title"])+" "+str(obj[i]["description"])+" "+str(obj[i]["content"]) #combine string
    TFIDF(total)    #
    l = occurence(total)

    frequency[str(obj[i]["content"])] = l


relativefreq={}
div = []

for i in doc:

   if(doc[i]!=0):
       dict1[i] = log_calc(len(obj) / doc[i])
       div.append(len(obj) / doc[i])
   else:
       dict1[i] = doc[i]
       div.append(doc[i])

for i in frequency:

    x = calculate_relative_frequency(frequency[i])
    relativefreq[i]=x



x=sorted(relativefreq.items(), key=lambda x: x[1])

print("The Highest Relative Frequency Article: "+ x[len(x)-1][0])   #highest relative frequency article


search_query = list(doc.keys())
document_containing_term = list(doc.values())
log_values = list(dict1.values())

for i in range(len(search_query)):
    y.add_row([search_query[i], document_containing_term[i],div[i],log_values[i]])

data_str = y.get_html_string()  #create TFIDF table html code

articles = list(frequency.keys())
words_and_frequency = list(frequency.values())

for i in range(len(articles)):
    z.add_row([articles[i],words_and_frequency[i][0],words_and_frequency[i][1]])

data = z.get_html_string()  #create frequency table html code

with open("TFIDF.html", "w") as textFile:  #create TFIDF table html file
    textFile.write(data_str)


with open("frequency_table.html", "w") as textFile:  #create frequency table html file
    textFile.write(data)


