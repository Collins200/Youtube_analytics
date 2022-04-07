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
pytrends = TrendReq(hl='en-US',requests_args={'verify':False})

app = Flask(__name__)

@app.route("/")
def index():

    results = []
    for country in pycountry.countries:
        results.append({
            "key": country.alpha_2,
            "text": "{}".format(country.name, country.alpha_2),
            })
    al=[]
    for d in results:
        a=(d['text'])
        al.append(a)
    
    timeframes = [{'key': 'today 5-y', 'text': '5 year period'},
                  {'key': 'today 12-m', 'text': '1 year period'},
                  {'key': 'today 3-m', 'text': '3 months period'},
                  {'key': 'today 1-m', 'text': '1 month period'}]
    period=[]
    for a in timeframes:
        d=(a['text'])
        period.append(d)
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

    
    
   
    keyword=['Fitness']
    # extract data about keywords
    # your_input=str(input('Enter the keyword: '))
    # your_input='Computer'
    # for k in your_input:
    #     keyword.append(k)
    # keyword.insert(0, your_input)
    # pytrends.build_payload(keyword,timeframe= 'today 3-m',gprop = 'youtube')

    pytrends.build_payload(keyword,timeframe=f'2020-02-26 {date.today()}', gprop = 'youtube', geo='AU')
    # word=keyword.pop()
    word='Fitness'
    
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

    # extract country-level data about the keywords
    data1=pytrends.interest_by_region(resolution='COUNTRY',inc_low_vol=True)
    data1.index.name = None
    data1.columns=[word]
    

    dat2=data1.astype(float).nlargest(10, word)
    #plot bar char with Pandas
    dat2.plot(kind='bar')

    # add titles
    plt.suptitle("Contries with highest searches of the keyword {}".format(word))
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

    df = pd.read_excel('/home/collins/Documents/APPLICATION/static/youtubers.xlsx')
    df.columns=['Country','YoutuberName','ContentType']

    return render_template('index.html',al=al,word=word,one=one,two=two,three=three,four=four,period=period,tables=[data.to_html(classes='data', header="true")],table1=[data1.to_html(classes='data1', header="true")],url='/static/images/plot.png',url1='/static/images/plot1.png',table3=[df.to_html(classes='data3')])

if __name__ =='__main__':

    app.run(debug=True,port=80,host='127.0.0.1')