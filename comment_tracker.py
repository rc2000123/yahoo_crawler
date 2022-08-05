import requests
import time    
import dbconnect as db
import datetime
import sys
import logging
from tqdm import tqdm
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

logger = rootLogger


with db.connect(logger) as conn:
    res = db.executeSQL(conn,"select id from yahoo_posts where comment_num is NULL",fetch=True)
    id_list = [x for (x,) in res]
        
    cnt = 10
    #rs_all = []
    rs_raw = []

    for context_id in tqdm(id_list):
        print(context_id)
        print("start")
        total_comments = 0
        
        cur_id_list = []

        for strt_idx in range(-1, 30000, cnt):
            print(strt_idx, cnt)
            url = f'https://tw.news.yahoo.com/_td/api/resource/canvass.getMessageListForContext_ns;apiVersion=v1;\
            context={context_id};count={cnt};index=v%3D1%3As%3Dpopular%3Asl%3D1643274360%3Aoff%3D{strt_idx}\
            ;lang=zh-Hant-TW;namespace=yahoo_content;oauthConsumerKey=frontpage.oauth.canvassKey;\
            oauthConsumerSecret=frontpage.oauth.canvassSecret;rankingProfile=;region=TW;sortBy=popular;\
            spaceId=2144909876;type=null;userActivity=true?bkt=news-TW-zh-Hant-TW-def&device=desktop&\
            ecma=modern&feature=cacheContentCanvas%2CenableCCPAFooter%2CenableCMP%2CenableConsentData%2CenableGDPRFooter\
            %2CenableGuceJs%2CenableGuceJsOverlay%2Clivecoverage%2CnewContentAttribution%2CnewLogo%2CoathPlayer%2CvideoDocking\
            %2Ccomments&intl=tw&lang=zh-Hant-TW&partner=none&prid=8854vh1gv4o3g&region=TW&site=news&tz=Asia%2FTaipei&ver=2.0.26426025&returnMeta=true'.replace('    ', '')
            while True:
                try:
                    rs = requests.get(url)
                    if rs.json().get('data'):
                        break
                except Exception as e:
                    print(e)
                    time.sleep(5)

            if rs.json()['data']['canvassMessages'] == []:
                break
            rs_raw.extend(rs.json()['data']['canvassMessages'])
            cur_id_list+=rs.json()['data']['canvassMessages']

            msg_list = rs.json()['data']['canvassMessages']
            for msg in msg_list:
                try:
                    url = msg['meta']['contextInfo']['url']
                except:
                    url = ""
                if (db.insertComment(conn,msg['contextId'],msg['messageId'],msg['meta']['author']['guid'],msg['meta']['author']['nickname'],msg['meta']['createdAt'],msg['meta']['updatedAt'],url,msg['details']['userText'])):
                    total_comments+=1
        db.executeSQL(conn,f"UPDATE yahoo_posts SET comment_num = {total_comments} WHERE id='{context_id}'")


