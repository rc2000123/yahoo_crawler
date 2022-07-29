import requests
import time    
import dbconnect as db
import datetime
db.connect()



while True:
    #print(offset)
    url ='https://tw.news.yahoo.com/_td-news/api/resource/NewsSearchService'
    rs = requests.get(url)
    epoch_time = int(time.time())
    print(epoch_time)

    print(datetime.datetime.fromtimestamp(epoch_time).strftime("%m/%d/%Y, %H:%M:%S"))
    news_list = rs.json()
    for news in news_list:
        published_at = news['published_at']   
        if published_at.endswith(" 分鐘前"):
            published_at = published_at.removesuffix(' 分鐘前')
            published_at = epoch_time - int(published_at) * 60
        elif published_at.endswith(" 幾秒鐘前"):
            published_at = published_at.removesuffix(' 幾秒鐘前')
            published_at = epoch_time

        sql_str = "INSERT INTO yahoo_posts (id,provider_id,provider_name,published_at,summary,title,url) VALUES ('{id}','{provider_id}','{name}','{published_at}','{summary}','{title}','{url}')".format(id = news['id'], provider_id = news['provider_id'],name = news['provider_name'],published_at = published_at,summary = news['summary'],title = news['title'],url = news['url'])
        try:
            db.executeSQL(sql_str)
        except:
            print("duplicate")

    time.sleep(60)
db.disconnect()
