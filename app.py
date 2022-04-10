from unicodedata import name
from flask import Flask,render_template,url_for,request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
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
# 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://frlfqedqxcgdgc:7c686ae3294a9352b3dbc71a2153cf304449622e2524080eee3972f1cbaaf4fe@ec2-52-73-155-171.compute-1.amazonaws.com:5432/d4pfojjqsai9bd'
db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app,db)

# model 

class Youtubers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Country=db.Column(db.String(100), unique=True, nullable=False)
    YoutuberName=db.Column(db.String(100),  nullable=False)
    ContentType=db.Column(db.String(100),  nullable=False)



    def __repr__(self):
        return '<Youtuber %r>' % self.YoutuberName

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

        my_country= request.form.get("inputState")
        x=[item for item in results if item["text"] == country][0]
        codes = x["key"]
        codes=codes.upper()
        selectedtime= request.form.get("period")
        y=[item for item in timeframes if item["text"] == selectedtime ][0]
        timee = y["key"]

    
    
    # states=state.pop()
    keyword=['Computer']
    # extract data about keywords
    # your_input=str(input('Enter the keyword: '))
    # your_input='Computer'
    # for k in your_input:
    #     keyword.append(k)
    # keyword.insert(0, your_input)
    # pytrends.build_payload(keyword,timeframe= 'today 3-m',gprop = 'youtube')

    # pytrends.build_payload(keyword,timeframe=f'2020-02-26 {date.today()}', gprop = 'youtube', geo='AU')
    
    pytrends.build_payload(keyword,timeframe='today 5-y', gprop = 'youtube', geo='AU')
    # word=keyword.pop()
    word='Computer'
    
    # specify and get data
    data= pytrends.interest_over_time()
    data = data.drop(labels=['isPartial'],axis='columns')
    data.index.name = None
    data.columns=[word]
    # dataa=data.to_dict()

    plt.plot(data,label= word)
   
    # add titles
    plt.suptitle("Graphical analysis of keyword searches on youtube as a percentage")
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
    # dataa1=data1.to_dict()

 
    
    dat2=data1.astype(float).nlargest(10, word)
    #plot bar char with Pandas
    dat2.plot(kind='bar',color='#ff028a')


    # add titles
    plt.suptitle("Contries with highest searches of the keyword '{}' as a percentage".format(word))
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
    df.columns=['id','Country','YoutuberName','ContentType']


    
    ContentType=df[df.iloc[:,1]=='Kenya'].iloc[0,3]
    YoutuberName=df[df.iloc[:,1]=='Kenya'].iloc[0,2]

    # test
    df_queries = pytrends.related_queries()
    top_related_queries = df_queries.get(word).get("top")
    # top_related_queries.sort_values(['value'], ascending = False).head(10).reset_index(drop = True)
    rising_related_queries= df_queries.get(word).get("rising")
    # rising_related_queries.sort_values(['value'], ascending = False).head(10)


    ###NOTE!!!!Let it print "Enter a more valid word in case of error"

    return render_template('index.html',al=al,word=word,one=one,two=two,three=three,Country=[],
    table1=[data1.to_html(classes='data1 table', header="true")],four=four,period=period,
    YoutuberName=YoutuberName,ContentType=ContentType,tables=[data.to_html(classes='data  table', header="true")],
    top_related_query=[top_related_queries.to_html(classes='data table', header="true")if( top_related_queries is not None) else "No related keyword in your country"],
    rising_related_query=[rising_related_queries.to_html(classes='data table', header="true") if(rising_related_queries is not None) else "No related keyword in your country"],
    url='/static/images/plot.png',
    url1='/static/images/plot1.png',table3=[df.to_html(classes='data3 table')])

if __name__ =='__main__':

    app.run(debug=True,port=80,host='127.0.0.1')