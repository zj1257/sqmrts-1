# coding=utf-8
# !/usr/bin/python
import sys
import re
sys.path.append('..')
from base.spider import Spider
import urllib.parse
import base64
from Crypto.Cipher import AES

class Spider(Spider):  # 元类 默认的元类 type
    def getName(self):
        return "创艺影视"

    def init(self, extend=""):
        print("============{0}============".format(extend))
        pass

    def homeContent(self, filter):
        result = {}
        cateManual = {
            "电影": "1",
            "剧集": "2",
            "动漫": "4",
            "综艺": "3",
            "纪录片": "30"
        }
        classes = []
        for k in cateManual:
            classes.append({
                'type_name': k,
                'type_id': cateManual[k]
            })

        result['class'] = classes
        if (filter):
            result['filters'] = self.config['filter']
        return result

    def homeVideoContent(self):
        url = 'https://www.30dian.cn/'
        rsp = self.fetch(url)
        root = self.html(self.cleanText(rsp.text))
        aList = root.xpath("//ul[@class='myui-vodlist clearfix']/li")
        videos = []
        for a in aList:
            # print(aList)
            name = a.xpath('./div/a/@title')[0]
            pic = a.xpath('./div/a/@data-original')[0]
            mark = a.xpath("./div/a/span/span[@class='tag']/text()")[0]
            sid = a.xpath("./div/a/@href")[0].replace("/", "").replace("voddetail", "").replace(".html", "")
            videos.append({
                "vod_id": sid,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": mark
            })
        result = {
            'list': videos
        }
        return result

    def categoryContent(self, tid, pg, filter, extend):
        result = {}
        # header = {"User-Agent": "Mozilla/5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.114 Mobile Safari/537.36"}
        url = 'https://www.30dian.cn/vodshow/{0}--hits------{1}---.html'.format(tid, pg)
        rsp = self.fetch(url)
        root = self.html(self.cleanText(rsp.text))
        aList = root.xpath("//ul[@class='myui-vodlist clearfix']/li")
        videos = []
        for a in aList:
            name = a.xpath('./div/a/@title')[0]
            pic = a.xpath('./div/a/@data-original')[0]
            mark = a.xpath("./div/a/span/span[@class='tag']/text()")[0]
            sid = a.xpath("./div/a/@href")[0].replace("/", "").replace("voddetail", "").replace(".html", "")
            videos.append({
                "vod_id": sid,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": mark
            })
        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = 999
        result['limit'] = 5
        result['total'] = 9999
        return result

    def detailContent(self, array):
        tid = array[0]
        url = 'https://www.30dian.cn/voddetail/{0}.html'.format(tid)
        rsp = self.fetch(url)
        root = self.html(self.cleanText(rsp.text))
        divContent = root.xpath("//div[@class='col-lg-wide-75 col-md-wide-7 col-xs-1 padding-0']")[0]
        title = divContent.xpath(".//div[@class='myui-content__detail']/h1/text()")[0]
        pic = divContent.xpath(".//div[@class='myui-content__thumb']/a/img/@data-original")[0]
        det = divContent.xpath(".//div[@class='col-pd text-collapse content']/span[@class='data']")[0]
        if det.text is None:
            detail = det.xpath(".//p/text()")[0]
        else:
            detail = det.text
        vod = {
            "vod_id": tid,
            "vod_name": title,
            "vod_pic": pic,
            "type_name": "",
            "vod_year": "",
            "vod_area": "",
            "vod_remarks": "",
            "vod_actor": "",
            "vod_director": "",
            "vod_content": detail
        }
        infoArray = divContent.xpath(".//div[@class='myui-content__detail']/p[contains(@class,'data')]")
        for info in infoArray:
            content = info.xpath('string(.)')
            flag = "分类" in content
            if flag == True:
                infon = content.replace("\t","").replace("\n","").strip().split('\r')
                for inf in infon:
                    if inf.startswith('分类'):
                        vod['type_name'] = inf.replace("分类：", "")
                    if inf.startswith('地区'):
                        vod['vod_area'] = inf.replace("地区：", "")
                    if inf.startswith('年份'):
                        vod['vod_year'] = inf.replace("年份：", "")
            if content.startswith('主演'):
                vod['vod_actor'] = content.replace("\xa0", "/").replace("主演：", "").strip('/')
            if content.startswith('更新'):
                vod['vod_remarks'] = content.replace("更新：", "")
            if content.startswith('导演'):
                vod['vod_director'] = content.replace("\xa0", "").replace("导演：", "").strip('/')

        vod_play_from = '$$$'
        playFrom = []
        vodHeader = divContent.xpath(".//div[@class='myui-panel_hd']/div/ul/li/a[contains(@href,'playlist')]/text()")
        for v in vodHeader:
            playFrom.append(v.replace(" ", ""))
        vod_play_from = vod_play_from.join(playFrom)
        vod_play_url = '$$$'
        playList = []
        vodList = divContent.xpath(".//div[contains(@id,'playlist')]")
        for vl in vodList:
            vodItems = []
            aList = vl.xpath('./ul/li/a')
            if len(aList) <= 0:
                name = '无法找到播放源'
                tId = '00000'
                vodItems.append(name + "$" + tId)
            else:
                for tA in aList:
                    href = tA.xpath('./@href')[0]
                    name = tA.xpath("./text()")[0].replace(" ", "")
                    tId = self.regStr(href, '/vodplay/(\\S+).html')
                    vodItems.append(name + "$" + tId)
            joinStr = '#'
            joinStr = joinStr.join(vodItems)
            playList.append(joinStr)
        vod_play_url = vod_play_url.join(playList)

        vod['vod_play_from'] = vod_play_from
        vod['vod_play_url'] = vod_play_url
        result = {
            'list': [
                vod
            ]
        }
        return result

    def searchContent(self, key, quick):
        url = 'https://www.30dian.cn/vodsearch/-------------.html?wd={0}'.format(key)
        rsp = self.fetch(url)
        root = self.html(self.cleanText(rsp.text))
        aList = root.xpath("//ul[contains(@class,'myui-vodlist__media clearfix')]/li")
        videos = []
        for a in aList:
            name = a.xpath(".//div[@class='detail']/h4/a/text()")[0]
            pic = a.xpath(".//a[contains(@class,'myui-vodlist__thumb')]//@data-original")[0]
            mark = a.xpath(".//span[@class='tag']/text()")[0]
            sid = a.xpath(".//div[@class='detail']/h4/a/@href")[0]
            sid = self.regStr(sid,'/voddetail/(\\S+).html')
            videos.append({
                "vod_id": sid,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": mark
            })
        result = {
            'list': videos
        }
        return result
    def parseCBC(self, enc, key, iv):
        keyBytes = key.encode("utf-8")
        ivBytes = iv.encode("utf-8")
        cipher = AES.new(keyBytes, AES.MODE_CBC, ivBytes)
        msg = cipher.decrypt(enc)
        paddingLen = msg[len(msg) - 1]
        return msg[0:-paddingLen]

    def playerContent(self, flag, id, vipFlags):
        result = {}
        if id == '00000':
            return {}
        url = 'https://www.30dian.cn/vodplay/{0}.html'.format(id)
        rsp = self.fetch(url)
        root = self.html(self.cleanText(rsp.text))
        scripts = root.xpath("//div[@class='embed-responsive clearfix']/script[@type='text/javascript']/text()")[0]
        ukey = re.findall(r"url(.*)url_next", scripts)[0].replace('"', "").replace(',', "").replace(':', "")
        pf = re.findall(r'\"from\":\"(.*?)\"', scripts)[0]
        purl = urllib.parse.unquote(ukey)
        if purl.startswith('http'):
            purl = purl
            if pf == 'wjm3u8':
                prsp = self.fetch(purl)
                purle = prsp.text.strip('\n').split('\n')[-1]
                purls = re.findall(r"http.*://.*?/", purl)[0].strip('/')
                purl = purls + purle
        else:
            scrurl = 'https://vip.30dian.cn/?url={0}'.format(purl)
            script = self.fetch(scrurl)
            html = script.text
            pat = 'var le_token = \\"([\\d\\w]+)\\"'
            cpat = 'getVideoInfo\\(\\"(.*)\\"\\)'
            content = self.regStr(html, cpat)
            iv = self.regStr(html, pat)
            key = 'A42EAC0C2B408472'
            purl = self.parseCBC(base64.b64decode(content), key, iv).decode()
        result["parse"] = 0
        result["playUrl"] = ''
        result["url"] = purl
        result["header"] = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"}
        return result

    config = {
        "player": {},
        "filter": {}
    }
    header = {}

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def localProxy(self, param):
        action = {
            'url': '',
            'header': '',
            'param': '',
            'type': 'string',
            'after': ''
        }
        return [200, "video/MP2T", action, ""]