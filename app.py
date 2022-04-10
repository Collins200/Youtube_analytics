from unicodedata import name
from flask import Flask,render_template,url_for,request
from pytrends.request import TrendReq
import pycountry
import numpy as np
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
import os
# create a pytrends object.request data from Google trends
# pytrends = TrendReq(hl='en-US',requests_args={'verify':False})
pytrends = TrendReq(hl='en-US',timeout=None,retries=4)

app = Flask(__name__)

@app.route("/",methods=['GET', 'POST'])
def index():

    results = []
    for country in pycountry.countries:
        results.append({
            "key": country.alpha_2,
            "text": "{}".format(country.name, country.alpha_2),
            })

    # results=[{"key": country.alpha_2,"text": "{}".format(country.name, country.alpha_2),}for country in pycountry.countries]

    # al=[]
    # for d in results:
    #     a=(d['text'])
    #     al.append(a)
    al=[d['text'] for d in results]

    
    timeframes = [{'key': 'today 5-y', 'text': '5 year period'},
                  {'key': 'today 12-m', 'text': '1 year period'},
                  {'key': 'today 3-m', 'text': '3 months period'},
                  {'key': 'today 1-m', 'text': '1 month period'}]
    # period=[]
    # for a in timeframes:
    #     d=(a['text'])
    #     period.append(d)
    period=[(a['text']) for a in timeframes]
        
    if request.method=='POST':        
        searchword = request.form.get("searchword")
        searchword=searchword.capitalize()
        searchword=searchword.replace(" ","%20")

        country= request.form.get("inputState")
        x=[item for item in results if item["text"] == country][0]
        codes = x["key"]
        codes=codes.upper()
        selectedtime= request.form.get("period")
        y=[item for item in timeframes if item["text"] == selectedtime ][0]
        timee = y["key"]

    
    
    # states=state.pop()
    keyword=['Dog']
    # extract data about keywords
    # your_input=str(input('Enter the keyword: '))
    # your_input='Computer'
    # for k in your_input:
    #     keyword.append(k)
    # keyword.insert(0, your_input)
    # pytrends.build_payload(keyword,timeframe= 'today 3-m',gprop = 'youtube')

    # pytrends.build_payload(keyword,timeframe=f'2020-02-26 {date.today()}', gprop = 'youtube', geo='AU')
    
    pytrends.build_payload(keyword,timeframe='today 5-y', gprop = 'youtube', geo='KE')
    # word=keyword.pop()
    word='Dog'
    
    # specify and get data
    data= pytrends.interest_over_time()
    data = data.drop(labels=['isPartial'],axis='columns')
    data.index.name = None
    data.columns=[word]
    plt.plot(data,label= word)
   
    # add titles
    plt.suptitle("Graphical analysis of keyword searches on youtube")
    plt.xlabel('period')
    plt.ylabel('searches')

    # add legend
    plt.legend(loc='best', shadow=True)
    plt.savefig('static/images/plot.png')

    pytrend = TrendReq(hl='en-US',timeout=None,retries=4)
    pytrend.build_payload(keyword,timeframe='today 5-y', gprop = 'youtube', geo='')
    # extract country-level data about the keywords

    data1=pytrend.interest_by_region(resolution='COUNTRY',inc_low_vol=True)
    data1.index.name = None
    data1.columns=[word]

 
    
    dat2=data1.astype(float).nlargest(10, word)
    #plot bar char with Pandas
    dat2.plot(kind='bar',color='#ff028a')


    # add titles
    plt.suptitle("Contries with highest searches of the keyword '{}'".format(word))
    plt.xlabel("Countries")
    plt.ylabel("average number of searches")
    plt.legend(loc='best', shadow=True)
    plt.savefig('static/images/plot1.png')

    mean = round(data.mean(),2)
    one=str(mean[word])

    # print(word + ': ' + str(mean[word]))

    avg = round(data[word][-52:].mean(),2)
    trend = round(((avg/mean[word])-1)*100,2)
    two=str(trend)
    three=abs(trend)
    four=mean[word]

    target = os.path.join(app.static_folder, 'youtubers.csv')
    df = pd.read_csv(target)
    df.columns=['Country','YoutuberName','ContentType']


    
    ContentType=df[df.iloc[:,0]=='Kenya'].iloc[0,2]
    YoutuberName=df[df.iloc[:,0]=='Kenya'].iloc[0,1]

    # test
    df_queries = pytrends.related_queries()
    top_related_queries = df_queries.get(word).get("top")
    # top_related_queries.sort_values(['value'], ascending = False).head(10).reset_index(drop = True)
    rising_related_queries= df_queries.get(word).get("rising")
    # rising_related_queries.sort_values(['value'], ascending = False).head(10)


    ###NOTE!!!!Let it print "Enter a more valid word in case of error"

    return render_template('index.html',al=al,word=word,one=one,two=two,three=three,Country=[],table1=[data1.to_html(classes='data1', header="true")],
    four=four,period=period,YoutuberName=YoutuberName,ContentType=ContentType,tables=[data.to_html(classes='data', header="true")],top_related_queries=[top_related_queries.to_html(classes='data', header="true")],rising_related_queries=[rising_related_queries.to_html(classes='data', header="true")],
    url='/static/images/plot.png',
    url1='/static/images/plot1.png',table3=[df.to_html(classes='data3')])

if __name__ =='__main__':

    app.run(debug=True,port=80,host='127.0.0.1')