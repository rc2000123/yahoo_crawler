import requests
import time    
import dbconnect as db
import datetime
import sys
import logging

logging.basicConfig(
    datefmt='%Y-%m-%d:%H:%M:%S',
    force=True,
    level=logging.DEBUG)


logFormatter = logging.Formatter("%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s")

rootLogger = logging.getLogger()

fileHandler = logging.FileHandler("log.txt")
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

'''
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logging.debug("Debug logging test...")
logging.basicConfig(filename="log.txt", level=logging.DEBUG)
'''
logger = rootLogger


with db.connect(logger) as conn:


    offset = 0
    while True:
        print(offset)
        url =f'https://tw.news.yahoo.com/_td-news/api/resource/NewsSearchService;offset={offset}'
        rs = requests.get(url)

        if rs.json() == []:
            break

        epoch_time = int(time.time())
        str_time = datetime.datetime.fromtimestamp(epoch_time).strftime("%m/%d/%Y, %H:%M:%S")
        logger.info("current cycle: "+str_time)

        try:
            news_list = rs.json()
            time.sleep(10)
        except:
            continue

        for news in news_list:
            try:
                published_at = news['published_at']   
                if published_at.endswith(" 分鐘前"):
                    published_at = published_at.removesuffix(' 分鐘前')
                    published_at = epoch_time - int(published_at) * 60
                elif published_at.endswith("幾秒前"):
                    #published_at = published_at.removesuffix(' 幾秒鐘前')
                    published_at = epoch_time
                elif published_at.endswith(" 小時前"):
                    published_at = published_at.removesuffix(" 小時前")
                    published_at = epoch_time - int(published_at) * 60 * 60

                else:
                    raise Exception(published_at + " published_at parsing error") 
                if(db.insertPost(conn,news['id'],news['provider_id'],news['provider_name'],published_at,news['summary'],news['title'],news['url'],datetime.datetime.fromtimestamp(published_at).strftime("%m/%d/%Y, %H:%M:%S"))):
                    logger.info("inserted: " + news['title'] + "at: " + datetime.datetime.fromtimestamp(published_at).strftime("%m/%d/%Y, %H:%M:%S"))
            except:
                logger.error("Error in news insertion, continuing for now")
            #sql_str = "INSERT INTO yahoo_posts (id,provider_id,provider_name,published_at,summary,title,url,time) VALUES ('{id}','{provider_id}','{name}','{published_at}','{summary}','{title}','{url}','{time}')".format(id = news['id'], provider_id = news['provider_id'],name = news['provider_name'],published_at = published_at,summary = news['summary'],title = news['title'],url = news['url'],time = datetime.datetime.fromtimestamp(published_at).strftime("%m/%d/%Y, %H:%M:%S"))
            #if(db.executeSQL(sql_str)):
            #    logger.info("inserted: " + news['title'] + "at: " + datetime.datetime.fromtimestamp(published_at).strftime("%m/%d/%Y, %H:%M:%S"))
        


    while True:
        #print(offset)
        url ='https://tw.news.yahoo.com/_td-news/api/resource/NewsSearchService'
        rs = requests.get(url)
        epoch_time = int(time.time())
        str_time = datetime.datetime.fromtimestamp(epoch_time).strftime("%m/%d/%Y, %H:%M:%S")
        logger.info("current cycle: "+str_time)

        try:
            news_list = rs.json()
            time.sleep(10)
        except:
            continue

        for news in news_list:
            published_at = news['published_at']   
            if published_at.endswith(" 分鐘前"):
                published_at = published_at.removesuffix(' 分鐘前')
                published_at = epoch_time - int(published_at) * 60
            elif published_at.endswith("幾秒前"):
                #published_at = published_at.removesuffix(' 幾秒鐘前')
                published_at = epoch_time
            elif published_at.endswith(" 小時前"):
                published_at = published_at.removesuffix(" 小時前")
                published_at = epoch_time - int(published_at) * 60 * 60

            else:
                raise Exception(published_at + " published_at parsing error") 
            if(db.insertPost(conn,news['id'],news['provider_id'],news['provider_name'],published_at,news['summary'],news['title'],news['url'],datetime.datetime.fromtimestamp(published_at).strftime("%m/%d/%Y, %H:%M:%S"))):
                logger.info("inserted: " + news['title'] + "at: " + datetime.datetime.fromtimestamp(published_at).strftime("%m/%d/%Y, %H:%M:%S"))
            
            #sql_str = "INSERT INTO yahoo_posts (id,provider_id,provider_name,published_at,summary,title,url,time) VALUES ('{id}','{provider_id}','{name}','{published_at}','{summary}','{title}','{url}','{time}')".format(id = news['id'], provider_id = news['provider_id'],name = news['provider_name'],published_at = published_at,summary = news['summary'],title = news['title'],url = news['url'],time = datetime.datetime.fromtimestamp(published_at).strftime("%m/%d/%Y, %H:%M:%S"))
            #if(db.executeSQL(sql_str)):
            #    logger.info("inserted: " + news['title'] + "at: " + datetime.datetime.fromtimestamp(published_at).strftime("%m/%d/%Y, %H:%M:%S"))
        time.sleep(60)
