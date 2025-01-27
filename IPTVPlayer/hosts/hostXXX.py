﻿# -*- coding: utf-8 -*-
# Modified by Blindspot - 2022.04.28.
# Fixed YouPorn and RedTube
###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.components.ihost import IHost, CDisplayListItem, RetHost, CUrlItem
import Plugins.Extensions.IPTVPlayer.libs.pCommon as pCommon
from Plugins.Extensions.IPTVPlayer.libs import ph
from Plugins.Extensions.IPTVPlayer.tools.iptvtypes import strwithmeta
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, CSearchHistoryHelper, CSelOneLink, GetTmpDir, GetCookieDir, iptv_system, GetPluginDir, byteify, rm
from Plugins.Extensions.IPTVPlayer.iptvdm.iptvdh import DMHelper
from Plugins.Extensions.IPTVPlayer.libs.urlparser import urlparser 
from Plugins.Extensions.IPTVPlayer.tools.iptvfilehost import IPTVFileHost
from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _, SetIPTVPlayerLastHostError, GetIPTVSleep, GetIPTVNotify
from Plugins.Extensions.IPTVPlayer.libs.youtube_dl.utils import clean_html 
from Plugins.Extensions.IPTVPlayer.libs.urlparserhelper import decorateUrl, getDirectM3U8Playlist, unpackJSPlayerParams, TEAMCASTPL_decryptPlayerParams
###################################################
# FOREIGN import
###################################################
import re, urllib, urllib2, base64, math, hashlib, random
try:
    import simplejson
except:
    import json as simplejson   
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Components.config import config, ConfigSelection, ConfigYesNo, ConfigText, ConfigInteger, getConfigListEntry, ConfigPIN, ConfigDirectory
from time import sleep, time as time_time
from datetime import datetime
from os import remove as os_remove, path as os_path, system as os_system
import urlparse
###################################################
# E2 GUI COMMPONENTS 
###################################################
from Plugins.Extensions.IPTVPlayer.tools.e2ijs import js_execute
from Screens.MessageBox import MessageBox
from Plugins.Extensions.IPTVPlayer.components.asynccall import MainSessionWrapper
###################################################
# Config options for HOST
###################################################
config.plugins.iptvplayer.datalinkek_login     = ConfigText(default = "", fixed_size = False)
config.plugins.iptvplayer.datalinkek_password  = ConfigText(default = "", fixed_size = False)
config.plugins.iptvplayer.xxxwymagajpin = ConfigYesNo(default = True)
config.plugins.iptvplayer.xxxlist = ConfigDirectory(default = "/hdd/")
config.plugins.iptvplayer.xxxsortuj = ConfigYesNo(default = True)
config.plugins.iptvplayer.xxxsearch = ConfigYesNo(default = False)
config.plugins.iptvplayer.xxxsortmfc = ConfigYesNo(default = False)
config.plugins.iptvplayer.xxxsortall = ConfigYesNo(default = True)
config.plugins.iptvplayer.camsoda = ConfigSelection(default="0", choices = [("0",_("https")), ("1",_("rtmp"))])
config.plugins.iptvplayer.xhamstertag = ConfigYesNo(default = False)
config.plugins.iptvplayer.chaturbate = ConfigSelection(default="", choices = [("",_("all")), ("female/",_("female")), ("couple/",_("couple")), ("trans/",_("trans")), ("male/",_("male"))])
config.plugins.iptvplayer.cam4 = ConfigSelection(default="0", choices = [("0",_("https")), ("1",_("rtmp"))])
config.plugins.iptvplayer.fotka = ConfigSelection(default="0", choices = [("0",_("https")), ("1",_("rtmp"))])
config.plugins.iptvplayer.xxxupdate = ConfigYesNo(default = False)
config.plugins.iptvplayer.xxxzbiornik = ConfigYesNo(default = False)
config.plugins.iptvplayer.xxx4k = ConfigYesNo(default = False)
config.plugins.iptvplayer.yourporn = ConfigInteger(4, (1, 99))  
config.plugins.iptvplayer.beeg = ConfigYesNo(default = True)

def GetConfigList():
    optionList = []
    optionList.append(getConfigListEntry(_("DataLinkek Login"), config.plugins.iptvplayer.datalinkek_login))
    optionList.append(getConfigListEntry(_("DataLinkek Password"), config.plugins.iptvplayer.datalinkek_password))
    optionList.append( getConfigListEntry(_("Pin protection for plugin")+" :", config.plugins.iptvplayer.xxxwymagajpin ) )
    optionList.append( getConfigListEntry(_("Path to xxxlist.txt :"), config.plugins.iptvplayer.xxxlist) )
    optionList.append( getConfigListEntry(_("Sort xxxlist :"), config.plugins.iptvplayer.xxxsortuj) )
    optionList.append( getConfigListEntry(_("Sort Myfreecams :"), config.plugins.iptvplayer.xxxsortmfc) )
    optionList.append( getConfigListEntry(_("Global search :"), config.plugins.iptvplayer.xxxsearch) )
    optionList.append( getConfigListEntry(_("Global sort :"), config.plugins.iptvplayer.xxxsortall) )
    optionList.append( getConfigListEntry(_("CHATURBATE preferences :"), config.plugins.iptvplayer.chaturbate) )
    #optionList.append( getConfigListEntry(_("Cam4 stream :"), config.plugins.iptvplayer.cam4) )
    #optionList.append( getConfigListEntry(_("Camsoda stream :"), config.plugins.iptvplayer.camsoda) )
    #optionList.append( getConfigListEntry(_("Fotka.pl stream :"), config.plugins.iptvplayer.fotka) )
    optionList.append( getConfigListEntry(_("Add tags to XHAMSTER :"), config.plugins.iptvplayer.xhamstertag) )
    optionList.append( getConfigListEntry(_("Show Profiles in ZBIORNIK MINI :"), config.plugins.iptvplayer.xxxzbiornik) )
    optionList.append( getConfigListEntry(_("YOURPORN Server :"), config.plugins.iptvplayer.yourporn) )
    optionList.append( getConfigListEntry(_("Show changelog :"), config.plugins.iptvplayer.xxxupdate) )
    optionList.append( getConfigListEntry(_("BEEG FullHD :"), config.plugins.iptvplayer.beeg) )
    optionList.append( getConfigListEntry(_("Playback UHD :"), config.plugins.iptvplayer.xxx4k) )

    return optionList
###################################################

###################################################
# Title of HOST
###################################################
def gettytul():
    return 'XXX'

class IPTVHost(IHost):
    LOGO_NAME = 'XXXlogo.png'
    PATH_TO_LOGO = resolveFilename(SCOPE_PLUGINS, 'Extensions/IPTVPlayer/icons/logos/' + LOGO_NAME )

    def __init__(self):
        printDBG( "init begin" )
        self.host = Host()
        self.prevIndex = []
        self.currList = []
        self.prevList = []
        printDBG( "init end" )
        
    def isProtectedByPinCode(self):
        return config.plugins.iptvplayer.xxxwymagajpin.value
    
    def getLogoPath(self):  
        return RetHost(RetHost.OK, value = [self.PATH_TO_LOGO])

    def getInitList(self):
        printDBG( "getInitList begin" )
        self.prevIndex = []
        self.currList = self.host.getInitList()
        self.host.setCurrList(self.currList)
        self.prevList = []
        printDBG( "getInitList end" )
        return RetHost(RetHost.OK, value = self.currList)

    def getListForItem(self, Index = 0, refresh = 0, selItem = None):
        printDBG( "getListForItem begin" )
        self.prevIndex.append(Index)
        self.prevList.append(self.currList)
        self.currList = self.host.getListForItem(Index, refresh, selItem)
        printDBG( "getListForItem end" )
        return RetHost(RetHost.OK, value = self.currList)

    def getPrevList(self, refresh = 0):
        printDBG( "getPrevList begin" )
        if(len(self.prevList) > 0):
            self.prevIndex.pop()
            self.currList = self.prevList.pop()
            self.host.setCurrList(self.currList)
            printDBG( "getPrevList end OK" )
            return RetHost(RetHost.OK, value = self.currList)
        else:
            printDBG( "getPrevList end ERROR" )
            return RetHost(RetHost.ERROR, value = [])

    def getCurrentList(self, refresh = 0):
        printDBG( "getCurrentList begin" )
        printDBG( "getCurrentList end" )
        return RetHost(RetHost.OK, value = self.currList)

    def getLinksForVideo(self, Index = 0, item = None):
        return RetHost(RetHost.NOT_IMPLEMENTED, value = [])
        
    def getResolvedURL(self, url):
        printDBG( "getResolvedURL begin" )
        if url != None and url != '':        
            ret = self.host.getResolvedURL(url)
            if ret != None and ret != '':        
               printDBG( "getResolvedURL ret: "+str(ret))
               list = []
               list.append(ret)
               printDBG( "getResolvedURL end OK" )
               return RetHost(RetHost.OK, value = list)
            else:
               printDBG( "getResolvedURL end" )
               return RetHost(RetHost.NOT_IMPLEMENTED, value = [])                
        else:
            printDBG( "getResolvedURL end" )
            return RetHost(RetHost.NOT_IMPLEMENTED, value = [])

    def getSearchResults(self, pattern, searchType = None):
        printDBG( "getSearchResults begin" )
        printDBG( "getSearchResults pattern: " +pattern)
        self.prevIndex.append(0)
        self.prevList.append(self.currList)
        self.currList = self.host.getSearchResults(pattern, searchType)
        printDBG( "getSearchResults end" )
        return RetHost(RetHost.OK, value = self.currList)

    ###################################################
    # Additional functions on class IPTVHost
    ###################################################

class Host:
    XXXversion = "2022.04.20.0"
    XXXremote  = "0.0.0.0"
    currList = []
    MAIN_URL = ''
    SEARCH_proc = ''
    
    def __init__(self):
        printDBG( 'Host __init__ begin' )
        self.cm = pCommon.common()
        self.up = urlparser() 
        self.history = CSearchHistoryHelper('xxx')
        self.sessionEx = MainSessionWrapper() 
        self.currList = []
        printDBG( 'Host __init__ end' )

    def setCurrList(self, list):
        printDBG( 'Host setCurrList begin' )
        self.currList = list
        printDBG( 'Host setCurrList end' )
        return 

    def getInitList(self):
        printDBG( 'Host getInitList begin' )
        _url = 'https://gitlab.com/iptv-host-xxx/iptv-host-xxx/raw/master/IPTVPlayer/hosts/hostXXX.py'
        query_data = { 'url': _url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        try:
           data = self.cm.getURLRequestData(query_data)
           #printDBG( 'Host init data: '+data )
           r=self.cm.ph.getSearchGroups(data, '''XXXversion = ['"]([^"^']+?)['"]''', 1, True)[0]
           if r:
              printDBG( 'XXXremote = '+r )
              self.XXXremote=r
        except:
           printDBG( 'Host init query error' )
        self.currList = self.listsItems(-1, '', 'main-menu')
        printDBG( 'Host getInitList end' )
        return self.currList

    def getListForItem(self, Index = 0, refresh = 0, selItem = None):
        printDBG( 'Host getListForItem begin' )
        valTab = []
        if len(self.currList[Index].urlItems) == 0:
           return valTab
        valTab = self.listsItems(Index, self.currList[Index].urlItems[0], self.currList[Index].urlSeparateRequest)
        self.currList = valTab
        printDBG( 'Host getListForItem end' )
        return self.currList

    def getSearchResults(self, pattern, searchType = None):
        printDBG( "Host getSearchResults begin" )
        printDBG( "Host getSearchResults pattern: " +pattern)
        valTab = []
        valTab = self.listsItems(-1, pattern, 'SEARCH')
        self.currList = valTab
        printDBG( "Host getSearchResults end" )
        return self.currList

    def _cleanHtmlStr(self, str):
        str = str.replace('<', ' <').replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        return clean_html(str).strip()

    def FullUrl(self, url):
        if url.startswith('//'):
            url = 'http:' + url
        return url

    def getPage(self, baseUrl, cookie_domain, cloud_domain, params={}, post_data=None):
        COOKIEFILE = os_path.join(GetCookieDir(), cookie_domain)
        self.USER_AGENT = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/37.0.2062.120 Chrome/37.0.2062.120 Safari/537.36'
        self.HEADER = {'User-Agent': self.USER_AGENT, 'Accept': 'text/html'}
        params['cloudflare_params'] = {'domain':cloud_domain, 'cookie_file':COOKIEFILE, 'User-Agent':self.USER_AGENT}
        return self.cm.getPageCFProtection(baseUrl, params, post_data)

    def getPage4k(self, baseUrl, cookie_domain, cloud_domain, params={}, post_data=None):
        COOKIEFILE = os_path.join(GetCookieDir(), cookie_domain)
        self.USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:21.0) Gecko/20100101 Firefox/21.0'
        def _getFullUrl(url):
            if self.cm.isValidUrl(url):
                return url
            else:
                return urlparse.urljoin(baseUrl, url) 
        if params == {}: params = dict(self.defaultParams)
        params['cookie_items'] = {'xxx':'ok'}
        params['cloudflare_params'] = {'domain':cloud_domain, 'cookie_file':COOKIEFILE, 'User-Agent':self.USER_AGENT, 'full_url_handle':_getFullUrl}
        return self.cm.getPageCFProtection(baseUrl, params, post_data)

    def _getPage(self, url, addParams = {}, post_data = None):
        
        try:
            import httplib
            def patch_http_response_read(func):
                def inner(*args):
                    try:
                        return func(*args)
                    except httplib.IncompleteRead, e:
                        return e.partial
                return inner
            prev_read = httplib.HTTPResponse.read
            httplib.HTTPResponse.read = patch_http_response_read(httplib.HTTPResponse.read)
        except Exception: printExc()
        sts, data = self.cm.getPage(url, addParams, post_data)
        try: httplib.HTTPResponse.read = prev_read
        except Exception: printExc()
        return sts, data

    def get_Page(self, baseUrl, addParams={}, post_data=None):
        if addParams == {}: addParams = dict(self.defaultParams)
        return self.cm.getPage(baseUrl, addParams, post_data)

    def listsItems(self, Index, url, name = ''):
        printDBG( 'Host listsItems begin' )
        printDBG( 'Host listsItems url: '+url )
        valTab = []
        self.format4k = config.plugins.iptvplayer.xxx4k.value
        self.beegfullhd = config.plugins.iptvplayer.beeg.value

        if name == 'main-menu':
           printDBG( 'Host listsItems begin name='+name )
           #if self.XXXversion <> self.XXXremote and self.XXXremote <> "0.0.0.0":
              #valTab.append(CDisplayListItem('---UPDATE---','UPDATE MENU',        CDisplayListItem.TYPE_CATEGORY,           [''], 'UPDATE',  '', None)) 
           valTab.append(CDisplayListItem('XHAMSTER',       'xhamster.com',       CDisplayListItem.TYPE_CATEGORY, ['https://xhamster.com/categories'],     'xhamster','https://1000logos.net/wp-content/uploads/2018/12/xHamster-Logo-768x432.png', None)) 
           valTab.append(CDisplayListItem('HOME MOVIES TUBE',     'http://www.homemoviestube.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.homemoviestube.com/channels/'],'HomeMoviesTube', 'http://www.homemoviestube.com/images/logo.png', None)) 
           valTab.append(CDisplayListItem('ZBIORNIK MINI',     'https://mini.zbiornik.com', CDisplayListItem.TYPE_CATEGORY, ['https://mini.zbiornik.com/filmy'],'ZBIORNIKMINI', 'https://static.zbiornik.com/upimg/0160d9c44a354d20e81f0e6df5fe832e.jpg', None)) 
           valTab.append(CDisplayListItem('HCLIPS',     'http://www.hclips.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.hclips.com/categories/'],'hclips', 'https://i.pinimg.com/474x/d3/16/78/d31678f3c99564740ab5b097e7792927.jpg', None)) 
           valTab.append(CDisplayListItem('4TUBE',          'www.4tube.com',      CDisplayListItem.TYPE_CATEGORY, ['https://www.4tube.com/tags'],          '4TUBE',   'http://cdn1.ht.ui.4tube.com/assets/img/layout/4tube-logo-1f503fd81c.png', None)) 
           valTab.append(CDisplayListItem('EPORNER',        'www.eporner.com',    CDisplayListItem.TYPE_CATEGORY, ['https://www.eporner.com/cats/'],   'eporner', 'http://static.eporner.com/new/logo.png', None)) 
           valTab.append(CDisplayListItem('TUBE8',          'www.tube8.com',      CDisplayListItem.TYPE_CATEGORY, ['http://www.tube8.com/categories.html'], 'tube8',   'http://cdn1.static.tube8.phncdn.com/images/t8logo.png', None)) 
           valTab.append(CDisplayListItem('YOUPORN',        'wwww.youporn.com',   CDisplayListItem.TYPE_CATEGORY, ['https://www.youporn.com/categories/'],'youporn', 'https://fs.ypncdn.com/cb/bundles/youpornwebfront/images/l_youporn_black.png?v=9b34af679da9f8f8279fb875c7bcea555a784ec3', None)) 
           valTab.append(CDisplayListItem('PORNHUB',        'www.pornhub.com',    CDisplayListItem.TYPE_CATEGORY, ['https://www.pornhub.com/categories'],    'pornhub', 'https://mk0onemorecupofd9ppb.kinstacdn.com/wp-content/uploads/2018/11/Make-Money-Pornhub.jpg', None)) 
           valTab.append(CDisplayListItem('HDPORN',         'www.hdporn.net',     CDisplayListItem.TYPE_CATEGORY, ['http://www.hdporn.net/channels/'],      'hdporn',  'http://www.hdporn.com/gfx/logo.jpg', None)) 
           valTab.append(CDisplayListItem('REDTUBE',        'www.redtube.com',    CDisplayListItem.TYPE_CATEGORY, ['http://www.redtube.com/categories'],      'redtube', 'http://img02.redtubefiles.com/_thumbs/design/logo/redtube_260x52_black.png', None)) 
           valTab.append(CDisplayListItem('HENTAIGASM',     'hentaigasm.com',     CDisplayListItem.TYPE_CATEGORY, ['http://hentaigasm.com'],                'hentaigasm','http://hentaigasm.com/wp-content/themes/detube/images/logo.png', None)) 
           valTab.append(CDisplayListItem('XVIDEOS',        'www.xvideos.com',    CDisplayListItem.TYPE_CATEGORY, ['http://www.xvideos.com'],               'xvideos', 'http://emblemsbf.com/img/31442.jpg', None)) 
           valTab.append(CDisplayListItem('XNXX',           'www.xnxx.com',       CDisplayListItem.TYPE_CATEGORY, ['http://www.xnxx.com'],                  'xnxx',    'http://www.naughtyalysha.com/tgp/xnxx/xnxx-porn-recip.jpg', None)) 
           valTab.append(CDisplayListItem('BEEG',           'beeg.com',           CDisplayListItem.TYPE_CATEGORY, ['https://beeg.com/'],                      'beeg',    'https://beeg.com/img/logo-light.77847dbd.jpg', None)) 
           valTab.append(CDisplayListItem('PORNRABBIT',     'www.pornrabbit.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.pornrabbit.com/'],'pornrabbit','https://www.ismytube.com/media/channels/24.png', None)) 
           valTab.append(CDisplayListItem('PORNHD',     'www.pornhd.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.pornhd.com/category'],'pornhd','https://pbs.twimg.com/profile_images/527104689444093952/PbRNZmMT_400x400.png', None)) 
           valTab.append(CDisplayListItem('AH-ME',     'www.ah-me.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.ah-me.com/channels.php'],'AH-ME','https://ahmestatic.fuckandcdn.com/ahmestatic/v30/common/ah-me/img/logo.jpg', None)) 
           valTab.append(CDisplayListItem('AMATEURPORN',     'https://www.amateurporn.me', CDisplayListItem.TYPE_CATEGORY, ['https://www.amateurporn.me/categories/'],'AMATEURPORN', 'https://www.amateurporn.me/images/logo.png', None)) 
           valTab.append(CDisplayListItem('YOUJIZZ',     'http://www.youjizz.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.youjizz.com/categories'],'YOUJIZZ', 'http://www.sample-made.com/cms/content/uploads/2015/05/youjizz_logo-450x400.jpg', None)) 
           valTab.append(CDisplayListItem('DACHIX',     'http://www.dachix.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.dachix.com/'],'DACHIX', 'http://thumbs.dachix.com/images/dachixcom_logo_noir.png', None)) 
           valTab.append(CDisplayListItem('DRTUBER',     'http://www.drtuber.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.drtuber.com/categories'],'DRTUBER', 'http://static.drtuber.com/templates/frontend/mobile/images/logo.png', None)) 
           valTab.append(CDisplayListItem('TNAFLIX',     'https://www.tnaflix.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.tnaflix.com/categories'],'TNAFLIX', 'https://pbs.twimg.com/profile_images/1109542593/logo_400x400.png', None)) 
           valTab.append(CDisplayListItem('DATALINKEK',     'https://datalinkek.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.datalinkek.com'],'DATALINKEK', 'https://datalinkek.com/images/styles/twisteddarkGreen/style/logo.png', None)) 
           valTab.append(CDisplayListItem('EXTREMETUBE',     'http://www.extremetube.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.extremetube.com/video-categories'],'EXTREMETUBE', 'http://www.wp-tube-plugin.com/feed-images/extremetube.png', None)) 
           valTab.append(CDisplayListItem('RUS.PORN',     'https://rusvidos.tv', CDisplayListItem.TYPE_CATEGORY, ['http://rus.porn/'],'RUSPORN', 'http://mixporn24.com/images/logo.png', None)) 
           #valTab.append(CDisplayListItem('PORN720',     'http://porn720.net/', CDisplayListItem.TYPE_CATEGORY, ['http://porn720.net/'],'PORN720', 'http://porn720.net/wp-content/themes/porn720/img/logo.png', None)) 
           valTab.append(CDisplayListItem('PORNTREX',     'http://www.porntrex.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.porntrex.com/categories/'],'PORNTREX', 'https://www.porntrex.com/images/logo.png', None)) 
           #valTab.append(CDisplayListItem('PORNDOE',     'https://www.porndoe.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.porndoe.com/categories'],'PORNDOE', 'https://pbs.twimg.com/media/C10-39tUQAEJbE5.jpg', None)) 
           valTab.append(CDisplayListItem('PORNfromCZECH',     'http://www.pornfromczech.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.pornfromczech.com/'],'PORNFROMCZECH', 'https://www.bing.com/th?id=OIP.LA7c-hQkzRto2v_bqXV1MQHaBJ&pid=Api', None)) 
           valTab.append(CDisplayListItem('FILMYPORNO',     'http://www.filmyporno.tv', CDisplayListItem.TYPE_CATEGORY, ['http://www.filmyporno.tv/channels/'],'FILMYPORNO', 'http://www.filmyporno.tv/templates/default_tube2016/images/logo.png', None)) 
           valTab.append(CDisplayListItem('CLIPHUNTER',     'http://www.cliphunter.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.cliphunter.com/categories/'],'CLIPHUNTER', 'http://www.cliphunter.com/gfx/new/logo.png', None)) 
           valTab.append(CDisplayListItem('EMPFLIX',     'http://www.empflix.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.empflix.com/categories.php'],'EMPFLIX', 'https://www.empflix.com/images/logo_emp.jpg', None)) 
           valTab.append(CDisplayListItem('THUMBZILLA',     'http://www.thumbzilla.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.thumbzilla.com/'],'THUMBZILLA', 'https://cdn-d-static.pornhub.com/tz-static/images/pc/logo.png?cache=2016111010', None)) 
           valTab.append(CDisplayListItem('YUVUTU',     'http://www.yuvutu.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.yuvutu.com/categories/'],'YUVUTU', 'http://www.yuvutu.com/themes/yuvutu_v2/images/yuvutu_logo.png', None)) 
           valTab.append(CDisplayListItem('PORNICOM',     'http://pornicom.com', CDisplayListItem.TYPE_CATEGORY, ['http://pornicom.com/categories/'],'PORNICOM', 'http://pornicom.com/images/logo.png', None)) 
           valTab.append(CDisplayListItem('HDZOG',     'http://www.hdzog.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.hdzog.com/categories/'],'HDZOG', 'https://pbs.twimg.com/profile_images/484686238402629632/5fzwWkJQ_bigger.png', None)) 
           #valTab.append(CDisplayListItem('PORNOMENGE',     'https://www.pornomenge.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.pornomenge.com/kategorien/'],'PORNOMENGE', 'https://th.servitubes.com/videos/8/1/b/5/1/81b51795337b047be07d3b3790b97c923535dffb.mp4-preview-3.jpg', None)) 
           valTab.append(CDisplayListItem('TUBEPORNCLASSIC',     'http://tubepornclassic.com/', CDisplayListItem.TYPE_CATEGORY, ['http://tubepornclassic.com/categories/'],'TUBEPORNCLASSIC', 'https://tubepornclassic.com/static/images/favicons/android-icon-192x192.png', None)) 
           valTab.append(CDisplayListItem('KOLOPORNO',     'https://www.koloporno.com/', CDisplayListItem.TYPE_CATEGORY, ['https://www.koloporno.com/kategoriach/'],'KOLOPORNO', 'https://pbs.twimg.com/profile_images/638608521072934912/sqy78GQm.png', None)) 
           valTab.append(CDisplayListItem('REALGFPORN',     'https://www.realgfporn.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.realgfporn.com/channels/'],'REALGFPORN', 'https://www.realgfporn.com/assets/img/logo.png', None)) 
           valTab.append(CDisplayListItem('PLAYVIDS',     'https://www.playvids.com/', CDisplayListItem.TYPE_CATEGORY, ['https://www.playvids.com/categories&jsclick=1'],'PLAYVIDS', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS9PrWdcYR2t0pJjXg_Wi02ZyiP6E1PJ0mmilizp745_fazgzxu&s', None)) 
           valTab.append(CDisplayListItem('FUX',     'http://www.fux.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.fux.com'],'fux', 'https://cdn1-ht-assets.fux.com/Fux.png', None)) 
           valTab.append(CDisplayListItem('PORNTUBE',     'http://www.porntube.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.porntube.com'],'PORNTUBE', 'https://cdn1-ht-assets.porntube.com/PornTube.png', None)) 
           valTab.append(CDisplayListItem('PORNERBROS',     'http://www.pornerbros.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.pornerbros.com'],'pornerbros', 'https://cdn1-ht-assets.pornerbros.com/PornerBros.png', None)) 
           valTab.append(CDisplayListItem('MOVIEFAP',     'http://www.moviefap.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.moviefap.com/browse/'],'MOVIEFAP', 'http://www.moviefap.com/images/logo.gif', None)) 
           valTab.append(CDisplayListItem('YOURPORN.SEXY',     'https://sxyprn.com', CDisplayListItem.TYPE_CATEGORY, ['https://sxyprn.com'],'yourporn', 'http://cdn.itsyourporn.com/assets/images/logo.jpg', None)) 
           valTab.append(CDisplayListItem('FREEOMOVIE',     'https://www.freeomovie.to', CDisplayListItem.TYPE_CATEGORY, ['https://www.freeomovie.to'],'freeomovie', 'https://www.freeomovie.to/wp-content/uploads/2013/04/logo.png', None)) 
           valTab.append(CDisplayListItem('KATESTUBE',     'http://www.katestube.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.katestube.com/categories/'],'KATESTUBE', 'https://www.katestube.com/images/logo.png', None)) 
           valTab.append(CDisplayListItem('PORNONE',     'https://pornone.com', CDisplayListItem.TYPE_CATEGORY, ['https://pornone.com/categories/'],'pornone', 'https://th-eu4.pornone.com/images/logo-light-theme.png', None)) 
           valTab.append(CDisplayListItem('HOTMOVS',     'http://hotmovs.com', CDisplayListItem.TYPE_CATEGORY, ['http://hotmovs.com/categories/'],'hotmovs', 'http://hotmovs.com/images/logo.png', None)) 
           valTab.append(CDisplayListItem('PORNOXO',     'https://www.pornoxo.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.pornoxo.com'],'pornoxo', 'http://www.web-tv-sexe.fr/logo/pornoxo.jpg', None)) 
           valTab.append(CDisplayListItem('PINFLIX',     'http://www.pinflix.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.pinflix.com/category'],'pinflix', 'https://pbs.twimg.com/profile_images/568766044114657280/JYh2ZSF_.png', None)) 
           valTab.append(CDisplayListItem('UPORNIA',     'http://www.upornia.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.upornia.com/categories/'],'upornia', 'https://pbs.twimg.com/profile_images/603525677451640833/AE2qwJ5C_400x400.png', None)) 
           valTab.append(CDisplayListItem('TXXX',     'http://www.txxx.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.txxx.com/categories/'],'txxx', 'https://www.txxx.com/images/desktop-logo.png', None)) 
           valTab.append(CDisplayListItem('SUNPORNO',     'https://www.sunporno.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.sunporno.com/channels/'],'sunporno', 'https://sunstatic.fuckandcdn.com/sunstatic/v31/common/sunporno/img/logo_top.png', None)) 
           valTab.append(CDisplayListItem('SEXU',     'http://sexu.com', CDisplayListItem.TYPE_CATEGORY, ['http://sexu.com/'],'sexu', 'https://images-platform.99static.com/-xYD7Tguk14AOVySxG_bMkoJodU=/500x500/top/smart/99designs-contests-attachments/41/41945/attachment_41945457', None)) 
           valTab.append(CDisplayListItem('TUBEWOLF',     'http://www.tubewolf.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.tubewolf.com'],'tubewolf', 'http://images.tubewolf.com/logo.png', None)) 
           valTab.append(CDisplayListItem('ALPHAPORNO',     'http://www.alphaporno.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.alphaporno.com'],'tubewolf', 'http://images.alphaporno.com/logo.png', None)) 
           valTab.append(CDisplayListItem('ZEDPORN',     'http://zedporn.com', CDisplayListItem.TYPE_CATEGORY, ['https://zedporn.com'],'tubewolf', 'http://images.zedporn.com/new-logo.png', None)) 
           valTab.append(CDisplayListItem('CROCOTUBE',     'http://crocotube.com', CDisplayListItem.TYPE_CATEGORY, ['http://crocotube.com'],'tubewolf', 'http://crocotube.com/images/logo.png', None)) 
           valTab.append(CDisplayListItem('ASHEMALETUBE',     'https://www.ashemaletube.com/', CDisplayListItem.TYPE_CATEGORY, ['https://www.ashemaletube.com/'],'ASHEMALETUBE', 'https://adminex.ashemaletube.com/images/logo/ast.png', None)) 
           #valTab.append(CDisplayListItem('MOMXXXFUN',     'https://momxxxfun.com/', CDisplayListItem.TYPE_CATEGORY, ['https://momxxxfun.com/categories'],'MOMXXXFUN', 'https://momxxxfun.com/images/logo/logo.png', None)) 
           valTab.append(CDisplayListItem('STREAMPORN',     'https://streamporn.pw', CDisplayListItem.TYPE_CATEGORY, ['https://streamporn.pw'],'streamporn', 'https://streamporn.pw/wp-content/uploads/2018/05/fsfsfsf-1.png', None)) 
           valTab.append(CDisplayListItem('ONLINEPORNFREE',     'https://onlinepornfree.xyz/', CDisplayListItem.TYPE_CATEGORY, ['https://onlinepornfree.xyz/'],'onlinepornfree', 'https://adultdvdparadise.com/wp-content/uploads/2019/04/looooooo.png', None)) 
           valTab.append(CDisplayListItem('MYDIRTYHOBBY',     'https://www.mydirtyhobby.to', CDisplayListItem.TYPE_CATEGORY, ['https://www.mydirtyhobby.to'],'MYDIRTYHOBBY', 'https://www.mydirtyhobby.to/images/logo/logo.png', None)) 
           valTab.append(CDisplayListItem('XXXSTREAMS',     'http://xxxstreams.org/', CDisplayListItem.TYPE_CATEGORY, ['http://xxxstreams.org/'],'xxxstreams', 'https://previews.123rf.com/images/sila5775/sila57751506/sila5775150600244/40710228-xxx-designed-using-grunge-brush-on-white-background-sign-logo-symbol-icon-graphic-vector-.jpg', None)) 
           valTab.append(CDisplayListItem('PANDAMOVIE',     'https://pandamovie.info', CDisplayListItem.TYPE_CATEGORY, ['https://pandamovie.info'],'123PANDAMOVIE', 'https://pandamovie.info/wp-content/uploads/2019/01/pandamovie-new-clolor.png', None)) 
           valTab.append(CDisplayListItem('FULLXXXMOVIES',     'http://fullxxxmovies.net', CDisplayListItem.TYPE_CATEGORY, ['http://fullxxxmovies.net/'],'FULLXXXMOVIES', 'https://fullxxxmovies.net/wp-content/uploads/2020/01/cropped-FullXXXMovies_3.png', None)) 
           valTab.append(CDisplayListItem('PORNREWIND',     'https://www.pornrewind.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.pornrewind.com/categories/'],'PORNREWIND', 'https://www.pornrewind.com/static/images/logo-light-pink.png', None)) 
           valTab.append(CDisplayListItem('BALKANJIZZ',     'https://www.balkanjizz.com/', CDisplayListItem.TYPE_CATEGORY, ['https://www.balkanjizz.com/kategorije-pornica'],'BALKANJIZZ', 'https://www.balkanjizz.com/images/logo/logo.png', None)) 
           valTab.append(CDisplayListItem('PORNORUSSIA',     'https://pornorussia.tv/', CDisplayListItem.TYPE_CATEGORY, ['https://pornorussia.tv/'],'PORNORUSSIA', 'https://pornorussia.tv/images/logo.png', None)) 
           valTab.append(CDisplayListItem('LETMEJERK',     'https://www.letmejerk.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.letmejerk.com/category'],'LETMEJERK', 'https://image.freepik.com/darmowe-ikony/gra%C4%87_318-135191.jpg', None)) 
           valTab.append(CDisplayListItem('GOTPORN',     'https://www.gotporn', CDisplayListItem.TYPE_CATEGORY, ['https://www.gotporn.com/categories?src=hm'],'GOTPORN', 'https://cdn2-static-cf.gotporn.com/desktop/img/gotporn-logo.png', None)) 
           valTab.append(CDisplayListItem('ANALDIN',     'https://www.analdin.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.analdin.com/categories/'],'ANALDIN', 'https://www.analdin.com/images/logo-retina.png', None)) 
           valTab.append(CDisplayListItem('NETFLIXPORNO',     'https://netflixporno.net/', CDisplayListItem.TYPE_CATEGORY, ['https://netflixporno.net/'],'NETFLIXPORNO', 'https://netflixporno.net/wp-content/uploads/2018/04/netflixporno-1.png', None)) 
           valTab.append(CDisplayListItem('FAPSET',     'https://fapset.com', CDisplayListItem.TYPE_CATEGORY, ['https://fapset.com'],'fapset', 'https://fapset.com/templates/Default/images/logo.png', None)) 
           valTab.append(CDisplayListItem('DAFTSEX',     'https://daftsex.com', CDisplayListItem.TYPE_CATEGORY, ['https://daftsex.com/categories'],'daftsex', 'https://daftsex.com/img/daftlogo196x196.png', None)) 
           valTab.append(CDisplayListItem('LOVE HOME PORN',     'https://lovehomeporn.com', CDisplayListItem.TYPE_CATEGORY, ['https://lovehomeporn.com/videos'],'lovehomeporn', 'https://cdn.static.lovehomeporn.com/templates/frontend/purple/new_images/logo-helloween.png', None)) 
           valTab.append(CDisplayListItem('EROPROFILE',     'http://www.eroprofile.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.eroprofile.com'],'EROPROFILE', 'https://static.eroprofile.com/img/v1/header_logo.png', None)) 
           valTab.append(CDisplayListItem('ABSOLUPORN',     'http://www.absoluporn.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.absoluporn.com/en/lettre-tag.html'],'absoluporn', 'http://www.absoluporn.com/image/deco/logo.gif', None)) 
           valTab.append(CDisplayListItem('AMATEUR COOL',     'https://www.amateurcool.com/', CDisplayListItem.TYPE_CATEGORY, ['https://www.amateurcool.com/channels/'],'amateurcool', 'https://www.amateurcool.com/templates/amateur-cool/images/logo.png', None)) 
           valTab.append(CDisplayListItem('PORNGO',     'https://porngo.com', CDisplayListItem.TYPE_CATEGORY, ['https://porngo.com/categories/'],'porngo', 'https://cdn6.f-cdn.com/contestentries/1524870/34599086/5d1936269c415_thumb900.jpg', None)) 
           valTab.append(CDisplayListItem('ANYBUNNY',     'http://anybunny.com', CDisplayListItem.TYPE_CATEGORY, ['http://anybunny.com'],'anybunny', 'http://anybunny.com/images/logo.png', None)) 
           valTab.append(CDisplayListItem('DATOPORN',     'http://dato.porn', CDisplayListItem.TYPE_CATEGORY, ['https://dato.porn/categories/'],'datoporn', 'https://pbs.twimg.com/media/CtzxPlEWgAAiIjH.png', None)) 
           valTab.append(CDisplayListItem('HQPORNER',     'https://hqporner.com', CDisplayListItem.TYPE_CATEGORY, ['https://hqporner.com/porn-categories.php'],'hqporner', 'https://www.filmyporno.blog/wp-content/uploads/2018/12/channel-hqporner.jpg', None)) 
           valTab.append(CDisplayListItem('SPANKBANG',     'https://spankbang.com', CDisplayListItem.TYPE_CATEGORY, ['https://spankbang.com/categories'],'spankbang', 'https://static.spankbang.com/static_desktop/Images/logo_desktop_v4@2x.png', None)) 
           valTab.append(CDisplayListItem('CUMLOUDER',     'https://www.cumlouder.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.cumlouder.com/categories'],'cumlouder', 'https://1000logos.net/wp-content/uploads/2019/02/CumLouder-Logo.png', None)) 
           valTab.append(CDisplayListItem('PORN00',     'http://www.porn00.org', CDisplayListItem.TYPE_CATEGORY, ['http://www.porn00.org/categories/'],'porn00', 'https://www.porn00.org/static/images/logo.png', None)) 
           valTab.append(CDisplayListItem('WATCHPORNX',     'https://watchpornx.com/', CDisplayListItem.TYPE_CATEGORY, ['https://watchpornx.com/'],'watchpornx', 'https://watchpornfree.info/wp-content/uploads/2019/01/watchpornfreews-1-e1525276673535.png', None)) 
           valTab.append(CDisplayListItem('P720',     'https://p720.net', CDisplayListItem.TYPE_CATEGORY, ['https://p720.net/categories/'],'P720', 'https://p720.net/static/images/logo.png', None)) 
           valTab.append(CDisplayListItem('PORNOPERSIK',     'https://pornopersik.com', CDisplayListItem.TYPE_CATEGORY, ['https://pornopersik.com/categories/'],'pornopersik', 'https://pornopersik.com/static/images/logo.png', None)) 
           valTab.append(CDisplayListItem('ANYPORN',     'https://anyporn.com', CDisplayListItem.TYPE_CATEGORY, ['https://anyporn.com/categories/'],'ANYPORN', 'https://anyporn.com/images/logo.png', None)) 
           valTab.append(CDisplayListItem('ANON-V',     'https://anon-v.com', CDisplayListItem.TYPE_CATEGORY, ['https://anon-v.com/categories/'],'ANON-V', 'https://anon-v.com/logo350.png', None)) 
           valTab.append(CDisplayListItem('BRAVOPORN',     'https://www.bravoporn.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.bravoporn.com/c/'],'bravoporn', 'https://www.bravoporn.com/v/images/logo.png', None)) 
           valTab.append(CDisplayListItem('BRAVOTEENS',     'https://www.bravoteens.com/', CDisplayListItem.TYPE_CATEGORY, ['https://www.bravoteens.com//cats/'],'bravoteens', 'https://www.bravoteens.com/tb/images/logo.png', None)) 
           valTab.append(CDisplayListItem('SLEAZYNEASY',     'https://www.sleazyneasy.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.sleazyneasy.com/categories/'],'sleazyneasy', 'https://cdni.sleazyneasy.com/images/favicon-152.png', None)) 
           valTab.append(CDisplayListItem('VJAV',     'https://vjav.com/main/', CDisplayListItem.TYPE_CATEGORY, ['https://vjav.com/categories/'],'vjav', 'https://vjav.com/static/images/logo-lg.svg?v=4', None)) 
           valTab.append(CDisplayListItem('JAVHOHO',     'https://javhoho.com', CDisplayListItem.TYPE_CATEGORY, ['https://javhoho.com/category/free-jav-uncensored/'],'javhoho', 'https://javhoho.com/wp-content/uploads/2019/11/JAVhoho.com-logo.png', None)) 
           valTab.append(CDisplayListItem('FORCEDCELEBS',     'https://forcedcelebs.net', CDisplayListItem.TYPE_CATEGORY, ['https://forcedcelebs.net'],'forcedcelebs', '', None)) 
           valTab.append(CDisplayListItem('FAMILYPORN',     'https://familyporn.tv', CDisplayListItem.TYPE_CATEGORY, ['https://familyporn.tv/categories/'],'familyporn', 'https://familyporn.tv/images/logo-alt.png', None)) 
           valTab.append(CDisplayListItem('BITPORNO',     'https://www.bitporno.com/', CDisplayListItem.TYPE_CATEGORY, ['https://www.bitporno.com/'],'bitporno', 'https://www.bitporno.com/images/logobt.png', None)) 
           valTab.append(CDisplayListItem('EBUXXX',     'https://ebuxxx.net', CDisplayListItem.TYPE_CATEGORY, ['https://ebuxxx.net'],'ebuxxx', '', None)) 


           if config.plugins.iptvplayer.xxxsortall.value:
               valTab.sort(key=lambda poz: poz.name)

           if config.plugins.iptvplayer.xxxsearch.value:
               self.SEARCH_proc=name
               valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
               valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),             CDisplayListItem.TYPE_SEARCH,             [''], '',        '', None)) 

           #valTab.insert(0,CDisplayListItem(_('PROSZĘ PRZEKAŻ 1% PODATKU NA KRS 0000049063'),  _('KRS 0000049063\nSTOWARZYSZENIE "OTWÓRZMY PRZED NIMI ŻYCIE"\nUL. KOŚCIUSZKI 43   32-065 KRZESZOWICE\nPRZEKAŻ 1 % SWOJEGO PODATKU\nPODARUJ NASZYM NIEPEŁNOSPRAWNYM SŁOŃCE'),             CDisplayListItem.TYPE_MORE,             [''], '',        '', None)) 
           valTab.append(CDisplayListItem('FOTKA-PL-KAMERKI',     'http://www.fotka.pl/kamerki', CDisplayListItem.TYPE_CATEGORY, ['http://api.fotka.pl/v2/cams/get?page=1&limit=100&gender=f'],'FOTKA-PL-KAMERKI', 'https://pbs.twimg.com/profile_images/3086758992/6fb5cc2ee2735c334d0363bcb01a52ca_400x400.png', None)) 
           url = 'https://chaturbate.com/tags/%s' % config.plugins.iptvplayer.chaturbate.value
           valTab.append(CDisplayListItem('CHATURBATE',     'chaturbate.com', CDisplayListItem.TYPE_CATEGORY, [url],'CHATURBATE','http://www.adultcamfriendx.com/wp-content/uploads/2016/11/chaturbate-cams-logo.png', None)) 
           valTab.append(CDisplayListItem('XHAMSTERLIVE',       "Kamerki",       CDisplayListItem.TYPE_CATEGORY,['http://xhamsterlive.com'], 'xhamsterlive', 'https://cdn.stripst.com/assets/icons/favicon-196x196_xhamsterlive.com.png',None))
           valTab.append(CDisplayListItem('CAM4',     'https://www.cam4.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.cam4.com'],'CAM4-KAMERKI', 'https://www.cam4models.com/images/c4logo_white.png', None)) 
           #valTab.append(CDisplayListItem('MYFREECAMS',     'http://www.myfreecams.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.myfreecams.com/#Homepage'],'MYFREECAMS', 'http://www.adultcamfriendx.com/wp-content/uploads/2016/11/myfreecams-webcams-logo.png', None)) 
           #valTab.append(CDisplayListItem('LIVEJASMIN',     'http://www.livejasmin.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.livejasmin.com/en/girl/free+chat?selectedFilters=12'],'LIVEJASMIN', 'http://livejasmins.fr/livejasmin-france.png', None)) 
           valTab.append(CDisplayListItem('BONGACAMS',     'https://bongacams.com/', CDisplayListItem.TYPE_CATEGORY, ['https://en.bongacams.com/'],'BONGACAMS', 'http://i.bongacams.com/images/bongacams_logo3_header.png', None)) 
           valTab.append(CDisplayListItem('SHOWUP   - live cams',       'showup.tv',          CDisplayListItem.TYPE_CATEGORY, ['http://showup.tv'],                     'showup',  'https://i.pinimg.com/originals/cd/73/1d/cd731d0be3bb2cabcecd6d7bdfe50ae9.png', None)) 
           #valTab.append(CDisplayListItem('ZBIORNIK - live cams',       'zbiornik.tv',       CDisplayListItem.TYPE_CATEGORY, ['http://zbiornik.com/live/'],            'zbiornik','http://static.zbiornik.com/images/zbiornikBig.png', None)) 
           valTab.append(CDisplayListItem('CAMSODA',       'http://www.camsoda.com',       CDisplayListItem.TYPE_CATEGORY, ['http://www.camsoda.com/api/v1/browse/online'],            'CAMSODA','https://cachew.camsoda.com/assets/img/camsoda-logo-160x50.png', None)) 
           valTab.append(CDisplayListItem('STREAMATE',       'https://streamate.com',       CDisplayListItem.TYPE_CATEGORY, ['https://streamate.com'],            'STREAMATE','https://m2.nsimg.net/3.0/auto/skin/sm/assets/ffe71-1453326178-logo.png', None)) 
           try: 
               phImage = urlparser.decorateUrl('http://media4.nkdcdn.com/images/siteImages/textImages/common/phtml/whiteLabel/new.naked/logo.png', {'Referer': 'https://www.naked.com'})
               valTab.append(CDisplayListItem('CAMSTER',       'https://www.naked.com',       CDisplayListItem.TYPE_CATEGORY, ['https://www.naked.com/'],            'NAKED', phImage, None)) 
           except Exception: 
               printExc()
           valTab.append(CDisplayListItem('ADULT-TV',     'http://www.adulttvlive.net/category/live-18-tv/', CDisplayListItem.TYPE_CATEGORY, ['http://www.adulttvlive.net/category/live-18-tv/'],'ADULTTV', '', None)) 
           valTab.append(CDisplayListItem('+++ XXXLIST +++   XXXversion = '+str(self.XXXversion), '+++ XXXLIST +++   XXXversion = '+str(self.XXXversion), CDisplayListItem.TYPE_CATEGORY, [''],'XXXLIST', '', None)) 
           if config.plugins.iptvplayer.xxxupdate.value:
               valTab.append(CDisplayListItem('CHANGELOG',                    'CHANGELOG',   CDisplayListItem.TYPE_CATEGORY, ['https://gitlab.com/iptv-host-xxx/iptv-host-xxx/commits/master.atom'], 'UPDATE-ZMIANY', '', None)) 
           self.yourporn = config.plugins.iptvplayer.yourporn.value

           return valTab

        # ########## #
        if 'HISTORY' == name:
           printDBG( 'Host listsItems begin name='+name )
           for histItem in self.history.getHistoryList():
               valTab.append(CDisplayListItem(histItem['pattern'], 'Szukaj ', CDisplayListItem.TYPE_CATEGORY, [histItem['pattern'],histItem['type']], 'SEARCH', '', None))          
            
           return valTab           
        # ########## #
        if 'SEARCH' == name:
           printDBG( 'Host listsItems begin name='+name )
           pattern = url 
           if Index==-1: 
              self.history.addHistoryItem( pattern, 'video')
           if self.SEARCH_proc == '': return []               
           if self.SEARCH_proc == 'main-menu':
              valTab=[]
              self.MAIN_URL = 'https://www.4tube.com'
              valtemp = self.listsItems(-1, url, '4TUBE-search')
              for item in valtemp: item.name='4TUBE - '+item.name
              valTab = valTab + valtemp

              valtemp = self.listsItems(-1, url, 'ahme-search')
              for item in valtemp: item.name='AH-ME - '+item.name
              valTab = valTab + valtemp

              self.MAIN_URL = 'http://www.cliphunter.com' 
              valtemp = self.listsItems(-1, url, 'CLIPHUNTER-search')
              for item in valtemp: item.name='CLIPHUNTER - '+item.name
              valTab = valTab + valtemp

              self.MAIN_URL = 'http://www.dachix.com' 
              valtemp = self.listsItems(-1, url, 'DACHIX-search')
              for item in valtemp: item.name='DACHIX - '+item.name
              valTab = valTab + valtemp

              self.MAIN_URL = 'http://www.drtuber.com' 
              valtemp = self.listsItems(-1, url, 'DRTUBER-search')
              for item in valtemp: item.name='DRTUBER - '+item.name
              valTab = valTab + valtemp

              self.MAIN_URL = 'http://www.eporner.com' 
              valtemp = self.listsItems(-1, url, 'eporner-search')
              for item in valtemp: item.name='EPORNER - '+item.name
              valTab = valTab + valtemp

              self.MAIN_URL = 'https://www.fux.com'
              valtemp = self.listsItems(-1, url, '4TUBE-search')
              for item in valtemp: item.name='FUX - '+item.name
              valTab = valTab + valtemp

#              valtemp = self.listsItems(-1, url, 'hdzog-search')
#              for item in valtemp: item.name='HDZOG - '+item.name              
#              valTab = valTab + valtemp

              self.MAIN_URL = 'http://www.homemoviestube.com'
              valtemp = self.listsItems(-1, url, 'HomeMoviesTube-search')
              for item in valtemp: item.name='HomeMoviesTube - '+item.name
              valTab = valTab + valtemp

              valtemp = self.listsItems(-1, url, 'KATESTUBE-search')
              for item in valtemp: item.name='KATESTUBE - '+item.name
              valTab = valTab + valtemp

              self.MAIN_URL = 'https://www.koloporno.com' 
              valtemp = self.listsItems(-1, url, 'KOLOPORNO-search')
              for item in valtemp: item.name='KOLOPORNO - '+item.name
              valTab = valTab + valtemp

              valtemp = self.listsItems(-1, url, 'MOVIEFAP-search')
              for item in valtemp: item.name='MOVIEFAP - '+item.name
              valTab = valTab + valtemp

              self.MAIN_URL = 'https://porndoe.com' 
              valtemp = self.listsItems(-1, url, 'porndoe-search')
              for item in valtemp: item.name='PORNDOE - '+item.name              
              valTab = valTab + valtemp 

              self.MAIN_URL = 'https://www.pornerbros.com'
              valtemp = self.listsItems(-1, url, '4TUBE-search')
              for item in valtemp: item.name='PORNERBROS - '+item.name
              valTab = valTab + valtemp

              self.MAIN_URL = 'https://www.pornhd.com' 
              valtemp = self.listsItems(-1, url, 'pornhd-search')
              for item in valtemp: item.name='PORNHD - '+item.name
              valTab = valTab + valtemp

              self.MAIN_URL = 'http://www.pornhub.com' 
              valtemp = self.listsItems(-1, url, 'pornhub-search')
              for item in valtemp: item.name='PORNHUB - '+item.name              
              valTab = valTab + valtemp

              valtemp = self.listsItems(-1, url, 'pornicom-search')
              for item in valtemp: item.name='PORNICOM - '+item.name              
              valTab = valTab + valtemp

              self.MAIN_URL = 'https://www.porntube.com'
              valtemp = self.listsItems(-1, url, '4TUBE-search')
              for item in valtemp: item.name='PORNTUBE - '+item.name
              valTab = valTab + valtemp

              valtemp = self.listsItems(-1, url, 'PORNFROMCZECH-search')
              for item in valtemp: item.name='PORNFROMCZECH - '+item.name              
              valTab = valTab + valtemp 

              valtemp = self.listsItems(-1, url, 'REALGFPORN-search')
              for item in valtemp: item.name='REALGFPORN - '+item.name
              valTab = valTab + valtemp

              self.MAIN_URL = 'http://www.redtube.com' 
              valtemp = self.listsItems(-1, url, 'redtube-search')
              for item in valtemp: item.name='REDTUBE - '+item.name
              valTab = valTab + valtemp

              self.MAIN_URL = 'http://www.thumbzilla.com' 
              valtemp = self.listsItems(-1, url, 'THUMBZILLA-search')
              for item in valtemp: item.name='THUMBZILLA - '+item.name              
              valTab = valTab + valtemp

              self.MAIN_URL = 'http://www.tube8.com' 
              valtemp = self.listsItems(-1, url, 'tube8-search')
              for item in valtemp: item.name='TUBE8 - '+item.name
              valTab = valTab + valtemp

              valtemp = self.listsItems(-1, url, 'xhamster-search')
              for item in valtemp: item.name='XHAMSTER - '+item.name              
              valTab = valTab + valtemp 
 
              self.MAIN_URL = 'http://www.xnxx.com' 
              valtemp = self.listsItems(-1, url, 'xnxx-search')
              for item in valtemp: item.name='XNXX - '+item.name
              valTab = valTab + valtemp

              self.MAIN_URL = 'http://www.xvideos.com' 
              valtemp = self.listsItems(-1, url, 'xvideos-search')
              for item in valtemp: item.name='XVIDEOS - '+item.name              
              valTab = valTab + valtemp

              self.MAIN_URL = 'http://www.youjizz.com' 
              valtemp = self.listsItems(-1, url, 'YOUJIZZ-search')
              for item in valtemp: item.name='YOUJIZZ - '+item.name
              valTab = valTab + valtemp

              self.MAIN_URL = 'http://www.youporn.com' 
              valtemp = self.listsItems(-1, url, 'youporn-search')
              for item in valtemp: item.name='YOUPORN - '+item.name
              valTab = valTab + valtemp
 
              self.MAIN_URL = 'https://yourporn.sexy'
              valtemp = self.listsItems(-1, url, 'yourporn-search')
              for item in valtemp: item.name='YOURPORN.SEXY - '+item.name
              valTab = valTab + valtemp

              self.MAIN_URL = '' 
              return valTab
           valTab = self.listsItems(-1, url, self.SEARCH_proc)
           return valTab

        if 'UPDATE' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab.append(CDisplayListItem(self.XXXversion+' - Local version',   'Local  XXXversion', CDisplayListItem.TYPE_CATEGORY, [''], '', '', None)) 
           valTab.append(CDisplayListItem(self.XXXremote+ ' - Remote version',  'Remote XXXversion', CDisplayListItem.TYPE_CATEGORY, [''], '', '', None)) 
           valTab.append(CDisplayListItem('Changelog',                    'Changelog',   CDisplayListItem.TYPE_CATEGORY, ['https://gitlab.com/iptv-host-xxx/iptv-host-xxx/commits/master.atom'], 'UPDATE-ZMIANY', '', None)) 
           valTab.append(CDisplayListItem('Update Now',                         'Update Now',        CDisplayListItem.TYPE_CATEGORY, [''], 'UPDATE-NOW',    '', None)) 
           valTab.append(CDisplayListItem('Update Now & Restart Enigma2',                         'Update Now & Restart Enigma2',        CDisplayListItem.TYPE_CATEGORY, ['restart'], 'UPDATE-NOW',    '', None)) 
           return valTab
        if 'UPDATE-ZMIANY' == name:
           printDBG( 'Host listsItems begin name='+name )
           try:
              data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error' )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phCats = re.findall("<entry>.*?<title>(.*?)</title>.*?<updated>(.*?)</updated>.*?<name>(.*?)</name>", data, re.S)
           if phCats:
              for (phTitle, phUpdated, phName ) in phCats:
                  phUpdated = phUpdated.replace('T', '   ')
                  phUpdated = phUpdated.replace('Z', '   ')
                  phUpdated = phUpdated.replace('+01:00', '   ')
                  phUpdated = phUpdated.replace('+02:00', '   ')
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  printDBG( 'Host listsItems phUpdated: '+phUpdated )
                  printDBG( 'Host listsItems phName: '+phName )
                  valTab.append(CDisplayListItem(phUpdated+' '+phName+'  >>  '+decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [''],'', '', None)) 
           return valTab
        if 'UPDATE-NOW' == name:
           printDBG( 'HostXXX listsItems begin name='+name )
           _url = 'https://gitlab.com/iptv-host-xxx/iptv-host-xxx/commits/master'
           query_data = { 'url': _url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
              #printDBG( 'Host init data: '+data )
              crc=self.cm.ph.getSearchGroups(data, '''/commit/([^"^']+?)['"]''', 1, True)[0]
              printDBG( 'crc = '+crc )
              if not crc: error
           except:
              printDBG( 'Host init query error' )
              valTab.append(CDisplayListItem('ERROR - Błąd init: '+_url,   'ERROR', CDisplayListItem.TYPE_CATEGORY, [''], '', '', None)) 
              return valTab

           tmpDir = GetTmpDir() 
           source = os_path.join(tmpDir, 'iptv-host-xxx.tar.gz') 
           dest = os_path.join(tmpDir , '') 
           _url = 'https://gitlab.com/iptv-host-xxx/iptv-host-xxx/repository/archive.tar.gz?ref=master'              
           output = open(source,'wb')
           query_data = { 'url': _url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              output.write(self.cm.getURLRequestData(query_data))
              output.close()
              os_system ('sync')
              printDBG( 'HostXXX pobieranie iptv-host-xxx.tar.gz' )
           except:
              if os_path.exists(source):
                 os_remove(source)
              printDBG( 'HostXXX Błąd pobierania iptv-host-xxx.tar.gz' )
              valTab.append(CDisplayListItem('ERROR - Blad pobierania: '+_url,   'ERROR', CDisplayListItem.TYPE_CATEGORY, [''], '', '', None)) 
              return valTab
           if os_path.exists(source):
              printDBG( 'HostXXX Jest plik '+source )
           else:
              printDBG( 'HostXXX Brak pliku '+source )

           cmd = 'tar -xzf "%s" -C "%s" 2>&1' % ( source, dest )  
           try: 
              os_system (cmd)
              os_system ('sync')
              printDBG( 'HostXXX rozpakowanie  ' + cmd )
           except:
              printDBG( 'HostXXX Błąd rozpakowania iptv-host-xxx.tar.gz' )
              os_system ('rm -f %s' % source)
              os_system ('rm -rf %siptv-host-xxx-%s' % (dest, crc))
              valTab.append(CDisplayListItem('ERROR - Blad rozpakowania %s' % source,   'ERROR', CDisplayListItem.TYPE_CATEGORY, [''], '', '', None)) 
              return valTab


           try:
              od = '%siptv-host-xxx-master-%s/'% (dest, crc)
              do = resolveFilename(SCOPE_PLUGINS, 'Extensions/') 
              cmd = 'cp -rf "%s"/* "%s"/ 2>&1' % (os_path.join(od, 'IPTVPlayer'), os_path.join(do, 'IPTVPlayer'))
              printDBG('HostXXX kopiowanie1 cmd[%s]' % cmd)
              os_system (cmd)
              #printDBG('HostXXX kopiowanie2 cmd[%s]' % cmd)
              #iptv_system(cmd)
              os_system ('sync')
           except:
              printDBG( 'HostXXX blad kopiowania' )
              os_system ('rm -f %s' % source)
              os_system ('rm -rf %siptv-host-xxx-master-%s' % (dest, crc))
              valTab.append(CDisplayListItem('ERROR - blad kopiowania',   'ERROR', CDisplayListItem.TYPE_CATEGORY, [''], '', '', None)) 
              return valTab


           ikony = GetPluginDir('icons/PlayerSelector/')
           if os_path.exists('%sXXX100' % ikony):
              printDBG( 'HostXXX Jest '+ ikony + 'XXX100 ' )
              os_system('mv %sXXX100 %sXXX100.png' % (ikony, ikony)) 
           if os_path.exists('%sXXX120' % ikony):
              printDBG( 'HostXXX Jest '+ ikony + 'XXX120 '  )
              os_system('mv %sXXX120 %sXXX120.png' % (ikony, ikony))
           if os_path.exists('%sXXX135' % ikony):
              printDBG( 'HostXXX Jest '+ ikony + 'XXX135 '  )
              os_system('mv %sXXX135 %sXXX135.png' % (ikony, ikony))

           try:
              cmd = GetPluginDir('hosts/hostXXX.py')
              with open(cmd, 'r') as f:  
                 data = f.read()
                 f.close() 
                 wersja = re.search('XXXversion = "(.*?)"', data, re.S)
                 aktualna = wersja.group(1)
                 printDBG( 'HostXXX aktualna wersja wtyczki '+aktualna )
           except:
              printDBG( 'HostXXX error openfile ' )


           printDBG( 'HostXXX usuwanie plikow tymczasowych' )
           os_system ('rm -f %s' % source)
           os_system ('rm -rf %siptv-host-xxx-master-%s' % (dest, crc))

           if url:
              try:
                 msg = '\n\n Wersja hostXXX w tunerze %s' % aktualna
                 self.sessionEx.open(MessageBox, _("Update completed successfully. For the moment, the system will reboot.")+ msg, type = MessageBox.TYPE_INFO, timeout = 10)
                 sleep (10)
                 from enigma import quitMainloop
                 quitMainloop(3)
              except: pass
           valTab.append(CDisplayListItem('Update End. Please manual restart enigma2',   'Restart', CDisplayListItem.TYPE_CATEGORY, [''], '', '', None)) 
           printDBG( 'HostXXX listsItems end' )
           return valTab

##################################################################
        if 'tube8' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.tube8.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'tube8.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'categories-subnav', '</ul>', False)[1]
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phTitle: phTitle = self._cleanHtmlStr(item).strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-thumb=['"]([^"^']+?)['"]''', 1, True)[0] 
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'tube8-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem('--- Most Viewed ---', 'Most Viewed',               CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/most-viewed/page/1/'],      'tube8-clips', '', None)) 
           valTab.insert(0,CDisplayListItem('--- Top Rated ---', 'Top Rated',                 CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/top/page/1/'],       'tube8-clips', '', None)) 
           valTab.insert(0,CDisplayListItem('--- Longest ---', 'Longest', CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/longest/page/1/'],      'tube8-clips', '', None)) 
           valTab.insert(0,CDisplayListItem('--- New Videos ---',  'New Videos',  CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/newest/page/1/'],       'tube8-clips', '', None)) 
           self.SEARCH_proc='tube8-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'tube8-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.tube8.com/searches.html?q='+url.replace(' ','+'), 'tube8-clips')
           return valTab              
        if 'tube8-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.tube8.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'tube8.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return
           printDBG( 'Host listsItems data: '+data )
           nextPage = self.cm.ph.getSearchGroups(data, '''rel="next"\shref=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
           data2 = self.cm.ph.getDataBeetwenMarkers(data, 'id="category_video_list', 'footer', False)[1]
           if '' == data2: data2 = self.cm.ph.getDataBeetwenMarkers(data, 'Video Results For', 'footer', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data2, '<figure', '</figure>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''data-video_url=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-thumb=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''video-duration">([^>]+?)<''', 1, True)[0] 
              if phUrl and not 'title]' in phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if nextPage:
              valTab.append(CDisplayListItem('Next', 'Page: '+nextPage, CDisplayListItem.TYPE_CATEGORY, [nextPage], name, '', None))                
           return valTab

        if 'xnxx' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.xnxx.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'xnxx.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE, 'return_data': True}
           sts, data = self.cm.getPage(url, self.defaultParams)
           if not sts: return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('"categories":(.*?),"more_links"', data, re.S)
           if not parse: return valTab
           #printDBG( 'Host listsItems parse.group(1): '+parse.group(1) )
           result = simplejson.loads(parse.group(1))
           if result:
              for item in result:
                 phUrl = str(item["url"].replace('\/','/'))  
                 phTitle = str(item["label"]) 
                 if not 'jpg' in phTitle:
                    valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'xnxx-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem('--- Hits ---', 'Hits',               CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/hits/'],      'xnxx-clips', '', None)) 
           valTab.insert(0,CDisplayListItem('--- Best Videos ---', 'Best Videos', CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/best/'],      'xnxx-clips', '', None)) 
           valTab.insert(0,CDisplayListItem('--- New Videos ---',  'New Videos',  CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL],       'xnxx-clips', '', None)) 
           self.SEARCH_proc='xnxx-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),_('Search'),                  CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'xnxx-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.xnxx.com/?k='+url.replace(' ','+'), 'xnxx-clips')
           return valTab              
        if 'xnxx-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.xnxx.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'xnxx.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE, 'return_data': True}
           sts, data = self.cm.getPage(url, self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           match = re.search("pagination(.*?)Next", data, re.S)
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'id="video', '</p></div>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](/video[^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''</span></span>([^>]+?)<''', 1, True)[0].strip()
              if not phTime: phTime = self.cm.ph.getSearchGroups(item, '''<p class="metadata">([^>]+?)-''', 1, True)[0].strip()
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+phUrl, 1)], 0, phImage, None)) 
           if match: match = re.findall('href="(.*?)"', match.group(1), re.S)
           if match:
              phUrl = match[-1]
              #printDBG( 'Host listsItems page phUrl: '+phUrl )
              valTab.append(CDisplayListItem('Next', 'Page: '+phUrl.split('/')[-2], CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl], name, '', None))                
           return valTab

        if 'zbiornik' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://zbiornik.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'zbiornik.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page('http://zbiornik.tv/accept/yes/Lw==')
           if not sts: return valTab
           #printDBG( 'Host listsItems data: '+data )
           sex = ''
           hash = ''
           ph1 = re.search('var streams = (.*?)}];', data, re.S)
           if ph1: 
              ph1 = ph1.group(1)+'}]'
              #printDBG( 'Host listsItems json: '+ph1 )
              result = simplejson.loads(ph1)
              try:
                 for item in result:
                     phash = re.search('"phash":"(.*?)"', data, re.S)
                     if phash: hash=phash.group(1)
                     if str(item["accType"])=='1': sex = 'male'
                     if str(item["accType"])=='2': sex = 'female'
                     if str(item["accType"])=='3': sex = 'couple'
                     phImage = 'http://camshot.zbiornik.com/'+str(item["broadcasturl"])+'-224.jpg'
                     rtmpUrl = 'rtmp://'+str(item["server"])+'/videochat/?'+hash
                     playpath = str(item["broadcasturl"])
                     swfUrl = 'https://zbiornik.tv/wowza.swf?v50&b=100'
                     baseUrl = 'https://zbiornik.tv/'+str(item["nick"])
                     app = ' app=videochat/?'+hash
                     flashVer = ' flashVer=WIN 28,0,0,161'
                     #streamUrl = 'rtmp://'+str(item["server"])+'/videochat/?'+hash+' playpath='+str(item["broadcasturl"])+' swfUrl=http://zbiornik.tv/wowza.swf?v50&b=100 pageUrl=http://zbiornik.tv/'+str(item["nick"])+' live=1'
                     #streamUrl = rtmpUrl + ' playpath=' + playpath +  ' tcUrl=' + rtmpUrl + ' swfUrl=' + swfUrl + ' pageUrl=' + baseUrl + ' app='+app+' live=1 conn=S:OK'+ flashVer
                     streamUrl = 'rtmp://'+str(item["server"])+'/videochat/ playpath='+str(item["broadcasturl"])+' swfVfy=https://zbiornik.tv/wowza.swf?v50&b=100 pageUrl=https://zbiornik.tv/'+str(item["nick"])+app+' live=1'
                     if str(item["accType"])<>'1':
                        valTab.append(CDisplayListItem(str(item["nick"])+'    {'+sex+'}',str(item["nick"]),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', streamUrl, 0)], 0, phImage, None)) 
              except Exception as e:
                 printExc()
           return valTab

        if 'showup' == name:
           self.MAIN_URL = 'http://showup.tv' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'showup.cookie')
           #url = 'https://showup.tv/site/accept_rules?ref=https://showup.tv/'
           url = 'https://showup.tv'
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           #accept_rules.showup.tv/
           self.defaultParams['cookie_items'] = {'accept_rules':'true'}
           sts, data = self.get_Page(url)
           if not sts: return
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li data-equalizer-watch class="stream"', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = phUrl[1:] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phDesc = self.cm.ph.getSearchGroups(item, '''<p>([^>]+?)</p>''', 1, True)[0]
              transcoderaddr = self.cm.ph.getSearchGroups(item, '''transcoderaddr=['"]([^"^']+?)['"]''', 1, True)[0] 
              streamid = self.cm.ph.getSearchGroups(item, '''streamid=['"]([^"^']+?)['"]''', 1, True)[0] 
              uid = self.cm.ph.getSearchGroups(item, '''uid=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl =  'rtmp://'+transcoderaddr+':1935/webrtc/'+streamid+'_aac'
              phImage = 'http://showup.tv/'+phImage
              valTab.append(CDisplayListItem(phTitle,phTitle+'     '+decodeHtml(phDesc),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 0)], 0, phImage, None)) 
           return valTab

        if 'xvideos' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.xvideos.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'xvideos.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="dyn', '</li>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''href=.*?>([^>]+?)</a>''', 1, True)[0].strip()
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'xvideos-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name) 
           valTab.insert(0,CDisplayListItem('--- Pornstars ---',   'Pornstars',   CDisplayListItem.TYPE_CATEGORY, ['https://www.xvideos.com/pornstars-index/list'], 'xvideos-pornstars', '', None)) 
           valTab.insert(0,CDisplayListItem('--- Best Videos ---', 'Best Videos', CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/best/'],     'xvideos-clips', '', None)) 
           valTab.insert(0,CDisplayListItem('--- New Videos ---',  'New Videos',  CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL],              'xvideos-clips', '', None)) 
           valTab.insert(0,CDisplayListItem('--- 100% Verified ---',  '100% Verified',  CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/verified/videos'],              'xvideos-clips', '', None)) 
           #valTab.insert(0,CDisplayListItem('--- Channels ---',  'Channels',  CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/channels'],              'xvideos-clips', '', None)) 
           valTab.insert(0,CDisplayListItem('--- Porno po polsku ---',  'Porno po polsku',  CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/porn/polski'],              'xvideos-clips', '', None)) 
           self.SEARCH_proc='xvideos-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'xvideos-pornstars' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.xvideos.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'xvideos.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'class="tags-list">', 'footer', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phTitle = self._cleanHtmlStr(item).strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'xvideos-clips', '', None)) 
           return valTab
        if 'xvideos-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.xvideos.com/?k='+url.replace(' ','+'), 'xvideos-clips')
           return valTab              
        if 'xvideos-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.xvideos.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'xvideos.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getDataBeetwenMarkers(data, '"active" href=', '</ul></div>', False)[1]
           next = self.cm.ph.getSearchGroups(next, '''href=['"](/[^"^']+?)['"]''', 1, True)[0].replace('&amp;','&').replace(' ','+')
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'id="video', '</p></div>')
           for item in data:
              phTitle = re.compile('''title=['"]([^'^"]+?)['"]''').findall(item) 
              for titel in phTitle:
                 if not 'Verified' in titel: 
                    phTitle = titel
                    break
              if not phTitle: phTitle = 'VIDEO'
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](/video[^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''duration">([^>]+?)<''', 1, True)[0] 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime.strip()+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+phUrl, 1)], 0, phImage, None)) 
           if next:
              valTab.append(CDisplayListItem('Next', 'Page: '+self.MAIN_URL+next, CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+next], name, '', None))                
           return valTab

        if 'hentaigasm' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://hentaigasm.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'hentaigasm.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return
           printDBG( 'Host listsItems data: '+data )
           parse = re.search('Genres(.*?)</div></div>', data, re.S|re.I)
           if not parse: return valTab
           phCats = re.findall("<a href='(.*?)'.*?>(.*?)<", parse.group(1), re.S)
           if phCats:
              for (phUrl, phTitle) in phCats:
                  valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'hentaigasm-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- New ---", "New",        CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL], 'hentaigasm-clips', '',None))
           return valTab
        if 'hentaigasm-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           sts, data = self.get_Page(url)
           if not sts: return
           #printDBG( 'Host listsItems data: '+data )
           phMovies = re.findall('<div class="thumb">.*?title="(.*?)" href="(.*?)".*?<img src="(.*?)"', data, re.S)
           if phMovies:
              for (phTitle, phUrl, phImage) in phMovies:
                  phImage = phImage.replace(' ','%20')
                  valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           match = re.search("<div class='wp-pagenavi'>(.*?)</div>", data, re.S)
           if match: match = re.findall("href='(.*?)'", match.group(1), re.S)
           if match:
                  phUrl = match[-1]
                  valTab.append(CDisplayListItem('Next', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [phUrl], name, '', None))                
           return valTab

        if 'youporn' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.youporn.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'youporn.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host getResolvedURL data: '+data )
           #data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a data-espnode=', '</a>')
           data2 = self.cm.ph.getDataBeetwenMarkers(data, 'categories_list porn-categories action', 'footer', False)[1]
           if not data2: data2 = data
           data = self.cm.ph.getAllItemsBeetwenMarkers(data2, '<a href="/category/', '</a>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              #phTitle = self.cm.ph.getSearchGroups(item, '''ListElement">([^>]+?)<''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](/category/[^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl + 'time/?'
              if phTitle and phUrl: 
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'youporn-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Most Discussed ---",     "Most Discussed",     CDisplayListItem.TYPE_CATEGORY,["https://www.youporn.com/most_discussed/"],                   'youporn-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Favorited ---",     "Most Favorited",     CDisplayListItem.TYPE_CATEGORY,["https://www.youporn.com/most_favorited/"],                   'youporn-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Viewed ---",        "Most Viewed",        CDisplayListItem.TYPE_CATEGORY,["https://www.youporn.com/most_viewed/"],                      'youporn-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---",          "Top Rated",          CDisplayListItem.TYPE_CATEGORY,["https://www.youporn.com/top_rated/"],                        'youporn-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- New ---",                "New",                CDisplayListItem.TYPE_CATEGORY,["https://www.youporn.com/"],                                  'youporn-clips', '',None))
           self.SEARCH_proc='youporn-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'youporn-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.youporn.com/search/?query=%s' % url.replace(' ','+'), 'youporn-clips')
           return valTab              
        if 'youporn-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.youporn.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'youporn.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host getResolvedURL data: '+data )
           next = self.cm.ph.getSearchGroups(data, '''rel=['"]next['"]\s*href=['"]([^"^']+?)['"]''', 1, True)[0] 
           #data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'data-video-id', '<i class="icon-thin-x">')
           data2 = self.cm.ph.getDataBeetwenMarkers(data, 'data-espnode="videolist', 'footer', False)[1]
           if len(data2): data = data2
           data = data.split('data-video-id=')
           if len(data): del data[0]
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?jpg)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0].replace("&amp;","&")
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0].replace("&amp;","&") 
              phRuntime = self.cm.ph.getSearchGroups(item, '''duration">([^>]+?)<''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = 'https://www.youporn.com' + phUrl
              if len(phUrl)>5 and phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phRuntime.strip()+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              next = next.replace("&amp;","&")
              if next.startswith('/'): next = 'https://www.youporn.com' + next
              valTab.append(CDisplayListItem('Next', 'Next: '+next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))                
           self.MAIN_URL = '' 
           return valTab

        if 'redtube' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.redtube.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'redtube.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li id="categor', '</li>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''data-thumb_url=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'redtube-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Most Favored ---", "Most Favored", CDisplayListItem.TYPE_CATEGORY,["http://www.redtube.com/mostfavored?period=alltime"], 'redtube-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Viewed ---",  "Most Viewed",  CDisplayListItem.TYPE_CATEGORY,["http://www.redtube.com/mostviewed?period=alltime"],  'redtube-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---",    "Top Rated",    CDisplayListItem.TYPE_CATEGORY,["http://www.redtube.com/top?period=alltime"],         'redtube-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Newest ---",       "Newest",       CDisplayListItem.TYPE_CATEGORY,["http://www.redtube.com/"],                           'redtube-clips', '',None))
           self.SEARCH_proc='redtube-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'redtube-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.redtube.com/?search=%s' % url.replace(' ', '+'), 'redtube-clips')
           return valTab      
        if 'redtube-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.redtube.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'redtube.cookie')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getSearchGroups(data, '''<link rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
           data2 = self.cm.ph.getDataBeetwenMarkers(data, '<ul id="block_browse"', 'footer', False)[1]
           if not data2: data2 = self.cm.ph.getDataBeetwenMarkers(data, '<ul id="search_results_block"', '</ul>', False)[1]
           if not data2: data2 = data
           data = self.cm.ph.getAllItemsBeetwenMarkers(data2, '<li id=', '</li>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''data-mediumthumb=['"]([^"^']+?)['"]''', 1, True)[0]
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''data-thumb_url=['"]([^"^']+?)['"]''', 1, True)[0]
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0]
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0]
              phRuntime = self.cm.ph.getDataBeetwenMarkers(item, '<span class="duration">', '</a>', False)[1]
              phRuntime = self._cleanHtmlStr(phRuntime).strip() 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phRuntime and not '/premium/' in phUrl:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phRuntime+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              valTab.append(CDisplayListItem('Next', next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))                
           return valTab

        if 'xhamster' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://xhamster.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'xhamster.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'letter-block', 'footer', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
           for item in data:
              phTitle = self._cleanHtmlStr(item).strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](https://xhamster.com/categories/[^"^']+?)['"]''', 1, True)[0]
              if config.plugins.iptvplayer.xhamstertag.value and not phUrl:
                 phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](https://xhamster.com/tags/[^"^']+?)['"]''', 1, True)[0] 
                 if phUrl and phTitle: phTitle = phTitle+'   (tags)'
              if phUrl and phTitle:
                 valTab.append(CDisplayListItem(phTitle.strip(),phTitle.strip(),CDisplayListItem.TYPE_CATEGORY, [phUrl],'xhamster-clips', '', None)) 
           valTab.insert(0,CDisplayListItem("--- HD ---",       "HD",       CDisplayListItem.TYPE_CATEGORY,["http://xhamster.com/categories/hd-videos"], 'xhamster-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Best monthly ---",       "Best monthly",       CDisplayListItem.TYPE_CATEGORY,["http://xhamster.com/best/monthly"], 'xhamster-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Pornstars ---",       "Pornstars",       CDisplayListItem.TYPE_CATEGORY,["http://xhamster.com/pornstars"], 'xhamster-pornostars', '',None))
           valTab.insert(0,CDisplayListItem("--- New ---",       "New",       CDisplayListItem.TYPE_CATEGORY,["http://xhamster.com/"], 'xhamster-clips', '',None))
           self.SEARCH_proc='xhamster-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'xhamster-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.xhamster.com/search.php?from=suggestion&q=%s&qcat=video' % url.replace(' ','+'), 'xhamster-clips')
           return valTab              
        if 'xhamster-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'xhamster.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getSearchGroups(data, '''data-page="next"\shref=['"]([^"^']+?)['"]''', 1, True)[0] 
           if not next: next = self.cm.ph.getSearchGroups(data, '''rel="next"\shref=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = data.split('video-id=')
           if len(data): del data[0]
           #printDBG('Adatok: '+str(data)) 
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              allRuntime = self.cm.ph.getAllItemsBeetwenMarkers(item, 'duration>', '</span>', False)
              for phRuntime in allRuntime:
                  allRuntime[allRuntime.index(phRuntime)] = 'Hossz: ' + phRuntime
              #printDBG('Ido: '+str(phRuntime)) 
              views =self.cm.ph.getSearchGroups(item, '''text">([^>]+?)</span''', 1, True)[0] 
              like = self.cm.ph.getSearchGroups(item, '''like".*?text">([^>]+?)<''', 1, True)[0] 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phRuntime+'] '+decodeHtml(phTitle)+'\n'+views+'\n'+like,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              next = next.replace('&amp;','&')
              if next.startswith('/'): next = 'https://xhamster.com' + next
              next = decodeUrl(next)
              valTab.append(CDisplayListItem('Next', 'Page: '+next.split('/')[-1], CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))
           return valTab
        if 'xhamster-pornostars' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'xhamster.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'letter-block', 'footer', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
           for item in data:
              phTitle = self._cleanHtmlStr(item).strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](https://xhamster.com/pornstars/[^"^']+?)['"]''', 1, True)[0]
              if phUrl:
                 valTab.append(CDisplayListItem(phTitle.strip(),phTitle.strip(),CDisplayListItem.TYPE_CATEGORY, [phUrl],'xhamster-clips', '', None)) 
           return valTab

        if 'xhamsterlive' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://xhamsterlive.com' 
           #url='http://xhamsterlive.com/api/front/models'
           url='https://go.hpyrdr.com/api/models?limit=9999'
           COOKIEFILE = os_path.join(GetCookieDir(), 'xhamsterlive.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           country = ''
           Url = ''
           result = simplejson.loads(data)
           try:
              for item in result["models"]:
                 ID = str(item["id"]) 
                 Name = str(item["username"])
                 try:
                    Url = str(item["stream"]['url'])
                    #printDBG( 'Host Url: '+Url )
                 except Exception:
                    printExc()
                 Image = str(item["snapshotUrl"].replace('\/','/'))  
                 status = str(item["status"])
                 try:
                    country = ' [Country: '+str(item["modelsCountry"]).upper()+']'
                 except Exception:
                    printExc()
                 if status == "public":
                    valTab.append(CDisplayListItem(Name,Name+country,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', Url, 0)], 0, Image, None)) 
           except Exception:
              printExc()
           return valTab

        if 'eporner' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.eporner.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'eporner.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           #data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'div class="categoriesbox', '</div> </div>')
           data = data.split('class="categoriesbox')
           if len(data): del data[0]
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = phTitle.replace(' movies', '').replace('Porn Videos', '')
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'eporner-clips', phImage, phUrl)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- 4k ---",        "4k",        CDisplayListItem.TYPE_CATEGORY,["https://www.eporner.com/category/4k-porn/"], 'eporner-clips', '','/4k/'))
           valTab.insert(0,CDisplayListItem("--- HD ---",        "HD",        CDisplayListItem.TYPE_CATEGORY,["http://www.eporner.com/hd/"], 'eporner-clips', '','/hd/'))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---", "Top Rated", CDisplayListItem.TYPE_CATEGORY,["http://www.eporner.com/top_rated/"], 'eporner-clips', '','/top_rated/'))
           valTab.insert(0,CDisplayListItem("--- Popular ---",   "Popular",   CDisplayListItem.TYPE_CATEGORY,["http://www.eporner.com/weekly_top/"], 'eporner-clips', '','/weekly_top/'))
           valTab.insert(0,CDisplayListItem("--- On Air ---",    "On Air",    CDisplayListItem.TYPE_CATEGORY,["http://www.eporner.com/currently/"], 'eporner-clips', '','/currently/'))
           valTab.insert(0,CDisplayListItem("--- New ---",       "New",       CDisplayListItem.TYPE_CATEGORY,["http://www.eporner.com/"], 'eporner-clips', '',''))
           self.SEARCH_proc='eporner-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'eporner-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.eporner.com/search/%s/' % url.replace(' ','+'), 'eporner-clips')
           return valTab    
        if 'eporner-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           self.MAIN_URL = 'http://www.eporner.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'eporner.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getSearchGroups(data, '''<link rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0]
           data = data.split('data-vp')
           if len(data): del data[0]
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phRuntime = self.cm.ph.getSearchGroups(item, '''mbtim".+?>([^>]+?)<''', 1, True)[0]
              mbrate = self.cm.ph.getSearchGroups(item, '''mbrate".+?>([^>]+?)<''', 1, True)[0]
              mbvie = self.cm.ph.getSearchGroups(item, '''mbvie".+?>([^>]+?)<''', 1, True)[0]
              if mbrate: mbrate = '['+mbrate+'] '
              if mbvie: mbvie = '[Views: '+mbvie+'] '
              size = self.cm.ph.getSearchGroups(item, '''<span>([^>]+?)</span>''', 1, True)[0]
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle)+'    '+size,'['+phRuntime+'] '+decodeHtml(phTitle)+'    '+size+'\n'+mbrate+mbvie,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              if next.startswith('/'): next = self.MAIN_URL + next
              valTab.append(CDisplayListItem('Next', 'Next: '+ next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', catUrl))                
           return valTab

        if 'pornhub' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.pornhub.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornhub.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self._getPage(url, self.defaultParams)
           if not sts: return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="cat', '</li>')
           #printDBG( 'Host2 getResolvedURL data: '+str(data) )
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'pornhub-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- HD ---",         "HD",          CDisplayListItem.TYPE_CATEGORY,["https://www.pornhub.com/video?c=38"], 'pornhub-clips', 'http://cdn1a.static.pornhub.phncdn.com/images/categories/38.jpg',None))
           valTab.insert(0,CDisplayListItem("--- Longest ---",    "Longest",     CDisplayListItem.TYPE_CATEGORY,["https://www.pornhub.com/video?o=lg"], 'pornhub-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---",  "Top Rated",   CDisplayListItem.TYPE_CATEGORY,["https://www.pornhub.com/video?o=tr"], 'pornhub-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Viewed ---","Most Viewed", CDisplayListItem.TYPE_CATEGORY,["https://www.pornhub.com/video?o=mv"], 'pornhub-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Recent ---","Most Recent", CDisplayListItem.TYPE_CATEGORY,["https://www.pornhub.com/video?o=mr"], 'pornhub-clips', '',None))
           self.SEARCH_proc='pornhub-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'pornhub-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.pornhub.com/video/search?search=%s' % url.replace(' ','+'), 'pornhub-clips')
           return valTab    
        if 'pornhub-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.pornhub.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornhub.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self._getPage(url, self.defaultParams)
           if not sts: return valTab
           #printDBG( 'Host2 getResolvedURL data: '+data )
           next = self.cm.ph.getSearchGroups(data, '''"page_next"><a href=['"]([^"^']+?)['"]''')[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'videoblock', '</li>')
           #printDBG( 'Host2 getResolvedURL data: '+str(data) )
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&') 
              phImage = self.cm.ph.getSearchGroups(item, '''data-mediumthumb=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phRuntime = self.cm.ph.getSearchGroups(item, '''"duration">([^"^']+?)<''', 1, True)[0] 
              phAdded = self.cm.ph.getSearchGroups(item, '''class="added">([^"^']+?)<''', 1, True)[0] 
              OldImage = self.cm.ph.getSearchGroups(item, '''data-image=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.MAIN_URL+phUrl
              if not OldImage:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phRuntime+'] '+decodeHtml(phTitle)+ '\n[Added: '+phAdded+'] ',CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              valTab.append(CDisplayListItem('Next', 'Next '+re.sub('.+page=', '', next), CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+next.replace('&amp;','&')], name, '', None))        
           return valTab

        if 'hdporn' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.hdporn.net'
           COOKIEFILE = os_path.join(GetCookieDir(), 'hdporn.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="content">', '</div>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&') 
              phImage = self.cm.ph.getSearchGroups(item, '''<img\ssrc=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.getFullUrl(phUrl, self.MAIN_URL)
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'hdporn-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",           CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/top-rated/"]  , 'hdporn-clips','', None))
           valTab.insert(0,CDisplayListItem("--- Home ---","Home",           CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL]  , 'hdporn-clips','', None))
           return valTab
        if 'hdporn-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'hdporn.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return
           printDBG( 'Host listsItems data: '+data )
           next = re.findall('<div id="pagination">.*?</div>', data, re.S)
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="content', '</div>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt="([^"]+?)"''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&') 
              phRuntime = self.cm.ph.getSearchGroups(item, '''TIME:([^"^']+?)<''', 1, True)[0].strip()
              phUrl = self.cm.getFullUrl(phUrl, self.MAIN_URL)
              valTab.append(CDisplayListItem(phTitle,'['+phRuntime+'] '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              next = re.findall("</a><a href='(.*?)'>", next[0], re.S)
              if len(next)>0:
                 #next = self.cm.getFullUrl(next[0], self.MAIN_URL)
                 valTab.append(CDisplayListItem('Next', next[0].replace('.html',''), CDisplayListItem.TYPE_CATEGORY, [self.cm.getFullUrl(next[0], url)], name, '', None))                
              return valTab
  
        if 'beeg' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://beeg.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'beeg.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return
           printDBG( 'Host listsItems data: '+data )
           self.beeg_version = self.cm.ph.getSearchGroups(data, '''cpl/(\d+)\.js''', 1, True)[0] 
           if not self.beeg_version: self.beeg_version = self.cm.ph.getSearchGroups(data, '''beeg_version = (\d+);''', 1, True)[0] 
           if not self.beeg_version: self.beeg_version = '1589461492752' 

           printDBG( 'Host beeg_version: '+str(self.beeg_version) )
           url = 'https://beeg.com/static/cpl/%s.js' % self.beeg_version
           sts, data = self.get_Page(url)
           if not sts: return
           printDBG( 'Host listsItems data2: '+data )
           self.beeg_salt = self.cm.ph.getSearchGroups(data, '''beeg_salt=['"]([^"^']+?)['"]''', 1, True)[0] 
           self.beeg_api = '//beeg.com/api/v6/' 

           printDBG( 'Host self.beeg_salt: '+self.beeg_salt )
           printDBG( 'Host self.beeg_api: '+self.beeg_api )

           url = 'https:%s%s/index/main/0/mobile' % (self.beeg_api, self.beeg_version)
           sts, data = self.get_Page(url)
           if not sts: return
           printDBG( 'Host listsItems data3: '+data )
           result = byteify(simplejson.loads(data))
           for item in result["tags"]:
              phTitle = str(item["tag"]).title()
              phUrl = 'http:%s%s/index/tag/$PAGE$/mobile?tag=%s' % (self.beeg_api, self.beeg_version, urllib.quote(phTitle, '').lower())
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'beeg-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           return valTab    
        if 'beeg-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.beegfullhd = config.plugins.iptvplayer.beeg.value
           catUrl = self.currList[Index].possibleTypesOfSearch
           printDBG( 'Host listsItems cat-url: '+str(catUrl) )
           next = url
           if catUrl == None: 
              self.page = 0
           else:
              self.page += 1
           url = url.replace('$PAGE$', '%s' % str(self.page))
           printDBG( 'Host current url: '+url )
           printDBG( 'Host current next: '+next )
           printDBG( 'Host current page: '+ str(self.page) )
           COOKIEFILE = os_path.join(GetCookieDir(), 'beeg.cookie')
           sts, data = self.get_Page(url)
           if not sts: return
           printDBG( 'Host listsItems data: '+data )
           try:
              result = byteify(simplejson.loads(data))
              if result:
                 for item in result["videos"]:
                    phTitle = str(item["title"])
                    if not phTitle: phTitle = str(item["ps_name"])
                    #phVideoId = str(item["id"])
                    try:
                       Added = str(item["datetime"])
                    except Exception:
                       printExc()
                       Added = ''
                    try:
                       Time = str(item["duration"])
                       m, s = divmod(int(Time), 60)
                       Time = "[%02d:%02d] " % (m, s)
                    except Exception:
                       printExc()
                       Time = ''
                    try:
                       pid = self.cm.ph.getSearchGroups(str(item["thumbs"]), '''pid['"]:([^"^']+?),''', 1, True)[0].strip()
                       start = self.cm.ph.getSearchGroups(str(item["thumbs"]), '''start['"]:([^"^']+?),''', 1, True)[0].strip()
                       end = self.cm.ph.getSearchGroups(str(item["thumbs"]), '''end['"]:([^"^']+?),''', 1, True)[0].strip()
                       phVideoSvId = str(item["svid"])+'?v=2&p='+pid+'&s='+start+'&e='+end
                    except Exception:
                       printExc()
                       phVideoSvId = ''
                    phUrl = 'https:%s%s/video/%s' % (self.beeg_api, self.beeg_version, phVideoSvId)
                    try:
                        Image = self.cm.ph.getSearchGroups(str(item["thumbs"]), '''image['"]:\s['"]([^"^']+?)['"]''', 1, True)[0]
                        phImage = 'http://img.beeg.com/236x177/%s' % Image
                        if not Image: phImage = 'https://i.pinimg.com/474x/8e/89/91/8e89916e7e4d8c0b314d548578d4aba5.jpg'
                    except:
                        phImage = 'https://i.pinimg.com/474x/8e/89/91/8e89916e7e4d8c0b314d548578d4aba5.jpg'
                    valTab.append(CDisplayListItem(phTitle,Time+phTitle+'\nAdded: '+Added,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, phVideoSvId)) 
           except Exception:
              printExc()
           valTab.append(CDisplayListItem('Next', 'Page: '+str(self.page+2), CDisplayListItem.TYPE_CATEGORY, [next], name, '', 'Next'))                
           return valTab

        if 'pornrabbit' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.pornrabbit.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornrabbit.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'pornrabbit.cookie', 'pornrabbit.com', self.defaultParams)
           if not sts: return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, '<ul class=mCustomScrollbar>', '<div class=block-btn>', False)[1]
           #printDBG( 'Ezt talaltam: '+data )
           #data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a href=', '</span>')
           phTitle = self.cm.ph.getAllItemsBeetwenMarkers(data, 'title=', '>', False)
           
           #printDBG( 'Cimek: '+phTitle )
           phUrl = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a href="', '" title', False)
           #printDBG( 'Linkek: '+phUrl )
           for i in phTitle:
               
               valTab.insert(0,CDisplayListItem(i,i,CDisplayListItem.TYPE_CATEGORY, [phUrl[phTitle.index(i)]],'pornrabbit-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)   
           valTab.insert(0,CDisplayListItem("--- Most Viewed ---","Most Viewed",     CDisplayListItem.TYPE_CATEGORY,['https://www.pornrabbit.com/most-viewed/'],             'pornrabbit-clips',    '', None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,['https://www.pornrabbit.com/top-rated/'],             'pornrabbit-clips',    '', None))
           valTab.insert(0,CDisplayListItem("--- New ---","New",     CDisplayListItem.TYPE_CATEGORY,['https://www.pornrabbit.com/videos/'],             'pornrabbit-clips',    '', None))
           self.SEARCH_proc='pornrabbit-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'pornrabbit-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.pornrabbit.com/%s/' % url.replace(' ','-'), 'pornrabbit-clips')
           return valTab
        if 'pornrabbit-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornrabbit.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'pornrabbit.cookie', 'pornrabbit.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getDataBeetwenMarkers(data, 'pagination', 'Next', False)[1]
           #data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<!-- item -->', '<!-- item END -->')
           data = data.split('data-video=')
           if len(data): del data[0]
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0].replace(' Porn Videos','')
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0]
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Runtime = self.cm.ph.getSearchGroups(item, '''<span>([^>]+?)<''', 1, True)[0] 
              if Runtime:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Runtime+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              next = re.compile('''href=['"]([^'^"]+?)['"]''').findall(next) 
              if next:
                 next = next[-1]
                 if next.startswith('/'): next = 'https://www.pornrabbit.com' + next
                 if next.startswith('page'): next = re.sub('page.+', '', url) + next
                 valTab.append(CDisplayListItem('Next', next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None)) 
           return valTab

        if 'pornhd' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.pornhd.com/category' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornhd.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'pornhd.cookie', 'pornhd.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+str(data) )
           for item in data:
               phTitle = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="small-thumb-title">', '</div>', False)
               Urllist = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a href="', '" class="', False)
               printDBG( Urllist )
               #for item in Urllist:
                   #phUrl = self.MAIN_URL + Urllist
           
           for i in phTitle:
               valTab.insert(0,CDisplayListItem(i,i,CDisplayListItem.TYPE_CATEGORY, [phUrl[phTitle.index(i)]],'pornrabbit-clips', '', None))
           #for item in data:
            #  phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
            # phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
            #  if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
             # phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0]
             # if phUrl.startswith('/'): phUrl = 'https://www.pornhd.com' + phUrl 
             # if phTitle:
              #   valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'pornhd-clips', self.FullUrl(phImage), phUrl)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Channel ---",       "Channel",       CDisplayListItem.TYPE_CATEGORY,["https://www.pornhd.com/channel"], 'pornhd-pornstars', '',None))
           valTab.insert(0,CDisplayListItem("--- Pornstars ---",       "Pornstars",       CDisplayListItem.TYPE_CATEGORY,["https://www.pornhd.com/pornstars"], 'pornhd-pornstars', '',None))
           valTab.insert(0,CDisplayListItem("--- New ---",       "New",       CDisplayListItem.TYPE_CATEGORY,["https://www.pornhd.com/"], 'pornhd-clips', '',None))
           self.SEARCH_proc='pornhd-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'pornhd-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.pornhd.com/search?search=%s' % url.replace(' ','+'), 'pornhd-clips')
           return valTab
        if 'pornhd-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornhd.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'pornhd.cookie', 'pornhd.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+str(data) )
           next = self.cm.ph.getDataBeetwenMarkers(data, 'pagination', 'Next', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<article class="video-item ">', '</article>')
           for item in data:
              Title = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              Image = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0].replace('.webp','.jpg')
              if not Image: Image = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0].replace('.webp','.jpg')
              Url = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              Runtime = self.cm.ph.getSearchGroups(item, '''duration">([^"^']+?)<''', 1, True)[0] 
              if Url.startswith('/'): Url = 'http://www.pornhd.com' + Url 
              valTab.append(CDisplayListItem(decodeHtml(Title),'['+Runtime+'] '+decodeHtml(Title),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', Url, 1)], 0, Image, None)) 
           if next:
              next = re.compile('''href=['"]([^'^"]+?)['"]''').findall(next) 
              if next:
                 next = next[-1]
                 if next.startswith('/'): next = 'http://www.pornhd.com' + next
                 valTab.append(CDisplayListItem('Next', 'Page : '+next.split('=')[-1], CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))             
           return valTab
        if 'pornhd-channel' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.pornhd.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornhd.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'pornhd.cookie', 'pornhd.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+str(data) )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'class="tag', '</div>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              Title = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              Image = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Url = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if Url.startswith('/'): Url = 'http://www.pornhd.com' + Url 
              if Title:
                 valTab.append(CDisplayListItem(decodeHtml(Title),decodeHtml(Title),CDisplayListItem.TYPE_CATEGORY, [Url],'pornhd-clips', Image, None)) 
           return valTab
        if 'pornhd-pornstars' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.pornhd.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornhd.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'pornhd.cookie', 'pornhd.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+str(data) )
           cookieHeader = self.cm.getCookieHeader(COOKIEFILE)
           next = self.cm.ph.getDataBeetwenMarkers(data, 'pagination', 'Next', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<article class="small-thumb">', '</article>')
           for item in data:
              Title = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              Image = self.FullUrl(self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0])
              if not Image: Image = self.FullUrl(self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0])
              Url = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if Url.startswith('/'): Url = 'http://www.pornhd.com' + Url 
              Image = strwithmeta(Image, {'Referer':url, 'Cookie':cookieHeader})
              valTab.append(CDisplayListItem(decodeHtml(Title),decodeHtml(Title),CDisplayListItem.TYPE_CATEGORY, [Url],'pornhd-clips', Image, None)) 
           if next:
              next = re.compile('''href=['"]([^'^"]+?)['"]''').findall(next) 
              if next:
                 next = next[-1]
                 if next.startswith('/'): next = 'http://www.pornhd.com' + next
                 valTab.append(CDisplayListItem('Next', 'Page : '+next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None)) 
           return valTab

        if 'AH-ME' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.ah-me.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="moviec', '</div>')
           #printDBG( 'Host2 data: '+str(data) )
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              valTab.append(CDisplayListItem(phTitle,phUrl,CDisplayListItem.TYPE_CATEGORY, [phUrl],'AH-ME-clips', phImage, phUrl)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Long movies ---",       "Long movies",       CDisplayListItem.TYPE_CATEGORY,["https://www.ah-me.com/long-movies/page1.html"], 'AH-ME-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top rated ---",       "Top rated",       CDisplayListItem.TYPE_CATEGORY,["https://www.ah-me.com/top-rated/page1.html"], 'AH-ME-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- High definition ---",       "High definition",       CDisplayListItem.TYPE_CATEGORY,["https://www.ah-me.com/high-definition/page1.html"], 'AH-ME-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most favorited ---",       "Most favorited",       CDisplayListItem.TYPE_CATEGORY,["https://www.ah-me.com/mostfavorites/page1.html"], 'AH-ME-clips', '',None))
           self.SEARCH_proc='ahme-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'ahme-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.ah-me.com/search/%s/' % url.replace(' ','+'), 'AH-ME-clips')
           return valTab
        if 'AH-ME-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           self.MAIN_URL = 'http://www.ah-me.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getDataBeetwenMarkers(data, 'next"><a class="color" href="', '">Next', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="moviec', '/span></p>')
           #printDBG( 'Host2 data: '+str(data) )
           for item in data:
              Title = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              Image = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Url = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              Runtime = self.cm.ph.getSearchGroups(item, '''class="time">([^"^']+?)<''', 1, True)[0] 
              valTab.append(CDisplayListItem(decodeHtml(Title),'['+Runtime+'] '+decodeHtml(Title),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', Url, 1)], 0, Image, None)) 
           if next:
              printDBG( 'Host next: '+next )
              valTab.append(CDisplayListItem('Next', 'Next', CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))                
           return valTab

        if 'CHATURBATE' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://chaturbate.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'chaturbate.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER}
           sts, data = self.get_Page(url)
           if not sts: return
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, '<ul class="paging">', '</ul>', False)[1]
           catUrl = self.currList[Index].possibleTypesOfSearch
           if catUrl<>'next':
              valTab.append(CDisplayListItem('Female', 'Female',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/female-cams/'],'CHATURBATE-clips', '', None)) 
              valTab.append(CDisplayListItem('Featured', 'Featured',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL],'CHATURBATE-clips', '', None)) 
              valTab.append(CDisplayListItem('Couple', 'Couple',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/couple-cams/'],'CHATURBATE-clips', '', None)) 
              valTab.append(CDisplayListItem('Transsexual', 'Transsexual',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/transsexual-cams/'],'CHATURBATE-clips', '', None)) 
              valTab.append(CDisplayListItem('HD', 'HD',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/hd-cams/'],'CHATURBATE-clips', '', None)) 
              valTab.append(CDisplayListItem('Teen (18+)', 'Teen',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/teen-cams/'],'CHATURBATE-clips', '', None)) 
              valTab.append(CDisplayListItem('18 to 21', '18 to 21',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/18to21-cams/'],'CHATURBATE-clips', '', None)) 
              valTab.append(CDisplayListItem('20 to 30', '20 to 30',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/20to30-cams/'],'CHATURBATE-clips', '', None)) 
              valTab.append(CDisplayListItem('30 to 50', '30 to 50',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/30to50-cams/'],'CHATURBATE-clips', '', None)) 
              valTab.append(CDisplayListItem('Euro Russian', 'Euro Russian',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/euro-russian-cams/'],'CHATURBATE-clips', '', None)) 
              valTab.append(CDisplayListItem('Exhibitionist', 'Exhibitionist',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/exhibitionist-cams/'],'CHATURBATE-clips', '', None)) 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a href="/tag/', '</a>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item)
              phUrl = self.MAIN_URL + phUrl 
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'CHATURBATE-clips', '', None)) 
           if next_page:
              next_page = self.cm.ph.getAllItemsBeetwenMarkers(next_page, '<li', '</li>')
              for item in next_page:
                 next = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
              if next.startswith('/'): next = self.MAIN_URL + next 
              if next == '#': return valTab
              valTab.append(CDisplayListItem('Next', next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', 'next'))  
           return valTab
        if 'CHATURBATE-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'chaturbate.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return
           printDBG( 'Host listsItems data: '+data )
           cookieHeader = self.cm.getCookieHeader(COOKIEFILE)
           match = re.search('class="endless_separator".*?<li><a href="(.*?)"', data, re.S)
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="room_list_room', 'viewers</li>')
           #printDBG( 'Host2 data: '+str(data) )
           for item in data:
              Title = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              Image = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Url = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              Gender=''
              Age=self.cm.ph.getSearchGroups(item, '''<span class="age gender.">([^>]+?)<''', 1, True)[0]
              Description=''
              Location=self.cm.ph.getSearchGroups(item, '''location" style="display: none;">([^>]+?)<''', 1, True)[0]
              Viewers=''
              bitrate = self.cm.ph.getSearchGroups(item, '''thumbnail_label.*?>([^>]+?)<''', 1, True)[0]
              if Url.startswith('/'): Url = self.MAIN_URL + Url 
              Image = strwithmeta(Image, {'Referer':url, 'Cookie':cookieHeader})
              valTab.append(CDisplayListItem(decodeHtml(Title),decodeHtml(Title)+'   [Age: '+decodeHtml(Age)+']           [Location: '+decodeHtml(Location)+']   [info: '+bitrate+']',CDisplayListItem.TYPE_VIDEO, [CUrlItem('', Url, 1)], 0, Image, None)) 
           if match:
              printDBG( 'Host listsItems Next: '  +match.group(1) )
              if match.group(1).startswith('/'): Url = self.MAIN_URL + match.group(1) 
              valTab.append(CDisplayListItem('Next', match.group(1), CDisplayListItem.TYPE_CATEGORY, [Url], name, '', None))                
           return valTab

        if 'AMATEURPORN' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.amateurporn.net' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'amateurporn.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           cookieHeader = self.cm.getCookieHeader(COOKIEFILE)
           match = re.search('class="endless_separator".*?<li><a href="(.*?)"', data, re.S)
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a class="item"', '</a>')
           #printDBG( 'Host2 data: '+str(data) )
           for item in data:
              Title = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              Image = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Url = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              Gender=''
              Age=self.cm.ph.getSearchGroups(item, '''<span class="age gender.">([^>]+?)<''', 1, True)[0]
              Description=''
              Location=self.cm.ph.getSearchGroups(item, '''location" style="display: none;">([^>]+?)<''', 1, True)[0]
              Viewers=''
              bitrate = self.cm.ph.getSearchGroups(item, '''thumbnail_label.*?>([^>]+?)<''', 1, True)[0]
              if Url.startswith('/'): Url = self.MAIN_URL + Url 
              valTab.append(CDisplayListItem(Title,Url,CDisplayListItem.TYPE_CATEGORY, [Url],'AMATEURPORN-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           self.SEARCH_proc='AMATEURPORN-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'AMATEURPORN-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.amateurporn.me/search/%s/' % url.replace(' ','+'), 'AMATEURPORN-clips')
           return valTab
        if 'AMATEURPORN-clips' == name:
            printDBG( 'Host listsItems begin name='+name )
            COOKIEFILE = os_path.join(GetCookieDir(), 'amateurporn.cookie')
            self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
            self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
            sts, data = self.get_Page(url)
            if not sts: return valTab
            printDBG( 'Host listsItems data: '+data )
            next = self.cm.ph.getDataBeetwenMarkers(data, '<li class="next">', '</li>', False)[1]
            data = data.split('<div class="item  ">')
            if len(data): del data[0]
            for item in data:
                phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].replace('Model ','')
                phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
                phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
                Runtime = self.cm.ph.getSearchGroups(item, '''duration">([^>]+?)<''', 1, True)[0] 
                Added = self.cm.ph.getSearchGroups(item, '''added"><em>([^>]+?)<''', 1, True)[0] 
                if Added: Added = 'Added: '+ Added
                if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
                if phImage.startswith('//'): phImage = 'http:' + phImage
                valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Runtime+'] '+phTitle+'\n'+Added,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
            if next:
                page = self.cm.ph.getSearchGroups(str(next), '''from:([^"^']+?)['"]''')[0]
                next = url + '?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=post_date&from='+page
                valTab.append(CDisplayListItem('Next', 'Page : '+page, CDisplayListItem.TYPE_CATEGORY, [next], name, '', 'Next'))                
            return valTab

        if 'FOTKA-PL-KAMERKI' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = url 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           parse = re.search('"rooms":(.*?),"status":"OK"', data, re.S)
           if not parse: return valTab
           #printDBG( 'Host listsItems parse.group(1): '+parse.group(1) )
           result = simplejson.loads(parse.group(1))
           if result:
              for item in result:
                 try:
                    Name = str(item["name"])
                    Age = str(item["age"])
                    Url = str(item["streamUrl"].replace('\/','/'))+' live=1'
                    Title = str(item["title"])
                    Viewers = str(item["viewers"])
                    Image = str(item["av_126"].replace('\/','/'))
                    hls = str(item["streamMPEGHLSUrl"].replace('\/','/'))
                    try:
                       Image = str(item["av_640"].replace('\/','/'))
                    except Exception: printExc()
                    if config.plugins.iptvplayer.fotka.value == '0': Url = hls.replace('https','http').replace('manifest.hls','index.m3u8')
                    valTab.append(CDisplayListItem(Name,'[Age : '+Age+']'+'   [Views:  '+Viewers+']      '+Title, CDisplayListItem.TYPE_VIDEO, [CUrlItem('', Url, 0)], 0, Image, None)) 
                 except Exception: printExc()
           return valTab

        if 'CAM4-KAMERKI' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.cam4.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'cam4.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           url = 'https://cam4.com/tags?json=true&index=0&count=75&category='
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return valTab
           self.page = 1
           printDBG( 'Host listsItems data: '+data )
           try:
              result = byteify(simplejson.loads(data))
              if result:
                 for item in result:
                    phTitle = str(item["name"])
                    valTab.append(CDisplayListItem(phTitle, phTitle, CDisplayListItem.TYPE_CATEGORY, [phTitle], 'CAM4-KAMERKI-clips', '', None))                
           except Exception:
              printExc()
           valTab.sort(key=lambda poz: poz.name)
           #valTab.insert(0,CDisplayListItem("--- HD ---",       "HD",       CDisplayListItem.TYPE_CATEGORY,["hd"], 'CAM4-KAMERKI-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Poland ---",       "Polskie",       CDisplayListItem.TYPE_CATEGORY,["female&country=pl"], 'CAM4-KAMERKI-clips', '',None))
           #valTab.insert(0,CDisplayListItem("--- Couples ---",       "Pary",       CDisplayListItem.TYPE_CATEGORY,["couple"], 'CAM4-KAMERKI-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Male ---",       "Mężczyźni",       CDisplayListItem.TYPE_CATEGORY,["male"], 'CAM4-KAMERKI-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Transsexual ---",       "Transseksualiści",       CDisplayListItem.TYPE_CATEGORY,["shemale"], 'CAM4-KAMERKI-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- New ---",       "Nowe",       CDisplayListItem.TYPE_CATEGORY,["new"], 'CAM4-KAMERKI-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Female ---",       "Kobiety",       CDisplayListItem.TYPE_CATEGORY,["female"], 'CAM4-KAMERKI-clips', '',None))
           return valTab 
        if 'CAM4-KAMERKI-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           printDBG( 'Host listsItems cat-url: '+str(catUrl) )
           if catUrl == None: 
              self.page = 1
           else:
              self.page += 1
           COOKIEFILE = os_path.join(GetCookieDir(), 'cam4.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           Url = 'https://www.cam4.com/directoryCams?directoryJson=true&online=true&url=true&gender={0}&page={1}'.format(url, str(self.page))
           sts, data = self.get_Page(Url, self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host getResolvedURL data: '+data )
           try:
              result = byteify(simplejson.loads(data))
              if result:
                 for item in result["users"]:
                    phTitle = str(item["username"])
                    try:
                       phImage = 'https://snapshots.xcdnpro.com/thumbnails/{0}?s={1}'.format(str(item["username"]), str(item["thumbnailId"])) 
                    except Exception:
                       printExc()
                       phImage = str(item["profileImageLink"])
                    #phUrl = str(item["hlsPreviewUrl"])
                    try:
                       age = str(item["age"])
                       countryCode = str(item["countryCode"])
                    except Exception:
                       printExc()
                    phUrl = 'https://www.cam4.com/{0}'.format(str(item["username"]))
                    valTab.append(CDisplayListItem(phTitle,'[Age: '+age+']  ' + phTitle+'\nCountry: '+countryCode.upper(),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           except Exception:
              printExc()

           valTab.append(CDisplayListItem('Next ', 'Page: '+str(self.page), CDisplayListItem.TYPE_CATEGORY, [url], name, '', 'next'))                
           return valTab 

        if 'CAMSODA' == name:
            printDBG( 'Host listsItems begin name='+name )
            self.MAIN_URL = 'https://www.camsoda.com/' 
            COOKIEFILE = os_path.join(GetCookieDir(), 'camsoda.cookie')
            self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
            self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
            sts, data = self.get_Page(url)
            if not sts: return
            #printDBG( 'Host listsItems data: '+data )
            #"template":["username","display_name","connections","sort_value","subject_html","stream_name","tsize","server_prefix"]
            dane = re.search('"results":(.*?)}]', data, re.S)
            if dane: 
                dane = dane.group(1)+'}]'
                printDBG( 'Host listsItems json: '+dane )
                try:
                    result = simplejson.loads(dane)
                    tsize = '355x200'
                    Image = ''
                    if result:
                        for item in result:
                            subject_html = ''
                            try:
                                Name = str(item["username"]) #.encode("utf-8")
                                printDBG( 'Host Name: '+Name )
                            except Exception: printExc()
                            try:
                                Name = str(item["tpl"][1])
                                printDBG( 'Host Name: '+Name )
                            except Exception: printExc()
                            try:
                                stream_name = str(item["stream_name"]) #.encode("utf-8")
                                printDBG( 'Host stream_name: '+stream_name )
                            except Exception: printExc()
                            try:
                                stream_name = str(item["tpl"][2])
                                printDBG( 'Host stream_name: '+stream_name )
                            except Exception: printExc()
                            try:
                                subject_html = str(item["tpl"][5])
                                printDBG( 'Host subject_html: '+subject_html )
                            except Exception: printExc()
                            try:
                                enc = stream_name.split('-')[-1]
                            except Exception: printExc()
                            try:
                                Image = str(item["tpl"][9])
                            except Exception: printExc()
         
                            videourl = "https://www.camsoda.com/api/v1/video/vtoken/" + Name + "?username=guest_" + str(random.randrange(100, 55555))
                            if Image.startswith('//'): Image = 'http:' + Image 
                            try:
                               phImage = urlparser.decorateUrl(phImage, {'Referer': 'http://www.camsoda.com'})
                            except: pass
                            if config.plugins.iptvplayer.camsoda.value == '1':
                                videourl = 'rtmp'+videourl
                                stream = 'rtmp'
                            else:
                                stream = 'm3u8'
                            if stream_name:
                                valTab.append(CDisplayListItem(stream_name, stream_name+'   '+stream+'\n'+subject_html, CDisplayListItem.TYPE_VIDEO, [CUrlItem('', videourl, 1)], 0, Image, None)) 
                except Exception: printExc()
            return valTab 

        if 'STREAMATE' == name:
            printDBG( 'Host listsItems begin name='+name ) 
            self.MAIN_URL = 'https://streamate.com' 
            COOKIEFILE = os_path.join(GetCookieDir(), 'streamate.cookie')
            query_data = { 'url': url,  'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True }
            try:
                data = self.cm.getURLRequestData(query_data)
            except Exception as e:
                printExc()
                return valTab 
            printDBG( 'Host listsItems data: '+data )
            data = self.cm.ph.getDataBeetwenMarkers(data, '<div class="cats__content">', 'class="recents__list">', False)[1]
            data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
            for item in data:
                Title = self._cleanHtmlStr(item).split(' ')[1]
                Title = self.cm.ph.getDataBeetwenMarkers(item, '</span>', '</a>', False)[1]
                Title = str(Title).strip()
                Url = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
                if Url.startswith('/'): Url = 'https://streamate.com' + Url 
                valTab.append(CDisplayListItem(decodeHtml(Title),decodeHtml(Title),CDisplayListItem.TYPE_CATEGORY, [Url],'STREAMATE-clips', '', None)) 
            return valTab 
        if 'STREAMATE-clips' == name:
            printDBG( 'Host listsItems begin name='+name ) 
            self.MAIN_URL = 'https://streamate.com' 
            COOKIEFILE = os_path.join(GetCookieDir(), 'streamate.cookie')
            query_data = { 'url': url,  'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True }
            try:
                data = self.cm.getURLRequestData(query_data)
            except Exception as e:
                printExc()
                return valTab 
            printDBG( 'Host listsItems data: '+data )
            next = self.cm.ph.getDataBeetwenMarkers(data, 'class="pagination">', 'Next', False)[1]
            data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="js-dynamicsearch" data-status="online"', '</figure>')
            for item in data:
                phTitle = self.cm.ph.getSearchGroups(item, '''data-name=['"]([^"^']+?)['"]''', 1, True)[0] 
                phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
                phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
                phImage = self.cm.ph.getSearchGroups(item, '''data-thumbid=['"]([^"^']+?)['"]''', 1, True)[0] 
                age = self.cm.ph.getSearchGroups(item, '''"year">([^>]+?)<''', 1, True)[0].strip()
                if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
                if phImage.startswith('//'): phImage = 'http:' + phImage
                phImage = 'http://m2.nsimg.net/biopic/original4x3/' + phImage
                valTab.append(CDisplayListItem(decodeHtml(phTitle), decodeHtml(phTitle)+'  [Age:'+age+']', CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phTitle, 1)], 0, phImage, None)) 
            if next:
                next = re.compile('''href=['"]([^'^"]+?)['"]''').findall(next) 
                if next:
                    next = next[-1]
                    if next.startswith('/'): next = 'https://streamate.com' + next
                    valTab.append(CDisplayListItem('Next', 'Page : '+next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None)) 
            return valTab 

        if 'NAKED' == name:
            printDBG( 'Host listsItems begin name='+name ) 
            self.MAIN_URL = 'https://www.naked.com' 
            COOKIEFILE = os_path.join(GetCookieDir(), 'naked.cookie')
            host = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Mobile Safari/537.36'
            header = {'User-Agent': host, 'Accept':'application/json','Accept-Language':'en,en-US;q=0.7,en;q=0.3','X-Requested-With':'XMLHttpRequest','Content-Type':'application/x-www-form-urlencoded'} 
            query_data = {'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True }
            try:
                sts, data = self.cm.getPage(url, query_data)
            except Exception as e:
                printExc()
                return valTab 
            data = data.replace('\\','')
            printDBG( 'Host listsItems data: '+data )
            data = data.split('class="model-wrapper"')
            if len(data): del data[0]
            for item in data:
                phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].replace('Model ','')
                phUrl = self.cm.ph.getSearchGroups(item, '''class="modelLink"\shref=['"]([^"^']+?)['"]''', 1, True)[0] 
                phImage = self.cm.ph.getSearchGroups(item, '''live-image-src=['"]([^"^']+?)['"]''', 1, True)[0] 
                desc = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
                age = self.cm.ph.getSearchGroups(item, '''model-age">([^>]+?)<''', 1, True)[0] 
                if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
                if not 'http' in phUrl: phUrl = 'https://www.naked.com/?model=' + phUrl
                if phImage.startswith('//'): phImage = 'http:' + phImage
                valTab.append(CDisplayListItem(decodeHtml(phTitle), decodeHtml(phTitle)+'\n'+desc, CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
            return valTab 

        if 'YOUJIZZ' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.youjizz.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'youjizz.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return
           #printDBG( 'Host listsItems data: '+data )
           data2 = self.cm.ph.getDataBeetwenMarkers(data, 'class="footer-category category-link', 'footer-links', False)[1]
           if len(data2): data = data2
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li><a href="/categories/', '</li>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''">([^"^']+?)<''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item) 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'YOUJIZZ-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- HD ---",       "HD",       CDisplayListItem.TYPE_CATEGORY,["http://www.youjizz.com/search/HighDefinition-1.html#"], 'YOUJIZZ-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---",       "Top Rated",       CDisplayListItem.TYPE_CATEGORY,["http://www.youjizz.com/top-rated/1.html"], 'YOUJIZZ-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Newest ---",       "Newest",       CDisplayListItem.TYPE_CATEGORY,["http://www.youjizz.com/newest-clips/1.html"], 'YOUJIZZ-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Popular ---",       "Popular",       CDisplayListItem.TYPE_CATEGORY,["http://www.youjizz.com/most-popular/1.html"], 'YOUJIZZ-clips', '',None))
           self.SEARCH_proc='YOUJIZZ-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'YOUJIZZ-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.youjizz.com/search/%s-1.html' % url.replace(' ','+'), 'YOUJIZZ-clips')
           return valTab
        if 'YOUJIZZ-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           self.MAIN_URL = 'http://www.youjizz.com' 
           url = url.replace(' ','%20')
           COOKIEFILE = os_path.join(GetCookieDir(), 'youjizz.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return
           printDBG( 'Host listsItems data: '+data )
           next=''
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'pagination', '</div>', False)[1]
           next_page = self.cm.ph.getAllItemsBeetwenMarkers(next_page, '<li', '</li>')
           for item in next_page:
              next = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0]
           if next.startswith('/'): next = self.MAIN_URL + next
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="video-thumb', 'format-views')
           
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''class="">([^"^']+?)</a>''', 1, True)[0]
              printDBG( 'Cim:  '+phTitle )
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phImage=='': phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phRuntime = self.cm.ph.getSearchGroups(item, '''"time">([^"^']+?)<''', 1, True)[0] 
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle).strip(),'['+phRuntime+'] '+decodeHtml(phTitle).strip(),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+phUrl, 1)], 0, phImage, None)) 
           if next:
              valTab.append(CDisplayListItem('Next', next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))
           return valTab

        if 'DACHIX' == name:
           self.MAIN_URL = 'http://www.dachix.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           
           data = self.cm.getURLRequestData(query_data)
           printDBG( data )                    
           data = self.cm.ph.getDataBeetwenMarkers(data, 'Most Popular', '</section>', False)[1]
           printDBG( 'Kategoriak: '+ data )                    
           for item in data:
              phUrl = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a href="', '" class=', False)
              printDBG( 'Linkek: '+str(phUrl) )
              phTitle = self.cm.ph.getAllItemsBeetwenMarkers(data, 'g-bubble">', '</a></li>', False) 
              phImage = 'https://icdn.camshq.info/streamate/97908191/profile.jpeg'
           for i in phTitle:
              valTab.insert(0,CDisplayListItem(i,i,CDisplayListItem.TYPE_CATEGORY, [phUrl[phTitle.index(i)]],'DACHIX-clips', phImage, None))
              #valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl+"/videos"],'DACHIX-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           self.SEARCH_proc='DACHIX-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'DACHIX-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.dachix.com/s/%s' % url.replace(' ','+'), 'DACHIX-clips')
           return valTab
        if 'DACHIX-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           printDBG( 'Nyersadat: '+data )
           #next = self.cm.ph.getSearchGroups(data, '''rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<section class="l-listing-models">', '<div class="l-pagi', False) 
           printDBG( 'Modellek: '+str(data) )
           for item in data:
              phUrl = self.cm.ph.getAllItemsBeetwenMarkers(item, '<a href="',' >', False)
              phTitle = self.cm.ph.getAllItemsBeetwenMarkers(item, 'alt="', '"/>', False)
              phImage = self.cm.ph.getAllItemsBeetwenMarkers(item, '<img src="', '" alt', False)
              phRuntime = self.cm.ph.getSearchGroups(item, '''S">([^>]+?)[-<]''', 1, True)[0]
              printDBG( 'Linkek: '+str(data) )
              valTab.append(CDisplayListItem(phTitle, phTitle, CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None))
              valTab.sort(key=lambda poz: poz.name)
              printDBG( 'Modellek: '+str(data) )
              #if phUrl.startswith('/'): phUrl = 'http://www.dachix.com' + phUrl
              #if phUrl.startswith('www'): phUrl = 'http://' + phUrl
              #valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phRuntime+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           #if next:
           #   if next.startswith('/'): next = 'http://www.dachix.com' + next
           #   valTab.append(CDisplayListItem('Next', 'Page: '+next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))
           return valTab

        if 'DRTUBER' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.drtuber.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'drtuber.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'contain_cols', '</div> </div> </div> </div>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item) 
              if '/gay/' in phUrl: phTitle = phTitle + ' gay'
              if '/shemale/' in phUrl: phTitle = phTitle + ' shemale'
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl 
              valTab.append(CDisplayListItem(phTitle,phUrl,CDisplayListItem.TYPE_CATEGORY, [phUrl],'DRTUBER-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           self.SEARCH_proc='DRTUBER-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'DRTUBER-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.drtuber.com/search/videos/%s' % url.replace(' ','+'), 'DRTUBER-clips')
           return valTab
        if 'DRTUBER-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'drtuber.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return
           #printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getSearchGroups(data, '''class="next"><a href=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a href="/video/', '</a>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phRuntime = self.cm.ph.getSearchGroups(item, '''([\d]?\d\d:\d\d)''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = 'http://www.drtuber.com' + phUrl 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phRuntime+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              if next.startswith('/'): next = self.MAIN_URL + next 
              valTab.append(CDisplayListItem('Next', 'Page: '+next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))
           return valTab

        if 'MYFREECAMS' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.myfreecams.com/' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'myfreecams.cookie')
           rm(COOKIEFILE)
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE, 'return_data': True}
           sts, data = self.cm.getPage('https://new.myfreecams.com/server', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           #serwery = self.cm.ph.getDataBeetwenMarkers(data, 'ServerConfig = ', ';', False)[1]
           try:
              result = byteify(simplejson.loads(data))
              if result:
                 self.h5video_servers = result["h5video_servers"]
                 self.wzobs_servers = result["wzobs_servers"]
                 self.ngvideo_servers = result["ngvideo_servers"]
                 self.websocket_servers = result["websocket_servers"]
                 self.chat_servers = result["chat_servers"]
           except Exception:
              printExc()
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE, 'return_data': True}
           sts, data = self.cm.getPage(self.MAIN_URL, self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )

           self.cookieHeader = self.cm.getCookieHeader(COOKIEFILE)
           self.baf = 'baf='+self.cm.getCookieItem(COOKIEFILE,'baf')+';'
           self.cid = 'cid='+self.cm.getCookieItem(COOKIEFILE,'cid')+';'

           age = ''
           country = ''
           city = ''
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class=slm_c>', '</div>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = phUrl.split('/')[-1]
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(phTitle,age +phTitle+'\n'+city+' '+country,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phTitle, 1)], 0, phImage, None)) 
           if config.plugins.iptvplayer.xxxsortmfc.value: valTab.sort(key=lambda poz: poz.name)
           return valTab 

        if 'TNAFLIX' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.tnaflix.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'Categories</h', 'footer', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0].strip()
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'TNAFLIX-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Featured ---",       "Featured",       CDisplayListItem.TYPE_CATEGORY,["https://www.tnaflix.com/featured/?d=all&period=all"], 'TNAFLIX-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Popular ---",       "Most Popular",       CDisplayListItem.TYPE_CATEGORY,["https://www.tnaflix.com/popular/?d=all&period=all"], 'TNAFLIX-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---",       "Top Rated",       CDisplayListItem.TYPE_CATEGORY,["https://www.tnaflix.com/toprated/?d=all&period=all"], 'TNAFLIX-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- New ---",       "New",       CDisplayListItem.TYPE_CATEGORY,["https://www.tnaflix.com/new/?d=all&period=all"], 'TNAFLIX-clips', '',None))
           self.SEARCH_proc='TNAFLIX-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'TNAFLIX-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.tnaflix.com/search.php?what=%s&tab=' % url.replace(' ','+'), 'TNAFLIX-clips')
           return valTab
        if 'TNAFLIX-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getSearchGroups(data, '''rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'data-vid=', '</li>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].strip()
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              phRuntime = self.cm.ph.getSearchGroups(item, '''videoDuration'>([^>]+?)<''', 1, True)[0] 
              Added = self.cm.ph.getSearchGroups(item, '''floatLeft\'>([^>]+?)<''', 1, True)[0]
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phRuntime+'] '+decodeHtml(phTitle)+'\nAdded: '+Added,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              if next.startswith('/'): next = 'https://www.tnaflix.com' + next
              valTab.append(CDisplayListItem('Next', 'Page: '+next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))
           return valTab

        if 'LIVEJASMIN' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab.insert(0,CDisplayListItem('--- Transgender ---', 'Transgender', CDisplayListItem.TYPE_CATEGORY, ['http://www.livejasmin.com/en/transgender'], 'LIVEJASMIN-clips', '', None))
           valTab.insert(0,CDisplayListItem('--- Couple ---', 'Couple', CDisplayListItem.TYPE_CATEGORY, ['http://www.livejasmin.com/en/couple'], 'LIVEJASMIN-clips', '', None))
           valTab.insert(0,CDisplayListItem('--- Mature ---', 'Mature', CDisplayListItem.TYPE_CATEGORY, ['http://www.livejasmin.com/en/mature'], 'LIVEJASMIN-clips', '', None))
           valTab.insert(0,CDisplayListItem('--- Fetish ---', 'Fetish', CDisplayListItem.TYPE_CATEGORY, ['http://www.livejasmin.com/en/fetish'], 'LIVEJASMIN-clips', '', None))
           valTab.insert(0,CDisplayListItem('--- Lesbian ---', 'Lesbian', CDisplayListItem.TYPE_CATEGORY, ['http://www.livejasmin.com/en/lesbian'], 'LIVEJASMIN-clips', '', None))
           valTab.insert(0,CDisplayListItem('--- Soul_mate ---', 'Soul_mate', CDisplayListItem.TYPE_CATEGORY, ['http://www.livejasmin.com/en/soul_mate'], 'LIVEJASMIN-clips', '', None))
           valTab.insert(0,CDisplayListItem('--- Hot_flirt ---', 'Hot_flirt', CDisplayListItem.TYPE_CATEGORY, ['http://www.livejasmin.com/en/hot_flirt'], 'LIVEJASMIN-clips', '', None))
           valTab.insert(0,CDisplayListItem('--- Girl ---', 'Girl', CDisplayListItem.TYPE_CATEGORY, ['http://www.livejasmin.com/en/girl'], 'LIVEJASMIN-clips', '', None))
           return valTab 
        if 'LIVEJASMIN-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.livejasmin.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try: data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error cookie' )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           sessionID = self.cm.ph.getSearchGroups(data, '''"jsm2session":['"]([^"^']+?)['"]''')[0] 
           data2 = self.cm.ph.getDataBeetwenMarkers(data, 'listPagePerformers =', '];', False)[1]
           result = simplejson.loads(data2+']')
           phImage = ''
           if result:
              for item in result:
                 try:
                    phTitle = str(item["pid"])
                    phUrl = 'http://www.livejasmin.com/en/chat/'+phTitle+'?session='+sessionID
                    try:
                       ID = str(item["id"])
                       phImage = self.cm.ph.getDataBeetwenMarkers(data, 'container_'+ID, '</picture>', False)[1]
                       phImage = self.cm.ph.getSearchGroups(phImage, '''jpg-src=['"]([^"^']+?)['"]''')[0] 
                       #printDBG( 'Host phImage: '+str(phImage) )
                    except Exception:
                       printExc()
                    valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
                 except Exception:
                    printExc()
           data2 = None
           return valTab 

        if 'EXTREMETUBE' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.extremetube.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'extremetube.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'Categories</h1>', 'footer', False)[1]
           printDBG( 'Host listsItems data: '+data )
           if '<option value' in data:
              data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<option value', '</option>')
           elif 'fromPage=categories' in data:
              data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a class="thumb-cat', '</a>')
           else:
              data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phTitle: phTitle = self._cleanHtmlStr(item) 
              phUrl = self.cm.ph.getSearchGroups(item, '''value=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phUrl: phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              #phUrl = phUrl.replace('?fromPage=categories', '') + '?format=json&page=$PAGE$'
              #if not 'json' in phUrl: phUrl = phUrl + '?format=json&page=$PAGE$'
              if phTitle != "Select a Category":
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'EXTREMETUBE-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           self.SEARCH_proc='EXTREMETUBE-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'EXTREMETUBE-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.extremetube.com/videos?search=%s' % url.replace(' ','+'), 'EXTREMETUBE-clips')
           return valTab
        if 'EXTREMETUBE-clips' == name:
            printDBG( 'Host listsItems begin name='+name )
            COOKIEFILE = os_path.join(GetCookieDir(), 'extremetube.cookie')
            self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
            self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
            sts, data = self.get_Page(url)
            if not sts: return valTab
            printDBG( 'Host listsItems data: '+data )
            next = self.cm.ph.getSearchGroups(data, '''<link rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0]
            data = data.split('<li id="obj')
            if len(data): del data[0]
            for item in data:
                phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
                phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
                phImage = self.cm.ph.getSearchGroups(item, '''data-srcmedium=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&') 
                Runtime = self.cm.ph.getSearchGroups(item, '''data-duration=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&') 
                if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
                if phImage.startswith('//'): phImage = 'http:' + phImage
                valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Runtime+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
            if next:
                if next.startswith('/'): next = self.MAIN_URL + next
                valTab.append(CDisplayListItem('Next', 'Next: '+ next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))                
            return valTab


        if 'XXXLIST' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'xxxlist.txt' 
           URLLIST_FILE    = 'xxxlist.txt'
           self.filespath = config.plugins.iptvplayer.xxxlist.value
           self.sortList = config.plugins.iptvplayer.xxxsortuj.value
           self.currFileHost = IPTVFileHost() 
           self.currFileHost.addFile(self.filespath + URLLIST_FILE, encoding='utf-8')
           tmpList = self.currFileHost.getGroups(self.sortList)
           for item in tmpList:
               if '' == item: title = (_("Other"))
               else:          title = item
               valTab.append(CDisplayListItem(title,title,CDisplayListItem.TYPE_CATEGORY, [title],'XXXLIST-clips', '', None)) 
           return valTab
        if 'XXXLIST-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           desc = ''
           icon = ''
           tmpList = self.currFileHost.getAllItems(self.sortList)
           for item in tmpList:
               if item['group'] == url:
                   Title = item['title_in_group']
                   Url = item['url']
                   if item.get('icon', '') != '':
                      icon = item.get('icon', '')
                   if item.get('desc', '') != '':
                      desc = item['desc']
                   if Url.endswith('.mjpg') or Url.endswith('.cgi'):
                      valTab.append(CDisplayListItem(Title, Url,CDisplayListItem.TYPE_PICTURE, [CUrlItem('', Url, 1)], 0, '', None)) 
                   else:
                      valTab.append(CDisplayListItem(Title, Url+'\n'+desc,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', Url, 1)], 0, icon, None)) 
               elif url == (_("Other")) and item['group'] == '':
                   Title = item['full_title']
                   Url = item['url']
                   if item.get('icon', '') != '':
                      icon = item.get('icon', '')
                   if item.get('desc', '') != '':
                      desc = item['desc']
                   if Url.endswith('.mjpg') or Url.endswith('.cgi'):
                      valTab.append(CDisplayListItem(Title, Url,CDisplayListItem.TYPE_PICTURE, [CUrlItem('', Url, 1)], 0, '', None)) 
                   else:
                      valTab.append(CDisplayListItem(Title, Url+'\n'+desc,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', Url, 1)], 0, icon, None)) 
           return valTab

        if 'BONGACAMS' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://pl.bongacams.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'bongacams.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data ) 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a class="ht_item"', '</a>')
           for item in data:
              phTitle = self._cleanHtmlStr(item).strip()
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0].split('/')[-1]
              valTab.append(CDisplayListItem(phTitle,phUrl,CDisplayListItem.TYPE_CATEGORY, [phUrl],'BONGACAMS-clips', '', phTitle)) 
           valTab.insert(0,CDisplayListItem("--- Couples ---", "Pary",       CDisplayListItem.TYPE_CATEGORY,["couples"], 'BONGACAMS-clips', '',"---couples"))
           valTab.insert(0,CDisplayListItem("--- Male ---",       "Mężczyźni",       CDisplayListItem.TYPE_CATEGORY,["male"], 'BONGACAMS-clips', '',"---male"))
           valTab.insert(0,CDisplayListItem("--- Transsexual ---",       "Transseksualiści",       CDisplayListItem.TYPE_CATEGORY,["transsexual"], 'BONGACAMS-clips', '',"---transsexual"))
           valTab.insert(0,CDisplayListItem("--- New ---",       "Nowe",       CDisplayListItem.TYPE_CATEGORY,["new"], 'BONGACAMS-clips', '',"---new"))
           valTab.insert(0,CDisplayListItem("--- Female ---",       "Kobiety",       CDisplayListItem.TYPE_CATEGORY,["females"], 'BONGACAMS-clips', '',"---females"))
           return valTab 
        if 'BONGACAMS-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next = url
           if catUrl != 'Next': 
              self.page = 1
           else:
              self.page += 1
           COOKIEFILE = os_path.join(GetCookieDir(), 'bongacams.cookie')
           if catUrl.startswith('---'): 
              url1 = url
           else:
              url1 = 'females'
           url = 'https://en.bongacams.com/tools/listing_v3.php?livetab=%s&online_only=true&offset=%s&tag=%s' % (url1, str((self.page*24)-24), url)
           host = 'Mozilla/5.0 (iPad; CPU OS 8_1_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B466 Safari/600.1.4'
           header = {'User-Agent': host, 'Accept':'application/json','Accept-Language':'en,en-US;q=0.7,en;q=0.3','X-Requested-With':'XMLHttpRequest','Content-Type':'application/x-www-form-urlencoded', 'Referer':'https://en.bongacams.com/', 'Origin':'https://en.bongacams.com'}
           self.defaultParams = { 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True }
           sts, data = self.cm.getPage(url, self.defaultParams)
           if not sts: return valTab
           printDBG( 'second bonga-clips data: '+data )  

           x = 0

           result = byteify(simplejson.loads(data))
           if result:
              try:
                 for item in result["models"]:
                    age = ''
                    phImage = ''
                    #printDBG( 'Host item: '+str(item) )
                    try:
                       #online = str(item["online"])  
                       room = str(item["room"])
                       phTitle = str(item["username"]) 
                       phTitle2 = str(item["display_name"])
                    except Exception:
                       printExc()
                       continue
                    try:
                       phImage = str(item["thumb_image"]) 
                       if phImage.startswith('//'): phImage = 'http:' + phImage
                       phImage = phImage.replace ('.{ext}','.jpg')
                    except Exception:
                       printExc()
                    bitrate = '' 
                    try:
                       bitrate = str(item["vq"]) 
                    except Exception:
                       printExc()
                    try: 
                       age = ' [Age: '+str(item["display_age"])+']  ' 
                    except Exception:
                       printExc()
                    printDBG( 'Host phTitle: '+phTitle )
                    #printDBG( 'Host online: '+online )
                    printDBG( 'Host room: '+room )
                    phUrl = phTitle
                    if room != 'vip':
                       x += 1
                       valTab.append(CDisplayListItem(phTitle2+'   ['+bitrate.upper()+']',phTitle2+'  ('+phTitle+')   '+age+' ['+bitrate.upper()+']',CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
                 printDBG( 'Host ile: '+str(x) )
              except Exception:
                 printExc() 
           valTab.append(CDisplayListItem('Next', 'Page: '+str(self.page+1), CDisplayListItem.TYPE_CATEGORY, [next], name, '', 'Next'))                

           return valTab 

        if 'RUSPORN' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://rusporn.tv' 
           url = 'https://rusvidos.tv/index2.php'
           COOKIEFILE = os_path.join(GetCookieDir(), 'rusporn.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'category-list', '<div class="cls">', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)[<"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              printDBG( 'Host listsItems phUrl: '  +phUrl )
              printDBG( 'Host listsItems phTitle: '+phTitle )
              valTab.append(CDisplayListItem(phTitle,phUrl,CDisplayListItem.TYPE_CATEGORY, [phUrl+'?sort_by=post_date'],'RUSPORN-clips', '', phUrl)) 
           self.SEARCH_proc='RUSPORN-search'
           #valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           #valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'RUSPORN-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://rusvidos.tv/poisk/?q=%s' % url.replace(' ','+'), 'RUSPORN-clips')
           return valTab
        if 'RUSPORN-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getSearchGroups(data, '''class="next".*?from:(\d)"''', 1, True)[0] 
           data = data.split('class="item')
           if len(data): del data[0]
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if 'base64' in phImage:  phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phImage.startswith('//'): phImage = 'http:' + phImage
              Time = self.cm.ph.getSearchGroups(item, '''</i>([^>]+?)<''', 1, True)[0] 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time.strip()+']    '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              next_page = url.replace('&'+url.split('&')[-1],'')+'&from='+str(next)
              if '/search/' in url: next_page = url.replace('&'+url.split('&')[-1],'')+'&from_videos='+str(next)
              valTab.append(CDisplayListItem('Next', next_page.split('=')[-1], CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
           return valTab

        if 'PORN720' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://porn720.net' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'id="menu-menu', 'class="sub-header', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phTitle = self._cleanHtmlStr(item)
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              valTab.append(CDisplayListItem(phUrl.split('/')[-1],phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'PORN720-clips', '', phUrl)) 
           return valTab
        if 'PORN720-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           next = re.search('rel="next".*?href="(.*?)"', data, re.S)
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<figure', '</figure>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''clock-o"></i>([^>]+?)<''', 1, True)[0].strip()
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+']    '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              phUrl = next.group(1)
              valTab.append(CDisplayListItem('Next ', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [phUrl], name, '', catUrl))                
           return valTab

        if 'PORNTREX' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.porntrex.com' 
           self.format4k = config.plugins.iptvplayer.xxx4k.value
           COOKIEFILE = os_path.join(GetCookieDir(), 'porntrex.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE, 'return_data': True}
           sts, data = self.cm.getPage(url, self.defaultParams)
           if not sts: return valTab
           self.page = 0
           #printDBG( 'Host listsItems data: '+data )
           #data = self.cm.ph.getDataBeetwenMarkers(data, 'class="list-categories', 'footer', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="item"', '</a>')
           for item in data:
              #printDBG( 'Host item data: '+str(item) )
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phImage.startswith('//'): phImage = 'https:' + phImage
              try:
                 phImage = urlparser.decorateUrl(phImage, {'Referer': url})
              except: pass
              if phTitle:
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'PORNTREX-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           self.SEARCH_proc='PORNTREX-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'PORNTREX-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.porntrex.com/search/%s/' % url.replace(' ','+'), 'PORNTREX-clips')
           return valTab
        if 'PORNTREX-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           if catUrl == None: 
              self.page = 1
           else:
              self.page += 1
           if not '/search/' in url:
              url = url + '?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=post_date&from=%s' % self.page
           else:
              if self.page>1:
                 url = url + '?mode=async&function=get_block&block_id=list_videos_videos&q=dildo&category_ids=&sort_by=post_date&from_videos=%s&from_albums=%s' % (self.page, self.page)
           COOKIEFILE = os_path.join(GetCookieDir(), 'porntrex.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE, 'return_data': True}
           sts, data = self.cm.getPage(url, self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getSearchGroups(data, '''<li class="next"><a href="#videos".*?data-parameters="sort_by:post_date;from:([^"^']+?)['"]''', 1, True)[0]
           if not next:  next = self.cm.ph.getSearchGroups(data, '''<li class="next"><a href="#.*?from_albums:([^"^']+?)['"]''', 1, True)[0]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="video-', '</li></ul></div>')
           #printDBG( 'Host2 getResolvedURL data: '+str(data) )
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''fa-clock-o"></i>([^"^']+?)<''', 1, True)[0].strip()
              if phImage.startswith('//'): phImage = 'https:' + phImage
              try:
                 phImage = urlparser.decorateUrl(phImage, {'Referer': phUrl})
              except: pass
              if not '>Private<' in item:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+']    '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              valTab.append(CDisplayListItem('Next ', 'Page: '+next, CDisplayListItem.TYPE_CATEGORY, [url], name, '', 'next'))
           return valTab

        if 'PORNDOE' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://porndoe.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'porndoe.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return valTab
           printDBG( 'Nyers adat: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, '<div class="-holder-section">', '<div class="ctl-grid">', False)[1]
           printDBG( 'Host listsItems data: '+data )
           #for item in data:
           phTitle = self.cm.ph.getAllItemsBeetwenMarkers(data, '" title="', '">', False)
           printDBG( 'Kategoriak: '+str(data))
           phUrl = self.cm.ph.getAllItemsBeetwenMarkers(data, 'link" href="', '" title', False)
           #printDBG( 'Cimek: '+str(phUrl) )
           for i in phTitle:
               valTab.insert(0,CDisplayListItem(i,i,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl[phTitle.index(i)]],'PORNDOE-clips', '', None)) 
              #if phUrl:
                # valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'PORNDOE-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- By duration ---", "By duration", CDisplayListItem.TYPE_CATEGORY,['https://porndoe.com/videos?sort=duration-down'], 'PORNDOE-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most popular ---", "Most popular", CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos?sort=likes-down'], 'PORNDOE-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most viewed ---", "Most viewed", CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos?sort=views-down'], 'PORNDOE-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most recent ---", "Most recent", CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos'], 'PORNDOE-clips', '',None))
           self.SEARCH_proc='porndoe-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'porndoe-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://porndoe.com/search?keywords=%s' % url.replace(' ','+'), 'PORNDOE-clips')
           return valTab
        if 'PORNDOE-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           self.MAIN_URL = 'https://porndoe.com' 
           host = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
           COOKIEFILE = os_path.join(GetCookieDir(), 'porndoe.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return valTab
           printDBG( 'Ujabb adat: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, '<div class="videos-list', '<section class="-section -box-shadow-bottom">', False)[1]
           printDBG( 'Lekert info: ' +data)
           allTitle = self.cm.ph.getAllItemsBeetwenMarkers(data, '"video-item-title" target="_self" href="', '" ng-pop-under', False)
           printDBG( 'Minden cim: '+ str(allTitle))
           allUrl = self.cm.ph.getAllItemsBeetwenMarkers(data, '"video-item-title" target="_self" href="', '" title', False)
           allImage = self.cm.ph.getAllItemsBeetwenMarkers(data, 'viewBox="0 0 390 219" data-src="', '" data-first', False)
           allTime = self.cm.ph.getAllItemsBeetwenMarkers(data, 'data-duration="', '" data-vr', False)
           next = self.cm.ph.getDataBeetwenMarkers(data, "next' href='", "' />", False)[1]
           printDBG('Kovi: ' + next)
           for i in allUrl:
             phTitle = allTitle[allUrl.index(i)]
             phTitle = self.cm.ph.getDataBeetwenMarkers(phTitle, 'title="', phTitle[-4:-1], False)[1]
             printDBG( 'Cimek: ' +phTitle)
             phUrl   = allUrl[allUrl.index(i)]
             phUrl = self.MAIN_URL + phUrl
             printDBG( 'Linkek: ' +phUrl)
             phTime  = allTime[allUrl.index(i)]
             printDBG( 'Ido: ' +phTime)
             phImage = allImage[allUrl.index(i)]
             printDBG( 'Kepek: ' +phImage)
             #next = allnext[allUrl.index(i)]
             valTab.append(CDisplayListItem(phTitle,'['+phTime+']'+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
             valTab.append(CDisplayListItem('Next ', 'Page: '+next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))    
           return valTab

        if 'PORNFROMCZECH' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.pornfromczech.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornfromczech.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'pornfromczech.cookie', 'pornfromczech.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+str(data) )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li id="menu-item', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item) 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),phUrl,CDisplayListItem.TYPE_CATEGORY, [phUrl],'PORNFROMCZECH-clips', '', phUrl)) 
           self.SEARCH_proc='PORNFROMCZECH-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'PORNFROMCZECH-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://pornfromczech.com/?s=%s&x=0&y=0' % url.replace(' ','+'), 'PORNFROMCZECH-clips')
           return valTab              
        if 'PORNFROMCZECH-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornfromczech.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'pornfromczech.cookie', 'pornfromczech.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+str(data) )
           Movies = re.findall('<div\sclass="thumb">.*?<a\shref="(.*?)".*?title="(.*?)">.*?<img\ssrc="(.*?)".*?<p class="duration">(.*?)</p>', data, re.S) 
           if Movies:
              for (phUrl, phTitle, phImage, Time) in Movies:
                  Time = Time.strip()
                  phImage = urlparser.decorateUrl(phImage, {'Referer': url})
                  valTab.append(CDisplayListItem(decodeHtml(phTitle), '['+Time+']    '+decodeHtml(phTitle), CDisplayListItem.TYPE_CATEGORY, [phUrl], 'PORNFROMCZECH-serwer', phImage, decodeHtml(phTitle)))                
           match = re.search('rel="next" href="(.*?)"', data, re.S)
           if match:
              phUrl = match.group(1)
              valTab.append(CDisplayListItem('Next ', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [phUrl], name, '', None))                
           return valTab
        if 'PORNFROMCZECH-serwer' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornfromczech.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'pornfromczech.cookie', 'pornfromczech.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+str(data) )
           phserwer = ''
           phName = catUrl 
           data = ph.IFRAME.findall(data)
           for item in data:
              phUrl = self.cm.getFullUrl(item[1])
              phserwer = phUrl.split('/')[2]+' - '
              if 'exosrv' in phUrl: continue
              phUrl = urlparser.decorateUrl(phUrl, {'Referer': url})
              valTab.append(CDisplayListItem(phserwer+phName,phUrl,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, '', None)) 
           return valTab

        if 'FILMYPORNO' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.filmyporno.tv' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'filmyporno.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           #printDBG( 'Host listsItems data: '+data )
           #data = self.cm.ph.getDataBeetwenMarkers(data, '<h2>Kategorie', 'footer-top-col', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'item--channel col', '</div>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''img\ssrc=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'FILMYPORNO-clips', phImage, phUrl)) 
           valTab.insert(0,CDisplayListItem("--- NAJDŁUŻSZE ---",       "NAJDŁUŻSZE",                    CDisplayListItem.TYPE_CATEGORY,["http://www.filmyporno.tv/longest/"], 'FILMYPORNO-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- NAJCZĘŚCIEJ DYSKUTOWANE ---","NAJCZĘŚCIEJ DYSKUTOWANE", CDisplayListItem.TYPE_CATEGORY,["http://www.filmyporno.tv/most-discussed/"], 'FILMYPORNO-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- NAJLEPIEJ OCENIONE ---",     "NAJLEPIEJ OCENIONE",      CDisplayListItem.TYPE_CATEGORY,["http://www.filmyporno.tv/top-rated/"], 'FILMYPORNO-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- NAJPOPULARNIEJSZE ---",      "NAJPOPULARNIEJSZE",       CDisplayListItem.TYPE_CATEGORY,["http://www.filmyporno.tv/most-viewed/"], 'FILMYPORNO-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- NOWE FILMY ---",             "NOWE FILMY",              CDisplayListItem.TYPE_CATEGORY,["http://www.filmyporno.tv/videos/"], 'FILMYPORNO-clips', '',None))
           self.SEARCH_proc='FILMYPORNO-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'FILMYPORNO-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.filmyporno.tv/search/%s/' % url.replace(' ','+'), 'FILMYPORNO-clips')
           return valTab  
        if 'FILMYPORNO-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           COOKIEFILE = os_path.join(GetCookieDir(), 'filmyporno.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           #printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'rel="next"', '/>', False)[1]
           next_page = self.cm.ph.getSearchGroups(next_page, '''href=['"]([^"^']+?)['"]''')[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'item-col col', '</div>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''time">([^"^']+?)<''', 1, True)[0] 
              if phImage.startswith('//'): phImage = 'http:' + phImage
              Time = Time.strip()
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+']    '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              url = re.sub('page.+', '', url)
              valTab.append(CDisplayListItem('Next ', 'Page: '+url+next_page, CDisplayListItem.TYPE_CATEGORY, [url+next_page], name, '', None))                
           return valTab

        if 'CLIPHUNTER' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.cliphunter.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'cliphunter.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('id="submenu-categories">(.*?)</div>', data, re.S)
           if parse:
              phCats = re.findall('href="(/categories/.*?)".*?>(.*?)<', parse.group(1), re.S)
              if phCats:
                 for (phUrl, phTitle) in phCats:
                     phUrl = 'http://www.cliphunter.com%s/' % phUrl.replace(' ','%20')
                     if phTitle <> "More ... " and phTitle <> "HD": 
                        valTab.append(CDisplayListItem(decodeHtml(phTitle),phUrl,CDisplayListItem.TYPE_CATEGORY, [phUrl],'CLIPHUNTER-clips', '', phUrl)) 
           self.SEARCH_proc='CLIPHUNTER-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'CLIPHUNTER-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.cliphunter.com/search/%s' % url.replace(' ','+'), 'CLIPHUNTER-clips')
           return valTab
        if 'CLIPHUNTER-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           COOKIEFILE = os_path.join(GetCookieDir(), 'cliphunter.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           match = re.search('rel="next" href="(.*?)"', data, re.S)
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li mId=', '</li>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''vttl.*?">([^>]+?)<''', 1, True)[0].strip() 
              if not phTitle: phTitle = self._cleanHtmlStr(item).split('                    ')[4].strip()
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''pop-execute">([^>]+?)<''', 1, True)[0]
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              Time = Time.strip()
              phImage = urlparser.decorateUrl(phImage, {'Referer': url})
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+']    '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if match:
              next = match.group(1)
              if next.startswith('/'): next = self.MAIN_URL + next
              valTab.append(CDisplayListItem('Next ', 'Page: '+next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))                
           return valTab

        if 'EMPFLIX' == name:
           self.MAIN_URL = 'https://www.empflix.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'empflix.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return 
           #printDBG( 'Host listsItems data: '+data )
           genre = re.findall('"thumb"\shref="(.*?)".*?src="(.*?)".*?title="(.*?)"', data, re.S) 
           if genre:
              for (phUrl, phImage, phTitle) in genre:
                 phTitle = decodeHtml(phTitle).strip()
                 phImage = 'http:'+phImage
                 if not phTitle == "All": 
                    valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'EMPFLIX-clips', phImage, None)) 
           valTab.insert(0,CDisplayListItem("--- Featured ---",       "Featured",       CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/featured/?d=all&period=all"], 'EMPFLIX-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Popular ---",       "Most Popular",       CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/popular/?d=all&period=all"], 'EMPFLIX-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---",       "Top Rated",       CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/toprated/?d=all&period=all"], 'EMPFLIX-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- New ---",       "New",       CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/new/?d=all&period=all"], 'EMPFLIX-clips', '',None))
           self.SEARCH_proc='EMPFLIX-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'EMPFLIX-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.empflix.com/search.php?what=%s&tab=' % url.replace(' ','+'), 'EMPFLIX-clips')
           return valTab
        if 'EMPFLIX-clips' == name:
           COOKIEFILE = os_path.join(GetCookieDir(), 'empflix.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return valtab
           printDBG( 'Host listsItems data: '+data )
           match = re.findall('<a class="llNav".*?href="(.*?)"', data, re.S)
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'data-vid=', '</li>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''data-name=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phRuntime = self.cm.ph.getSearchGroups(item, '''videoDuration\'>([^>]+?)<''', 1, True)[0]
              Added = self.cm.ph.getSearchGroups(item, '''floatLeft\'>([^>]+?)<''', 1, True)[0]
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phTitle:
                 valTab.append(CDisplayListItem(phTitle,'['+phRuntime+'] '+phTitle+'\nAdded: '+ Added,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if match:
              phUrl = match[0]
              printDBG( 'Host listsItems page phUrl: '+phUrl )
              valTab.append(CDisplayListItem('Next', 'Page: '+phUrl.split('/')[-1].replace('?d=all',''), CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl], name, '', None))
           return valTab

        if 'THUMBZILLA' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.thumbzilla.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           Cats = re.findall('href="(/categories/.*?)".*?click\',\s\'(.*?)\'', data, re.S) 
           if Cats:
              for (phUrl, phTitle) in Cats:
                 phTitle = decodeHtml(phTitle)
                 if not phTitle == "All": 
                    valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'THUMBZILLA-clips', '', None)) 
           valTab.insert(0,CDisplayListItem("--- Homemade ---",     "Homemade",      CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/homemade"], 'THUMBZILLA-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- HD Videos ---","HD Videos", CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/hd"], 'THUMBZILLA-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Popular Videos ---",     "Popular Videos",      CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/popular"], 'THUMBZILLA-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top Videos ---",     "Top Videos",      CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/top"], 'THUMBZILLA-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Trending ---",     "Trending",      CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/trending"], 'THUMBZILLA-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Newest ---",     "Newest",      CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/newest"], 'THUMBZILLA-clips', '',None))
           self.SEARCH_proc='THUMBZILLA-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'THUMBZILLA-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.thumbzilla.com/tags/%s' % url.replace(' ','+'), 'THUMBZILLA-clips')
           return valTab          
        if 'THUMBZILLA-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.thumbzilla.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phMovies = re.findall('href="(/video/.*?)".*?src="(.*?)".*?"title">(.*?)<.*?"duration">(.*?)<', data, re.S)  
           if phMovies:
              for ( phUrl, phImage, phTitle, phRuntime) in phMovies:
                  if phUrl[:2] == "//":
                     phUrl = "http:" + phUrl
                  else:
                     phUrl = self.MAIN_URL + phUrl
                  if phImage[:2] == "//":
                     phImage = "http:" + phImage
                  valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phRuntime+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           match = re.findall('"next" href="(.*?)"', data, re.S)
           if match:
              phUrl = match[0]
              valTab.append(CDisplayListItem('Next', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [phUrl], name, '', None))
           self.MAIN_URL = '' 
           return valTab

        if 'ADULTTV' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.adulttvlive.net' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'adulttv.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'adulttv.cookie', 'adulttv.net', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data1: '+data )
           next_page = self.cm.ph.getSearchGroups(data, '''<link\s*rel=['"]next['"]\s*href=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<article', '</article>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phTitle: phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phImage.startswith('/'): phImage = 'http://www.adulttvlive.net' + phImage
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = 'http://www.adulttvlive.net' + phUrl
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           catUrl = self.currList[Index].possibleTypesOfSearch
           #if catUrl == None:
           #   valTab.insert(0,CDisplayListItem('BSX24','BSX24',CDisplayListItem.TYPE_VIDEO, [CUrlItem('', 'http://publish.thewebstream.co:1935/bsx24/livestream/playlist.m3u8', 0)], 0, 'http://ero-tv.org/wp-content/uploads/2014/08/babestation24.gif', None)) 
           #   valTab.insert(0,CDisplayListItem('PassionXXX','PassionXXX',CDisplayListItem.TYPE_VIDEO, [CUrlItem('', 'http://publish.thewebstream.co:1935/ppv/_definst_/rampanttv_passionxxx/playlist.m3u8', 0)], 0, 'https://pbs.twimg.com/profile_images/1001362356264464384/fQVOhNLk_400x400.jpg', None)) 

           if next_page:
              valTab.append(CDisplayListItem('Next', 'Page: '+next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', 'next'))
           return valTab

        if 'YUVUTU' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.yuvutu.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           self.page = 1
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="yv-element', 'videos</span>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              phTitle = re.sub(' - .+', '', phTitle)
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'YUVUTU-clips', phImage, None)) 
           return valTab
        if 'YUVUTU-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           self.page += 1
           phMovies = re.findall('class="thumb-image">.*?href="(.*?)".*?src="(.*?)".*?title="(.*?)"', data, re.S)  
           if phMovies:
              for ( phUrl, phImage, phTitle ) in phMovies:
                  phTitle = phTitle.replace(' - ','')
                  valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+phUrl, 1)], 0, phImage, None)) 
           url = re.sub('page.+', '', url)
           valTab.append(CDisplayListItem('Next', 'Page: '+str(self.page), CDisplayListItem.TYPE_CATEGORY, [url+'page/'+str(self.page)+'/'], name, '', None))
           return valTab

        if 'PORNICOM' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://pornicom.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornicom.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return valtab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, '<div class="items-list">', 'footer', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="item">', 'quantity')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'PORNICOM-clips', phImage, None))
           valTab.insert(0,CDisplayListItem("--- Most popular ---", "Most popular", CDisplayListItem.TYPE_CATEGORY,['http://www.pornicom.com/most-popular/'], 'PORNICOM-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Latest updates ---", "Latest updates", CDisplayListItem.TYPE_CATEGORY,['http://www.pornicom.com/latest-updates/'], 'PORNICOM-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top rated ---", "Top rated", CDisplayListItem.TYPE_CATEGORY,['http://www.pornicom.com/top-rated/'], 'PORNICOM-clips', '',None))
           self.SEARCH_proc='pornicom-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'pornicom-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.pornicom.com/search/?q=%s' % url.replace(' ','+'), 'PORNICOM-clips')
           return valTab
        if 'PORNICOM-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://pornicom.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornicom.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return valtab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'pagination', '</div>', False)[1]
           next_page = self.cm.ph.getDataBeetwenMarkers(next_page, '</span>', 'Page', False)[1]
           next_page = self.cm.ph.getSearchGroups(next_page, '''href=['"]([^"^']+?)['"]''')[0] 
           if next_page.startswith('/'): next_page = self.MAIN_URL + next_page
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="link"', 'views-info')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''<img\sclass="thumb"\ssrc=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''"duration">([^"^']+?)<''', 1, True)[0].strip()
              if not Time: Time = self.cm.ph.getSearchGroups(item, '''"duration" content=['"]([^"^']+?)['"]''', 1, True)[0].strip()
              phImage = urlparser.decorateUrl(phImage, {'Referer': url})
              valTab.append(CDisplayListItem(phTitle,'['+Time+']   '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page: 
              numer = next_page.split('/')[-2]
              valTab.append(CDisplayListItem('Next', 'Next '+numer, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
           return valTab

        if 'HDZOG' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.hdzog.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'hdzog.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           #printDBG( 'Host getResolvedURL data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'class="thumbs-categories">', 'video thumbs list', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''"title">([^"^']+?)<''', 1, True)[0]
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'HDZOG-clips', phImage, None))
           valTab.insert(0,CDisplayListItem("--- Longest ---", "Longest", CDisplayListItem.TYPE_CATEGORY,['http://www.hdzog.com/longest/'], 'HDZOG-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Popular ---", "Popular", CDisplayListItem.TYPE_CATEGORY,['http://www.hdzog.com/popular/'], 'HDZOG-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Newest ---", "Newest", CDisplayListItem.TYPE_CATEGORY,['http://www.hdzog.com/new/'], 'HDZOG-clips', '',None))
           self.SEARCH_proc='hdzog-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'hdzog-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://hdzog.com/search/%s/' % url.replace(' ','+'), 'HDZOG-clips')
           return valTab
        if 'HDZOG-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'hdzog.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           #printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'class="next">', '</li>', False)[1]
           next_page = self.cm.ph.getSearchGroups(next_page, '''href=['"]([^"^']+?)['"]''')[0] 
           if next_page.startswith('/'): next_page = 'http://www.hdzog.com' + next_page
           data = self.cm.ph.getDataBeetwenMarkers(data, 'class="thumbs-videos">', 'video thumbs list', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a href', '</a>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''class="time">([^"^']+?)<''', 1, True)[0] 
              valTab.append(CDisplayListItem(phTitle,'['+Time+']   '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page: 
              numer = next_page.split('/')[-2]
              valTab.append(CDisplayListItem('Next', 'Next '+numer, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
           return valTab

        if 'PORNOMENGE' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.pornomenge.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornomenge.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'pornomenge.cookie', 'pornomenge.com', self.defaultParams)
           if not sts: return ''
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="wrap-box-escena">', '</h4>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phTitle: phTitle = self.cm.ph.getSearchGroups(item, '''">([^"^']+?)</a>''', 1, True)[0]
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'PORNOMENGE-clips', '', None))
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Kanale ---", "Kanale", CDisplayListItem.TYPE_CATEGORY,['https://www.pornomenge.com/websites/videos/'], 'PORNOMENGE-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Pornostars ---", "Pornostars", CDisplayListItem.TYPE_CATEGORY,['https://www.pornomenge.com/pornostars/'], 'PORNOMENGE-Pornostars', '',None))
           valTab.insert(0,CDisplayListItem("--- Beste Videos ---", "Beste Videos", CDisplayListItem.TYPE_CATEGORY,['https://www.pornomenge.com/am-meisten-gestimmt/m/'], 'PORNOMENGE-clips', '',None))
           self.SEARCH_proc='PORNOMENGE-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'PORNOMENGE-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.heuteporno.com/suchen/?q=%s' % url.replace(' ','+'), 'PORNOMENGE-clips')
           return valTab
        if 'PORNOMENGE-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornomenge.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'pornomenge.cookie', 'pornomenge.com', self.defaultParams)
           if not sts: return ''
           #printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getSearchGroups(data, '''data-ajax-url=['"]([^"^']+?)['"]''')[0] 
           if next_page.startswith('/'): next_page = self.MAIN_URL + next_page
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="wrap-box-escena">', 'class="votar-escena')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''duracion">([^"^']+?)<''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+']   '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              if next_page.startswith('aHR'): next_page = urllib.unquote(base64.b64decode(next_page))
              if '/?page=0' in next_page: next_page = next_page.replace('page=0','page=2')
              numer = next_page.split('=')[-1]
              valTab.append(CDisplayListItem('Next', 'Next '+numer, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
           return valTab
        if 'PORNOMENGE-Pornostars' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornomenge.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'pornomenge.cookie', 'pornomenge.com', self.defaultParams)
           if not sts: return ''
           #printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'rel="next"', '/>', False)[1]
           next_page = self.cm.ph.getSearchGroups(next_page, '''href=['"]([^"^']+?)['"]''')[0] 
           if next_page.startswith('/'): next_page = self.MAIN_URL + next_page
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="wrap-box-chica">', 'class="clear"></div>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''duracion">([^"^']+?)<''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'PORNOMENGE-clips', '', None))
           if next_page: 
              numer = next_page.split('=')[-1]
              valTab.append(CDisplayListItem('Next', 'Next '+numer, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
           return valTab

        if 'TUBEPORNCLASSIC' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://tubepornclassic.com' 
           url = 'https://tubepornclassic.com/api/json/categories/14400/str.all.json'
           COOKIEFILE = os_path.join(GetCookieDir(), 'tubepornclassic.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'tubepornclassic.cookie', 'tubepornclassic.com', self.defaultParams)
           if not sts: return valTab
           self.page=1
           printDBG( 'Host data:%s' % data )
           try:
              result = byteify(simplejson.loads(data))
              for item in result["categories"]:
                 phUrl = 'https://tubepornclassic.com/api/json/videos/86400/str/latest-updates/60/categories.%s.%s.all..day.json'  % (str(item["dir"]), str(self.page))
                 phTitle = str(item["title"])
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'TUBEPORNCLASSIC-clips', '', None)) 
           except Exception:
              printExc()
           valTab.sort(key=lambda poz: poz.name)
           self.SEARCH_proc='TUBEPORNCLASSIC-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'TUBEPORNCLASSIC-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://tubepornclassic.com/api/videos.php?params=86400/str/relevance/60/search..1.all..day&s=%s' % url.replace(' ','+'), 'TUBEPORNCLASSIC-clips')
           return valTab
        if 'TUBEPORNCLASSIC-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://tubepornclassic.com' 
           catUrl = self.currList[Index].possibleTypesOfSearch
           printDBG( 'Host listsItems cat-url: '+str(catUrl) )
           next = url
           if catUrl == None: 
              self.page = 1
           else:
              self.page += 1
           COOKIEFILE = os_path.join(GetCookieDir(), 'tubepornclassic.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'tubepornclassic.cookie', 'tubepornclassic.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           try:
              result = byteify(simplejson.loads(data))
              for item in result["videos"]:
                 phTitle = str(item["title"])
                 video_id = str(item["video_id"])
                 scr = str(item["scr"])
                 phUrl = "https://tubepornclassic.com/api/videofile.php?video_id=%s&lifetime=8640000" % video_id
                 phTime = str(item["duration"])
                 added = str(item["post_date"])
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle)+'\nAdded: '+added,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, scr, None)) 
           except Exception:
              printExc()
           next_page = url.replace('.'+str(self.page)+'.','.'+str(self.page+1)+'.')
           valTab.append(CDisplayListItem('Next', 'Page: '+str(self.page+1), CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', 'next'))                
           return valTab

        if 'KOLOPORNO' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.koloporno.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'koloporno.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'koloporno.cookie', 'koloporno.com', self.defaultParams)
           if not sts: return ''
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="wrap-box-escena">', '</h4>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phTitle: phTitle = self.cm.ph.getSearchGroups(item, '''">([^"^']+?)</a>''', 1, True)[0]
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'KOLOPORNO-clips', '', None))
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Pornstars ---", "Pornstars", CDisplayListItem.TYPE_CATEGORY,['https://www.koloporno.com/pornstars/'], 'KOLOPORNO-Pornostars', '',None))
           valTab.insert(0,CDisplayListItem("--- Najlepsze Filmy ---", "Najlepsze Filmy", CDisplayListItem.TYPE_CATEGORY,['https://www.koloporno.com/najlepiej-oceniane/m/'], 'KOLOPORNO-clips', '',None))
           self.SEARCH_proc='KOLOPORNO-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'KOLOPORNO-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.koloporno.com/search/?q=%s' % url.replace(' ','+'), 'KOLOPORNO-clips')
           return valTab
        if 'KOLOPORNO-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.koloporno.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'koloporno.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'koloporno.cookie', 'koloporno.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getSearchGroups(data, '''data-ajax-url=['"]([^"^']+?)['"]''')[0] 
           if next_page.startswith('/'): next_page = self.MAIN_URL + next_page
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="wrap-box-escena">', 'class="votar-escena')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''duracion">([^"^']+?)<''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+']   '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              if next_page.startswith('aHR'): next_page = urllib.unquote(base64.b64decode(next_page))
              if '/?page=0' in next_page: next_page = next_page.replace ('page=0','page=2')
              numer = next_page.split('=')[-1]
              valTab.append(CDisplayListItem('Next', 'Next '+numer, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
           return valTab
        if 'KOLOPORNO-Pornostars' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'koloporno.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'koloporno.cookie', 'koloporno.com', self.defaultParams)
           if not sts: return ''
           #printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'rel="next"', '/>', False)[1]
           next_page = self.cm.ph.getSearchGroups(next_page, '''href=['"]([^"^']+?)['"]''')[0] 
           if next_page.startswith('/'): next_page = self.MAIN_URL + next_page
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="wrap-box-chica">', 'class="clear"></div>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''duracion">([^"^']+?)<''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'KOLOPORNO-clips', '', None))
           if next_page: 
              numer = next_page.split('/')[-1]
              valTab.append(CDisplayListItem('Next', 'Next '+numer, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
           return valTab

        if 'REALGFPORN' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.realgfporn.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="video-spot">', 'clearfix')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'REALGFPORN-clips', phImage, None))
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Longest ---", "Longest", CDisplayListItem.TYPE_CATEGORY,['https://www.realgfporn.com/longest/'], 'REALGFPORN-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Viewed ---", "Most Viewed", CDisplayListItem.TYPE_CATEGORY,['https://www.realgfporn.com/most-viewed/'], 'REALGFPORN-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---", "Top Rated", CDisplayListItem.TYPE_CATEGORY,['https://www.realgfporn.com/top-rated/'], 'REALGFPORN-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Recent ---", "Most Recent", CDisplayListItem.TYPE_CATEGORY,['https://www.realgfporn.com/most-recent/'], 'REALGFPORN-clips', '',None))
           self.SEARCH_proc='REALGFPORN-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'REALGFPORN-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.realgfporn.com/search/%s/page1.html' % url.replace(' ','+'), 'REALGFPORN-clips')
           return valTab
        if 'REALGFPORN-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.realgfporn.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'pagination', 'Next', False)[1]
           next_page = re.compile('href="(.*?)"').findall(next_page)
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="video-spot', '</strong>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](https://www.realgfporn.com/videos/[^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0].replace(' ','%20') 
              Time = self.cm.ph.getSearchGroups(item, '''duration">([^"^']+?)<''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if Time<>'Link' and phUrl:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+']   '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page: 
              url = re.sub('page.+', '', url)
              valTab.append(CDisplayListItem('Next', url+next_page[-1], CDisplayListItem.TYPE_CATEGORY, [url+next_page[-1]], name, '', None))
           return valTab

        if 'PLAYVIDS' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.playvids.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'playvids.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'playvids.cookie', 'playvids.com', self.defaultParams)
           if not sts: return ''
           if 'Rate Limit Exceeded' in data:
              msg = _("Last error:\n%s" % 'Rate Limit Exceeded')
              GetIPTVNotify().push('%s' % msg, 'error', 20)
           printDBG( 'Host listsItems data: '+str(data) )
           data = self.cm.ph.getDataBeetwenMarkers(data, '<div class="category-list', 'card-promotion', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = phUrl.split('/')[-1].replace('-',' ').replace('%20',' ').replace('%26','-')
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0].replace(' ','%20') 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('/'): phImage = self.MAIN_URL + phImage
              if phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'PLAYVIDS-clips', phImage, None))
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Pornstar ---", "Pornstar", CDisplayListItem.TYPE_CATEGORY,['https://www.playvids.com/pornstars&jsclick=1'], 'PLAYVIDS-pornstar', '',None))
           valTab.insert(0,CDisplayListItem("--- Channels ---", "Channels", CDisplayListItem.TYPE_CATEGORY,['https://www.playvids.com/channels&jsclick=1'], 'PLAYVIDS-channels', '',None))
           valTab.insert(0,CDisplayListItem("--- Trending ---", "Trending", CDisplayListItem.TYPE_CATEGORY,['https://www.playvids.com/Trending-Porn'], 'PLAYVIDS-clips', '',None))
           self.SEARCH_proc='PLAYVIDS-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'PLAYVIDS-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.playvids.com/sq?q=%s&jsclick=1&content=straight' % url.replace(' ','+'), 'PLAYVIDS-clips')
           return valTab
        if 'PLAYVIDS-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.playvids.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'playvids.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'playvids.cookie', 'playvids.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+str(data) )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'class="pagination"', '</ul>', False)[1]
           catUrl = self.currList[Index].possibleTypesOfSearch
           if catUrl == 'channels':
              data = data.split('<div id=')
           else:
              data = data.split('<div class="card thumbs_rotate')
           if len(data): del data[0]
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0].replace(' ','%20') 
              Time = self.cm.ph.getSearchGroups(item, '''duration">([^"^']+?)<''', 1, True)[0] 
              added = self.cm.ph.getSearchGroups(item, '''addition">([^"^']+?)<''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phTitle and Time:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+']  '+decodeHtml(phTitle)+'\n'+added,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page: 
              match = re.compile('href="(.*?)"').findall(next_page)
              if match:
                 next_page = self.MAIN_URL+match[-1]
                 printDBG( 'Host listsItems next_page: '  +next_page )
                 valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
           return valTab
        if 'PLAYVIDS-channels' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.playvids.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'playvids.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'playvids.cookie', 'playvids.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+str(data) )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'class="pagination"', '</ul>', False)[1]
           #data = self.cm.ph.getDataBeetwenMarkers(data, 'Popular channels', 'pagination', False)[1]
           #data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="card">', '</div>')
           data = data.split('<div class="card">')
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].replace('%20',' ').replace('%26','-') 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0].replace(' ','%20') 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('/'): phImage = self.MAIN_URL + phImage
              if phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'PLAYVIDS-clips', phImage, 'channels'))
           if next_page: 
              match = re.compile('href="(.*?)"').findall(next_page)
              if match:
                 next_page = self.MAIN_URL+match[-1]
                 printDBG( 'Host listsItems next_page: '  +next_page )
                 valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
           return valTab
        if 'PLAYVIDS-pornstar' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.playvids.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'playvids.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'playvids.cookie', 'playvids.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+str(data) )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'class="pagination"', '</ul>', False)[1]
           #data = self.cm.ph.getDataBeetwenMarkers(data, '<ul class="stars_list">', '</ul>', False)[1]
           #data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           data = data.split('<div class="card">')
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = phUrl.split('/')[-1].replace('-',' ')
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0].replace(' ','%20') 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('/'): phImage = self.MAIN_URL + phImage
              if phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'PLAYVIDS-clips', phImage, None))
           if next_page: 
              match = re.compile('href="(.*?)"').findall(next_page)
              if match:
                 next_page = self.MAIN_URL+match[-1]
                 printDBG( 'Host listsItems next_page: '  +next_page )
                 valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
           return valTab

        if '4TUBE' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.4tube.com'
           COOKIEFILE = os_path.join(GetCookieDir(), '4tube.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, '>Categories<', '>Channels<', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0].lower().replace('sex movies','')
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phTitle:
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'4TUBE-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Channels ---","Channels",   CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/channels"]  ,         '4TUBE-channels', '',None))
           valTab.insert(0,CDisplayListItem("--- Pornstars ---","Pornstars", CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/pornstars"],          '4TUBE-channels','',None))
           valTab.insert(0,CDisplayListItem("--- Most viewed ---","Most viewed",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/videos?sort=views&time=month"],             '4TUBE-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Highest Rated ---","Highest Rated", CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/videos?sort=rating&time=month"],             '4TUBE-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Lastest ---","Lastest",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/videos"],             '4TUBE-clips',    '',None))
           self.SEARCH_proc='4TUBE-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if '4TUBE-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, self.MAIN_URL+'/search?q=%s' % url.replace(' ','+'), '4TUBE-clips')
           return valTab              
        if '4TUBE-channels' == name:
           COOKIEFILE = os_path.join(GetCookieDir(), '4tube.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getSearchGroups(data, '''<link\srel="next"\shref=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a class="thumb-link"', '</div></a></div>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phVid = self.cm.ph.getSearchGroups(item, '''icon-video"></i>([^"^']+?)<''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''img\sdata-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,'[Video: '+phVid+']   '+phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl], '4TUBE-clips', phImage, None)) 
           if next_page:
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab
        if '4TUBE-clips' == name:
           COOKIEFILE = os_path.join(GetCookieDir(), '4tube.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           self.MAIN_URL = url.split('com/')[0]+'com'
           next_page = self.cm.ph.getSearchGroups(data, '''<link\srel="next"\shref=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="col thumb_video"', '</div></div>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''img data-master=['"]([^"^']+?)['"]''', 1, True)[0] 
              phRuntime = self.cm.ph.getSearchGroups(item, '''"duration-top">([^"^']+?)<''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phRuntime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'HomeMoviesTube' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.homemoviestube.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'homemoviestube.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE, 'return_data': True}
           sts, data = self.cm.getPage(url, self.defaultParams)
           if not sts: return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = data.split('class="category-item ')
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phImage.startswith('/'): phImage = self.MAIN_URL + phImage
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'HomeMoviesTube-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Longest ---","Longest", CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/longest/"],          'HomeMoviesTube-clips','',None))
           valTab.insert(0,CDisplayListItem("--- Most viewed ---","Most viewed",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/most-viewed/"],             'HomeMoviesTube-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated", CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/top-rated/"],             'HomeMoviesTube-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Most Recent ---","Most Recent",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/most-recent/"],             'HomeMoviesTube-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Latest Videos ---","Latest Videos",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL],             'HomeMoviesTube-clips',    '',None))
           self.SEARCH_proc='HomeMoviesTube-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'HomeMoviesTube-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, self.MAIN_URL+'/search/%s/page1.html' % url.replace(' ','+'), 'HomeMoviesTube-clips')
           return valTab              
        if 'HomeMoviesTube-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.homemoviestube.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'homemoviestube.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE, 'return_data': True}
           sts, data = self.cm.getPage(url, self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getSearchGroups(data, '''<li\sclass='next'><a href=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = data.split('class="film-item ')
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0].replace(' ','%20')
              phRuntime = self.cm.ph.getSearchGroups(item, '''"film-time">([^"^']+?)<''', 1, True)[0]
              added = self.cm.ph.getSearchGroups(item, '''"stat-added">([^"^']+?)<''', 1, True)[0] 
              views = self.cm.ph.getSearchGroups(item, '''views">([^>]+?)<''', 1, True)[0].strip()
              rated = self.cm.ph.getSearchGroups(item, '''rated">([^>]+?)<''', 1, True)[0].strip()
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phImage.startswith('/'): phImage = self.MAIN_URL + phImage
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,'['+phRuntime+']  '+phTitle+'\n'+views+'\n'+rated,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              if next_page.startswith('page'): next_page = '/' + next_page
              next_page = re.sub('page.+', '', url)+next_page
              valTab.append(CDisplayListItem(_("Next page"), next_page.split('/')[-1].replace('.html',''), CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'MOVIEFAP' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.moviefap.com'
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'Categories</h1>', '</ul>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item) 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'MOVIEFAP-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Most Recent ---","Most Recent",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/browse/?category=mr&page="],             'MOVIEFAP-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated", CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/browse/?category=tr&page="],             'MOVIEFAP-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Being Watched ---","Being Watched",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/browse/?category=bw&page="],             'MOVIEFAP-clips',    '',None))
           self.SEARCH_proc='MOVIEFAP-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'MOVIEFAP-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, self.MAIN_URL+'/search/%s' % url.replace(' ','+'), 'MOVIEFAP-clips')
           return valTab              
        if 'MOVIEFAP-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.moviefap.com'
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getDataBeetwenMarkers(data, 'class="current"', 'next', False)[1]
           next_page = self.cm.ph.getSearchGroups(next, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="video', '</div></div>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''img\ssrc=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              phRuntime = self.cm.ph.getSearchGroups(item, '''"videoleft">([^"^']+?)<''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,'['+phRuntime+']  '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              if next_page.startswith('/'): next_page = self.MAIN_URL + next_page
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'yourporn' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://sxyprn.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'yourporn.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self._getPage(url, self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+str(data) )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, "<a class='tdn'", '</a>')
           for item in data:
              #printDBG( 'Host listsItems item: '+str(item) )
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''>#([^#]+?)<''', 1, True)[0]
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = 'https://sxyprn.com' + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'yourporn-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Top Viewed ---","Top Viewed",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/popular/top-viewed.html"],             'yourporn-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated", CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/popular/top-rated.html"],             'yourporn-clips',    '',None))
           self.SEARCH_proc='yourporn-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'yourporn-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://sxyprn.com/%s.html' % url.replace(' ','+'), 'yourporn-clips')
           return valTab              
        if 'yourporn-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://sxyprn.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'yourporn.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self._getPage(url, self.defaultParams)
           if not sts: return 
           printDBG( 'Host listsItems data: '+str(data) )
           next_page = self.cm.ph.getSearchGroups(data, '''<link rel='next' href=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = data.split('data-postid=')
           for item in data:
              #printDBG( 'Host listsItems item: '+str(item) )
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](/post/[^"^']+?)['"]''', 1, True)[0] 
              if not phUrl: phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](http[^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"](//[^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''html\'\stitle=['"]([^"^']+?)['"]''', 1, True)[0]
              printDBG( 'Host phTitle1: '+phTitle )
              if len(phTitle)<4: phTitle = self.cm.ph.getSearchGroups(item, '''data-title=['"]([^"^'^{]+?)['"}]''', 1, True)[0]
              if len(phTitle)<4: phTitle = self.cm.ph.getSearchGroups(item, '''class=\'tdn\'\stitle=['"]([^"^'^{]+?)['"}]''', 1, True)[0]
              printDBG( 'Host phTitle2: '+phTitle )
              if ' porn blog' in phTitle or len(phTitle)<4: phTitle = self.cm.ph.getSearchGroups(item, '''blog">([^"^']+?)<''', 1, True)[0] 
              printDBG( 'Host phTitle3: '+phTitle )
              if len(phTitle)<4: phTitle = self.cm.ph.getSearchGroups(item, '''title\'>([^>]+?)<''', 1, True)[0]
              printDBG( 'Host phTitle4: '+phTitle )
              if len(phTitle)<4: phTitle = self.cm.ph.getSearchGroups(item, '''text_el">([^>]+?)<''', 1, True)[0]
              printDBG( 'Host phTitle5: '+phTitle )
              #if len(phTitle)<4: phTitle = 'No Title'
              phRuntime = self.cm.ph.getSearchGroups(item, '''>(\d\d:\d\d)<''', 1, True)[0] 
              if not phRuntime: phRuntime = self.cm.ph.getSearchGroups(item, '''>(\d\d:\d\d:\d\d)<''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = 'https://sxyprn.com' + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              phTitle = phTitle.replace('\n','')
              Title = phTitle[:95].split('#')[0]
              if 'External Link' in item:
                 phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](https?://gounlimited[^"^']+?)['"]''', 1, True)[0]
                 phRuntime = 'External Link'
                 Title = re.sub(r'http(.*?)mp4', '', Title)
                 Title = re.sub(r'http(.*?) ', '', Title)
                 if 'gounlimited.to' in phUrl:
                    if not 'embed' in phUrl:
                       phUrl = 'https://gounlimited.to' + '/embed-'+ phUrl.split('/')[3] +'.html'
              if phRuntime=='': continue 
              printDBG( 'Host phTitle6: '+phTitle )
              printDBG( 'Host phUrl: '+phUrl )
              printDBG( 'Host phImage: '+phImage )
              if phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(Title),'['+phRuntime+']  '+decodeHtml(phTitle[:95]),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              if next_page.startswith('/'): next_page = self.MAIN_URL + next_page
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'freeomovie' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.freeomovie.to/'
           COOKIEFILE = os_path.join(GetCookieDir(), 'freeomovie.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage4k(url, 'freeomovie.cookie', 'freeomovie.to', self.defaultParams)
           if not sts: return ''
           #printDBG( 'Host listsItems data: '+str(data) )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'Categories<', '</div>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item) 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'freeomovie-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Newest ---","Newest",     CDisplayListItem.TYPE_CATEGORY,['https://www.freeomovie.to'],             'freeomovie-clips',    '',None))
           self.SEARCH_proc='freeomovie-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'freeomovie-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.freeomovie.to/?s=%s' % url.replace(' ','+'), 'freeomovie-clips')
           return valTab              
        if 'freeomovie-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.freeomovie.to/'
           COOKIEFILE = os_path.join(GetCookieDir(), 'freeomovie.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage4k(url, 'freeomovie.cookie', 'freeomovie.to', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+str(data) )
           next_page = self.cm.ph.getSearchGroups(data, '''<link\s*rel=['"]next['"]\s*href=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="boxtitle">', 'class="metargt">')
           for item in data:
              #printDBG( 'Host listsItems item: '+str(item) )
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('/'): phImage = 'http:' + phImage
              phImage = urlparser.decorateUrl(phImage, {'Referer': url})
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [ phUrl], 'freeomovie-serwer', phImage, phImage)) 
           if next_page:
              if next_page.startswith('/'): next_page = self.MAIN_URL + next_page
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab
        if 'freeomovie-serwer' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           COOKIEFILE = os_path.join(GetCookieDir(), 'freeomovie.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage4k(url, 'freeomovie.cookie', 'freeomovie.to', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+str(data) )
           Title = self.cm.ph.getSearchGroups(data, '''"headline":['"]([^"^']+?)['"&]''', 1, True)[0] 
           if not Title: Title = self.cm.ph.getSearchGroups(data, '''<title>([^>]+?)<''', 1, True)[0]
           data = self.cm.ph.getDataBeetwenMarkers(data, '<div id="videocont"', '</div>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           printDBG( 'Elemek: '+str(data) )
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''(http[^"^']+?)['"&]''', 1, True)[0] 
              printDBG( 'Elso trukk: '+ phUrl )
              phTitle = phUrl.split('/')[2]
              printDBG( 'harmadik trukk: '+ phTitle )
              if phTitle=='': phTitle=phUrl
              printDBG( 'Ez a vege:: '+ phUrl )
              phUrl = urlparser.decorateUrl(phUrl, {'Referer': url})
              printDBG( 'Parser utan: '+ phUrl )
              if not 'filecrypt' in phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(Title)+' > '+phTitle,decodeHtml(Title)+' > '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, catUrl, None)) 

        if 'KATESTUBE' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.katestube.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'katestube.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           #data = self.cm.ph.getDataBeetwenMarkers(data, 'class="thumbs-list">', 'footer', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="thumb">', '</div>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''img src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'KATESTUBE-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Most Popular ---","Most Popular",     CDisplayListItem.TYPE_CATEGORY,['https://www.katestube.com/most-popular/'],             'KATESTUBE-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,['https://www.katestube.com/top-rated/'],             'KATESTUBE-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Latest ---","Latest",     CDisplayListItem.TYPE_CATEGORY,['https://www.katestube.com/latest-updates/'],             'KATESTUBE-clips',    '',None))
           self.SEARCH_proc='KATESTUBE-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'KATESTUBE-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.katestube.com/search/?q=%s' % url.replace(' ','+'), 'KATESTUBE-clips')
           return valTab              
        if 'KATESTUBE-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'katestube.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = ph.findall(data, '<a data=', 'Next') 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="thumb"', '</div>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''<img\ssrc=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''duration" class="length">([^"^']+?)<''', 1, True)[0].strip()
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('/'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(phTitle,'['+phTime+']  '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              next = self.cm.ph.getSearchGroups(next_page[-1], '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if next.startswith('/'): next = 'https://www.katestube.com' + next
              valTab.append(CDisplayListItem('Next', next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))                
           return valTab

        if 'ZBIORNIKMINI' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://mini.zbiornik.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'zbiornikmini.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           data2 = self.cm.ph.getDataBeetwenMarkers(data, '<div class="collapse navbar-collapse" id="photos-menu">', '</div>', False)[1]
           data2 = self.cm.ph.getAllItemsBeetwenMarkers(data2, '<a href=', '</a>')
           for item in data2:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item)
              if phUrl.startswith('/'): phUrl = 'https://mini.zbiornik.com' + phUrl
              printDBG( 'Host phTitle: '+phTitle )
              printDBG( 'Host phUrl: '+phUrl )
              if len(phUrl)>3:
                 if phTitle<>'2004' and phTitle<>'2005' and phTitle<>'2006':
                    valTab.append(CDisplayListItem(phTitle,phUrl.split('/')[-1],     CDisplayListItem.TYPE_CATEGORY,[phUrl],'ZBIORNIKMINI-filmy','https://static.zbiornik.com/upimg/0160d9c44a354d20e81f0e6df5fe832e.jpg',None))
           valTab.insert(0,CDisplayListItem("--- Ranking ---","Ranking",     CDisplayListItem.TYPE_CATEGORY,['https://mini.zbiornik.com/ludzie/ranking'],             'ZBIORNIKMINI-ranking',    '',None))
           valTab.insert(0,CDisplayListItem("--- Wyświetl profile ---","Wyświetl profile",     CDisplayListItem.TYPE_CATEGORY,['https://mini.zbiornik.com/ludzie/szukaj/0,1,1,1,0,1:0:0:0:18:50:2:0:0:1:0'],             'ZBIORNIKMINI-szukaj',    '',None))
           data2 = None
           return valTab    
        if 'ZBIORNIKMINI-szukaj' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'zbiornikmini.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, '<ul class="pager">', '</ul>', False)[1]
           if next_page:
              next_page = re.compile('href="(.*?)"').findall(next_page)
              if next_page[-1].startswith('/'): next_page = 'https://mini.zbiornik.com' + next_page[-1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="search-profile-box">', '</h5>')
           for item in data:
              phImage = self.cm.ph.getSearchGroups(item, '''url\(['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?filmy)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item) 
              if phUrl.startswith('/'): phUrl = 'https://mini.zbiornik.com' + phUrl
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl], 'ZBIORNIKMINI-filmy', phImage, None)) 
           if next_page:
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))  
           return valTab
        if 'ZBIORNIKMINI-ranking' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'zbiornikmini.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, '<ul class="pager">', '</ul>', False)[1]
           if next_page:
              next_page = re.compile('href="(.*?)"').findall(next_page)
              if next_page[-1].startswith('/'): next_page = 'https://mini.zbiornik.com' + next_page[-1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="panel-body">', '</h3>')
           for item in data:
              phImage = self.cm.ph.getSearchGroups(item, '''url\(['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item) 
              if phUrl.startswith('/'): phUrl = 'https://mini.zbiornik.com' + phUrl +'/filmy'
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl], 'ZBIORNIKMINI-filmy', phImage, None)) 
           if next_page:
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))  
           return valTab
        if 'ZBIORNIKMINI-filmy' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'zbiornikmini.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, '<ul class="pager">', '</ul>', False)[1]
           if next_page:
              next_page = re.compile('href="(.*?)"').findall(next_page)
              if next_page[-1].startswith('/'): next_page = 'https://mini.zbiornik.com' + next_page[-1]
           data2 = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a href="/film/', '</a></div>    </div>')
           if not data2: data2 = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a href="/film/', '</a>')
           for item in data2:
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)\n''', 1, True)[0]  
              exTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)Widoczne''', 1, True)[0]  
              Name = re.compile('cropped-info"><a href="/(.*?)"').findall(item)
              if Name: 
                 Name = Name[-1]
              else:
                 Name = ''
              if phUrl.startswith('/'): phUrl = 'https://mini.zbiornik.com' + phUrl
              if phTitle<>'#01':
                 valTab.append(CDisplayListItem(Name+' - '+decodeHtml(phTitle),Name+' - '+decodeHtml(exTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
                 if Name != '' and config.plugins.iptvplayer.xxxzbiornik.value:
                    valTab.append(CDisplayListItem(Name, Name, CDisplayListItem.TYPE_CATEGORY, ['https://mini.zbiornik.com/' +Name+'/filmy'], name, '', None))  
                    valTab.append(CDisplayListItem(Name+' fotki', Name, CDisplayListItem.TYPE_CATEGORY, ['https://mini.zbiornik.com/' +Name+'/zdjecia'], 'ZBIORNIKMINI-fotki', '', None))  
           if next_page:
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))  
           data2 = None
           return valTab
        if 'ZBIORNIKMINI-fotki' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'zbiornikmini.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, '<ul class="pager">', '</ul>', False)[1]
           if next_page:
              next_page = re.compile('href="(.*?)"').findall(next_page)
              if next_page[-1].startswith('/'): next_page = 'https://mini.zbiornik.com' + next_page[-1]
           data2 = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="cropped-wrap">', '</div>')
           if not data2: data2 = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a href="/film/', '</a>')
           for item in data2:
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)\n''', 1, True)[0]  
              exTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)Widoczne''', 1, True)[0]  
              Name = re.compile('cropped-info"><a href="/(.*?)"').findall(item)
              if Name: 
                 Name = Name[-1]
              else:
                 Name = ''
              if phUrl.startswith('/'): phUrl = 'https://mini.zbiornik.com' + phUrl
              if phTitle<>'#01':
                 valTab.append(CDisplayListItem(phTitle, phTitle,CDisplayListItem.TYPE_PICTURE, [CUrlItem('', phImage, 0)], 0, phImage, None)) 
           if next_page:
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))  
           data2 = None
           return valTab

        if 'pornone' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://pornone.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornone.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           data2 = self.cm.ph.getDataBeetwenMarkers(data, '>All Categories<', '</div>', False)[1]
           data2 = self.cm.ph.getAllItemsBeetwenMarkers(data2, '<a', '</a>')
           for item in data2:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''categoryName">([^>]+?)<''', 1, True)[0] 
              #phTitle = self._cleanHtmlStr(item) 
              phImage = self.cm.ph.getSearchGroups(item, '''<img src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phUrl and phTitle:
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'pornone-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Longest ---","Longest",     CDisplayListItem.TYPE_CATEGORY,['http://www.pornone.com/longest/'],             'pornone-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Most Votes ---","Most Votes",     CDisplayListItem.TYPE_CATEGORY,['http://www.pornone.com/votes/'],             'pornone-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Most Comments ---","Most Comments",     CDisplayListItem.TYPE_CATEGORY,['http://www.pornone.com/comments/'],             'pornone-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Most Favorited ---","Most Favorited",     CDisplayListItem.TYPE_CATEGORY,['http://www.pornone.com/favorites/'],             'pornone-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Most Viewed ---","Most Viewed",     CDisplayListItem.TYPE_CATEGORY,['http://www.pornone.com/views/'],             'pornone-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,['http://www.pornone.com/rating/'],             'pornone-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Newest ---","Newest",     CDisplayListItem.TYPE_CATEGORY,['http://www.pornone.com/newest/'],             'pornone-clips',    '',None))
           self.SEARCH_proc='pornone-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'pornone-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://pornone.com/search?q=%s' % url.replace(' ','+'), 'pornone-clips')
           return valTab              
        if 'pornone-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornone.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, '<link rel="next"', '>', False)[1]
           #data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="thumb"', '</div>')
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="video"', 'Rating')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''<img src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''"time">([^"^']+?)<''', 1, True)[0].strip()
              if phUrl.startswith('/'): phUrl = 'https://pornone.com' + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              next = self.cm.ph.getSearchGroups(next_page, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if next.startswith('/'): next = 'https://pornone.com' + next
              valTab.append(CDisplayListItem('Next', next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))                
           return valTab

        if 'hotmovs' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://hotmovs.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'hotmovs.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host getResolvedURL data: '+data )
           #data = self.cm.ph.getDataBeetwenMarkers(data, 'class="cats-all categories-list">', '</div>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<article', '</article>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'hotmovs-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Longest ---","Longest",     CDisplayListItem.TYPE_CATEGORY,['http://hotmovs.com/longest/'],             'hotmovs-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Most Popular ---","Most Popular",     CDisplayListItem.TYPE_CATEGORY,['http://hotmovs.com/most-popular/'],             'hotmovs-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,['http://hotmovs.com/top-rated/'],             'hotmovs-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Newest ---","Newest",     CDisplayListItem.TYPE_CATEGORY,['http://hotmovs.com/latest-updates/'],             'hotmovs-clips',    '',None))
           self.SEARCH_proc='hotmovs-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'hotmovs-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://hotmovs.com/search/?q=%s' % url.replace(' ','+'), 'hotmovs-clips')
           return valTab              
        if 'hotmovs-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'hotmovs.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host getResolvedURL data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'class="next"', '</a>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'data-video-id=', '</article>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''class="thumbnail__info__right">([^"^']+?)<''', 1, True)[0].strip()
              if phUrl.startswith('/'): phUrl = 'http://hotmovs.com' + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(phTitle,'['+phTime+']  '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              next = self.cm.ph.getSearchGroups(next_page, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if next.startswith('/'): next = 'http://hotmovs.com' + next
              if '/categories/' in next: next = next+'?mode=async&function=get_block&block_id=sphinx_list_cat_videos_videos_list'
              if next <> '#search':
                 valTab.append(CDisplayListItem('Next', next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))                
           return valTab

        if 'pornoxo' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.pornoxo.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornoxo.cookie')
           host = "Mozilla/5.0 (Linux; U; Android 4.1.1; en-us; androVM for VirtualBox ('Tablet' version with phone caps) Build/JRO03S) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30"
           header = {'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}   
           try: data = self.cm.getURLRequestData({ 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           printDBG( 'Host getResolvedURL data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'title="Main Page"', 'Top Users</div>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0].replace('Tube','') 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phTitle.startswith('+'): phTitle = ''
              if phTitle<>'':
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'pornoxo-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Longest ---","Longest",     CDisplayListItem.TYPE_CATEGORY,['https://www.pornoxo.com/videos/longest/'],             'pornoxo-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Most Popular ---","Most Popular",     CDisplayListItem.TYPE_CATEGORY,['https://www.pornoxo.com/videos/most-popular/today/'],             'pornoxo-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,['https://www.pornoxo.com/videos/top-rated/'],             'pornoxo-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Newest ---","Newest",     CDisplayListItem.TYPE_CATEGORY,['https://www.pornoxo.com/videos/newest/'],             'pornoxo-clips',    '',None))
           self.SEARCH_proc='pornoxo-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'pornoxo-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.pornoxo.com/search/%s/?sort=mw&so=y' % url.replace(' ','+'), 'pornoxo-clips')
           return valTab              
        if 'pornoxo-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornoxo.cookie')
           host = "Mozilla/5.0 (Linux; U; Android 4.1.1; en-us; androVM for VirtualBox ('Tablet' version with phone caps) Build/JRO03S) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30"
           header = {'Referer':url, 'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}   
           try: data = self.cm.getURLRequestData({ 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           printDBG( 'Host getResolvedURL data: '+data )
           next = self.cm.ph.getSearchGroups(data, '''rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'vidItem', 'class="clear"')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''([\d]?\d\d:\d\d)''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = 'https://www.pornoxo.com' + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(phTitle,'['+phTime+']  '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              if next.startswith('/'): next = 'https://www.pornoxo.com' + next
              valTab.append(CDisplayListItem('Next', next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))                
           return valTab

        if 'pinflix' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.pinflix.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'pinflix.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<article', '</article>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0]
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0]
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phTitle:
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'pinflix-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Pornstars ---","Pornstars", CDisplayListItem.TYPE_CATEGORY,['http://www.pinflix.com/pornstars'], 'pinflix-pornstars', '',None))
           valTab.insert(0,CDisplayListItem("--- Longest ---","Longest", CDisplayListItem.TYPE_CATEGORY,['http://www.pinflix.com/?order=longest'], 'pinflix-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Featured ---","Featured", CDisplayListItem.TYPE_CATEGORY,['http://www.pinflix.com/?order=featured'], 'pinflix-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated", CDisplayListItem.TYPE_CATEGORY,['http://www.pinflix.com/?order=top-rated'], 'pinflix-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Popular ---","Most Popular", CDisplayListItem.TYPE_CATEGORY,['http://www.pinflix.com/?order=most-popular'], 'pinflix-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Newest ---","Newest", CDisplayListItem.TYPE_CATEGORY,['http://www.pinflix.com/?order=newest'], 'pinflix-clips', '',None))
           self.SEARCH_proc='pinflix-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'pinflix-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.pinflix.com/search?search=%s' % url.replace(' ','+'), 'pinflix-clips')
           return valTab              
        if 'pinflix-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'pinflix.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getSearchGroups(data, '''data-next-page=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<article', '</article>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''srcset=['"]([^"^']+?\.jpg)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''img alt="([^"]+?)"''', 1, True)[0]  
              phTime = self.cm.ph.getSearchGroups(item, '''duration">([^>]+?)<''', 1, True)[0]  
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if 'video-item' in item:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              url = re.sub('&page.+', '', url)
              url = re.sub('\?page.+', '', url)
              if '?order' in url:
                 next_page = url+'&page='+next_page
              else:
                 next_page = url+'?page='+next_page
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab
        if 'pinflix-pornstars' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'pinflix.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'page active">', '<', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<article', '</article>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0]
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = 'https://www.pinflix.com' + phUrl
              if phTitle:
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'pinflix-clips', phImage, None)) 
           if next_page:
              next_page = 'https://www.pinflix.com/pornstars?page=' + str(int(next_page)+1)
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab  

        if 'upornia' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.upornia.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'upornia.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<article', '</article>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0]
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'upornia-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Longest ---","Longest",     CDisplayListItem.TYPE_CATEGORY,['https://upornia.com/longest/1/?date=all&type=all&duration=all'],             'upornia-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Most Popular ---","Most Popular",     CDisplayListItem.TYPE_CATEGORY,['https://upornia.com/most-popular/1/?date=day&type=all&duration=all'],             'upornia-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,['https://upornia.com/top-rated/1/?date=day&type=all&duration=all'],             'upornia-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Newest ---","Newest",     CDisplayListItem.TYPE_CATEGORY,['https://upornia.com/latest-updates/1/?date=all&type=all&duration=all'],             'upornia-clips',    '',None))
           self.SEARCH_proc='upornia-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'upornia-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://upornia.com/search/?q=%s' % url.replace(' ','+'), 'upornia-clips')
           return valTab              
        if 'upornia-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'upornia.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getSearchGroups(data, '''<li class="next">[^>]+?href=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<article', '</article>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt="([^"]+?)"''', 1, True)[0]  
              phTime = self.cm.ph.getSearchGroups(item, '''right">([^>]+?)<''', 1, True)[0]  
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('/'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              if next_page.startswith('/'): next_page = 'https://upornia.com' + next_page
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'txxx' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.txxx.com'
           url = 'https://txxx.com/api/json/categories/14400/str.all.json'
           COOKIEFILE = os_path.join(GetCookieDir(), 'txxx.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'txxx.cookie', 'txxx.com', self.defaultParams)
           if not sts: return valTab
           self.page=1
           printDBG( 'Host data:%s' % data )
           try:
              result = byteify(simplejson.loads(data))
              for item in result["categories"]:
                 phUrl = 'https://txxx.com/categories/%s/1/?sort=latest-updates&date=day&type=all' % str(item["dir"])
                 phUrl = 'https://txxx.com/api/json/videos/86400/str/latest-updates/60/categories.%s.%s.all..day.json'  % (str(item["dir"]), str(self.page))
                 phTitle = str(item["title"])
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'txxx-clips', '', None)) 
           except Exception:
              printExc()
           valTab.sort(key=lambda poz: poz.name)
           #valTab.insert(0,CDisplayListItem("--- Longest ---","Longest",     CDisplayListItem.TYPE_CATEGORY,['https://www.txxx.com/longest/'],             'txxx-clips',    '',None))
           #valTab.insert(0,CDisplayListItem("--- Most Popular ---","Most Popular",     CDisplayListItem.TYPE_CATEGORY,['https://www.txxx.com/most-popular/'],             'txxx-clips',    '',None))
           #valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,['https://www.txxx.com/top-rated/'],             'txxx-clips',    '',None))
           #valTab.insert(0,CDisplayListItem("--- Newest ---","Newest",     CDisplayListItem.TYPE_CATEGORY,['https://www.txxx.com/latest-updates/'],             'txxx-clips',    '',None))
           self.SEARCH_proc='txxx-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'txxx-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://txxx.com/api/videos.php?params=86400/str/relevance/60/search..1.all..day&s=%s' % url.replace(' ','+'), 'txxx-clips')
           return valTab              
        if 'txxx-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           printDBG( 'Host listsItems cat-url: '+str(catUrl) )
           next = url
           if catUrl == None: 
              self.page = 1
           else:
              self.page += 1
           COOKIEFILE = os_path.join(GetCookieDir(), 'txxx.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'txxx.cookie', 'txxx.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           try:
              result = byteify(simplejson.loads(data))
              for item in result["videos"]:
                 phTitle = str(item["title"])
                 video_id = str(item["video_id"])
                 scr = str(item["scr"])
                 phUrl = "https://txxx.com/api/videofile.php?video_id=%s&lifetime=8640000" % video_id
                 phTime = str(item["duration"])
                 added = str(item["post_date"])
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle)+'\nAdded: '+added,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, scr, None)) 
           except Exception:
              printExc()
           next_page = url.replace('.'+str(self.page)+'.','.'+str(self.page+1)+'.')
           valTab.append(CDisplayListItem('Next', 'Page: '+str(self.page+1), CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', 'next'))                
           return valTab

        if 'hclips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.hclips.com'
           url = 'https://hclips.com/api/json/categories/14400/str.all.json'
           COOKIEFILE = os_path.join(GetCookieDir(), 'hclips.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'hclips.cookie', 'hclips.com', self.defaultParams)
           if not sts: return valTab
           self.page=1
           printDBG( 'Host data:%s' % data )
           try:
              result = byteify(simplejson.loads(data))
              for item in result["categories"]:
                 phUrl = 'https://hclips.com/categories/%s/1/?sort=latest-updates&date=day&type=all' % str(item["dir"])
                 phUrl = 'https://hclips.com/api/json/videos/86400/str/latest-updates/60/categories.%s.%s.all..day.json'  % (str(item["dir"]), str(self.page))
                 phTitle = str(item["title"])
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'hclips-clips', '', None)) 
           except Exception:
              printExc()
           valTab.sort(key=lambda poz: poz.name)
           self.SEARCH_proc='hclips-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'hclips-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://hclips.com/api/videos.php?params=86400/str/relevance/60/search..1.all..day&s=%s' % url.replace(' ','+'), 'hclips-clips')
           return valTab              
        if 'hclips-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           printDBG( 'Host listsItems cat-url: '+str(catUrl) )
           next = url
           if catUrl == None: 
              self.page = 1
           else:
              self.page += 1
           COOKIEFILE = os_path.join(GetCookieDir(), 'hclips.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'hclips.cookie', 'hclips.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           try:
              result = byteify(simplejson.loads(data))
              for item in result["videos"]:
                 phTitle = str(item["title"])
                 video_id = str(item["video_id"])
                 scr = str(item["scr"])
                 phUrl = "https://hclips.com/api/videofile.php?video_id=%s&lifetime=8640000" % video_id
                 phTime = str(item["duration"])
                 added = str(item["post_date"])
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle)+'\nAdded: '+added,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, scr, None)) 
           except Exception:
              printExc()
           next_page = url.replace('.'+str(self.page)+'.','.'+str(self.page+1)+'.')
           valTab.append(CDisplayListItem('Next', 'Page: '+str(self.page+1), CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', 'next'))                
           return valTab

        if 'sunporno' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.sunporno.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'sunporno.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="thumb-container', '</div>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0]
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              if not phTitle: phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phImage.startswith('/'): phImage = self.MAIN_URL + phImage
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'sunporno-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           #valTab.insert(0,CDisplayListItem("--- Longest ---","Longest",     CDisplayListItem.TYPE_CATEGORY,['https://www.sunporno.com/long-movies/date-last-week/'],             'sunporno-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Most viewed ---","Most viewed",     CDisplayListItem.TYPE_CATEGORY,['https://www.sunporno.com/most-viewed/date-last-week/'],             'sunporno-clips',    '',None))
           #valTab.insert(0,CDisplayListItem("--- HD Porn ---","HD Porn",     CDisplayListItem.TYPE_CATEGORY,['https://www.sunporno.com/high-definition/date-last-week/'],             'sunporno-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,['https://www.sunporno.com/top-rated/date-last-week/'],             'sunporno-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Recent videos ---","Recent videos",     CDisplayListItem.TYPE_CATEGORY,['https://www.sunporno.com/most-recent/date-last-week/'],             'sunporno-clips',    '',None))
           self.SEARCH_proc='sunporno-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'sunporno-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.sunporno.com/search/%s/' % url.replace(' ','+'), 'sunporno-clips')
           return valTab              
        if 'sunporno-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'sunporno.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getSearchGroups(data, '''pag-next"\shref=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = data.split('data-id=')
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title="([^"]+?)"''', 1, True)[0]  
              phTime = self.cm.ph.getSearchGroups(item, '''"btime">([^>]+?)<''', 1, True)[0]  
              if phUrl.startswith('/'): phUrl = 'https://www.sunporno.com' + phUrl
              if phImage.startswith('/'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              if next_page.startswith('/'): next_page = 'https://www.sunporno.com' + next_page
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'sexu' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://sexu.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'sexu.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](/tag[^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item).strip() 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl 
              if phUrl:
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'sexu-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Trending ---","Trending",     CDisplayListItem.TYPE_CATEGORY,['http://sexu.com/trending/1'],             'sexu-clips',    '',None))
           #valTab.insert(0,CDisplayListItem("--- Hall of Fame ---","Hall of Fame",     CDisplayListItem.TYPE_CATEGORY,['http://sexu.com/all/1'],             'sexu-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Newest ---","Newest",     CDisplayListItem.TYPE_CATEGORY,['http://sexu.com/1'],             'sexu-clips',    '',None))
           self.SEARCH_proc='sexu-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'sexu-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://sexu.com/search?q=%s' % url.replace(' ','+'), 'sexu-clips')
           return valTab              
        if 'sexu-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'sexu.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getSearchGroups(data, '''pagination__arrow--next" href=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="grid__item">', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt="([^"]+?)"''', 1, True)[0]  
              phTime = self.cm.ph.getSearchGroups(item, '''counter">([^>]+?)<''', 1, True)[0]  
              if phUrl.startswith('/'): phUrl = 'http://sexu.com' + phUrl
              if phImage.startswith('/'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              if next_page.startswith('/'): next_page = 'http://sexu.com' + next_page
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'tubewolf' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = url #'http://www.tubewolf.com'
           url = url + '/categories/'
           COOKIEFILE = os_path.join(GetCookieDir(), 'tubewolf.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           if url.startswith('http://crocotube.com'): 
              data = self.cm.ph.getDataBeetwenMarkers(data, 'A-Z porn categories', 'Footer', False)[1]
              data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a class="ct-az-list-item', '</a>')
           elif url.startswith('https://www.alphaporno.com'): 
              data = self.cm.ph.getDataBeetwenMarkers(data, '>Categories<', 'Footer', False)[1]
              data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="thumb', '</li>')
           else:
              data = self.cm.ph.getDataBeetwenMarkers(data, 'Categories<', 'Categories<', False)[1]
              data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              if not phTitle: phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              if not phTitle: phTitle = self._cleanHtmlStr(item).strip() 
              phTitle = phTitle.replace(' Movies','')
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = url + phUrl 
              if phUrl:
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'tubewolf-clips', phImage, url)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/top-rated'],             'tubewolf-clips',    '',self.MAIN_URL))
           valTab.insert(0,CDisplayListItem("--- Most Popular ---","Most Popular",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/most-popular'],             'tubewolf-clips',    '',self.MAIN_URL))
           valTab.insert(0,CDisplayListItem("--- Newest ---","Newest",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/latest-updates'],             'tubewolf-clips',    '',self.MAIN_URL))
           self.SEARCH_proc='tubewolf-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'tubewolf-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, self.MAIN_URL+'/search/?q=%s' % url.replace(' ','+'), 'tubewolf-clips')
           return valTab              
        if 'tubewolf-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'tubewolf.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next_page = self.cm.ph.getSearchGroups(data, '''rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0] 
           if not next_page: next_page = self.cm.ph.getDataBeetwenMarkers(data, '<div class="ct-pagination">', 'Next', False)[1]
           if url.startswith('https://www.alphaporno.com'): data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a itemprop="url"', '</li>')
           if 'crocotube' in url: 
              data = self.cm.ph.getDataBeetwenMarkers(data, 'class="ct-videos-list', 'footer', False)[1]
              data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
           if url.startswith('https://www.tubewolf.com'): data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a itemprop="url"', '</div>')
           if url.startswith('https://zedporn.com'): data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="thumb', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title="([^"]+?)"''', 1, True)[0]  
              if not phTitle: phTitle = self.cm.ph.getSearchGroups(item, '''alt="([^"]+?)"''', 1, True)[0]  
              phTime = self.cm.ph.getSearchGroups(item, '''duration">([^>]+?)<''', 1, True)[0]  
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('/'): phImage = 'http:' + phImage
              phImage = urlparser.decorateUrl(phImage, {'Referer': url})
              if not 'Sponsored' in item and phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              if not next_page.startswith('http'):
                 next_page = re.compile('<a href="(.*?)"').findall(next_page)
                 next_page = next_page[-1]
                 if next_page.startswith('/'): next_page = self.MAIN_URL + next_page
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'PORNTUBE' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.porntube.com'
           url = url + '/tags'
           COOKIEFILE = os_path.join(GetCookieDir(), 'PORNTUBE.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getSearchGroups(data, '''window.INITIALSTATE = ['"]([^"^']+?)['"]''', 1, True)[0] 
           data = urllib.unquote(base64.b64decode(data))
           result = byteify(simplejson.loads(data))
           for item in result["page"]["embedded"]["topTags"]:
              phUrl = self.MAIN_URL + "/tags/" + str(item["slug"])
              phTitle = str(item["name"]).title()
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'PORNTUBE-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos?sort=rating&time=month'],             'PORNTUBE-clips',    '',self.MAIN_URL))
           valTab.insert(0,CDisplayListItem("--- Most Popular ---","Most Popular",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos?sort=views&time=month'],             'PORNTUBE-clips',    '',self.MAIN_URL))
           valTab.insert(0,CDisplayListItem("--- Newest ---","Newest",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos?sort=date'],             'PORNTUBE-clips',    '',self.MAIN_URL))
           self.SEARCH_proc='PORNTUBE-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'PORNTUBE-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, self.MAIN_URL+'/search/?q=%s' % url.replace(' ','+'), 'PORNTUBE-clips')
           return valTab              
        if 'PORNTUBE-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'PORNTUBE.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next_page = self.cm.ph.getSearchGroups(data, '''rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
           data = self.cm.ph.getSearchGroups(data, '''window.INITIALSTATE = ['"]([^"^']+?)['"]''', 1, True)[0] 
           data = urllib.unquote(base64.b64decode(data))
           printDBG( 'Host listsItems data: '+data )
           try:
              result = byteify(simplejson.loads(data))
              if result["page"]["embedded"].has_key('videos'):
                 node = result["page"]["embedded"]
              else:
                 node = result["page"]
              for item in node["videos"]["_embedded"]["items"]:
                 phUrl = self.MAIN_URL + "/api/videos/" + str(item["uuid"]) + "?ssr=false&slug=" + str(item["slug"]) + "&orientation="
                 phTitle = str(item["title"])
                 m, s = divmod(item['durationInSeconds'], 60)
                 phTime = "%02d:%02d" % (m, s)
                 phImage = str(item["thumbnailsList"][0])
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           except Exception:
              printExc()
           if next_page:
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'ASHEMALETUBE' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.ashemaletube.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'ASHEMALETUBE.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE, 'return_data': True}
           sts, data = self.getPage(url, 'ASHEMALETUBE.cookie', 'ashemaletube.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              if not 'Tube' in phTitle: continue
              if not '/videos/' in phUrl: continue
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = 'https://www.ashemaletube.com' + phUrl 
              phTitle = phTitle.replace ('Porn Tube','').replace ('Tube','')
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'ASHEMALETUBE-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Stories ---","Stories",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/stories/'],             'ASHEMALETUBE-clips',    '',self.MAIN_URL))
           valTab.insert(0,CDisplayListItem("--- Models ---","Models",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/models/'],             'ASHEMALETUBE-clips',    '',self.MAIN_URL))
           valTab.insert(0,CDisplayListItem("--- Best Recent ---","Best Recent",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL],             'ASHEMALETUBE-clips',    '',self.MAIN_URL))
           self.SEARCH_proc='ASHEMALETUBE-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'ASHEMALETUBE-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.ashemaletube.com/search/%s/' % url.replace(' ','+'), 'ASHEMALETUBE-clips')
           return valTab              
        if 'ASHEMALETUBE-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'ASHEMALETUBE.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE, 'return_data': True}
           sts, data = self.getPage(url, 'ASHEMALETUBE.cookie', 'ashemaletube.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next_page = self.cm.ph.getSearchGroups(data, '''rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
           data2 = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="js-pop thumb-item videospot', '</li>')
           if not data2: data2 = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="thumb-item videospot', '</li>')
           for item in data2:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''([\d]?\d\d:\d\d)''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = 'https://www.ashemaletube.com' + phUrl 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              if next_page.startswith('/'): next_page = 'https://www.ashemaletube.com' + next_page 
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'MOMXXXFUN' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://momxxxfun.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'momxxxfun.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           #data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a href', '</a>')
           data = data.split('<div class="popular-tag">')
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](/search/videos/[^"^']+?)['"]''', 1, True)[0] 
              phTitle = phUrl.split('/')[-1] #self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = 'https://momxxxfun.com' + phUrl 
              if phImage.startswith('/'): phImage = 'https://momxxxfun.com' + phImage 
              if phTitle:
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl+'?type=public'],'momxxxfun-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           self.SEARCH_proc='momxxxfun-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'momxxxfun-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://momxxxfun.com/search/videos/%s' % url.replace(' ','+'), 'momxxxfun-clips')
           return valTab              
        if 'momxxxfun-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'momxxxfun.cookie')
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next_page = self.cm.ph.getSearchGroups(data, '''</a></li><li><a href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
           data = data.split('<div class=" col-sm')
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''"duration">([^>]+?)<''', 1, True)[0].strip()
              if phTime=='': phTime = self.cm.ph.getSearchGroups(item, '''>HD </span>([^>]+?)<''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = 'https://momxxxfun.com' + phUrl 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              if next_page.startswith('/'): next_page = 'https://momxxxfun.com' + next_page 
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'streamporn' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://streamporn.pw'
           COOKIEFILE = os_path.join(GetCookieDir(), 'streamporn.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self._getPage(url, self.defaultParams)
           if not sts: return 
           printDBG( 'Host listsItems data: '+str(data) )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li id="menu-item', '</a>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              phTitle = self._cleanHtmlStr(item).strip() 
              if phTitle=='Studios': phTitle='.:'+phTitle+':.'
              if phTitle=='Years': phTitle='.:'+phTitle+':.'
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = 'https://streamporn.pw' + phUrl 
              if phImage.startswith('/'): phImage = 'https://streamporn.pw' + phImage 
              if phTitle<>'Hollywood Movies' and phTitle<>'Tvshows':
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'streamporn-clips', phImage, None)) 
           #valTab.sort(key=lambda poz: poz.name)
           self.SEARCH_proc='streamporn-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'streamporn-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://streamporn.pw/?s=%s' % url.replace(' ','+'), 'streamporn-clips')
           return valTab              
        if 'streamporn-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'streamporn.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self._getPage(url, self.defaultParams)
           if not sts: return 
           printDBG( 'Host listsItems data: '+str(data) )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next_page = self.cm.ph.getSearchGroups(data, '''<link rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
           if next_page =='': next_page = self.cm.ph.getSearchGroups(data, '''class='active'>.*?class='page larger' href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div data-movie-id', '<div class="jtip-bottom">')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''"duration">([^>]+?)<''', 1, True)[0].strip()
              if phTime=='': phTime = self.cm.ph.getSearchGroups(item, '''>HD </span>([^>]+?)<''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = 'https://streamporn.pw' + phUrl 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'streamporn-serwer', phImage, phImage)) 
           if next_page:
              if next_page.startswith('/'): next_page = 'https://streamporn.pw' + next_page 
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab
        if 'streamporn' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://streamporn.pw'
           COOKIEFILE = os_path.join(GetCookieDir(), 'streamporn.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self._getPage(url, self.defaultParams)
           if not sts: return 
           printDBG( 'Host listsItems data: '+str(data) )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li id="menu-item', '</a>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              phTitle = self._cleanHtmlStr(item).strip() 
              if phTitle=='Studios': phTitle='.:'+phTitle+':.'
              if phTitle=='Years': phTitle='.:'+phTitle+':.'
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = 'https://streamporn.pw' + phUrl 
              if phImage.startswith('/'): phImage = 'https://streamporn.pw' + phImage 
              if phTitle<>'Hollywood Movies' and phTitle<>'Tvshows':
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'streamporn-clips', phImage, None)) 
           #valTab.sort(key=lambda poz: poz.name)
           self.SEARCH_proc='streamporn-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'streamporn-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://streamporn.pw/?s=%s' % url.replace(' ','+'), 'streamporn-clips')
           return valTab              
        if 'streamporn-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'streamporn.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self._getPage(url, self.defaultParams)
           if not sts: return 
           printDBG( 'Host listsItems data: '+str(data) )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next_page = self.cm.ph.getSearchGroups(data, '''<link rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
           if next_page =='': next_page = self.cm.ph.getSearchGroups(data, '''class='active'>.*?class='page larger' href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div data-movie-id', '<div class="jtip-bottom">')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''"duration">([^>]+?)<''', 1, True)[0].strip()
              if phTime=='': phTime = self.cm.ph.getSearchGroups(item, '''>HD </span>([^>]+?)<''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = 'https://streamporn.pw' + phUrl 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'streamporn-serwer', phImage, phImage)) 
           if next_page:
              if next_page.startswith('/'): next_page = 'https://streamporn.pw' + next_page 
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab
        if 'streamporn-serwer' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'streamporn.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self._getPage(url, self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+str(data) )
           catUrl = self.currList[Index].possibleTypesOfSearch
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="hosts', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''"duration">([^>]+?)<''', 1, True)[0].strip()
              if phTime=='': phTime = self.cm.ph.getSearchGroups(item, '''>HD </span>([^>]+?)<''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = 'https://streamporn.pw' + phUrl 
              if '/goto/' in phUrl: 
                 self.defaultParams['header']['Referer'] = url
                 sts, data = self._getPage(phUrl, self.defaultParams)
                 if not sts: return 
                 printDBG( 'Host listsItems data2: '+str(data) )
                 phUrl = self.cm.ph.getSearchGroups(data, '''url=([^"^']+?)['"]''', 1, True)[0] 
                 printDBG( 'Host listsItems phUrl: '+str(phUrl) )
                 if '/goto/' in phUrl: 
                    sts, data = self._getPage(phUrl, self.defaultParams)
                    if not sts: return 
                    printDBG( 'Host listsItems data2: '+str(data) )
                    phUrl = self.cm.ph.getSearchGroups(data, '''url=([^"^']+?)['"]''', 1, True)[0] 
                    if '/goto/' in phUrl: 
                       sts, data = self._getPage(phUrl, self.defaultParams)
                       if not sts: return 
                       printDBG( 'Host listsItems data2: '+str(data) )
                       phUrl = self.cm.ph.getSearchGroups(data, '''url=([^"^']+?)['"]''', 1, True)[0] 
                 phUrl = self.cm.ph.getSearchGroups(data, '''url=([^"^']+?)['"]''', 1, True)[0] 
              phUrl = urlparser.decorateUrl(phUrl, {'Referer': url})
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, catUrl, None)) 
              return valTab

        if 'onlinepornfree' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://onlinepornfree.xyz'
           COOKIEFILE = os_path.join(GetCookieDir(), 'onlinepornfree.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self._getPage(url, self.defaultParams)
           if not sts: return 
           printDBG( 'Host listsItems data: '+str(data) )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li id="menu-item', '</a>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              phTitle = self._cleanHtmlStr(item).strip() 
              #if phTitle=='Studios': phTitle='.:'+phTitle+':.'
              #if phTitle=='Years': phTitle='.:'+phTitle+':.'
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = 'https://onlinepornfree.xyz' + phUrl 
              if phImage.startswith('/'): phImage = 'https://onlinepornfree.xyz' + phImage 
              if phTitle<>'Studios' and phTitle<>'Sitemap'  and phTitle<>'Contact'  and phTitle<>'Movies TV Series':
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'onlinepornfree-clips', phImage, None)) 
           #valTab.sort(key=lambda poz: poz.name)
           self.SEARCH_proc='onlinepornfree-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'onlinepornfree-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://onlinepornfree.xyz/?s=%s' % url.replace(' ','+'), 'onlinepornfree-clips')
           return valTab              
        if 'onlinepornfree-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'onlinepornfree.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self._getPage(url, self.defaultParams)
           if not sts: return 
           printDBG( 'Host listsItems data: '+str(data) )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next_page = self.cm.ph.getSearchGroups(data, '''<link rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
           if next_page =='': next_page = self.cm.ph.getSearchGroups(data, '''class='active'>.*?class='page larger' href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<article', '</article>')
           for item in data:
              phUrl = self.cm.getFullUrl(self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0], self.cm.getBaseUrl(url)) 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              if not phTitle: phTitle = self.cm.ph.getSearchGroups(item, '''Title">([^>]+?)<''', 1, True)[0].strip()
              phImage = self.cm.ph.getSearchGroups(item, '''<img src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''"duration">([^>]+?)<''', 1, True)[0].strip()
              if phTime=='': phTime = self.cm.ph.getSearchGroups(item, '''>HD </span>([^>]+?)<''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = 'https://onlinepornfree.xyz' + phUrl 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'onlinepornfree-serwer', phImage, phImage)) 
           if next_page:
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [self.cm.getFullUrl(next_page, self.cm.getBaseUrl(url))], name, '', None))                
           return valTab
        if 'onlinepornfree-serwer' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'onlinepornfree.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self._getPage(url, self.defaultParams)
           if not sts: return 
           printDBG( 'Host listsItems data: '+str(data) )
           catUrl = self.currList[Index].possibleTypesOfSearch
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="hosts', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''"duration">([^>]+?)<''', 1, True)[0].strip()
              if phTime=='': phTime = self.cm.ph.getSearchGroups(item, '''>HD </span>([^>]+?)<''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = 'https://onlinepornfree.xyz' + phUrl 
              if '/goto/' in phUrl: 
                 self.defaultParams['header']['Referer'] = url
                 sts, data = self._getPage(phUrl, self.defaultParams)
                 if not sts: return 
                 printDBG( 'Host listsItems data2: '+str(data) )
                 phUrl = self.cm.ph.getSearchGroups(data, '''url=([^"^']+?)['"]''', 1, True)[0] 
                 printDBG( 'Host listsItems phUrl: '+str(phUrl) )
                 if '/goto/' in phUrl: 
                    sts, data = self._getPage(phUrl, self.defaultParams)
                    if not sts: return 
                    printDBG( 'Host listsItems data2: '+str(data) )
                    phUrl = self.cm.ph.getSearchGroups(data, '''url=([^"^']+?)['"]''', 1, True)[0] 
                    if '/goto/' in phUrl: 
                       sts, data = self._getPage(phUrl, self.defaultParams)
                       if not sts: return 
                       printDBG( 'Host listsItems data2: '+str(data) )
                       phUrl = self.cm.ph.getSearchGroups(data, '''url=([^"^']+?)['"]''', 1, True)[0] 
              phUrl = urlparser.decorateUrl(phUrl, {'Referer': url})
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, catUrl, None)) 
           return valTab

        if 'fux' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.fux.com'
           url = url + '/tags'
           COOKIEFILE = os_path.join(GetCookieDir(), 'fux.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getSearchGroups(data, '''window.INITIALSTATE = ['"]([^"^']+?)['"]''', 1, True)[0] 
           data = urllib.unquote(base64.b64decode(data))
           result = byteify(simplejson.loads(data))
           for item in result["page"]["embedded"]["topTags"]:
              phUrl = self.MAIN_URL + "/tags/" + str(item["slug"])
              phTitle = str(item["name"]).title()
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'fux-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos?sort=rating&time=month'],             'fux-clips',    '',self.MAIN_URL))
           valTab.insert(0,CDisplayListItem("--- Most Popular ---","Most Popular",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos?sort=views&time=month'],             'fux-clips',    '',self.MAIN_URL))
           valTab.insert(0,CDisplayListItem("--- Newest ---","Newest",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos?sort=date'],             'fux-clips',    '',self.MAIN_URL))
           self.SEARCH_proc='fux-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'fux-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, self.MAIN_URL+'/search/?q=%s' % url.replace(' ','+'), 'fux-clips')
           return valTab              
        if 'fux-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'fux.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next_page = self.cm.ph.getSearchGroups(data, '''rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
           data = self.cm.ph.getSearchGroups(data, '''window.INITIALSTATE = ['"]([^"^']+?)['"]''', 1, True)[0] 
           data = urllib.unquote(base64.b64decode(data))
           printDBG( 'Host listsItems data: '+data )
           try:
              result = byteify(simplejson.loads(data))
              if result["page"]["embedded"].has_key('videos'):
                 node = result["page"]["embedded"]
              else:
                 node = result["page"]
              for item in node["videos"]["_embedded"]["items"]:
                 phUrl = self.MAIN_URL + "/api/videos/" + str(item["uuid"]) + "?ssr=false&slug=" + str(item["slug"]) + "&orientation="
                 phTitle = str(item["title"])
                 m, s = divmod(item['durationInSeconds'], 60)
                 phTime = "%02d:%02d" % (m, s)
                 phImage = str(item["thumbnailsList"][0])
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           except Exception:
              printExc()
           if next_page:
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'pornerbros' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.pornerbros.com'
           url = url + '/tags'
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornerbros.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getSearchGroups(data, '''window.INITIALSTATE = ['"]([^"^']+?)['"]''', 1, True)[0] 
           data = urllib.unquote(base64.b64decode(data))
           result = byteify(simplejson.loads(data))
           for item in result["page"]["embedded"]["topTags"]:
              phUrl = self.MAIN_URL + "/tags/" + str(item["slug"])
              phTitle = str(item["name"]).title()
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'pornerbros-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos?sort=rating&time=month'],             'pornerbros-clips',    '',self.MAIN_URL))
           valTab.insert(0,CDisplayListItem("--- Most Popular ---","Most Popular",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos?sort=views&time=month'],             'pornerbros-clips',    '',self.MAIN_URL))
           valTab.insert(0,CDisplayListItem("--- Newest ---","Newest",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos?sort=date'],             'pornerbros-clips',    '',self.MAIN_URL))
           self.SEARCH_proc='pornerbros-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'pornerbros-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, self.MAIN_URL+'/search/?q=%s' % url.replace(' ','+'), 'pornerbros-clips')
           return valTab              
        if 'pornerbros-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornerbros.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next_page = self.cm.ph.getSearchGroups(data, '''rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
           data = self.cm.ph.getSearchGroups(data, '''window.INITIALSTATE = ['"]([^"^']+?)['"]''', 1, True)[0] 
           data = urllib.unquote(base64.b64decode(data))
           printDBG( 'Host listsItems data: '+data )
           try:
              result = byteify(simplejson.loads(data))
              if result["page"]["embedded"].has_key('videos'):
                 node = result["page"]["embedded"]
              else:
                 node = result["page"]
              for item in node["videos"]["_embedded"]["items"]:
                 phUrl = self.MAIN_URL + "/api/videos/" + str(item["uuid"]) + "?ssr=false&slug=" + str(item["slug"]) + "&orientation="
                 phTitle = str(item["title"])
                 m, s = divmod(item['durationInSeconds'], 60)
                 phTime = "%02d:%02d" % (m, s)
                 phImage = str(item["thumbnailsList"][0])
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           except Exception:
              printExc()
           if next_page:
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'MYDIRTYHOBBY' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.mydirtyhobby.to'
           COOKIEFILE = os_path.join(GetCookieDir(), 'mydirtyhobby.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self._getPage(url, self.defaultParams)
           if not sts: return 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="well well-sm', 'div class="clearfix"')
           printDBG( 'Adatok: '+str(data) )
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''<img src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''"duration">([^>]+?)<''', 1, True)[0].strip()
              if phTime=='': phTime = self.cm.ph.getSearchGroups(item, '''>HD </span>([^>]+?)<''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = 'https://www.mydirtyhobby.to' + phUrl 
              if phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           valTab.insert(0,CDisplayListItem("--- Pornstars ---","Pornstars",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/pornstars'],             'MYDIRTYHOBBY-pornstars',    '',self.MAIN_URL))
           valTab.insert(0,CDisplayListItem("--- Videos ---","Videos",     CDisplayListItem.TYPE_CATEGORY,['https://mydirtyhobby.to/#'],             'MYDIRTYHOBBY-clips',    '',self.MAIN_URL))
           self.SEARCH_proc='MYDIRTYHOBBY-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'MYDIRTYHOBBY-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.mydirtyhobby.to/search/videos?search_query=%s' % url.replace(' ','+'), 'MYDIRTYHOBBY-clips')
           return valTab              
        if 'MYDIRTYHOBBY-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'mydirtyhobby.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self._getPage(url, self.defaultParams)
           if not sts: return 
           printDBG( 'Host listsItems data: '+str(data) )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'pagination', '&raquo;', False)[1]
           next_page = re.compile('href="(.*?)"').findall(next_page)
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="well well-sm', 'div class="clearfix"')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''<img src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''"duration">([^>]+?)<''', 1, True)[0].strip()
              if phTime=='': phTime = self.cm.ph.getSearchGroups(item, '''>HD </span>([^>]+?)<''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = 'https://www.mydirtyhobby.to' + phUrl 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              next_page = next_page[-1]
              if next_page.startswith('/'): next_page = 'https://www.mydirtyhobby.to' + next_page 
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab
        if 'MYDIRTYHOBBY-pornstars' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'mydirtyhobby.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self._getPage(url, self.defaultParams)
           if not sts: return 
           printDBG( 'Host listsItems data: '+str(data) )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'pagination', '&raquo;', False)[1]
           next_page = re.compile('href="(.*?)"').findall(next_page)
           data = self.cm.ph.getDataBeetwenMarkers(data, 'Neuste</a>', 'footer', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="well well-sm', 'div class="clearfix"')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = phUrl.split('/')[-1]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''"duration">([^>]+?)<''', 1, True)[0].strip()
              if phTime=='': phTime = self.cm.ph.getSearchGroups(item, '''>HD </span>([^>]+?)<''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = 'https://www.mydirtyhobby.to' + phUrl 
              if phImage.startswith('/'): phImage = 'https://www.mydirtyhobby.to' + phImage 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'MYDIRTYHOBBY-clips', phImage, phImage)) 
           if next_page:
              next_page = next_page[-1]
              if next_page.startswith('/'): next_page = 'https://www.mydirtyhobby.to' + next_page 
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
           return valTab
 
        if 'xxxstreams' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.xxxstreams.org'
           COOKIEFILE = os_path.join(GetCookieDir(), 'xxxstreams.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'xxxstreams.cookie', 'xxxstreams.org', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li id="menu-item', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item)
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if not 'xxxstreams' in phUrl: phTitle=''
              if 'Siterips' in phTitle: phTitle=''
              if phTitle:
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'xxxstreams-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           self.SEARCH_proc='xxxstreams-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'xxxstreams-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://xxxstreams.org/?s=%s' % url.replace(' ','+'), 'xxxstreams-clips')
           return valTab              
        if 'xxxstreams-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'xxxstreams.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'xxxstreams.cookie', 'xxxstreams.org', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           cookieHeader = self.cm.getCookieHeader(COOKIEFILE)
           next_page = self.cm.ph.getSearchGroups(data, '''rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<article', '</article>')
           for item in data:
              phImage = self.cm.ph.getSearchGroups(item, '''<img\ssrc=['"]([^"^']+?)['"]''', 1, True)[0] 
              item = self.cm.ph.getDataBeetwenMarkers(item, '<h1 class="entry-title">', '</h1>', False)[1]
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item)
              phImage = strwithmeta(phImage, {'Referer':self.MAIN_URL, 'Cookie':cookieHeader})
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              phUrl = strwithmeta(phUrl, {'Referer':self.MAIN_URL})
              if not 'UBIQFILE' in phTitle.upper():
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'xxxstreams-serwer', phImage, phTitle)) 
           if next_page:
              if next_page.startswith('/'): next_page = 'http://xxxstreams.org' + next_page
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab
        if 'xxxstreams-serwer' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'xxxstreams.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'xxxstreams.cookie', 'xxxstreams.org', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           phImage = self.cm.ph.getSearchGroups(data, '''"og:image" content=['"]([^"^']+?)['"]''', 1, True)[0] 
           phTitle = self.cm.ph.getSearchGroups(data, '''title" content=['"]([^"^']+?)['"]''', 1, True)[0] 
           phTime = self.cm.ph.getSearchGroups(data, '''description" content=['"]([^"^']+?)['"|]''', 1, True)[0].strip()
           if len(phTime)>8: phTime=phTime.split(' ')[-1]
           data = self.cm.ph.getDataBeetwenMarkers(data, '<span id=', '</div>', False)[1]
           data2 = self.cm.ph.getAllItemsBeetwenMarkers(data, '<p>', '</p>')
           for item in data2:
              if '|' in item:
                 phTime = item.split('|')[0].replace('<p>','')
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item)
              if 'HITFILE' in phTitle.upper(): continue
              if 'SHARE-ONLINE' in phTitle.upper(): continue
              if 'UBIQFILE' in phTitle.upper(): continue
              if 'RAPIDGATOR' in phTitle.upper(): continue
              if 'OPENLOAD' in phTitle.upper(): continue
              if 'SEVEREPORN' in phTitle.upper(): continue
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('/'): phImage = 'http:' + phImage
              if 'clipwatching.com' in phUrl:
                 if 'embed' not in phUrl:
                     video_id = self.cm.ph.getSearchGroups(phUrl, 'clipwatching.com/([A-Za-z0-9]{12})[/.-]')[0]
                     phUrl = 'http://clipwatching.com/embed-{0}.html'.format(video_id)
              if phTitle and catUrl:
                 phUrl = urlparser.decorateUrl(phUrl, {'Referer': self.MAIN_URL})
                 valTab.append(CDisplayListItem(decodeHtml(catUrl),'['+str(phTime.strip())+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           return valTab

        if '123PANDAMOVIE' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://pandamovie.info'
           COOKIEFILE = os_path.join(GetCookieDir(), '123PANDAMOVIE.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, '123PANDAMOVIE.cookie', '123pandamovie.me', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, '<ul class="genres scrolling">', '</ul>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item)
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'123PANDAMOVIE-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           #valTab.insert(0,CDisplayListItem("--- Pornstars ---","Pornstars",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/pornstars'],             '123PANDAMOVIE-years',    '',self.MAIN_URL))
           #valTab.insert(0,CDisplayListItem("--- Studios ---","Studios",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL],             '123PANDAMOVIE-years',    '', 'studios'))
           valTab.insert(0,CDisplayListItem("--- Years ---","Years",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL],             '123PANDAMOVIE-years',    '',self.MAIN_URL))
           valTab.insert(0,CDisplayListItem("--- Movies ---","Movies",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/movies'],             '123PANDAMOVIE-clips',    '',self.MAIN_URL))
           self.SEARCH_proc='123PANDAMOVIE-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if '123PANDAMOVIE-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, self.MAIN_URL+'/?s=%s' % url.replace(' ','+'), '123PANDAMOVIE-clips')
           return valTab              
        if '123PANDAMOVIE-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), '123PANDAMOVIE.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': False, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, '123PANDAMOVIE.cookie', '123pandamovie.me', self.defaultParams)
           if not sts: return ''
           #printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'arrow_pag', 'resppages', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<article', '</article>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''([\d]?\d\d:\d\d)''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'123PANDAMOVIE-serwer', phImage, None)) 
           if next_page:
              #printDBG( 'Host listsItems next_page: '+next_page )
              next_page = re.compile('href=[\"|\'](.*?)[\"|\']').findall(next_page)[-1]
              #printDBG( 'Host listsItems next_page one: '+next_page )
              if next_page.startswith('/'): next_page = self.MAIN_URL + next_page 
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab
        if '123PANDAMOVIE-serwer' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), '123PANDAMOVIE.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self._getPage(url, self.defaultParams)
           if not sts: return ''
           #printDBG( 'Host listsItems data: '+data )
           phImage = self.cm.ph.getSearchGroups(data, '''"og:image" content=['"]([^"^']+?)['"]''', 1, True)[0] 
           phTime = '' #self.cm.ph.getSearchGroups(data, '''description" content=['"]([^"^']+?)['"|]''', 1, True)[0].strip()
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="hosts', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phTitle: phTitle = self._cleanHtmlStr(item)
              if 'RapidGator' in phTitle: phTitle=''
              if 'Share-online' in phTitle: phTitle=''
              if 'Ubiqfile' in phTitle: phTitle=''
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('/'): phImage = 'http:' + phImage
              if '/goto/' in phUrl: 
                 self.defaultParams['header']['Referer'] = url
                 sts, data = self._getPage(phUrl, self.defaultParams)
                 if not sts: return 
                 printDBG( 'Host listsItems data2: '+str(data) )
                 phUrl = self.cm.ph.getSearchGroups(data, '''url=([^"^']+?)['"]''', 1, True)[0] 
                 printDBG( 'Host listsItems phUrl: '+str(phUrl) )
                 if '/goto/' in phUrl: 
                    sts, data = self._getPage(phUrl, self.defaultParams)
                    if not sts: return 
                    printDBG( 'Host listsItems data2: '+str(data) )
                    phUrl = self.cm.ph.getSearchGroups(data, '''url=([^"^']+?)['"]''', 1, True)[0] 
                    if '/goto/' in phUrl: 
                       sts, data = self._getPage(phUrl, self.defaultParams)
                       if not sts: return 
                       printDBG( 'Host listsItems data2: '+str(data) )
                       phUrl = self.cm.ph.getSearchGroups(data, '''url=([^"^']+?)['"]''', 1, True)[0]
              if phTitle:
                 phUrl = urlparser.decorateUrl(phUrl, {'Referer': url})
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           return valTab
        if '123PANDAMOVIE-years' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), '123PANDAMOVIE.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': False, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, '123PANDAMOVIE.cookie', '123pandamovie.me', self.defaultParams)
           if not sts: return ''
           #printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           #printDBG( 'Host catUrl: '+str(catUrl) )
           if catUrl == 'studios':
              data = self.cm.ph.getDataBeetwenMarkers(data, '>Studios<', '</ul>', False)[1]
           else:
              data = self.cm.ph.getDataBeetwenMarkers(data, 'Release Year', '</ul>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item)
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'123PANDAMOVIE-clips', '', None)) 
           return valTab

        if 'FULLXXXMOVIES' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://fullxxxmovies.net'
           COOKIEFILE = os_path.join(GetCookieDir(), 'fullxxxmovies.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'fullxxxmovies.cookie', 'fullxxxmovies.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li id="menu-item', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item)
              phImage = self.cm.ph.getSearchGroups(item, '''rel=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'https:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl 
              if phUrl.endswith('/'): phUrl = phUrl[ :(len(phUrl)-1)]
              if '/tag/' in phUrl:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'FULLXXXMOVIES-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- NEW ---","NEW",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL],             'FULLXXXMOVIES-clips',    '', None))
           self.SEARCH_proc='FULLXXXMOVIES-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'FULLXXXMOVIES-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://fullxxxmovies.net/?s=%s' % url.replace(' ','+'), 'FULLXXXMOVIES-clips')
           return valTab              
        if 'FULLXXXMOVIES-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'fullxxxmovies.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'fullxxxmovies.cookie', 'fullxxxmovies.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next_page = self.cm.ph.getSearchGroups(data, '''<link rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<article', '</article>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''reader-text">([^>]+?)<''', 1, True)[0].strip()
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''datetime=['"]([^"^']+?)['"]''', 1, True)[0].replace('T','').replace('+00:00','').replace('+01:00','')
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if not 'Ubiqfile' in phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle)+'\n'+'Added: '+phTime,CDisplayListItem.TYPE_CATEGORY, [phUrl],'FULLXXXMOVIES-serwer', phImage, phTitle)) 
           if next_page:
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab
        if 'FULLXXXMOVIES-serwer' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'fullxxxmovies.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'fullxxxmovies.cookie', 'fullxxxmovies.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           phImage = self.cm.ph.getSearchGroups(data, '''"og:image" content=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getDataBeetwenMarkers(data, '<div class="entry-content">', '</div>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item)
              phUrl = urlparser.decorateUrl(phUrl, {'Referer': url})
              if 'gounlimited.to' in phUrl:
                 if not 'embed' in phUrl:
                    phUrl = 'https://gounlimited.to' + '/embed-'+ phUrl.split('/')[3] +'.html'
              if 'Streaming' in item:
                 valTab.append(CDisplayListItem(decodeHtml(catUrl)+' > '+phUrl.split('/')[2],phUrl,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           return valTab

        if 'PORNREWIND' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.pornrewind.com' 
           self.format4k = config.plugins.iptvplayer.xxx4k.value
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornrewind.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           self.page = 0
           cats = ['3d','amateur','asmr','arab','anal','webcam','voyeur','teen','romantic', 'beards', 'big tits', 'big butt', 'big dick',
           'bisexual', 'blonde', 'blowjob', 'bondage', 'bukkake', 'casting', 'college', 'compilation', 'cosplay', 'couples', 'cuckold',
           'cumshots','dp', 'dildos toys', 'ebony', 'european', 'facial'
           ]
           for item in cats:
              phUrl = 'https://www.pornrewind.com/categories/%s/' % item.replace(' ','-')
              valTab.append(CDisplayListItem(item.upper(),item,CDisplayListItem.TYPE_CATEGORY, [phUrl],'PORNREWIND-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           self.SEARCH_proc='PORNREWIND-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'PORNREWIND-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.pornrewind.com/search/%s/' % url.replace(' ','+'), 'PORNREWIND-clips')
           return valTab
        if 'PORNREWIND-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           if catUrl == None: 
              self.page = 1
           else:
              self.page += 1
           if not '/search/' in url:
              url = url + '?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=post_date&from=%s' % self.page
           else:
              if self.page>1:
                 url = url + '?mode=async&function=get_block&block_id=list_videos_videos&q=dildo&category_ids=&sort_by=post_date&from_videos=%s&from_albums=%s' % (self.page, self.page)
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornrewind.cookie')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getDataBeetwenMarkers(data, '<li class="direction"><a', '</li>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="th', '</div>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''thumb-time">\s*<span>([^>]+?)<''', 1, True)[0].strip()
              Added = self.cm.ph.getSearchGroups(item, '''thumb-added">\s*<span>([^>]+?)<''', 1, True)[0].strip()
              if phImage.startswith('//'): phImage = 'https:' + phImage
              try:
                 phImage = urlparser.decorateUrl(phImage, {'Referer': 'https://www.pornrewind.com'})
              except: pass
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle)+'\n'+'Time: ['+Time+']'+'\n'+'Added: ['+Added+']',CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              next = self.cm.ph.getSearchGroups(next, '''href=['"]([^"^']+?)['"]''', 1, True)[0]
              if next.startswith('/'): next = 'https://www.pornrewind.com' + next
              valTab.append(CDisplayListItem('Next ', 'Page: '+next, CDisplayListItem.TYPE_CATEGORY, [url], name, '', 'next'))
           return valTab


        if 'BALKANJIZZ' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.balkanjizz.com' 
           self.format4k = config.plugins.iptvplayer.xxx4k.value
           COOKIEFILE = os_path.join(GetCookieDir(), 'balkanjizz.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           self.page = 0
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="col-sm', '</div> </a> </div>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0]
              if phUrl.startswith('/'): phUrl = 'https://www.balkanjizz.com' + phUrl
              if phImage.startswith('/'): phImage = 'https://www.balkanjizz.com' + phImage
              if phImage.startswith('//'): phImage = 'https:' + phImage
              try:
                 phImage = urlparser.decorateUrl(phImage, {'Referer': 'https://www.balkanjizz.com'})
              except: pass
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'BALKANJIZZ-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           self.SEARCH_proc='BALKANJIZZ-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'BALKANJIZZ-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.balkanjizz.com/search/videos?search_query=%s' % url.replace(' ','+'), 'BALKANJIZZ-clips')
           return valTab
        if 'BALKANJIZZ-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           COOKIEFILE = os_path.join(GetCookieDir(), 'balkanjizz.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getSearchGroups(data, '''</a></li><li><a href=['"]([^"^']+?)['"]''', 1, True)[0]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="col-sm', '</div> </div> </div>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''img src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''duration-bar pull-right">([^>]+?)<''', 1, True)[0].strip()
              Views = self.cm.ph.getSearchGroups(item, '''views-bar pull-left">([^>]+?)<''', 1, True)[0].strip()
              if phUrl.startswith('/'): phUrl = 'https://www.balkanjizz.com' + phUrl
              if phImage.startswith('//'): phImage = 'https:' + phImage
              try:
                 phImage = urlparser.decorateUrl(phImage, {'Referer': 'https://www.balkanjizz.com'})
              except: pass
              if phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle)+'\n'+'Time: ['+Time+']'+'\n'+'Views: ['+Views+']',CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)],'', phImage, None)) 
           if next:
              if next.startswith('/'): next = 'https://www.balkanjizz.com' + next
              valTab.append(CDisplayListItem('Next ', 'Page: '+next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', 'next'))
           return valTab

        if 'PORNORUSSIA' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://pornorussia.tv' 
           self.format4k = config.plugins.iptvplayer.xxx4k.value
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornorussia.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           self.page = 0
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a class="th', '</a>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0]
              if phUrl.startswith('/'): phUrl = 'https://pornorussia.tv' + phUrl
              if phImage.startswith('/'): phImage = 'https://pornorussia.tv' + phImage
              if phImage.startswith('//'): phImage = 'https:' + phImage
              try:
                 phImage = urlparser.decorateUrl(phImage, {'Referer': 'https://pornorussia.tv'})
              except: pass
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'PORNORUSSIA-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           self.SEARCH_proc='PORNORUSSIA-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'PORNORUSSIA-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://pornorussia.tv/s.php?poisk=%s' % url.replace(' ','+'), 'PORNORUSSIA-clips')
           return valTab
        if 'PORNORUSSIA-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornorussia.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getSearchGroups(data, '''class="more" href=['"]([^"^']+?)['"]''', 1, True)[0]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a class="th', '</a>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''img src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''th-duration">([^>]+?)<''', 1, True)[0].strip()
              if phUrl.startswith('/'): phUrl = 'https://pornorussia.tv' + phUrl
              if phImage.startswith('//'): phImage = 'https:' + phImage
              if phImage.startswith('/'): phImage = 'https://pornorussia.tv' + phImage
              try:
                 phImage = urlparser.decorateUrl(phImage, {'Referer': 'https://pornorussia.tv'})
              except: pass
              if phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)],'', phImage, None)) 
           if next:
              if next.startswith('/'): next = 'https://pornorussia.tv' + next
              valTab.append(CDisplayListItem('Next ', 'Page: '+next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', 'next'))
           return valTab

        if 'LETMEJERK' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.letmejerk.com' 
           self.format4k = config.plugins.iptvplayer.xxx4k.value
           COOKIEFILE = os_path.join(GetCookieDir(), 'letmejerk.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           self.defaultParams['header']['Referer'] = url
           self.defaultParams['header']['Origin'] = self.MAIN_URL
           #sts, data = self.get_Page(url)
           sts, data = self.getPage(url, 'letmejerk.cookie', 'letmejerk.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           self.page = 0
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phTitle = self._cleanHtmlStr(item)
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0]
              clas = self.cm.ph.getSearchGroups(item, '''class=['"]([^"^']+?)['"]''', 1, True)[0]
              if phUrl.startswith('/'): phUrl = 'https://www.letmejerk.com' + phUrl
              if clas=='category':
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'LETMEJERK-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- TOP ---","TOP",     CDisplayListItem.TYPE_CATEGORY,['https://www.letmejerk.com/?sort=top'],             'LETMEJERK-clips',    '', None))
           valTab.insert(0,CDisplayListItem("--- LATEST ---","LATEST",     CDisplayListItem.TYPE_CATEGORY,['https://www.letmejerk.com/?sort=latest'],             'LETMEJERK-clips',    '', None))
           self.SEARCH_proc='LETMEJERK-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'LETMEJERK-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.letmejerk.com/search.php?q=%s' % url.replace(' ','+'), 'LETMEJERK-clips')
           return valTab
        if 'LETMEJERK-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           for x in range(1, 3): 
              COOKIEFILE = os_path.join(GetCookieDir(), 'letmejerk.cookie')
              self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
              self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
              self.defaultParams['header']['Referer'] = url
              self.defaultParams['header']['Origin'] = self.MAIN_URL
              self.defaultParams['header']['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0"
              self.defaultParams['cookie_items'] = {'visited':'yes'}
              sts, data = self.getPage(url, 'letmejerk.cookie', 'letmejerk.com', self.defaultParams)
              if not sts: return valTab
              printDBG( 'Host listsItems data: '+data )
              next = self.cm.ph.getDataBeetwenMarkers(data, 'class="next"', '</ul>', False)[1]
              data = data.split('<div class="th">')
              if len(data): del data[0]
              if not len(data): continue
              for item in data:
                 phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
                 phImage = self.cm.ph.getSearchGroups(item, '''img src=['"]([^"^']+?)['"]''', 1, True)[0] 
                 if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
                 if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
                 phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
                 Time = self.cm.ph.getSearchGroups(item, '''clock"></i>([^>]+?)<''', 1, True)[0].strip()
                 if ''==Time: Time = self.cm.ph.getSearchGroups(item, '''clock-o"></i>([^>]+?)<''', 1, True)[0].strip()
                 if phUrl.startswith('/'): phUrl = 'https://www.letmejerk.com' + phUrl
                 if phImage.startswith('//'): phImage = 'https:' + phImage
                 try:
                    phImage = urlparser.decorateUrl(phImage, {'Referer': 'https://www.letmejerk.com'})
                 except: pass
                 if phTitle and not phUrl.endswith('/.html'):
                    valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)],'', phImage, None)) 
              if len(next)>18:
                 match = re.compile('href="(.*?)"').findall(next)
                 if not match: return valTab
                 next = match[-1].replace('&sort=','')
                 #url1 = url.replace(url.split('/')[-1],'')
                 #next = url1 + next
                 if next.startswith('/'): next = 'https://www.letmejerk.com' + next
                 valTab.append(CDisplayListItem('Next ', 'Page: '+next.split('=')[-1], CDisplayListItem.TYPE_CATEGORY, [next], name, '', 'next'))
              if len(data): break
           return valTab

        if 'GOTPORN' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.gotporn.com' 
           self.format4k = config.plugins.iptvplayer.xxx4k.value
           COOKIEFILE = os_path.join(GetCookieDir(), 'gotporn.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           data2 = self.cm.ph.getDataBeetwenMarkers(data, '<ul class="list categories-list', '</ul>', False)[1]
           data2 = self.cm.ph.getAllItemsBeetwenMarkers(data2, '<li>', '</li>')
           for item in data2:
              phTitle = self._cleanHtmlStr(item)
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0]
              if phUrl.startswith('/'): phUrl = 'https://www.gotporn.com' + phUrl
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'GOTPORN-clips', '', None)) 
           data2 = self.cm.ph.getDataBeetwenMarkers(data, '<ul class="list tags-list', '</ul>', False)[1]
           data2 = self.cm.ph.getAllItemsBeetwenMarkers(data2, '<li>', '</li>')
           for item in data2:
              phTitle = self._cleanHtmlStr(item)
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0]
              if phUrl.startswith('/'): phUrl = 'https://www.gotporn.com' + phUrl
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'GOTPORN-clips', '', None))
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- CHANNELS ---","CHANNELS",     CDisplayListItem.TYPE_CATEGORY,['https://www.gotporn.com/channels?src=hm'],             'GOTPORN-channels',    '', None))
           valTab.insert(0,CDisplayListItem("--- LATEST ---","LATEST",     CDisplayListItem.TYPE_CATEGORY,['https://www.gotporn.com'],             'GOTPORN-clips',    '', None))
           self.SEARCH_proc='GOTPORN-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'GOTPORN-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.gotporn.com/results?search_query=%s' % url.replace(' ','+'), 'GOTPORN-clips')
           return valTab
        if 'GOTPORN-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           COOKIEFILE = os_path.join(GetCookieDir(), 'gotporn.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getSearchGroups(data, '''<link rel='next' href=['"]([^"^']+?)['"]''', 1, True)[0]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="video-item', '</li>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-default-src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''duration">([^>]+?)<''', 1, True)[0].strip()
              if phUrl.startswith('/'): phUrl = 'https://www.gotporn.com' + phUrl
              if phImage.startswith('//'): phImage = 'https:' + phImage
              try:
                 phImage = urlparser.decorateUrl(phImage, {'Referer': 'https://www.gotporn.com'})
              except: pass
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)],'', phImage, None)) 
           if next:
              if next.startswith('/'): next = 'https://www.gotporn.com' + next
              valTab.append(CDisplayListItem('Next ', 'Page: '+next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', 'next'))
           return valTab
        if 'GOTPORN-channels' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           COOKIEFILE = os_path.join(GetCookieDir(), 'gotporn.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getSearchGroups(data, '''<link rel='next' href=['"]([^"^']+?)['"]''', 1, True)[0]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="channel-card', '</li> </ul>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phTitle: phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''duration">([^>]+?)<''', 1, True)[0].strip()
              if phUrl.startswith('/'): phUrl = 'https://www.gotporn.com' + phUrl
              if phImage.startswith('//'): phImage = 'https:' + phImage
              try:
                 phImage = urlparser.decorateUrl(phImage, {'Referer': 'https://www.gotporn.com'})
              except: pass
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'GOTPORN-clips', phImage, None)) 
              #   valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)],'', phImage, None)) 
           if next:
              if next.startswith('/'): next = 'https://www.gotporn.com' + next
              valTab.append(CDisplayListItem('Next ', 'Page: '+next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', 'next'))
           return valTab

        if 'ANALDIN' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.analdin.com' 
           self.format4k = config.plugins.iptvplayer.xxx4k.value
           COOKIEFILE = os_path.join(GetCookieDir(), 'analdin.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           data2 = self.cm.ph.getDataBeetwenMarkers(data, 'class="list-categories', 'footer', False)[1]
           data2 = self.cm.ph.getAllItemsBeetwenMarkers(data2, '<a class="item', '</a>')
           for item in data2:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0]
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0]
              if phTitle:
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'ANALDIN-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           #valTab.insert(0,CDisplayListItem("--- MOST VIEWED ---","MOST VIEWED",     CDisplayListItem.TYPE_CATEGORY,['https://www.analdin.com/most-popular/?mode=async&action=js_stats'],             'ANALDIN-clips',    '', None))
           #valTab.insert(0,CDisplayListItem("--- TOP RATED ---","TOP RATED",     CDisplayListItem.TYPE_CATEGORY,['https://www.analdin.com/top-rated/'],             'ANALDIN-clips',    '', None))
           valTab.insert(0,CDisplayListItem("--- LATEST ---","LATEST",     CDisplayListItem.TYPE_CATEGORY,['https://www.analdin.com/latest-updates/'],             'ANALDIN-clips',    '', None))
           self.SEARCH_proc='ANALDIN-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'ANALDIN-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.analdin.com/search/%s/' % url.replace(' ','+'), 'ANALDIN-clips')
           return valTab
        if 'ANALDIN-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           if catUrl == None: 
              self.page = 1
           else:
              self.page += 1
           if not '/search/' in url:
              url = url + '?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=post_date&from=%s&_=%s' % (self.page, time_time())
           else:
              if self.page>1:
                 url = url + '?mode=async&function=get_block&block_id=list_videos_videos&q=dildo&category_ids=&sort_by=post_date&from_videos=%s&from_albums=%s' % (self.page, self.page)
           if 'latest-updates' in url:
              url = url.replace(url.split('/')[-1],'')
           COOKIEFILE = os_path.join(GetCookieDir(), 'analdin.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getDataBeetwenMarkers(data, '<li class="next">', 'Next', False)[1]
           next = self.cm.ph.getSearchGroups(data, '''from:([^"^']+?)['"]''', 1, True)[0]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="item', '</a>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''class="title">([^>]+?)<''', 1, True)[0].strip() 
              phImage = self.cm.ph.getSearchGroups(item, '''thumb=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''duration">([^>]+?)<''', 1, True)[0].strip()
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'https:' + phImage
              try:
                 phImage = urlparser.decorateUrl(phImage, {'Referer': url})
              except: pass
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)],'', phImage, None)) 
           if next:
              #next = url
              if next.startswith('/'): next = self.MAIN_URL + next
              url = url.replace(url.split('/')[-1],'')
              #printDBG( 'Host time data: '+str(time_time()*10)) #.encode('utf-8') )
              valTab.append(CDisplayListItem('Next ', 'Page: '+str(self.page+1), CDisplayListItem.TYPE_CATEGORY, [url], name, '', 'next'))
           return valTab

        if 'NETFLIXPORNO' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://netflixporno.net'
           COOKIEFILE = os_path.join(GetCookieDir(), 'netflixporno.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'netflixporno.cookie', 'netflixporno.net', self.defaultParams)
           if not sts: return ''
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="Title">Categories</div>', '</div><div id="execphp-3"')
           #printDBG( 'Host listsItems data: '+data )
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item)
              phImage = self.cm.ph.getSearchGroups(item, '''rel=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'https:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl 
              if phUrl.endswith('/'): phUrl = phUrl[ :(len(phUrl)-1)]
              if '/genre/' in phUrl:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'NETFLIXPORNO-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- NEW ---","NEW",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL],             'NETFLIXPORNO-clips',    '', None))
           self.SEARCH_proc='NETFLIXPORNO-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'NETFLIXPORNO-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://netflixporno.net/?s=%s' % url.replace(' ','+'), 'NETFLIXPORNO-clips')
           return valTab              
        if 'NETFLIXPORNO-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'netflixporno.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'netflixporno.cookie', 'netflixporno.net', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next_page = self.cm.ph.getSearchGroups(data, '''<link\s*rel=['"]next['"]\s*href=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<article', '</article>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''Title">([^>]+?)<''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''rel="tag">([^>]+?)<''', 1, True)[0]
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if not 'Ubiqfile' in phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle)+'\n'+'Added: '+phTime,CDisplayListItem.TYPE_CATEGORY, [phUrl],'NETFLIXPORNO-serwer', phImage, phTitle)) 
           if next_page:
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab
        if 'NETFLIXPORNO-serwer' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'netflixporno.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'netflixporno.cookie', 'netflixporno.net', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           phImage = self.cm.ph.getSearchGroups(data, '''"og:image" content=['"]([^"^']+?)['"]''', 1, True)[0] 
           #data = self.cm.ph.getDataBeetwenMarkers(data, '<div class="entry-content">', '</div>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="hosts', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              if '/goto/' in phUrl: 
                 self.defaultParams['header']['Referer'] = url
                 sts, data = self._getPage(phUrl, self.defaultParams)
                 if not sts: return 
                 printDBG( 'Host listsItems data2: '+str(data) )
                 phUrl = self.cm.ph.getSearchGroups(data, '''url=([^"^']+?)['"]''', 1, True)[0] 
                 printDBG( 'Host listsItems phUrl: '+str(phUrl) )
                 if '/goto/' in phUrl: 
                    sts, data = self._getPage(phUrl, self.defaultParams)
                    if not sts: return 
                    printDBG( 'Host listsItems data2: '+str(data) )
                    phUrl = self.cm.ph.getSearchGroups(data, '''url=([^"^']+?)['"]''', 1, True)[0] 
                    if '/goto/' in phUrl: 
                       sts, data = self._getPage(phUrl, self.defaultParams)
                       if not sts: return 
                       printDBG( 'Host listsItems data2: '+str(data) )
                       phUrl = self.cm.ph.getSearchGroups(data, '''url=([^"^']+?)['"]''', 1, True)[0]
              phUrl = urlparser.decorateUrl(phUrl, {'Referer': url})
              valTab.append(CDisplayListItem(decodeHtml(phTitle),phUrl,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           return valTab

        if 'fapset' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://fapset.com' 
           self.format4k = config.plugins.iptvplayer.xxx4k.value
           COOKIEFILE = os_path.join(GetCookieDir(), 'fapset.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           data2 = self.cm.ph.getDataBeetwenMarkers(data, '<nav class="menu-inner" id="menu-inner">', '</nav>', False)[1]
           data2 = self.cm.ph.getAllItemsBeetwenMarkers(data2, '<li>', '</li>')
           for item in data2:
              phTitle = self._cleanHtmlStr(item)
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0]
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0]
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'fapset-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- LATEST ---","LATEST",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL],             'fapset-clips',    '', None))
           self.SEARCH_proc='fapset-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'fapset-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://fapset.com/search/%s/' % url.replace(' ','+'), 'fapset-clips')
           return valTab
        if 'fapset-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'fapset.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getDataBeetwenMarkers(data, '<span class="navigation">', '</div>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="thumb">', '</a></div>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''duration">([^>]+?)<''', 1, True)[0].strip()
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'https:' + phImage
              try:
                 phImage = urlparser.decorateUrl(phImage, {'Referer': url})
              except: pass
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)],'', phImage, None)) 
           if next:
              next = self.cm.ph.getSearchGroups(next, '''</span>\s*<a href=['"]([^"^']+?/page/\d+/)['"]''', 1, True)[0]
              if next.startswith('/'): next = self.MAIN_URL + next
              valTab.append(CDisplayListItem('Next ', 'Page: '+next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', 'next'))
           return valTab

        if 'daftsex' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://daftsex.com' 
           self.format4k = config.plugins.iptvplayer.xxx4k.value
           COOKIEFILE = os_path.join(GetCookieDir(), 'daftsex.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           self.page = 0
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="video-item">', '<div class="footer">')
           printDBG( 'Tartalom: '+str(data) )
           for item in data:
        
              phTitle = self.cm.ph.getAllItemsBeetwenMarkers(item, '"video-title">', '</div>', False)
              AllUrl = self.cm.ph.getAllItemsBeetwenMarkers(item, 'href="', '">\n<div', False)
              for phUrl in AllUrl:
                  AllUrl[AllUrl.index(phUrl)] = phUrl.replace('/video', 'https://daftsex.com/video')
              #printDBG( 'Linkek: '+ str(phUrl) )
              
              allImage = self.cm.ph.getAllItemsBeetwenMarkers(item, 'data-thumb="', '"></div>', False)
              for phImage in allImage:
                  allImage[allImage.index(phImage)] = phImage.replace('/img', 'https://daftsex.com/img')
              
              #printDBG( 'Kepek: '+str(phImage) )
           for i in phTitle:
              valTab.insert(0,CDisplayListItem(i,i,CDisplayListItem.TYPE_CATEGORY, AllUrl[phTitle.index(i)],'daftsex-clips', allImage[phTitle.index(i)], None))
           
              
              #valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'daftsex-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- LATEST ---","LATEST",     CDisplayListItem.TYPE_CATEGORY,['https://daftsex.com/hottest'],             'daftsex-clips',    '', None))
           self.SEARCH_proc='daftsex-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'daftsex-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           #valTab = self.listsItems(-1, 'https://daftsex.com/video/%s' % url.replace(' ','+'), 'daftsex-clips')
           return valTab
        if 'daftsex-clips' == name:
           url = 'https://daftsex.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'daftsex.cookie')
           catUrl = self.currList[Index].possibleTypesOfSearch
           if catUrl == 'next':
              self.page += 1
              post_data = {'page' : str(self.page)}
           else:
              self.page = 0
              post_data = {}
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           
           sts, data = self.get_Page(url, self.defaultParams, post_data)
           
           if not sts: return valTab
           printDBG( 'Adatok: '+data )
           next = self.cm.ph.getDataBeetwenMarkers(data, '>&uarr;<', '</div>', False)[1]
           data = self.cm.ph.getDataBeetwenMarkers(data, '<div class="videos">', '<div class="footer">', False)[1]
           phTitle = self.cm.ph.getAllItemsBeetwenMarkers(data, 'setTitle(this);">', '</div>', False)
           phImage = self.cm.ph.getAllItemsBeetwenMarkers(data, 'data-thumb="', '"></div>', False)
           phUrl = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a href="', '" data-webm', False)
           Time = self.cm.ph.getAllItemsBeetwenMarkers(data, '"video-time">', '</span>', False)
           Added = self.cm.ph.getAllItemsBeetwenMarkers(data, 'video-date"', '</span>', False)
           for item in phTitle:
              if phUrl[phTitle.index(item)].startswith('/'): 
                  phUrl[phTitle.index(item)] = self.MAIN_URL + str(phUrl[phTitle.index(item)])
              if phImage[phTitle.index(item)].startswith('//'): 
                  phImage[phTitle.index(item)] = 'https:' + str(phImage[phTitle.index(item)])
              try:
                 phImage[phTitle.index(item)] = urlparser.decorateUrl(phImage[phTitle.index(item)], {'Referer': url})
              except: 
                 pass
              valTab.append(CDisplayListItem(item, '['+Time[phTitle.index(item)]+'] '+ item +'\nAdded['+Added[phTitle.index(item)]+']',CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl[phTitle.index(item)], 1)],'', phImage[phTitle.index(item)], None)) 
           if next:
              valTab.append(CDisplayListItem('Next ', 'Page: '+str(self.page+1), CDisplayListItem.TYPE_CATEGORY, [url], name, '', 'next'))
           return valTab

        if 'lovehomeporn' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://lovehomeporn.com/' 
           self.format4k = config.plugins.iptvplayer.xxx4k.value
           COOKIEFILE = os_path.join(GetCookieDir(), 'lovehomeporn.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           self.page = 0
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a class="tag2', '</li>')
           for item in data:
              phTitle = self._cleanHtmlStr(item).strip()
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0]
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phUrl:
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'lovehomeporn-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Most Viewed ---","Most Viewed",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'videos?o=mv'],             'lovehomeporn-clips',    '', None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'videos?o=tr'],             'lovehomeporn-clips',    '', None))
           valTab.insert(0,CDisplayListItem("--- Most Recent ---","Most Recent",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'videos?o=mr'],             'lovehomeporn-clips',    '', None))
           self.SEARCH_proc='lovehomeporn-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'lovehomeporn-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://lovehomeporn.com/search?search_type=videos&search_query=%s' % url.replace(' ','+'), 'lovehomeporn-clips')
           return valTab
        if 'lovehomeporn-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'lovehomeporn.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getDataBeetwenMarkers(data, 'pagination', 'Next', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].replace('\n','').strip()
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0]
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''info">([^>]+?)<''', 1, True)[0].strip()
              Added = self.cm.ph.getSearchGroups(item, '''date">([^>]+?)<''', 1, True)[0].strip()
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phImage.endswith('.webp'): phImage = re.sub(r'/260(.*?)195/', '/260%D1%85195/', phImage.replace('webp','jpg'))
              phImage = strwithmeta(phImage, {'Referer':self.MAIN_URL})
              if phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)],'', phImage, None)) 
           if next:
              next = re.compile('href=[\"|\'](.*?)[\"|\']').findall(next)[-1]
              next = next.replace('&amp;','&')
              valTab.append(CDisplayListItem('Next ', 'Page: '+next.split('=')[-1], CDisplayListItem.TYPE_CATEGORY, [next], name, '', 'next'))
           return valTab

        if 'EROPROFILE' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.eroprofile.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'eroprofile.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           cats = '[{"title":"Amateur Moms/Mature","url":"13"},{"title":"Amateur Teens","url":"14"},{"title":"Amateurs","url":"12"},\
           {"title":"Asian","url":"19"},{"title":"Ass","url":"27"},{"title":"BDSM","url":"25"},{"title":"Big Ladies","url":"5"},\
           {"title":"Big Tits","url":"11"},{"title":"Bisexual","url":"18"},{"title":"Black / Ebony","url":"20"},{"title":"Celeb","url":"23"},\
           {"title":"Dogging","url":"33"},{"title":"Facial / Cum","url":"24"},{"title":"Fetish / Kinky","url":"10"},{"title":"Fucking / Sucking","url":"26"},\
           {"title":"Hairy","url":"7"},{"title":"Interracial","url":"15"},{"title":"Lesbian","url":"6"},{"title":"Lingerie / Panties","url":"30"},\
           {"title":"Nudist / Voyeur / Public","url":"16"},{"title":"Other / Cartoon","url":"28"},{"title":"Pregnant","url":"32"},\
           {"title":"Shemale / TS","url":"9"},{"title":"Squirting","url":"34"},{"title":"Swingers / Gangbang","url":"8"}]'
           result = simplejson.loads(cats)
           for item in result:
              title = str(item["title"])
              id = str(item["url"])
              url = 'http://www.eroprofile.com/m/videos/search?niche=%s&pnum=%s' % (id, '1')
              valTab.append(CDisplayListItem(title,title,CDisplayListItem.TYPE_CATEGORY, [url],'EROPROFILE-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Fun Videos ---",       "Fun Videos",       CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/m/videos/search?niche=17"], 'EROPROFILE-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Popular Videos ---",       "Popular Videos",       CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/m/videos/popular"], 'EROPROFILE-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Videos Home ---",       "Videos Home",       CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/m/videos/home"], 'EROPROFILE-clips', '',None))
           self.SEARCH_proc='EROPROFILE-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'EROPROFILE-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.eroprofile.com/m/videos/search?niche=13.14.12.19.27.25.5.11.18.20.23.24.10.26.17.7.15.6.30.16.28.9.8.32.33.34&text=%s&pnum=1' % url.replace(' ','+'), 'EROPROFILE-clips')
           return valTab
        if 'EROPROFILE-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'eroprofile.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getDataBeetwenMarkers(data, 'VideoListPageNav', 'marL', False)[1]
           data = data.split('<div class="video">')
           for item in data:
              printDBG( 'Host listsItems item: '+str(item) )
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              if phTitle=='': phTitle = self.cm.ph.getSearchGroups(item, '''videoTtl">([^>]+?)<''', 1, True)[0].strip()
              time = self.cm.ph.getSearchGroups(item, '''videoDur">([^>]+?)<''', 1, True)[0].strip()
              added = self.cm.ph.getSearchGroups(item, '''fsSmall">([^>]+?)<''', 1, True)[0].strip()
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              try:
                 phImage = urlparser.decorateUrl(phImage, {'Referer': url})
              except: pass
              if time and not 'Web Analytics' in phTitle and not 'tools' in time:
                 valTab.append(CDisplayListItem(phTitle,'['+time+'] '+phTitle+'\nAdded: '+added,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              next = re.compile('href=[\"|\'](.*?)[\"|\']').findall(next)[-1]
              next = next.replace('&amp;','&')
              if next.startswith('/'): next = self.MAIN_URL + next
              valTab.append(CDisplayListItem('Next', 'Page: '+next.split('=')[-1], CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))
           return valTab

        if 'absoluporn' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.absoluporn.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'absoluporn.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'pvicon-categorie', 'tags', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phTitle = self._cleanHtmlStr(decodeHtml(item)).strip()
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0].replace('..','')
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl.replace('..','')
              if phUrl:
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'absoluporn-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Most Viewed ---","Most Viewed",     CDisplayListItem.TYPE_CATEGORY,['http://www.absoluporn.com/en/wall-main-1.html'],             'absoluporn-clips',    '', None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,['http://www.absoluporn.com/en/wall-note-1.html'],             'absoluporn-clips',    '', None))
           valTab.insert(0,CDisplayListItem("--- Most Recent ---","Most Recent",     CDisplayListItem.TYPE_CATEGORY,['http://www.absoluporn.com/en/wall-date-1.html'],             'absoluporn-clips',    '', None))
           self.SEARCH_proc='absoluporn-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'absoluporn-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.absoluporn.com/en/search-%s-1.html' % url.replace(' ','+'), 'absoluporn-clips')
           return valTab
        if 'absoluporn-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'absoluporn.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getSearchGroups(data, '''<link rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&').replace('..','')
           #data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
           data = data.split('<div class="thumb-main">')
           if len(data): del data[0]
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0].replace('\n','').strip()
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0].replace('..','')
              Time = self.cm.ph.getSearchGroups(item, '''time">([^>]+?)<''', 1, True)[0].strip()
              Added = self.cm.ph.getSearchGroups(item, '''date">([^>]+?)<''', 1, True)[0].strip()
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              try:
                 phImage = urlparser.decorateUrl(phImage, {'Referer': self.MAIN_URL})
              except: pass
              if phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)],'', phImage, None)) 
           if next:
              if next.startswith('/'): next = self.MAIN_URL + next
              valTab.append(CDisplayListItem('Next ', 'Page: '+next.split('=')[-1].replace('.html',''), CDisplayListItem.TYPE_CATEGORY, [next], name, '', 'next'))
           return valTab

        if 'amateurcool' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.amateurcool.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'amateurcool.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'amateurcool.cookie', 'amateurcool.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Amateur adatok: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a href="//www.amateurcool.com/videos/', '<section class="inline-aff-sec">')

           for item in data:
              phTitle = self._cleanHtmlStr(decodeHtml(item)).strip()
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](https://www.amateurcool.com/channels/[^"^']+?)['"]''', 1, True)[0]
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phUrl:
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'amateurcool-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Most Viewed ---","Most Viewed",     CDisplayListItem.TYPE_CATEGORY,['https://www.amateurcool.com/most-viewed/page1.html'],             'amateurcool-clips',    '', None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,['https://www.amateurcool.com/top-rated/page1.html'],             'amateurcool-clips',    '', None))
           valTab.insert(0,CDisplayListItem("--- Most Recent ---","Most Recent",     CDisplayListItem.TYPE_CATEGORY,['https://www.amateurcool.com/most-recent/page1.html'],             'amateurcool-clips',    '', None))
           self.SEARCH_proc='amateurcool-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'amateurcool-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.amateurcool.com/search/%s/page1.html' % url.replace(' ','+'), 'amateurcool-clips')
           return valTab
        if 'amateurcool-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'amateurcool.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'amateurcool.cookie', 'amateurcool.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getDataBeetwenMarkers(data, 'pagination', 'NEXT', False)[1]
           data = data.split('<div class="item nb"')
           if len(data): del data[0]
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].replace('\n','').strip()
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0].replace('..','')
              Time = self.cm.ph.getSearchGroups(item, '''<span>([^>]+?)<''', 1, True)[0].replace('Video','').strip()
              Added = self.cm.ph.getSearchGroups(item, '''date">([^>]+?)<''', 1, True)[0].strip()
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              try:
                 phImage = phImage.replace(' ','%20')
                 phImage = urlparser.decorateUrl(phImage, {'Referer': self.MAIN_URL})
              except: pass
              if phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)],'', phImage, None)) 
           if next:
              next = re.compile('href=[\"|\'](.*?)[\"|\']').findall(next)[-1]
              next = next.replace('&amp;','&')
              if next.startswith('page'): next = url.replace(url.split('/')[-1],next)
              if next.startswith('/'): next = self.MAIN_URL + next
              valTab.append(CDisplayListItem('Next ', 'Page: '+next.split('/')[-1].replace('.html','').replace('page',''), CDisplayListItem.TYPE_CATEGORY, [next], name, '', 'next'))
           return valTab

        if 'porngo' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://porngo.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'porngo.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'porngo.cookie', 'porngo.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           if len(data)<100 and 'Maintenance' in data:
              msg = _("Last error:\n%s" % data)
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              return valTab
           data2 = self.cm.ph.getDataBeetwenMarkers(data, '<div class="letter-block">', '<div class="letter-block">', False)[1]
           if ''==data2: data2 = data
           data = self.cm.ph.getAllItemsBeetwenMarkers(data2, '<div class="letter-block__item">', '</div>')
           for item in data:
              phTitle = self._cleanHtmlStr(decodeHtml(item)).strip()
              if phTitle.startswith('-') or ''== phTitle: continue
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0]
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phUrl:
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'porngo-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Most Recent ---","Most Recent",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL],             'porngo-clips',    '', None))
           self.SEARCH_proc='porngo-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'porngo-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.porngo.com/search/%s/' % url.replace(' ','+'), 'porngo-clips')
           return valTab
        if 'porngo-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'porngo.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'porngo.cookie', 'porngo.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getDataBeetwenMarkers(data, 'pagination', '>Next', False)[1]
           data = data.split('<div class="thumb item ">')
           if len(data): del data[0]
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].replace('\n','').strip()
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0].replace('..','')
              Time = self.cm.ph.getSearchGroups(item, '''duration">([^>]+?)<''', 1, True)[0].strip()
              Added = self.cm.ph.getSearchGroups(item, '''pull-right no-rating">([^>]+?)<''', 1, True)[0].strip()
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              try:
                 phImage = urlparser.decorateUrl(phImage, {'Referer': self.MAIN_URL})
              except: pass
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              next = re.compile('href=[\"|\'](.*?)[\"|\']').findall(next)[-1]
              next = next.replace('&amp;','&')
              if next.startswith('/'): next = self.MAIN_URL + next
              valTab.append(CDisplayListItem('Next ', 'Page: '+ next.split('/')[-2],CDisplayListItem.TYPE_CATEGORY, [next], name, '', 'next'))
           return valTab

        if 'anybunny' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://anybunny.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'anybunny.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'anybunny.cookie', 'anybunny.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           #data = self.cm.ph.getDataBeetwenMarkers(data, 'pvicon-categorie', 'tags', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a class=linkscts', '</a>')
           for item in data:
              phTitle = self._cleanHtmlStr(decodeHtml(item)).replace('\n','').strip()
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](/top/[^"^']+?)['"]''', 1, True)[0]
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phUrl:
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'anybunny-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,['http://anybunny.com/top/'],             'anybunny-clips',    '', None))
           valTab.insert(0,CDisplayListItem("--- New ---","New",     CDisplayListItem.TYPE_CATEGORY,['http://anybunny.com/new/'],             'anybunny-clips',    '', None))
           self.SEARCH_proc='anybunny-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'anybunny-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://anybunny.com/top/%s' % url.replace(' ','+'), 'anybunny-clips')
           return valTab
        if 'anybunny-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'anybunny.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'anybunny.cookie', 'anybunny.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getDataBeetwenMarkers(data, 'topbtmse', '>Next page', False)[1]
           data = data.split('nuyrfe')
           if len(data): del data[0]
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].replace('\n','').strip()
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0].replace('..','')
              Time = self.cm.ph.getSearchGroups(item, '''<span>([^>]+?)<''', 1, True)[0].replace('Video','').strip()
              Added = self.cm.ph.getSearchGroups(item, '''date">([^>]+?)<''', 1, True)[0].strip()
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              try:
                 phImage = urlparser.decorateUrl(phImage, {'Referer': self.MAIN_URL})
              except: pass
              if phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)],'', phImage, None)) 
           if next:
              next = re.compile('href=[\"|\'](.*?)[\"|\']').findall(next)[-1]
              next = next.replace('&amp;','&')
              if next.startswith('/'): next = self.MAIN_URL + next
              valTab.append(CDisplayListItem('Next ', 'Page: '+next.split('=')[-1].replace('.html','').replace('page',''), CDisplayListItem.TYPE_CATEGORY, [next], name, '', 'next'))
           return valTab

        if 'datoporn' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://datoporn.co' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'datoporn.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'datoporn.cookie', 'dato.porn', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           data = data.split('<a class="item"')
           if len(data): del data[0]
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0].replace('\n','').strip()
              if not phTitle: phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].replace('\n','').strip()
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0]
              if phUrl.startswith('/'): phUrl = 'https://dato.porn' + phUrl
              if not 'sort_by' in phUrl: phUrl= phUrl+'?sort_by=post_date'     
              if phUrl:
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'datoporn-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           self.SEARCH_proc='datoporn-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'datoporn-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://dato.porn/search/%s/' % url.replace(' ','+'), 'datoporn-clips')
           return valTab
        if 'datoporn-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'datoporn.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'datoporn.cookie', 'datoporn.co', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getSearchGroups(data, '''class="next".*?from:(\d)"''', 1, True)[0] 
           data = data.split('<div class="item')
           if len(data): del data[0]
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0].replace('\n','').strip()
              if not phTitle: phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].replace('\n','')
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0]
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0].replace('..','')
              Time = self.cm.ph.getSearchGroups(item, '''duration">([^>]+?)<''', 1, True)[0].replace('Video','').strip()
              Added = self.cm.ph.getSearchGroups(item, '''added"><em>([^>]+?)<''', 1, True)[0].strip()
              if phUrl.startswith('/'): phUrl = 'https://dato.porn' + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              try:
                 phImage = urlparser.decorateUrl(phImage, {'Referer': 'https://dato.porn'})
              except: pass
              if phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+'] '+decodeHtml(phTitle)+'\n'+Added,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)],'', phImage, None)) 
           if next:
              next_page = url.replace('&'+url.split('&')[-1],'')+'&from='+str(next)
              if '/search/' in url: next_page = url.replace('&'+url.split('&')[-1],'')+'&from_videos='+str(next)
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
           return valTab

        if 'hqporner' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://hqporner.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'hqporner.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'hqporner.cookie', 'hqporner.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<section', '</section>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0]
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0]
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('/'): phImage = self.MAIN_URL + phImage
              if phUrl and phTitle:
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'hqporner-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           self.SEARCH_proc='hqporner-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'hqporner-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://hqporner.com/?s=%s' % url.replace(' ','+'), 'hqporner-clips')
           return valTab
        if 'hqporner-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'hqporner.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'hqporner.cookie', 'hqporner.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getDataBeetwenMarkers(data, 'pagination', '>Next', False)[1]
           data = data.split('<div class="6u">')
           if len(data): del data[0]
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].replace('\n','').strip()
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0].replace('..','')
              Time = self.cm.ph.getSearchGroups(item, '''fa-clock-o meta-data">([^>]+?)<''', 1, True)[0].strip()
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              try:
                 phImage = urlparser.decorateUrl(phImage, {'Referer': self.MAIN_URL})
              except: pass
              if phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)],'', phImage, None)) 
           if next:
              next = re.compile('href=[\"|\'](.*?)[\"|\']').findall(next)[-1]
              next = next.replace('&amp;','&')
              if next.startswith('/'): next = self.MAIN_URL + next
              valTab.append(CDisplayListItem('Next ', 'Page: '+next.split('=')[-1].replace('.html','').replace('page',''), CDisplayListItem.TYPE_CATEGORY, [next], name, '', 'next'))
           return valTab

        if 'spankbang' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://spankbang.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'spankbang.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'spankbang.cookie', 'spankbang.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
           for item in data:
              phTitle = self._cleanHtmlStr(decodeHtml(item)).replace('\n','').strip()
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0]
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](/s/[^"^']+?)['"]''', 1, True)[0]
              if not phUrl: phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](/tag/[^"^']+?)['"]''', 1, True)[0]
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('/'): phImage = self.MAIN_URL + phImage
              if phUrl and phTitle:
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'spankbang-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Trending ---","Trending",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/trending_videos/'],             'spankbang-clips',    '', None))
           valTab.insert(0,CDisplayListItem("--- Most Popular ---","Most Popular",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/most_popular/?period=week'],             'spankbang-clips',    '', None))
           valTab.insert(0,CDisplayListItem("--- New ---","New",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/new_videos/'],             'spankbang-clips',    '', None))
           self.SEARCH_proc='spankbang-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'spankbang-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://spankbang.com/s/%s/' % url.replace(' ','+'), 'spankbang-clips')
           return valTab
        if 'spankbang-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'spankbang.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'spankbang.cookie', 'spankbang.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getSearchGroups(data, '''<link rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&').replace('..','')
           if next == '': next = self.cm.ph.getSearchGroups(data, '''<li class="next"><a href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&').replace('..','')
           data = data.split('data-id=')
           if len(data): del data[0]
           for item in data:
              Added = ''
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].replace('\n','').strip()
              phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0].replace('..','')
              Time = self.cm.ph.getSearchGroups(item, '''clock-o"></i>([^>]+?)<''', 1, True)[0].strip()
              if not Time: Time = self.cm.ph.getSearchGroups(item, '''i-len">([^>]+?)<''', 1, True)[0].strip()
              if not Time: Time = self.cm.ph.getSearchGroups(item, '''</use></svg>([^>]+?)<''', 1, True)[0].strip()
              Added = self.cm.ph.getSearchGroups(item, '''&nbsp;<span>([^>]+?)<''', 1, True)[0].strip()
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              try:
                 phImage = urlparser.decorateUrl(phImage, {'Referer': self.MAIN_URL})
              except: pass
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+'] '+decodeHtml(phTitle)+'\n'+Added,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)],'', phImage, None)) 
           if next:
              if next.startswith('//'): next = 'http:' + next
              if next.startswith('/'): next = self.MAIN_URL + next
              valTab.append(CDisplayListItem('Next ', 'Page: '+next.split('/')[-2].replace('.html','').replace('page',''), CDisplayListItem.TYPE_CATEGORY, [next], name, '', 'next'))
           return valTab

        if 'cumlouder' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.cumlouder.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'cumlouder.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'cumlouder.cookie', 'cumlouder.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a tag-url=', '</a>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0]
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0]
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('/'): phImage = self.MAIN_URL + phImage
              if phUrl and phTitle:
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'cumlouder-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Channels ---","channels",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/channels/'],             'cumlouder-girls',    '', None))
           valTab.insert(0,CDisplayListItem("--- Series ---","series",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/series/'],             'cumlouder-girls',    '', None))
           valTab.insert(0,CDisplayListItem("--- Girls ---","girls",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/girls/'],             'cumlouder-girls',    '', None))
           self.SEARCH_proc='cumlouder-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'cumlouder-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.cumlouder.com/search/?q=%s' % url.replace(' ','+'), 'cumlouder-clips')
           return valTab
        if 'cumlouder-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'cumlouder.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'cumlouder.cookie', 'cumlouder.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getSearchGroups(data, '''<link rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&').replace('..','')
           if next == '': next = self.cm.ph.getSearchGroups(data, '''<li class="next"><a href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&').replace('..','')
           data = data.split('<a class="muestra-escena')
           if len(data): del data[0]
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].replace('\n','').strip()
              phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0].replace('..','')
              Time = self.cm.ph.getSearchGroups(item, '''minutos sprite"></span>([^>]+?)<''', 1, True)[0].strip()
              if not Time: Time = self.cm.ph.getSearchGroups(item, '''i-len">([^>]+?)<''', 1, True)[0].strip()
              Added = self.cm.ph.getSearchGroups(item, '''fecha sprite"></span>([^>]+?)<''', 1, True)[0].strip()
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              try:
                 phImage = urlparser.decorateUrl(phImage, {'Referer': self.MAIN_URL})
              except: pass
              if phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+'] '+decodeHtml(phTitle)+'\n'+Added,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)],'', phImage, None)) 
           if next:
              if next.startswith('//'): next = 'http:' + next
              if next.startswith('/'): next = self.MAIN_URL + next
              valTab.append(CDisplayListItem('Next ', 'Page: '+next.split('/')[-2].replace('.html','').replace('page',''), CDisplayListItem.TYPE_CATEGORY, [next], name, '', 'next'))
           return valTab
        if 'cumlouder-girls' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'cumlouder.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'cumlouder.cookie', 'cumlouder.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           data = data.split('class="muestra-escena')
           if len(data): del data[0]
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0]
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0]
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('/'): phImage = self.MAIN_URL + phImage
              if phUrl and phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'cumlouder-clips', phImage, None)) 
           #valTab.sort(key=lambda poz: poz.name)
           return valTab

        if 'porn00' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.porn00.org'
           COOKIEFILE = os_path.join(GetCookieDir(), 'porn00.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'porn00.cookie', 'porn00.org', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           #data = self.cm.ph.getDataBeetwenMarkers(data, '<ul class="category-menu', '</ul>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a class="item"', '</a>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].strip()
              if ''==phTitle: continue
              if ''==phUrl: continue
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phImage.startswith('//'): phImage = 'https:' + phImage
              if phUrl.startswith('//'): phUrl = 'https:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl 
              if phUrl:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'porn00-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           self.SEARCH_proc='porn00-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'porn00-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.porn00.org/search/?q=%s' % url.replace(' ','+'), 'porn00-clips')
           return valTab              
        if 'porn00-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'porn00.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'porn00.cookie', 'porn00.org', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next = self.cm.ph.getDataBeetwenMarkers(data, '<li class="next">', '</li>', False)[1]
           data = data.split('<div class="item')
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''([\d]?\d\d:\d\d)''', 1, True)[0] 
              Added = self.cm.ph.getSearchGroups(item, '''added">[<em>]?([^>]+?)<''', 1, True)[0].strip()
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+'] '+decodeHtml(phTitle)+'\n'+Added,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)],'', phImage, None)) 
           if next:
              page = self.cm.ph.getSearchGroups(str(next), '''from:([^"^']+?)['"]''')[0]
              next = url + '?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=post_date&from='+page
              valTab.append(CDisplayListItem('Next', 'Page : '+page, CDisplayListItem.TYPE_CATEGORY, [next], name, '', 'Next'))                
           return valTab

        if 'watchpornx' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://watchpornx.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'watchpornx.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'watchpornx.cookie', 'watchpornx.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="cat-item', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item)
              if phUrl.startswith('//'): phUrl = 'https:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'watchpornx-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Pornstars ---","Pornstars",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL],             'watchpornx-years',    '',"Pornstars"))
           valTab.insert(0,CDisplayListItem("--- Years ---","Years",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL],             'watchpornx-years',    '',"Years"))
           valTab.insert(0,CDisplayListItem("--- Studios ---","Studios",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL],             'watchpornx-years',    '',"Studios"))
           #valTab.insert(0,CDisplayListItem("--- Clips & Scenes ---","Clips & Scenes",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/category/clips-scenes'],             'watchpornx-clips',    '',self.MAIN_URL))
           valTab.insert(0,CDisplayListItem("--- Featured ---","Featured",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/category/featured-movies'],             'watchpornx-clips',    '',self.MAIN_URL))
           valTab.insert(0,CDisplayListItem("--- New ---","New",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL],             'watchpornx-clips',    '', None))
           self.SEARCH_proc='watchpornx-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'watchpornx-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://watchpornx.com/?s=%s' % url.replace(' ','+'), 'watchpornx-clips')
           return valTab              
        if 'watchpornx-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'watchpornx.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'watchpornx.cookie', 'watchpornx.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next_page = self.cm.ph.getSearchGroups(data, '''<link\s*rel=['"]next['"]\s*href=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<article', '</article>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''Title">([^>]+?)<''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''rel="tag">([^>]+?)<''', 1, True)[0]
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if not 'Ubiqfile' in phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle)+'\n'+phTime,CDisplayListItem.TYPE_CATEGORY, [phUrl],'watchpornx-serwer', phImage, phTitle)) 
           if next_page:
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab
        if 'watchpornx-serwer' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'watchpornx.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'watchpornx.cookie', 'watchpornx.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           phImage = self.cm.ph.getSearchGroups(data, '''"og:image" content=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getDataBeetwenMarkers(data, 'playcontainer"', '<div id="pandamoviebannertop1">', False)[1]
           printDBG( 'Adatok: '+str(data) )
           for item in data:
              allUrl = self.cm.ph.getAllItemsBeetwenMarkers(item, 'href="', ' rel="nofollow"', False) 
              for phUrl in allUrl:
                  allUrl[allUrl.index(phUrl)] = 'Hostok: ' + phUrl
#              printDBG( 'Linkek: '+str(phUrl))
              allTitle = self.cm.ph.getAllItemsBeetwenMarkers(item, 'title="', '" href=', False)
              for phTitle in allTitle:
                  allTitle[allTitle.index(phTitle)] = 'Cim' + phTitle
 #             printDBG( 'Cimek: '+str(phTitle))
              #phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              #if '/goto/' in phUrl: 
              #   self.defaultParams['header']['Referer'] = url
              #   sts, data = self._getPage(phUrl, self.defaultParams)
               #  if not sts: return 
               #  printDBG( 'Host listsItems data2: '+str(data) )
                # phUrl = self.cm.ph.getSearchGroups(data, '''url=([^"^']+?)['"]''', 1, True)[0] 
                 #printDBG( 'Host listsItems phUrl: '+str(phUrl) )
                 #if '/goto/' in phUrl: 
                  #  sts, data = self._getPage(phUrl, self.defaultParams)
                   # if not sts: return 
                    #printDBG( 'Host listsItems data2: '+str(data) )
                    #phUrl = self.cm.ph.getSearchGroups(data, '''url=([^"^']+?)['"]''', 1, True)[0] 
                    #if '/goto/' in phUrl: 
                     #  sts, data = self._getPage(phUrl, self.defaultParams)
                      # if not sts: return 
                      # printDBG( 'Host listsItems data2: '+str(data) )
                       #phUrl = self.cm.ph.getSearchGroups(data, '''url=([^"^']+?)['"]''', 1, True)[0]
              #phUrl = urlparser.decorateUrl(phUrl, {'Referer': url})
              valTab.append(CDisplayListItem(phTitle,phUrl,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           return valTab
        if 'watchpornx-years' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'watchpornx.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': False, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'watchpornx.cookie', 'watchpornx.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           #printDBG( 'Host catUrl: '+str(catUrl) )
           if catUrl == 'Studios':
              data = self.cm.ph.getDataBeetwenMarkers(data, 'Studios<', '</ul>', False)[1]
           elif catUrl == 'Years':
              data = self.cm.ph.getDataBeetwenMarkers(data, 'Years', '</ul>', False)[1]
           elif catUrl == 'Pornstars':
              data = self.cm.ph.getDataBeetwenMarkers(data, 'Pornstars', '</ul>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item)
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'watchpornx-clips', '', None)) 
           return valTab

        if 'P720' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://p720.net'
           COOKIEFILE = os_path.join(GetCookieDir(), 'P720.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'P720.cookie', 'p720.net', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           data = data.split('<a class="item"')
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phTitle: phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'https:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl 
              if phImage.startswith('//'): phImage = 'http:' + phImage + '/' 
              if phImage.startswith('/'): phImage = self.MAIN_URL + phImage
              if not 'CCBIll' in phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl+'?sort_by=post_date'],'P720-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Most Viewed ---","Most Viewed",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/most-popular/'+'?sort_by=post_date'],             'P720-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/top-rated/'+'?sort_by=post_date'],             'P720-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Latest ---","Latest",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/latest-updates/'+'?sort_by=post_date'],             'P720-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Home ---","Home",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/?sort_by=post_date'],             'P720-clips',    '',None))
           self.SEARCH_proc='P720-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'P720-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://p720.net/search/%s/?sort_by=post_date' % url.replace(' ','+'), 'P720-clips')
           return valTab              
        if 'P720-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'P720.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'P720.cookie', 'p720.net', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next = self.cm.ph.getSearchGroups(data, '''(\d)">Next''', 1, True)[0] 
           data2 = self.cm.ph.getDataBeetwenMarkers(data, 'id="list_videos_most_recent_videos', 'footer', False)[1]
           if data2: data = data2
           n = '<div class="item'
           s = '<div class="video-rating pull-right'
           if not n in data and not s in data:  return valTab
           if n in data: data = data.split(n)
           if s in data: data = data.split(s)
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''class="duration">([^>]+?)<''', 1, True)[0].strip()
              Added = self.cm.ph.getSearchGroups(item, '''added"><em>([^>]+?)<''', 1, True)[0].strip()
              if not Added: Added = self.cm.ph.getSearchGroups(item, '''pull-left">([^>]+?)<''', 1, True)[0].strip()
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if 'label-private">PRIVATE<' in item: phTitle = phTitle + '   {PRIVATE}'
              if not 'CCBIll' in phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+'] '+decodeHtml(phTitle)+'\n'+Added,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              next_page = url.replace('&'+url.split('&')[-1],'')+'&from='+str(next)
              if '/search/' in url: next_page = url.replace('&'+url.split('&')[-1],'')+'&from_videos='+str(next)
              #valTab.append(CDisplayListItem('Next', next_page.split('=')[-1], CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'pornopersik' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://pornopersik.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornopersik.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'pornopersik.cookie', 'pornopersik.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           data = data.split('<a class="item"')
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phTitle: phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'https:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl 
              if phImage.startswith('//'): phImage = 'http:' + phImage + '/' 
              if phImage.startswith('/'): phImage = self.MAIN_URL + phImage
              if not 'CCBIll' in phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl+'?sort_by=post_date'],'pornopersik-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Most Viewed ---","Most Viewed",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/most-popular/'+'?sort_by=post_date'],             'pornopersik-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/top-rated/'+'?sort_by=post_date'],             'pornopersik-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Latest ---","Latest",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/latest-updates/'+'?sort_by=post_date'],             'pornopersik-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Home ---","Home",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/?sort_by=post_date'],             'pornopersik-clips',    '',None))
           self.SEARCH_proc='pornopersik-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'pornopersik-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://pornopersik.com/search/%s/?sort_by=post_date' % url.replace(' ','+'), 'pornopersik-clips')
           return valTab              
        if 'pornopersik-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornopersik.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'pornopersik.cookie', 'pornopersik.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next = self.cm.ph.getSearchGroups(data, '''class="next".*?from:(\d)"''', 1, True)[0] 
           data2 = self.cm.ph.getDataBeetwenMarkers(data, 'id="list_videos_most_recent_videos', 'footer', False)[1]
           if data2: data = data2
           n = '<div class="item'
           s = '<div class="video-rating pull-right'
           if not n in data and not s in data:  return valTab
           if n in data: data = data.split(n)
           if s in data: data = data.split(s)
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''class="duration">([^>]+?)<''', 1, True)[0].strip()
              Added = self.cm.ph.getSearchGroups(item, '''added"><em>([^>]+?)<''', 1, True)[0].strip()
              if not Added: Added = self.cm.ph.getSearchGroups(item, '''pull-left">([^>]+?)<''', 1, True)[0].strip()
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if 'label-private">PRIVATE<' in item: phTitle = phTitle + '   {PRIVATE}'
              if not 'CCBIll' in phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+'] '+decodeHtml(phTitle)+'\n'+Added,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              next_page = url.replace('&'+url.split('&')[-1],'')+'&from='+str(next)
              if '/search/' in url: next_page = url.replace('&'+url.split('&')[-1],'')+'&from_videos='+str(next)
              #valTab.append(CDisplayListItem('Next', next_page.split('=')[-1], CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'ANYPORN' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://anyporn.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'anyporn.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'anyporn.cookie', 'anyporn.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           data = data.split('<a class="item"')
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phTitle: phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'https:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl 
              if phImage.startswith('//'): phImage = 'http:' + phImage + '/' 
              if phImage.startswith('/'): phImage = self.MAIN_URL + phImage
              if not 'CCBIll' in phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl+'?sort_by=post_date'],'anyporn-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- HD ---","HD",     CDisplayListItem.TYPE_CATEGORY,['https://anyporn.com/categories/hd/?sort_by=post_date'],             'anyporn-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Most Viewed ---","Most Viewed",     CDisplayListItem.TYPE_CATEGORY,['https://anyporn.com/popular/?sort_by=post_date'],             'anyporn-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Latest ---","Latest",     CDisplayListItem.TYPE_CATEGORY,['https://anyporn.com/newest/?sort_by=post_date'],             'anyporn-clips',    '',None))
           #valTab.insert(0,CDisplayListItem("--- Home ---","Home",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/?sort_by=post_date'],             'anyporn-clips',    '',None))
           self.SEARCH_proc='anyporn-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'anyporn-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://anyporn.com/search/%s/' % url.replace(' ','+'), 'anyporn-clips')
           return valTab              
        if 'anyporn-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'anyporn.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'anyporn.cookie', 'anyporn.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next = self.cm.ph.getSearchGroups(data, '''next".*?from:(\d)">Next''', 1, True)[0] 
           data2 = self.cm.ph.getDataBeetwenMarkers(data, 'id="list_videos_most_recent_videos', 'footer', False)[1]
           if data2: data = data2
           n = "<div class='item"
           s = '<div class="video-rating pull-right'
           if not n in data and not s in data:  return valTab
           if n in data: data = data.split(n)
           if s in data: data = data.split(s)
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''durationid.*?innerHTML\s*?=\s*?"([^"^']+?)"''', 1, True)[0].strip()
              Added = self.cm.ph.getSearchGroups(item, '''added"><em>([^>]+?)<''', 1, True)[0].strip()
              if not Added: Added = self.cm.ph.getSearchGroups(item, '''pull-left">([^>]+?)<''', 1, True)[0].strip()
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if 'label-private">PRIVATE<' in item: phTitle = phTitle + '   {PRIVATE}'
              if not 'CCBIll' in phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+'] '+decodeHtml(phTitle)+'\n'+Added,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              if '?' in url:
                 next_page = url.replace('&'+url.split('&')[-1],'')+'&from='+str(next)
              else:
                 next_page = url.replace('&'+url.split('&')[-1],'')+'?from='+str(next)
              if '/search/' in url: next_page = url.replace('&'+url.split('&')[-1],'')+'&from_videos='+str(next)
              #valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
              valTab.append(CDisplayListItem('Next', next_page.split('=')[-1], CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'ANON-V' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://anon-v.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'anon-v.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'anon-v.cookie', 'anon-v.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           data = data.split('<a class="item"')
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phTitle: phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'https:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl 
              if phImage.startswith('//'): phImage = 'http:' + phImage + '/' 
              if phImage.startswith('/'): phImage = self.MAIN_URL + phImage
              if not 'CCBIll' in phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl+'?sort_by=post_date'],'anon-v-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           #valTab.insert(0,CDisplayListItem("--- Most Popular ---","Most Popular",     CDisplayListItem.TYPE_CATEGORY,['https://anon-v.com/most-popular/?sort_by=post_date'],             'anon-v-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Latest ---","Latest",     CDisplayListItem.TYPE_CATEGORY,['https://anon-v.com/latest-updates/?sort_by=post_date'],             'anon-v-clips',    '',None))
           self.SEARCH_proc='anon-v-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'anon-v-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://anon-v.com/search/%s/' % url.replace(' ','+'), 'anon-v-clips')
           return valTab              
        if 'anon-v-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'anon-v.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'anon-v.cookie', 'anon-v.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next = self.cm.ph.getSearchGroups(data, '''next".*?from:(\d)">Next''', 1, True)[0] 
           data2 = self.cm.ph.getDataBeetwenMarkers(data, 'id="list_videos_most_recent_videos', 'footer', False)[1]
           if data2: data = data2
           n = '<div class="item'
           s = '<div class="video-rating pull-right'
           if not n in data and not s in data:  return valTab
           if n in data: data = data.split(n)
           if s in data: data = data.split(s)
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''duration">([^>]+?)<''', 1, True)[0].strip()
              Added = self.cm.ph.getSearchGroups(item, '''added"><em>([^>]+?)<''', 1, True)[0].strip()
              if not Added: Added = self.cm.ph.getSearchGroups(item, '''pull-left">([^>]+?)<''', 1, True)[0].strip()
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              phImage = strwithmeta(phImage, {'Referer':self.MAIN_URL})
              if not 'CCBIll' in phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+'] '+decodeHtml(phTitle)+'\n'+Added,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              if '?' in url:
                 next_page = url.replace('&'+url.split('&')[-1],'')+'&from='+str(next)
              else:
                 next_page = url.replace('&'+url.split('&')[-1],'')+'?from='+str(next)
              if '/search/' in url: next_page = url.replace('&'+url.split('&')[-1],'')+'&from_videos='+str(next)
              #valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
              valTab.append(CDisplayListItem('Next', next_page.split('=')[-1], CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'bravoporn' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.bravoporn.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'bravoporn.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'bravoporn.cookie', 'bravoporn.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not '/c/' in phUrl: continue
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phTitle: phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              if phTitle=='': continue
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'https:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl 
              if phImage.startswith('//'): phImage = 'http:' + phImage + '/' 
              if phImage.startswith('/'): phImage = self.MAIN_URL + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl+'?sort_by=post_date'],'bravoporn-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Popular ---","Popular",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/most-popular/'],             'bravoporn-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Newest ---","Newest",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/latest-updates/'],             'bravoporn-clips',    '',None))
           self.SEARCH_proc='bravoporn-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'bravoporn-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.bravoporn.com/s/?q=%s' % url.replace(' ','+'), 'bravoporn-clips')
           return valTab              
        if 'bravoporn-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'bravoporn.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'bravoporn.cookie', 'bravoporn.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next = self.cm.ph.getSearchGroups(data, '''<a href=['"]([^"^']+?)['"]\sclass="next nopop"''', 1, True)[0] 
           n = 'class="video_block'
           s = '<div class="video-rating pull-right'
           if not n in data and not s in data:  return valTab
           if n in data: data = data.split(n)
           if s in data: data = data.split(s)
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''time">([^>]+?)<''', 1, True)[0].strip()
              Added = self.cm.ph.getSearchGroups(item, '''added"><em>([^>]+?)<''', 1, True)[0].strip()
              if not Added: Added = self.cm.ph.getSearchGroups(item, '''pull-left">([^>]+?)<''', 1, True)[0].strip()
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+'] '+decodeHtml(phTitle)+'\n'+Added,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              #printDBG( 'Host listsItems next: '+next )
              if next.startswith('/'): next = self.MAIN_URL + next
              valTab.append(CDisplayListItem(_("Next page"), 'Page: '+next.split('/')[-2], CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))                
           return valTab

        if 'bravoteens' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.bravoteens.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'bravoteens.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'bravoteens.cookie', 'bravoteens.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           data = data.split('<div class="preview-item">')
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phTitle: phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'https:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl 
              if phImage.startswith('//'): phImage = 'https:' + phImage
              if phImage.startswith('/'): phImage = self.MAIN_URL + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl+'?sort_by=post_date'],'bravoteens-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/top/'],             'bravoteens-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Popular ---","Popular",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/popular/'],             'bravoteens-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- New ---","New",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/new/'],             'bravoteens-clips',    '',None))
           self.SEARCH_proc='bravoteens-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'bravoteens-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.bravoteens.com/search/?q=%s' % url.replace(' ','+'), 'bravoteens-clips')
           return valTab              
        if 'bravoteens-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'bravoteens.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'bravoteens.cookie', 'bravoteens.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next = self.cm.ph.getDataBeetwenMarkers(data, 'class="pagination', '</div>', False)[1]
           n = 'class="preview-item"'
           s = '<div class="video-rating pull-right'
           if not n in data and not s in data:  return valTab
           if n in data: data = data.split(n)
           if s in data: data = data.split(s)
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''time">([^>]+?)<''', 1, True)[0].strip()
              Added = self.cm.ph.getSearchGroups(item, '''date">([^>]+?)<''', 1, True)[0].strip()
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+'] '+decodeHtml(phTitle)+'\n'+Added,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              try:
                 next_page = re.compile('</span>.+?<a href="(.+?)"', re.DOTALL).findall(next)[-1]
                 if next_page.startswith('/'): next_page = self.MAIN_URL + next_page
                 valTab.append(CDisplayListItem(_("Next page"), 'Page: '+next_page.split('/')[-2], CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
              except Exception:
                 printExc()
           return valTab

        if 'sleazyneasy' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.sleazyneasy.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'sleazyneasy.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'sleazyneasy.cookie', 'sleazyneasy.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           data = data.split('<div class="thumb">')
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phTitle: phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'https:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl 
              if phImage.startswith('//'): phImage = 'https:' + phImage
              if phImage.startswith('/'): phImage = self.MAIN_URL + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl+'?sort_by=post_date'],'sleazyneasy-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/top-rated/'],             'sleazyneasy-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Popular ---","Popular",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/most-popular/'],             'sleazyneasy-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- New ---","New",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/latest-updates/'],             'sleazyneasy-clips',    '',None))
           self.SEARCH_proc='sleazyneasy-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'sleazyneasy-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.sleazyneasy.com/search/?q=%s' % url.replace(' ','+'), 'sleazyneasy-clips')
           return valTab              
        if 'sleazyneasy-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'sleazyneasy.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'sleazyneasy.cookie', 'sleazyneasy.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next = self.cm.ph.getDataBeetwenMarkers(data, 'class="pager', '</div>', False)[1]
           n = '<span class="thumb-info">'
           s = '<div class="video-rating pull-right'
           if not n in data and not s in data:  return valTab
           if n in data: data = data.split(n)
           if s in data: data = data.split(s)
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](https://www.sleazyneasy.com/videos/[^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              if phTitle=='ASACP': continue
              phImage = self.cm.ph.getSearchGroups(item, '''data-poster=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''<i>([^>]+?)<''', 1, True)[0].strip()
              Added = self.cm.ph.getSearchGroups(item, '''truncate">([^>]+?)<''', 1, True)[0].strip()
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+'] '+decodeHtml(phTitle)+'\n'+Added,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              try:
                 next_page = re.compile('href="(.+?)"', re.DOTALL).findall(next)[-1]
                 if next_page.startswith('/'): next_page = self.MAIN_URL + next_page
                 valTab.append(CDisplayListItem(_("Next page"), 'Page: '+next_page.split('/')[-2], CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
              except Exception:
                 printExc()
           return valTab

        if 'vjav' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://vjav.com/main/'
           COOKIEFILE = os_path.join(GetCookieDir(), 'vjav.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'vjav.cookie', 'VJAV.COM', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           data = data.split('<li class="header__list-item">')
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phTitle: phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'https:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl 
              if phImage.startswith('//'): phImage = 'https:' + phImage
              if phImage.startswith('/'): phImage = self.MAIN_URL + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl+'?sort_by=post_date'],'vjav-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/top-rated/'],             'vjav-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Popular ---","Popular",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/most-popular/'],             'vjav-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- New ---","New",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/latest-updates/'],             'vjav-clips',    '',None))
           self.SEARCH_proc='vjav-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'vjav-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.vjav.com/search/?q=%s' % url.replace(' ','+'), 'vjav-clips')
           return valTab              
        if 'vjav-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'vjav.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'vjav.cookie', 'vjav.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next = self.cm.ph.getDataBeetwenMarkers(data, '<li class="next">', '</li>', False)[1]
           n = 'data-id='
           s = '<div class="video-rating pull-right'
           if not n in data and not s in data:  return valTab
           if n in data: data = data.split(n)
           if s in data: data = data.split(s)
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              if phTitle=='ASACP': continue
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''duration">([^>]+?)<''', 1, True)[0].strip()
              Added = self.cm.ph.getSearchGroups(item, '''truncate">([^>]+?)<''', 1, True)[0].strip()
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+'] '+decodeHtml(phTitle)+'\n'+Added,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              try:
                 page = self.cm.ph.getSearchGroups(str(next), '''page:([^"^']+?)['"]''')[0]
                 url = url.replace(url.split('/')[-1],'')
                 next = url + '?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=post_date&from='+page
                 valTab.append(CDisplayListItem('Next', 'Page : '+page, CDisplayListItem.TYPE_CATEGORY, [next], name, '', 'Next'))  
              except Exception:
                 printExc()
           return valTab

        if 'javhoho' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://javhoho.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'javhoho.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'javhoho.cookie', 'javhoho.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           data = data.split('<a class="item')
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phTitle: phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'https:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl 
              if phImage.startswith('//'): phImage = 'https:' + phImage
              if phImage.startswith('/'): phImage = self.MAIN_URL + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl+'?sort_by=post_date'],'javhoho-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Free Asian Porn ---","Free Asian Porn",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/category/free-asian-porn/'],             'javhoho-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Free Korean Porn ---","Free Korean Porn",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/category/free-korean-porn/'],             'javhoho-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Free Chinese Porn ---","Free Chinese Porn",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/category/free-chinese-porn/'],             'javhoho-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Free JAV Censored ---","Free JAV Censored",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/category/free-jav-censored/'],             'javhoho-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Free JAV Uncensored ---","Free JAV Uncensored",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/category/free-jav-uncensored/'],             'javhoho-clips',    '',None))
           self.SEARCH_proc='javhoho-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'javhoho-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://javhoho.com/search/%s/' % url.replace(' ','+'), 'javhoho-clips')
           return valTab              
        if 'javhoho-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'javhoho.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'javhoho.cookie', 'javhoho.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next = self.cm.ph.getSearchGroups(data, '''<link rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
           n = '<div id="post-'
           s = '<div class="video-rating pull-right'
           if not n in data and not s in data:  return valTab
           if n in data: data = data.split(n)
           if s in data: data = data.split(s)
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              if phTitle=='ASACP': continue
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''duration">([^>]+?)<''', 1, True)[0].strip()
              Added = self.cm.ph.getSearchGroups(item, '''date">([^>]+?)<''', 1, True)[0].strip()
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+'] '+decodeHtml(phTitle)+'\n'+Added,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              try:
                 valTab.append(CDisplayListItem('Next', 'Page : '+next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', 'Next'))  
              except Exception:
                 printExc()
           return valTab 
   
        if 'forcedcelebs' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://forcedcelebs.net'
           COOKIEFILE = os_path.join(GetCookieDir(), 'forcedcelebs.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           data = data.split('<a class="item')
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phTitle: phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'https:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl 
              if phImage.startswith('//'): phImage = 'https:' + phImage
              if phImage.startswith('/'): phImage = self.MAIN_URL + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl+'?sort_by=post_date'],'forcedcelebs-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           #valTab.insert(0,CDisplayListItem("--- Free Scenes ---","Free Scenes",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos/free'],             'forcedcelebs-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Celebrity Scenes ---","Celebrity Scenes",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos/celebrities'],             'forcedcelebs-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Porn Rape Scenes ---","Porn Rape Scenes",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos/pornrape'],             'forcedcelebs-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Porn Scenes ---","Porn Scenes",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos/porn'],             'forcedcelebs-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Rape Scenes ---","Rape Scenes",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos/rape'],             'forcedcelebs-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Incest Scenes ---","Incest Scenes",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos/incest'],             'forcedcelebs-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Forced Scenes ---","Forced Scenes",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos/forced'],             'forcedcelebs-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Home ---","Home",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL],             'forcedcelebs-clips',    '',None))
           self.SEARCH_proc='forcedcelebs-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'forcedcelebs-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://forcedcelebs.net/search?query=%s' % url.replace(' ','+'), 'forcedcelebs-clips')
           return valTab              
        if 'forcedcelebs-clips' == name:
           COOKIEFILE = os_path.join(GetCookieDir(), 'forcedcelebs.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           tmp = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a ', '</a>')
           next = ''
           for item in tmp:
              if '&raquo;' not in item: continue
              next = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''')[0]
              if next.startswith('/'): next = self.MAIN_URL + next
           tmp = '' 
           n = '<div class="thumb">'
           s = '<div class="video-rating pull-right'
           if not n in data and not s in data:  return valTab
           if n in data: data = data.split(n)
           if s in data: data = data.split(s)
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              if phTitle=='ASACP': continue
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''duration">([^>]+?)<''', 1, True)[0].strip()
              Added = self.cm.ph.getSearchGroups(item, '''date">([^>]+?)<''', 1, True)[0].strip()
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+'] '+decodeHtml(phTitle)+'\n'+Added,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              try:
                 valTab.append(CDisplayListItem(_("Next page"), 'Page : '+next.split('=')[-1], CDisplayListItem.TYPE_CATEGORY, [next], name, '', 'Next'))  
              except Exception:
                 printExc()
           return valTab 

        if 'familyporn' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://familyporn.tv'
           COOKIEFILE = os_path.join(GetCookieDir(), 'familyporn.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           data2 = data.split('<div class="th">')
           if len(data2): del data2[0]
           for item in data2:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phTitle: phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'https:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl 
              if phImage.startswith('//'): phImage = 'https:' + phImage
              if phImage.startswith('/'): phImage = self.MAIN_URL + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl+'?sort_by=post_date'],'familyporn-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not '/tags/' in phUrl: continue
              phTitle = self._cleanHtmlStr(item).strip()+'   [tag]'
              if phUrl.startswith('//'): phUrl = 'https:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl+'?sort_by=post_date'],'familyporn-clips', phImage, None)) 
           self.SEARCH_proc='familyporn-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'familyporn-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://familyporn.tv/search/%s/' % url.replace(' ','+'), 'familyporn-clips')
           return valTab              
        if 'familyporn-clips' == name:
           COOKIEFILE = os_path.join(GetCookieDir(), 'familyporn.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next = self.cm.ph.getDataBeetwenMarkers(data, 'class="page-current">', '</nav>', False)[1]
           n = 'data-item-id='
           s = '<div class="video-rating pull-right'
           if not n in data and not s in data:  return valTab
           if n in data: data = data.split(n)
           if s in data: data = data.split(s)
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              if phTitle=='': continue
              phImage = self.cm.ph.getSearchGroups(item, '''data-poster=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''time"></i><span>([^>]+?)<''', 1, True)[0].strip()
              Added = self.cm.ph.getSearchGroups(item, '''calendar"></i><span>([^>]+?)<''', 1, True)[0].strip()
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+'] '+decodeHtml(phTitle)+'\n'+Added,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              try:
                 tmp = self.cm.ph.getAllItemsBeetwenMarkers(next, '<li>', '</li>')
                 for item in tmp:
                    next = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''')[0]
                    if next=='': error
                    if next.startswith('/'): next = self.MAIN_URL + next
                 valTab.append(CDisplayListItem(_("Next page"), 'Page : '+next.split('/')[-2], CDisplayListItem.TYPE_CATEGORY, [next], name, '', 'Next'))  
              except Exception:
                 printExc()
           return valTab 

        if 'bitporno' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://bitporno.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'bitporno.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not '/cat-' in phUrl: continue
              phTitle = self._cleanHtmlStr(item).strip()
              if phUrl.startswith('//'): phUrl = 'https:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'bitporno-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           self.SEARCH_proc='bitporno-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'bitporno-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.bitporno.com/?q=%s' % url.replace(' ','+'), 'bitporno-clips')
           return valTab              
        if 'bitporno-clips' == name:
           COOKIEFILE = os_path.join(GetCookieDir(), 'bitporno.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return valTab
           #printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next = self.cm.ph.getDataBeetwenMarkers(data, 'class="pages-active"', 'class="pages"', False)[1]
           n = '<div class="entry square_entry'
           s = '<div class="video-rating pull-right'
           if not n in data and not s in data:  return valTab
           if n in data: data = data.split(n)
           if s in data: data = data.split(s)
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
              phTitle = self.cm.ph.getSearchGroups(item, '''<div style.*?>([^>]+?)<''', 1, True)[0]
              if phTitle=='': continue
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''time"></i><span>([^>]+?)<''', 1, True)[0].strip()
              Added = self.cm.ph.getSearchGroups(item, '''</a> - ([^>]+?)<''', 1, True)[0].strip()
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+'] '+decodeHtml(phTitle)+'\n'+Added,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              try:
                 next = self.cm.ph.getSearchGroups(next, '''href=['"]([^"^']+?)['"]''')[0]
                 if next.startswith('/'): next = self.MAIN_URL + next
                 valTab.append(CDisplayListItem(_("Next page"), 'Page : '+next.split('-')[-1], CDisplayListItem.TYPE_CATEGORY, [next], name, '', 'Next'))  
              except Exception:
                 printExc()
           return valTab 

        if 'ebuxxx' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://ebuxxx.net'
           COOKIEFILE = os_path.join(GetCookieDir(), 'ebuxxx.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'class="nav"', '</nav>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item).strip()
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'https:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl 
              if phImage.startswith('//'): phImage = 'https:' + phImage
              if phImage.startswith('/'): phImage = self.MAIN_URL + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl+'?sort_by=post_date'],'ebuxxx-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           self.SEARCH_proc='ebuxxx-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'ebuxxx-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://ebuxxx.net/index.php?do=search&subaction=search&story=%s' % url.replace(' ','+'), 'ebuxxx-clips')
           return valTab              
        if 'ebuxxx-clips' == name:
           COOKIEFILE = os_path.join(GetCookieDir(), 'ebuxxx.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next = self.cm.ph.getDataBeetwenMarkers(data, 'pnext', 'Next', False)[1]
           n = '<div class="item">'
           s = '<div class="video-rating pull-right'
           if not n in data and not s in data:  return valTab
           if n in data: data = data.split(n)
           if s in data: data = data.split(s)
           if len(data): del data[0]
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].split('|')[0].strip()
              if phTitle=='': continue
              if phUrl=='': continue
              phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''time">([^>]+?)<''', 1, True)[0].strip()
              Added = self.cm.ph.getSearchGroups(item, '''calendar"></i><span>([^>]+?)<''', 1, True)[0].strip()
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phImage.startswith('/'): phImage = self.MAIN_URL + phImage
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+decodeHtml(phTime)+'] '+decodeHtml(phTitle)+'\n'+Added,CDisplayListItem.TYPE_CATEGORY, [phUrl], 'ebuxxx-serwer', phImage, None)) 
           if next:
              try:
                 next = self.cm.ph.getSearchGroups(next, '''href=['"]([^"^']+?)['"]''')[0]
                 if next.startswith('/'): next = self.MAIN_URL + next
                 valTab.append(CDisplayListItem(_("Next page"), 'Page : '+next.split('/')[-2], CDisplayListItem.TYPE_CATEGORY, [next], name, '', 'Next'))  
              except Exception:
                 printExc()
           return valTab 
        if 'ebuxxx-serwer' == name:
           COOKIEFILE = os_path.join(GetCookieDir(), 'ebuxxx.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           phTitle = self.cm.ph.getSearchGroups(data, '''title" content=['"]([^"^']+?)['"]''', 1, True)[0] 
           phImage = self.cm.ph.getSearchGroups(data, '''image" content=['"]([^"^']+?)['"]''', 1, True)[0] 
           videoPage = self.cm.ph.getAllItemsBeetwenMarkers(data, '<iframe', '</iframe>')
           for item in videoPage:
              #printDBG( 'Host video: '+item )
              phUrl = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              phUrl = phUrl.replace ('&#58;', ':')
              printDBG( 'Ez a vege: '+phUrl )
              sts, data = self.get_Page(phUrl)
              printDBG( 'Adatok: '+data )
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phUrl),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           return valTab 
		   
        return valTab

    def getLinksForVideo(self, url):
        printDBG("Urllist.getLinksForVideo url[%s]" % url)
        videoUrls = []
        uri, params   = DMHelper.getDownloaderParamFromUrl(url)
        printDBG(params)
        uri = urlparser.decorateUrl(uri, params)
       
        urlSupport = self.up.checkHostSupport( uri )
        if 1 == urlSupport:
            retTab = self.up.getVideoLinkExt( uri )
            videoUrls.extend(retTab)
            printDBG("Video url[%s]" % videoUrls)
            return videoUrls

    def getParser(self, url):
        printDBG( 'Host getParser begin' )
        printDBG( 'Host getParser mainurl: '+self.MAIN_URL )
        printDBG( 'Host getParser url    : '+url )
        if url.startswith('http://www.4tube.com'):                    return 'http://www.4tube.com'
        if url.startswith('https://www.4tube.com'):                   return 'http://www.4tube.com'
        if url.startswith('https://www.fux.com'):                     return 'http://www.4tube.com'
        if url.startswith('http://www.pornerbros.com'):               return 'http://www.4tube.com'
        if url.startswith('https://www.pornerbros.com'):              return 'http://www.4tube.com'
        if url.startswith('https://www.porntube.com'):                return 'http://www.4tube.com'
        if url.startswith('https://www.ah-me.com'):                   return 'http://www.ah-me.com'
        if url.startswith('http://www.cliphunter.com'):               return 'http://www.cliphunter.com'
        if url.startswith('http://www.dachix.com'):                   return 'http://www.dachix.com'
        if url.startswith('http://www.drtuber.com'):                  return 'http://www.drtuber.com'
        if url.startswith('http://www.eporner.com'):                  return 'http://www.eporner.com'
        if url.startswith('http://www.yourupload.com'):               return 'https://www.yourupload.com'
        if url.startswith('http//yourupload.com'):                    return 'https://www.yourupload.com'
        if url.startswith('https://www.yourupload.com'):              return 'https://www.yourupload.com'
        if url.startswith('https://yourupload.com'):                  return 'https://www.yourupload.com'
        if url.startswith('https://www.hclips.com'):                  return 'http://www.hclips.com'
        if url.startswith('https://hclips.com'):                      return 'http://www.hclips.com'
        if url.startswith('http://www.hdporn.net'):                   return 'http://www.hdporn.net'
        if url.startswith('http://hdsite.net'):                       return 'https://hdsite.net'
        if url.startswith('https://hdsite.net'):                      return 'https://hdsite.net'
        if url.startswith('http://www.hdzog.com'):                    return 'http://www.hdzog.com'
        if url.startswith('http://hentaigasm.com'):                   return 'http://hentaigasm.com'
        if url.startswith('http://www.homemoviestube.com'):           return 'http://www.homemoviestube.com'
        if url.startswith('http://hotmovs.com'):                      return 'http://www.hdzog.com'
        if url.startswith('https://www.katestube.com'):               return 'https://www.katestube.com'
        if url.startswith('http://www.katestube.com'):                return 'https://www.katestube.com'
        if url.startswith('https://www.koloporno.com'):               return 'https://www.koloporno.com'
        if url.startswith('https://mangovideo'):                      return 'https://mangovideo'
        if url.startswith('https://www.pinflix.com'):                 return 'https://www.pinflix.com'
        if url.startswith('https://videos.porndig.com'):              return 'https://porndig.com'
        if url.startswith('https://www.playvids.com'):                return 'https://www.playvids.com'
        if url.startswith('https://porndoe.com'):                     return 'https://porndoe.com'
        if url.startswith('https://porndoe.com'):                     return 'https://porndoe.com'
        if url.startswith('https://www.porndoe.com'):                 return 'https://porndoe.com'
        if url.startswith('http://www.pornhd.com'):                   return 'http://www.pornhd.com'
        if url.startswith('http://www.pornhub.com/embed/'):           return 'http://www.pornhub.com/embed/'
        if url.startswith('https://www.pornhub.com/embed/'):          return 'http://www.pornhub.com/embed/'
        if url.startswith('http://pl.pornhub.com/embed/'):            return 'http://www.pornhub.com/embed/'
        if url.startswith('http://pl.pornhub.com'):                   return 'http://www.pornhub.com'
        if url.startswith('http://www.pornhub.com'):                  return 'http://www.pornhub.com'
        if url.startswith('https://www.pornhub.com'):                 return 'http://www.pornhub.com'
        if url.startswith('http://m.pornhub.com'):                    return 'http://m.pornhub.com'
        if url.startswith('http://pornicom.com'):                     return 'http://pornicom.com'
        if url.startswith('https://pornicom.com'):                    return 'http://pornicom.com'
        if url.startswith('http://www.pornicom.com'):                 return 'http://pornicom.com'
        if url.startswith('https://www.pornicom.com'):                return 'http://pornicom.com'
        if url.startswith('https://www.pornoxo.com'):                 return 'https://www.pornoxo.com'
        if url.startswith('http://www.pornrabbit.com'):               return 'http://www.pornrabbit.com'
        if url.startswith('https://www.pornrewind.com'):              return 'https://www.pornrewind.com'
        if url.startswith('https://www.realgfporn.com'):              return 'https://www.realgfporn.com'
        if url.startswith('http://embed.redtube.com'):                return 'http://embed.redtube.com'
        if url.startswith('http://www.redtube.com'):                  return 'http://www.redtube.com'
        if url.startswith('https://spankbang.com'):                   return 'https://spankbang.com'
        if url.startswith('http://www.thumbzilla.com'):               return 'http://www.thumbzilla.com'
        if url.startswith('http://www.tnaflix.com'):                  return 'https://www.tnaflix.com'
        if url.startswith('https://alpha.tnaflix.com'):               return 'https://alpha.tnaflix.com'
        if url.startswith('http://www.tube8.com/embed/'):             return 'http://www.tube8.com/embed/'
        if url.startswith('http://www.tube8.com'):                    return 'http://www.tube8.com'
        if url.startswith('http://m.tube8.com'):                      return 'http://m.tube8.com'
        if url.startswith('https://www.tube8.com'):                   return 'http://www.tube8.com'
        if url.startswith('https://pornone.com'):                     return 'https://pornone.com'
        if url.startswith('http://xhamster.com'):                     return 'http://xhamster.com'
        if url.startswith('https://xhamster.com'):                    return 'http://xhamster.com'
        if url.startswith('http://www.xnxx.com'):                     return 'http://www.xnxx.com'
        if url.startswith('http://www.xvideos.com'):                  return 'http://www.xvideos.com'
        if url.startswith('https://porngo.com'):                      return 'https://porngo.com'
        if url.startswith('http://www.youjizz.com'):                  return 'http://www.youjizz.com'
        if url.startswith('http://www.youporn.com/embed/'):           return 'http://www.youporn.com/embed/'
        if url.startswith('http://www.youporn.com'):                  return 'http://www.youporn.com'
        if url.startswith('https://www.youporn.com'):                 return 'http://www.youporn.com'
        if url.startswith('https://sxyprn.com'):                      return 'https://yourporn.sexy'
        if url.startswith('https://mini.zbiornik.com'):               return 'https://mini.zbiornik.com'
        if url.startswith('http://sexkino.to'):                       return 'http://sexkino.to'
        if url.startswith('http://www.plashporn.com'):                return 'http://sexkino.to'
        if url.startswith('http://www.alphaporno.com'):               return 'http://www.tubewolf.com'
        if url.startswith('http://crocotube.com'):                    return 'http://www.tubewolf.com'
        if url.startswith('http://www.tubewolf.com'):                 return 'http://www.tubewolf.com'
        if url.startswith('http://zedporn.com'):                      return 'http://www.tubewolf.com'
        if url.startswith('https://www.alphaporno.com'):               return 'http://www.tubewolf.com'
        if url.startswith('https://crocotube.com'):                    return 'http://www.tubewolf.com'
        if url.startswith('https://www.tubewolf.com'):                 return 'http://www.tubewolf.com'
        if url.startswith('https://zedporn.com'):                      return 'http://www.tubewolf.com'
        if url.startswith('https://www.ashemaletube.com'):            return 'https://www.ashemaletube.com'
        if url.startswith('https://upstream.to'):                     return 'https://upstream.to'
        if url.startswith('https://prostream.to'):                    return 'https://prostream.to'

# URLPARSER
        if url.startswith('https://gounlimited.to'):                  return 'xxxlist.txt'
        if url.startswith('http://gounlimited.to'):                  return 'xxxlist.txt'
        if url.startswith('http://openload.co'):                      return 'xxxlist.txt'
        if url.startswith('https://oload.tv'):                        return 'xxxlist.txt'
        if url.startswith('http://www.cda.pl'):                       return 'xxxlist.txt'
        if url.startswith('http://hqq.tv'):                           return 'xxxlist.txt'
        if url.startswith('https://hqq.tv'):                          return 'xxxlist.txt'
        if url.startswith('https://www.rapidvideo.com'):              return 'xxxlist.txt'
        if url.startswith('http://videomega.tv'):                     return 'xxxlist.txt'
        if url.startswith('http://www.flashx.tv'):                    return 'xxxlist.txt'
        if url.startswith('http://streamcloud.eu'):                   return 'xxxlist.txt'
        if url.startswith('http://thevideo.me'):                      return 'xxxlist.txt'
        if url.startswith('https://vidoza.net'):                      return 'xxxlist.txt'
        if url.startswith('http://fileone.tv'):                       return 'xxxlist.txt'
        if url.startswith('https://fileone.tv'):                      return 'xxxlist.txt'
        if url.startswith('https://streamcherry.com'):                return 'xxxlist.txt'
        if url.startswith('https://vk.com'):                          return 'xxxlist.txt'
        if url.startswith('https://www.fembed.com'):                  return 'xxxlist.txt'
        if url.startswith('https://videobin.co'):                     return 'https://videobin.co'
        if url.startswith('http://dato.porn'):                        return 'http://dato.porn'
        if url.startswith('https://dato.porn'):                       return 'http://dato.porn'
        if url.startswith('http://datoporn.co'):                      return 'http://dato.porn'
        if url.startswith('https://datoporn.co'):                     return 'http://dato.porn'
        if url.startswith('http://datoporn.com'):                     return 'http://dato.porn'
        if url.startswith('https://datoporn.com'):                    return 'http://dato.porn'
        if url.startswith('https://vidlox.tv'):                       return 'https://vidlox.tv'
        if self.MAIN_URL == 'https://www.freeomovie.to/':             return 'xxxlist.txt'
        if self.MAIN_URL == 'https://streamporn.pw':                  return 'xxxlist.txt' 
        if self.MAIN_URL == 'https://onlinepornfree.xyz':             return 'xxxlist.txt' 
        if self.MAIN_URL == 'http://www.xxxstreams.org':              return 'xxxlist.txt' 
        if self.MAIN_URL == 'https://pandamovie.info':                return 'xxxlist.txt' 
        if self.MAIN_URL == 'http://fullxxxmovies.net':               return 'xxxlist.txt'
        if self.MAIN_URL == 'https://www.pornrewind.com':             return 'xxxlist.txt'
        if self.MAIN_URL == 'http://www.pornfromczech.com':           return 'xxxlist.txt' 
        if self.MAIN_URL == 'http://netflixporno.net':                return 'xxxlist.txt'
        if self.MAIN_URL == 'https://watchpornx.com':                 return 'xxxlist.txt'
        if self.MAIN_URL == 'https://ebuxxx.net':                     return 'xxxlist.txt'

# A TO DO ...
        if url.startswith('http://www.slutsxmovies.com/embed/'): return 'http://www.nuvid.com'
        if url.startswith('http://www.cumyvideos.com/embed/'):   return 'http://www.nuvid.com'
        #if url.startswith('http://www.x3xtube.com'):         return 'file: '
        if url.startswith('http://www.nuvid.com'):           return 'http://www.nuvid.com'
        if url.startswith('http://www.wankoz.com'):          return 'file: '
        if url.startswith('http://hornygorilla.com'):        return 'file: '
        #if url.startswith('http://www.vikiporn.com'):        return '1file: "'
        if url.startswith('http://www.fetishshrine.com'):    return 'file: '
        if url.startswith('http://www.sunporno.com'):        return 'http://www.sunporno.com'
        if url.startswith('http://theclassicporn.com'):      return "video_url: '"
        if url.startswith('http://www.faphub.xxx'):          return 'http://www.faphub.xxx'
        if url.startswith('http://www.sleazyneasy.com'):     return 'file: '
        if url.startswith('http://www.proporn.com'):         return 'http://www.proporn.com'
        if url.startswith('http://www.tryboobs.com'):        return "video_url: '"
        if url.startswith('http://www.viptube.com'):         return 'http://www.nuvid.com'
        if url.startswith('http://pervclips.com'):           return 'http://www.wankoz.com'
        if url.startswith('http://www.jizz.us'):             return 'http://www.x3xtube.com'
        if url.startswith('http://www.pornstep.com'):        return 'videoFile="'
        if url.startswith('http://www.azzzian.com'):         return "video_url: '"
        if url.startswith('http://www.porndreamer.com'):     return 'http://www.x3xtube.com'
        if url.startswith('http://www.tubeon.com'):          return 'http://www.tubeon.com'
        if url.startswith('http://www.finevids.xxx'):        return "video_url: '"
        if url.startswith('http://www.pornwhite.com'):       return 'file: '
        if url.startswith('http://www.xfig.net'):            return 'videoFile="'
        if url.startswith('http://www.pornoid.com'):         return "video_url: '"
        if url.startswith('http://tubeq.xxx'):               return 'http://www.faphub.xxx'
        if url.startswith('http://www.wetplace.com'):        return "video_url: '"
        if url.startswith('http://sexylies.com'):            return 'http://sexylies.com'
        if url.startswith('http://www.eskimotube.com'):      return 'http://www.eskimotube.com'
        if url.startswith('http://www.pornalized.com'):      return "video_url: '"
        if url.startswith('http://www.porn5.com'):           return 'http://www.porn5.com'
        if url.startswith('http://www.pornyeah.com'):        return 'http://www.pornyeah.com'
        if url.startswith('http://www.porn.com'):            return 'http://www.porn5.com'
        if url.startswith('http://www.yeptube.com'):         return 'http://www.yeptube.com'
        if url.startswith('http://www.pornpillow.com'):      return 'http://www.pornpillow.com'
        if url.startswith('http://porneo.com'):              return 'http://www.nuvid.com'
        if url.startswith('http://www.5fing.com'):           return 'file: '
        if url.startswith('http://www.pornroxxx.com'):       return "0p'  : '"
        if url.startswith('http://www.hd21.com'):            return "0p'  : '"
        if url.startswith('http://www.pornrox.com'):         return "0p'  : '"
        if url.startswith('http://www.flyflv.com'):          return 'http://www.flyflv.com'
        if url.startswith('http://www.xtube.com'):           return 'https://vidlox.tv'
        if url.startswith('http://xxxkingtube.com'):         return 'http://xxxkingtube.com'
        if url.startswith('http://www.boyfriendtv.com'):     return 'source src="'
        if url.startswith('http://pornxs.com'):              return 'http://pornxs.com'
        if url.startswith('http://pornsharing.com'):         return 'http://pornsharing.com'
        if url.startswith('http://www.vivatube.com'):        return 'http://vivatube.com'
        if url.startswith('http://www.clipcake.com'):        return 'videoFile="'
        if url.startswith('http://www.cliplips.com'):        return 'videoFile="'
        if url.startswith('http://www.sheshaft.com'):        return 'file: '
        if url.startswith('http://www.vid2c.com'):           return 'videoFile="'
        if url.startswith('http://www.bonertube.com'):       return 'videoFile="'

# Test mjpg
        if url.endswith('.mjpg'):                            return 'mjpg_stream'
        if url.endswith('.cgi'):                             return 'mjpg_stream'
        if self.MAIN_URL == 'http://hotmovs.com':            return 'http://www.hdzog.com'
        if self.MAIN_URL == 'https://pornone.com':         return self.MAIN_URL
        if self.MAIN_URL == 'https://sxyprn.com':            return self.MAIN_URL
        if self.MAIN_URL == 'http://www.moviefap.com':       return self.MAIN_URL
        if self.MAIN_URL == 'http://www.homemoviestube.com': return self.MAIN_URL
        if self.MAIN_URL == 'http://www.hdzog.com':          return self.MAIN_URL
        if self.MAIN_URL == 'https://www.4tube.com':         return 'http://www.4tube.com'
        if self.MAIN_URL == 'https://www.fux.com':           return 'http://www.4tube.com'
        if self.MAIN_URL == 'https://www.pornerbros.com':    return 'http://www.4tube.com'
        if self.MAIN_URL == 'https://www.porntube.com':      return 'http://www.4tube.com'
        if self.MAIN_URL == 'https://www.playvids.com':      return self.MAIN_URL
        if self.MAIN_URL == 'https://www.realgfporn.com':    return self.MAIN_URL
        if self.MAIN_URL == 'http://tubepornclassic.com':    return 'http://tubepornclassic.com'
        if self.MAIN_URL == 'https://www.koloporno.com':     return self.MAIN_URL
        if self.MAIN_URL == 'https://www.pornomenge.com':    return self.MAIN_URL
        if self.MAIN_URL == 'http://www.yuvutu.com':         return self.MAIN_URL
        if self.MAIN_URL == 'https://www.camsoda.com/':      return self.MAIN_URL
        if self.MAIN_URL == 'http://www.thumbzilla.com':     return self.MAIN_URL
        if self.MAIN_URL == 'http://www.cliphunter.com':     return self.MAIN_URL
        if self.MAIN_URL == 'http://www.filmyporno.tv':      return self.MAIN_URL
        if self.MAIN_URL == 'https://porndoe.com':           return self.MAIN_URL
        if self.MAIN_URL == 'http://www.porntrex.com':       return self.MAIN_URL
        if self.MAIN_URL == 'http://porn720.net':            return self.MAIN_URL
        if self.MAIN_URL == 'http://rusporn.tv':             return self.MAIN_URL
        if self.MAIN_URL == 'https://www.extremetube.com':   return self.MAIN_URL
        if self.MAIN_URL == 'http://www.el-ladies.com':      return self.MAIN_URL
        if self.MAIN_URL == 'http://www.livejasmin.com':     return self.MAIN_URL
        if self.MAIN_URL == 'https://pl.bongacams.com':      return self.MAIN_URL
        if self.MAIN_URL == 'https://www.tnaflix.com':       return self.MAIN_URL
        if self.MAIN_URL == 'https://www.empflix.com':       return self.MAIN_URL
        if self.MAIN_URL == 'https://www.myfreecams.com/':   return self.MAIN_URL
        if self.MAIN_URL == 'http://www.drtuber.com':        return self.MAIN_URL
        if self.MAIN_URL == 'http://www.dachix.com':         return self.MAIN_URL
        if self.MAIN_URL == 'http://www.youjizz.com':        return self.MAIN_URL
        if self.MAIN_URL == 'https://www.cam4.com':          return self.MAIN_URL
        if self.MAIN_URL == 'http://www.amateurporn.net':    return self.MAIN_URL
        if self.MAIN_URL == 'https://chaturbate.com':        return self.MAIN_URL
        if self.MAIN_URL == 'http://www.ah-me.com':          return self.MAIN_URL
        if self.MAIN_URL == 'http://www.pornhd.com':         return self.MAIN_URL
        if self.MAIN_URL == 'http://www.pornrabbit.com':     return self.MAIN_URL
        if self.MAIN_URL == 'http://beeg.com':               return self.MAIN_URL
        if self.MAIN_URL == 'http://www.tube8.com':          return self.MAIN_URL
        if self.MAIN_URL == 'http://www.redtube.com':        return self.MAIN_URL
        if self.MAIN_URL == 'http://www.youporn.com':        return self.MAIN_URL
        if self.MAIN_URL == 'http://showup.tv':              return self.MAIN_URL
        if self.MAIN_URL == 'http://www.xnxx.com':           return self.MAIN_URL
        if self.MAIN_URL == 'http://www.xvideos.com':        return self.MAIN_URL
        if self.MAIN_URL == 'http://hentaigasm.com':         return self.MAIN_URL
        if self.MAIN_URL == 'http://xhamsterlive.com':       return 'http://xhamster.com/cams'
        if self.MAIN_URL == 'http://xhamster.com':           return self.MAIN_URL
        if self.MAIN_URL == 'http://www.eporner.com':        return self.MAIN_URL
        if self.MAIN_URL == 'http://www.pornhub.com':        return self.MAIN_URL
        if self.MAIN_URL == 'http://www.4tube.com':          return self.MAIN_URL
        if self.MAIN_URL == 'http://www.hdporn.net':         return self.MAIN_URL
        if self.MAIN_URL == 'http://m.tube8.com':            return self.MAIN_URL
        if self.MAIN_URL == 'http://m.pornhub.com':          return self.MAIN_URL
        if self.MAIN_URL == 'https://www.katestube.com':     return self.MAIN_URL
        if self.MAIN_URL == 'http://www.hclips.com':         return 'http://www.hclips.com'
        if self.MAIN_URL == 'https://www.pinflix.com':       return self.MAIN_URL
        if self.MAIN_URL == 'http://www.upornia.com':        return 'http://www.hdzog.com'
        if self.MAIN_URL == 'https://www.txxx.com':          return 'https://www.txxx.com'
        if self.MAIN_URL == 'https://www.sunporno.com':      return 'http://www.sunporno.com'
        if self.MAIN_URL == 'http://sexu.com':               return self.MAIN_URL
        if self.MAIN_URL == 'http://www.tubewolf.com':       return self.MAIN_URL
        if self.MAIN_URL == 'https://streamate.com':         return self.MAIN_URL 
        if self.MAIN_URL == 'https://momxxxfun.com':         return self.MAIN_URL 
        if self.MAIN_URL == 'https://www.mydirtyhobby.to':   return self.MAIN_URL 
        if self.MAIN_URL == 'http://www.adulttvlive.net':    return self.MAIN_URL
        if self.MAIN_URL == 'https://www.balkanjizz.com':    return self.MAIN_URL 
        if self.MAIN_URL == 'https://pornorussia.tv':        return self.MAIN_URL 
        if self.MAIN_URL == 'https://www.letmejerk.com':     return self.MAIN_URL 
        if self.MAIN_URL == 'https://www.gotporn.com':       return self.MAIN_URL 
        if self.MAIN_URL == 'https://www.analdin.com':       return self.MAIN_URL 
        if self.MAIN_URL == 'https://fapset.com':            return self.MAIN_URL
        if self.MAIN_URL == 'https://daftsex.com':           return self.MAIN_URL
        if self.MAIN_URL == 'https://lovehomeporn.com/':     return self.MAIN_URL
        if self.MAIN_URL == 'https://www.eroprofile.com':    return self.MAIN_URL
        if self.MAIN_URL == 'http://www.absoluporn.com':     return self.MAIN_URL 
        if self.MAIN_URL == 'https://www.amateurcool.com':   return self.MAIN_URL 
        if self.MAIN_URL == 'http://anybunny.com':           return self.MAIN_URL  
        if self.MAIN_URL == 'https://hqporner.com':          return self.MAIN_URL 
        if self.MAIN_URL == 'https://www.naked.com':         return self.MAIN_URL  
        if self.MAIN_URL == 'https://www.cumlouder.com':     return self.MAIN_URL
        if self.MAIN_URL == 'http://www.porn00.org':         return self.MAIN_URL
        if self.MAIN_URL == 'https://p720.net':              return self.MAIN_URL
        if self.MAIN_URL == 'https://pornopersik.com':       return 'https://p720.net'
        if self.MAIN_URL == 'https://anyporn.com':           return self.MAIN_URL
        if self.MAIN_URL == 'https://anon-v.com':            return self.MAIN_URL
        if self.MAIN_URL == 'https://www.bravoporn.com':     return 'https://anyporn.com'
        if self.MAIN_URL == 'https://www.bravoteens.com':    return 'https://anyporn.com'
        if self.MAIN_URL == 'https://www.sleazyneasy.com':   return 'https://www.sleazyneasy.com'
        if self.MAIN_URL == 'https://vjav.com':              return 'http://www.hdzog.com'
        if self.MAIN_URL == 'https://javhoho.com':           return self.MAIN_URL
        if self.MAIN_URL == 'https://forcedcelebs.net':      return self.MAIN_URL
        if self.MAIN_URL == 'https://porngo.com':            return self.MAIN_URL
        if self.MAIN_URL == 'https://familyporn.tv':         return self.MAIN_URL
        if self.MAIN_URL == 'https://bitporno.com':         return self.MAIN_URL


        return ''

    def getResolvedURL(self, url):
        printDBG( 'Host getResolvedURL begin' )
        printDBG( 'Host getResolvedURL url: '+url )
        videoUrl = ''
        parser = self.getParser(url)
        printDBG( 'Host getResolvedURL parser: '+parser )
        #if parser == '': return url

        if 'gounlimited.to' in url:
            if 'embed' not in url:
                url = 'https://gounlimited.to/embed-{0}.html'.format(url.split('/')[3])
        if 'clipwatching.com' in url:
            if 'embed' not in url:
                video_id = self.cm.ph.getSearchGroups(url, 'clipwatching.com/([A-Za-z0-9]{12})[/.-]')[0]
                url = 'http://clipwatching.com/embed-{0}.html'.format(video_id)

        if parser == 'mjpg_stream':
           try:
              stream=urllib.urlopen(url)
              bytes=''
              while True:
                 bytes+=stream.read(1024)
                 a = bytes.find('\xff\xd8')
                 b = bytes.find('\xff\xd9')
                 if a!=-1 and b!=-1:
                    jpg = bytes[a:b+2]
                    bytes= bytes[b+2:]
                    with open('/tmp/obraz.jpg', 'w') as titleFile:  
                       titleFile.write(jpg) 
                       return 'file:///tmp/obraz.jpg'
           except: pass
           return ''

        if parser == 'http://www.porntrex.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'porntrex.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'porntrex.cookie', 'porntrex.com', self.defaultParams)
           if not sts: return ''
           #printDBG( 'Host listsItems data: '+str(data) )
           if 'video is a private' in data:
              SetIPTVPlayerLastHostError(_(' This video is a private.'))
              return []
           if self.format4k:
              videoPage = self.cm.ph.getSearchGroups(data, '''video_alt_url5: ['"]([^"^']+?)['"]''')[0] 
              if videoPage:
                 printDBG( 'Host videoPage video_alt_url5 4k: '+videoPage )
                 return strwithmeta(videoPage, {'Referer':url})
              videoPage = self.cm.ph.getSearchGroups(data, '''video_alt_url4: ['"]([^"^']+?)['"]''')[0] 
              if videoPage:
                 printDBG( 'Host videoPage video_alt_url4 High HD: '+videoPage )
                 return strwithmeta(videoPage, {'Referer':url})
              videoPage = self.cm.ph.getSearchGroups(data, '''video_alt_url3: ['"]([^"^']+?)['"]''')[0] 
              if videoPage:
                 printDBG( 'Host videoPage video_alt_url3 Full High: '+videoPage )
                 return strwithmeta(videoPage, {'Referer':url})
           videoPage = self.cm.ph.getSearchGroups(data, '''video_alt_url2: ['"]([^"^']+?)['"]''')[0] 
           if videoPage:
              printDBG( 'Host videoPage video_alt_url2 HD: '+videoPage )
              return strwithmeta(videoPage, {'Referer':url})
           videoPage = self.cm.ph.getSearchGroups(data, '''video_alt_url: ['"]([^"^']+?)['"]''')[0] 
           if videoPage:
              printDBG( 'Host videoPage video_alt_url Medium: '+videoPage )
              return strwithmeta(videoPage, {'Referer':url})
           videoPage = self.cm.ph.getSearchGroups(data, '''video_url: ['"]([^"^']+?)['"]''')[0] 
           if videoPage:
              printDBG( 'Host videoPage video_url Low: '+videoPage )
              return strwithmeta(videoPage, {'Referer':url})
           return ''

        if parser == 'http://www.hclips.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'hclips.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'hclips.cookie', 'hclips.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           videoUrl = re.search('video_url":"([^"]+)', data).group(1)
           replacemap = {'M':'\u041c', 'A':'\u0410', 'B':'\u0412', 'C':'\u0421', 'E':'\u0415', '=':'~', '+':'.', '/':','}
           for key in replacemap:
               videoUrl = videoUrl.replace(replacemap[key], key)
           videoUrl = base64.b64decode(videoUrl)
           if videoUrl.startswith('//'): videoUrl = 'https:' + videoUrl
           if videoUrl.startswith('/'): videoUrl = 'https://hclips.com' + videoUrl
           return urlparser.decorateUrl(videoUrl, {'Referer': url})

        if parser == 'http://tubepornclassic.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'tubepornclassic.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'tubepornclassic.cookie', 'tubepornclassic.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           videoUrl = ph.search(data, '''video_url":"([^"]+?)"''')[0]
           replacemap = {'M':'\u041c', 'A':'\u0410', 'B':'\u0412', 'C':'\u0421', 'E':'\u0415', '=':'~', '+':'.', '/':','}
           for key in replacemap:
               videoUrl = videoUrl.replace(replacemap[key], key)
           videoUrl = base64.b64decode(videoUrl)
           if videoUrl.startswith('//'): videoUrl = 'https:' + videoUrl
           if videoUrl.startswith('/'): videoUrl = 'https://tubepornclassic.com' + videoUrl
           return urlparser.decorateUrl(videoUrl, {'Referer': url})

        if parser == 'http://www.hdzog.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'hdzog.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'hdzog.cookie', 'hdzog.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+str(data) )
           posturl = 'https://%s/sn4diyux.php' % url.split('/')[2]
           pC3 = re.search('''pC3:'([^']+)''', data)
           if not pC3: return ''
           pC3 = pC3.group(1)
           vidid = re.search('''video_id["|']?:\s?(\d+)''', data).group(1)
           postdata = '%s,%s' % (vidid, pC3)
           sts, data = self.getPage(posturl, 'hclips.cookie', 'hclips.com', self.defaultParams, post_data={'param': postdata})
           if not sts: return ''
           printDBG( 'Host listsItems data: '+str(data) )
           videoUrl = re.search('video_url":"([^"]+)', data).group(1)
           printDBG( 'Host videoUrl:%s' % videoUrl )
           replacemap = {'M':'\u041c', 'A':'\u0410', 'B':'\u0412', 'C':'\u0421', 'E':'\u0415', '=':'~', '+':'.', '/':','}
           for key in replacemap:
               videoUrl = videoUrl.replace(replacemap[key], key)
           videoUrl = base64.b64decode(videoUrl)
           return urlparser.decorateUrl(videoUrl, {'Referer': url})

        if parser == 'http://www.upornia.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'upornia.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           #printDBG( 'Host getResolvedURL data: '+data )
           
           try:
              video_url = self.cm.ph.getSearchGroups(data, '''var video_url=['"]([^"^']+?)['"]''')[0]
              hash = self.cm.ph.getSearchGroups(data, '''/get_file/(\d+/[^"^']+?)/''')[0] 
              #printDBG( 'Host video_url: '+video_url )
              decoder = 'Dpww3Dw64=function(b){var c="",d=0;/[^\u0410\u0412\u0421\u0415\u041cA-Za-z0-9\.\,\~]/g.exec(b)'\
              '&&console.log("error decoding url");b=b.replace(/[^\u0410\u0412\u0421\u0415\u041cA-Za-z0-9\.\,\~]/g,"");'\
              'do{var f="\u0410\u0412\u0421D\u0415FGHIJKL\u041cNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~".'\
              'indexOf(b.charAt(d++)),e="\u0410\u0412\u0421D\u0415FGHIJKL\u041cNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~".'\
              'indexOf(b.charAt(d++)),g="\u0410\u0412\u0421D\u0415FGHIJKL\u041cNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~".'\
              'indexOf(b.charAt(d++)),h="\u0410\u0412\u0421D\u0415FGHIJKL\u041cNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~".'\
              'indexOf(b.charAt(d++)),f=f<<2|e>>4,e=(e&15)<<4|g>>2,k=(g&3)<<6|h,c=c+String.fromCharCode(f);'\
              '64!=g&&(c+=String.fromCharCode(e));64!=h&&(c+=String.fromCharCode(k))}while(d<b.length);return unescape(c)};'
              js = decoder + '\n' + 'var video_url="'+video_url+'";\n'+'vidurl = (Dpww3Dw64(video_url));'  
              #printDBG( 'Host getResolvedURL js: '+js )
              urls = js_execute( js+ '\nfor (n in this){print(n+"="+this[n]+";");}')
              videoUrl = self.cm.ph.getSearchGroups(urls['data'], '''vidurl=([^"^']+?);''')[0]
              if hash: videoUrl = videoUrl.replace(videoUrl.split('/')[-6]+'/'+videoUrl.split('/')[-5],hash)
              if videoUrl: return videoUrl
           except Exception:
              printExc()
           printDBG( 'Host start embed' )
           videoPage = self.cm.ph.getSearchGroups(data, '''(https://upornia.com/embed/[^"^']+?)[&"]''')[0] 
           if not videoPage: videoPage = self.cm.ph.getSearchGroups(data, '''(https://www.txxx.com/embed/[^"^']+?)[&"]''')[0] 
           if videoPage:
              try: data2 = self.cm.getURLRequestData({ 'url': videoPage, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
              except:
                 printDBG( 'Host getResolvedURL query error url: '+videoPage )
                 return ''
              #printDBG( 'Host getResolvedURL data embed: '+data )
              videoUrl = self.cm.ph.getSearchGroups(data2, '''video_url=['"]([^"^']+?)['"]''')[0]
              if 'http' in videoUrl: return videoUrl
           printDBG( 'Host direct link' )
           videoPage = self.cm.ph.getSearchGroups(data, '''(https://upornia.com/get_file/[^"^']+?)['"]''')[0] 
           if videoPage: return videoPage
           videoPage = self.cm.ph.getSearchGroups(data, '''(https://www.txxx.com/get_file/[^"^']+?)['"]''')[0] 
           if videoPage: return videoPage
           return ''

        if parser == 'http://beeg.com':
           URL = url
           sts, data = self.get_Page(URL)
           if not sts: return
           printDBG( 'second beeg-clips data: '+data )
           if '"error"' in data: 
              URL = url.replace('/'+url.split('/')[-2], '')
              sts, data = self.get_Page(URL)
              if not sts: return
              printDBG( 'second beeg-clips data2: '+data )
              #SetIPTVPlayerLastHostError(_(' Video not found.'))
              #return []
           phUrl=''
           try:
              if data.startswith('{'): data = '['+data+']'
              result = byteify(simplejson.loads(data))
              for item in result:
                 if str(item["240p"]) != 'None': phUrl = str(item["240p"])
                 if str(item["480p"]) != 'None': phUrl = str(item["480p"])
                 if str(item["720p"]) != 'None': phUrl = str(item["720p"])
                 if self.beegfullhd: 
                    if str(item["1080p"]) != 'None': phUrl = str(item["1080p"])
                 if self.format4k:
                    if str(item["2160p"]) != 'None': phUrl = str(item["2160p"])
           except Exception:
              printExc()
           if phUrl== '':
              SetIPTVPlayerLastHostError(_(' Video not found.'))
              return []
           if phUrl.startswith('//'): phUrl = 'http:' + phUrl
           phUrl = phUrl.replace('{DATA_MARKERS}','data=pc.DE')
           if not self.beeg_salt: return phUrl
           key = re.search(r'/key=(.*?)%2Cend=', phUrl, 0) 
           key = key.group(1)
           printDBG( 'key encrypt : '+key )
           key = decrypt_key(key, self.beeg_salt)
           printDBG( 'key decrypt: '+key )
           videoUrl = re.sub(r'/key=(.*?)%2Cend=', '/key='+key+',end=', phUrl)
           return videoUrl
  
        if parser == 'http://showup.tv':
           COOKIEFILE = os_path.join(GetCookieDir(), 'showup.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           printDBG( 'Host getResolvedURL data: '+data )
           parse = re.search("var srvE = '(.*?)'", data, re.S)
           if parse:
              printDBG( 'Host Url: '+url)
              printDBG( 'Host rtmp: '+ parse.group(1))
              rtmp = parse.group(1)
           startChildBug = re.search("startChildBug\(user\.uid, '', '([\s\S]+?)'", data, re.I);
           if startChildBug:
              s = startChildBug.group(1)
              printDBG( 'Host startChildBug: '+ s)
              ip = ''
              t = re.search(r"(.*?):(.*?)", s, re.I)
              if t.group(1) == 'j12.showup.tv': ip = '94.23.171.122'
              if t.group(1) == 'j13.showup.tv': ip = '94.23.171.121'
              if t.group(1) == 'j11.showup.tv': ip = '94.23.171.115'
              if t.group(1) == 'j14.showup.tv': ip = '94.23.171.120'
              printDBG( 'Host IP: '+ip)
              port = s.replace(t.group(1)+':', '')
              printDBG( 'Host Port: '+port)
              modelName = url.replace('http://showup.tv/','')
              printDBG( 'Host modelName: '+modelName)

              libsPath = GetPluginDir('libs/')
              import sys
              sys.path.insert(1, libsPath)
              import websocket 
              wsURL1 = 'ws://'+s
              wsURL2 = 'ws://'+ip+':'+port
              printDBG( 'Host wsURL1: '+wsURL1)
              printDBG( 'Host wsURL2: '+wsURL2)
              ws = websocket.create_connection(wsURL2)

              zapytanie = '{ "id": 0, "value": ["", ""]}'
              zapytanie = zapytanie.decode("utf-8")
              printDBG( 'Host zapytanie1: '+zapytanie)
              ws.send(zapytanie) 
              result = ws.recv()
              printDBG( 'Host result1: '+result)

              zapytanie = '{ "id": 2, "value": ["%s"]}' % modelName
              zapytanie = zapytanie.decode("utf-8")
              printDBG( 'Host zapytanie2: '+zapytanie)
              ws.send(zapytanie) 
              result = ws.recv()
              printDBG( 'Host result2: '+result)

              playpath = re.search('value":\["(.*?)"', result)

              if playpath:
                 Checksum =  playpath.group(1)  
                 if len(Checksum)<30: 
                    for x in range(1, 10): 
                       ws.send(zapytanie)
                       result = ws.recv()
                       czas = re.search('(\d+)\[:\](\d+)\[', result )
                       if czas:
                          printDBG( 'Host czas.group(1): '+czas.group(1) )
                          printDBG( 'Host czas.group(2): '+czas.group(2) )
                          czas = int(czas.group(1)) - int(czas.group(2))
                          printDBG( 'Host a: '+str(czas) )
                          a = str(czas)
                          if a=='0': a = 'kilka'
                          Checksum = 'PRIVATE - Czekaj '+a+' sekund'
                          break
                    if Checksum=='' or Checksum=='failure': Checksum='OFFLINE'
                    ws.close() 
                    SetIPTVPlayerLastHostError(Checksum)
                    return []
                 videoUrl = 'rtmp://cdn-t0.showup.tv:1935/webrtc/'+Checksum+'_aac' # token=fake'
                 ws.close() 
                 try:
                    import commands
                    for x in range(1, 9): 
                       cmd = '/usr/bin/rtmpdump -B 1 -r "%s"' % videoUrl.replace('cdn-t0','cdn-t0'+str(x))
                       wow = commands.getoutput(cmd)
                       printDBG( 'HostXXX cmd > '+ cmd )
                       #printDBG( 'HostXXX rtmpdump > '+ wow )
                       if not 'StreamNotFound' in wow:
                          return videoUrl.replace('cdn-t0','cdn-t0'+str(x))+' live=1'
                       printDBG( 'HostXXX GUZIK ' )
                 except:
                    printDBG( 'HostXXX error commands.getoutput ' )
                 return videoUrl.replace('cdn-t0','cdn-t01')+' live=1'

           return ''

        def base_myfreecam(serwer, url):
           data = ''
           newurl = 'http://video%s.myfreecams.com:1935/NxServer/mfc_%s.f4v_aac/playlist.m3u8' % (serwer, url)
           try:
              data = urllib2.urlopen(newurl, timeout=1)
              #printDBG( 'Host data.meta:  '+str(data.meta) )
           except:
              printDBG( 'Host error newurl:  '+newurl )
           if data:
              return newurl

        if parser == 'https://www.myfreecams.com/':
           printDBG("Connecting to Chat Server:%s" % str(random.choice(self.chat_servers)))
           host = "Mozilla/5.0 (Linux; U; Android 4.1.1; en-us; androVM for VirtualBox ('Tablet' version with phone caps) Build/JRO03S) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30"
           videoUrl = myfreecam_start(url, str(random.choice(self.chat_servers)))
           if videoUrl != '':
              key = self.cm.ph.getSearchGroups(videoUrl, '''video([^"^']+?)\.''')[0] 
              id = self.cm.ph.getSearchGroups(videoUrl, '''mfc_([^"^']+?)\.''')[0] 
              printDBG( 'Host key:  '+key )
              printDBG( 'Host id:  '+id )
              referer = 'https://www.myfreecams.com/_html/player.html?broadcaster_id={0}&target=new_window&username={1}'.format(id, url)
              try:
                 server_type = None
                 value = None
                 if self.h5video_servers.get(str(key)):
                    value = self.h5video_servers[str(key)]
                    server_type = 'h5video_servers'
                    videoUrl = videoUrl.replace('video'+key,value)
                 elif self.wzobs_servers.get(str(key)):
                    value = self.wzobs_servers[str(key)]
                    server_type = 'wzobs_servers'
                    videoUrl = videoUrl.replace('video'+key,value)
                    videoUrl = videoUrl.replace('mfc_','mfc_a_')
                 elif self.ngvideo_servers.get(str(key)):
                    value = self.ngvideo_servers[str(key)]
                    server_type = 'ngvideo_servers'
                    SetIPTVPlayerLastHostError(_('Not supported.'))
                    return []
                 printDBG( 'value: %s server_type: %s' % (value, server_type) )
              except Exception:
                 printExc()
              printDBG( 'Host videoUrl:  '+videoUrl )
              videoUrl = strwithmeta(videoUrl, {'Origin': 'https://www.myfreecams.com'})
              videoUrl = strwithmeta(videoUrl, {'Cookie':self.cookieHeader})
              videoUrl = strwithmeta(videoUrl, {'iptv_proto':'m3u8', 'iptv_livestream':True})

              #videoUrl = strwithmeta(videoUrl, {'Cookie':self.cookieHeader+'gw=1; user_id=0; _gat_gtag_UA_295864_20=1;'})
              #videoUrl = strwithmeta(videoUrl, {'Origin': 'https://new.myfreecams.com', 'Cookie':self.cid, 'Referer':'https://new.myfreecams.com', 'User-Agent': ''})
              #videoUrl = urlparser.decorateUrl(videoUrl, {'Origin': 'https://new.myfreecams.com', 'iptv_proto':'m3u8', 'iptv_livestream':True, 'User-Agent':host, 'Referer':'https://new.myfreecams.com'})

              tmp = getDirectM3U8Playlist(videoUrl, checkExt=False, variantCheck=False, checkContent=True, sortWithMaxBitrate=99999999)
              for item in tmp:
                 printDBG( 'Host listsItems valtab: '  +str(item))
                 return item['url']
           return ''


        def _get_stream_uid(username):
           m = hashlib.md5(username.encode('utf-8') + str(time_time()).encode('utf-8'))
           return m.hexdigest()

        if parser == 'https://pl.bongacams.com':
           printDBG( 'Host url:  '+url )
           username = url 
           printDBG( 'Host username:  '+username )
           COOKIEFILE = os_path.join(GetCookieDir(), 'bongacams.cookie')
           host = 'Mozilla/5.0 (iPad; CPU OS 8_1_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B466 Safari/600.1.4'
           header = {'User-Agent': host, 'Accept':'text/html,application/json','Accept-Language':'en,en-US;q=0.7,en;q=0.3', 'Referer':'https://en.bongacams.com/'+username, 'Origin':'https://en.bongacams.com'} 
           self.defaultParams = { 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True }
           sts, data = self.cm.getPage('https://en.bongacams.com/'+username, self.defaultParams)
           if not sts: return ''
           #printDBG( 'Parser Bonga data: '+data ) 
           amf = self.cm.ph.getSearchGroups(data, '''MobileChatService\(\'\/([^"^']+?)\'\+\$''')[0] 
           if not amf: amf = 'tools/amf.php?x-country=pl&m=1&res='
           url_amf = 'https://en.bongacams.com/' + amf + str(random.randint(2100000, 3200000))
           printDBG( 'Host url_amf:  '+url_amf )
           postdata = {'method' : 'getRoomData', 'args[]' : username} 
           header = {'User-Agent': host, 'Accept':'text/html,application/xhtml+xml,application/xml,application/json','Accept-Language':'en,en-US;q=0.7,en;q=0.3','X-Requested-With':'XMLHttpRequest', 'Referer':'https://en.bongacams.com/'+username, 'Origin':'https://en.bongacams.com'} 
           self.defaultParams = { 'url': url_amf, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': True, 'return_data': True }
           sts, data = self.cm.getPage(url_amf, self.defaultParams, postdata)
           if not sts: return ''
           #printDBG( 'Parser Bonga link2: '+data ) 
           serwer = self.cm.ph.getSearchGroups(data, '''"videoServerUrl":['"]([^"^']+?)['"]''', 1, True)[0] 
           printDBG( 'Parser Bonga serwer: '+serwer ) 
           url_m3u8 = 'https:' + serwer.replace('\/','/') + '/hls/stream_' +username + '/playlist.m3u8'
           if serwer: 
              videoUrl = urlparser.decorateUrl(url_m3u8, {'User-Agent': host, 'Referer':'https://bongacams.com/'+username})
              if self.cm.isValidUrl(videoUrl): 
                 tmp = getDirectM3U8Playlist(videoUrl)
                 #if not tmp: return ''
                 try: tmp = sorted(tmp, key=lambda item: int(item.get('bitrate', '0')))
                 except Exception: pass
                 for item in tmp:
                    printDBG( 'Host listsItems valtab: '  +str(item))
                 try:
                    if item['bitrate']=='unknown': 
                       return ''
                    return item['url']
                    printDBG( 'item bitrate: '  +str(item['bitrate']))
                 except Exception: pass
           return ''

        if parser == 'http://www.livejasmin.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'livejasmin.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE, 'return_data': True}
           sts, data = self.getPage(url, 'livejasmin.cookie', 'livejasmin.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+str(data) )
           performerid = self.cm.ph.getSearchGroups(data, '''performerid":['"]([^"^']+?)['"]''', 1, True)[0] 
           sbip = self.cm.ph.getSearchGroups(data, '''sbip":['"]([^"^']+?)['"]''', 1, True)[0] 
           sbhash = self.cm.ph.getSearchGroups(data, '''sbhash":['"]([^"^']+?)['"]''', 1, True)[0] 
           #stream = urllib.unquote('https://dss-live-109-71-162-52.dditscdn.com/stream?url=rtmp%3A%2F%2F109.71.162.52%2FmemberChat%2FjasminSoniaCrystall3a6ac2233e19448a3ee26466ed126451%3FsessionId-7133bcde23b0f6ea7ee68440b313d4d1%7CclientInstanceId-44077313838477700147795168240074&stream=free%2Fstream_864_480_830&cid=420210&pid=83906493378')
           stream = 'https://dss-live-'+sbip.replace('.','-')+'.dditscdn.com/stream?url=rtmp://'+sbip+'/memberChat/'+performerid+sbhash
           #stream = 'https://dss-hls-'+sbip.replace('.','-')+'.dditscdn.com/h5live/http/playlist.m3u8'
           #self.defaultParams['max_data_size'] = 0
           sts, data = self.getPage(stream, 'livejasmin.cookie', 'livejasmin.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+str(data) )

           return data.meta['url']

           return ''

        if parser == 'https://www.cam4.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'cam4.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return ''
           self.page = 1
           printDBG( 'Host listsItems data: '+data )

           Url = self.cm.ph.getSearchGroups(data, '''hlsUrl: ['"]([^"^']+?)['"]''')[0]+'?referer=cam4.com&timestamp='+str(int(time_time()*1000))
           #Url = urlparser.decorateUrl(Url, {'User-Agent': host})
           if self.cm.isValidUrl(Url): 
              tmp = getDirectM3U8Playlist(Url, checkExt=False, variantCheck=False, checkContent=True, sortWithMaxBitrate=99999999)
              for item in tmp:
                 printDBG( 'Host listsItems valtab: '  +str(item))
                 return item['url'] #urlparser.decorateUrl(item['url'], {'User-Agent': host})
           return ''

        if parser == 'https://www.camsoda.com/':
            if 'rtmp' in url:
                rtmp = 1
            else:
                rtmp = 0
            url = url.replace('rtmp','')
            query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
            try: data = self.cm.getURLRequestData(query_data)
            except:
                printDBG( 'Host getResolvedURL query error url: '+url )
                return ''
            #printDBG( 'Host getResolvedURL data: '+data )
            dane = '['+data+']'
            #printDBG( 'Host listsItems json: '+dane )
            result = simplejson.loads(dane)
            if result:
                try:
                    for item in result:
                        token = str(item["token"])
                        app = str(item["app"])
                        serwer = str(item["edge_servers"][0])
                        #edge_servers2 = str(item["edge_servers"][1])
                        stream_name = str(item["stream_name"])
                        #printDBG( 'Host listsItems token: '+token )
                        #printDBG( 'Host listsItems app: '+app )
                        #printDBG( 'Host listsItems edge_servers1: '+serwer )
                        #printDBG( 'Host listsItems edge_servers2: '+edge_servers2 )
                        #printDBG( 'Host listsItems stream_name: '+stream_name )
                        name = re.sub('-enc.+', '', stream_name)
                        if rtmp == 0:
                            #Url = 'https://%s/%s/mp4:%s_mjpeg/playlist.m3u8?token=%s' % (serwer, app, stream_name, token )
                            Url = 'https://%s/%s/mp4:%s_aac/playlist.m3u8?token=%s' % (serwer, app, stream_name, token )
                            USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0'
                            Url = urlparser.decorateUrl(Url, {'User-Agent': USER_AGENT})
                            if self.cm.isValidUrl(Url): 
                                tmp = getDirectM3U8Playlist(Url)
                                for item in tmp:
                                    #printDBG( 'Host listsItems valtab: '  +str(item))
                                    if str(item["with"])=='0':
                                        SetIPTVPlayerLastHostError(' OFFLINE')
                                        return []
                                    return item['url']
                            SetIPTVPlayerLastHostError(' OFFLINE')
                            return []
                        else:
                            Url = 'rtmp://%s:1935/%s?token=%s/ playpath=?mp4:%s swfUrl=https://www.camsoda.com/lib/video-js/video-js.swf live=1 pageUrl=https://www.camsoda.com/%s' % (serwer, app, token, stream_name, name)
                            return Url
                except Exception: printExc()
            return ''

        if parser == 'xxxlist.txt':
           videoUrls = self.getLinksForVideo(url)
           if videoUrls:
              for item in videoUrls:
                 Url = item['url']
                 Name = item['name']
                 printDBG( 'Host url:  '+Url )
                 return Url
           return ''

        if parser == 'http://xhamster.com/cams':
           config='http://xhamsterlive.com/api/front/config'
           COOKIEFILE = os_path.join(GetCookieDir(), 'xhamsterlive.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(config)
           if not sts: return ''
           printDBG( 'Host listsItems data1: '+data )
           parse = re.search('"sessionHash":"(.*?)"', data, re.S) 
           if not parse: return ''
           sessionHash = parse.group(1) 
           printDBG( 'Host sessionHash: '+sessionHash )

           models='http://xhamsterlive.com/api/front/models'
           COOKIEFILE = os_path.join(GetCookieDir(), 'xhamsterlive.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(models)
           if not sts: return ''
           printDBG( 'Host listsItems data2: '+data )
           result = simplejson.loads(data)
           try:
              for item in result["models"]:
                 ID = str(item["id"]) 
                 Name = item["username"]
                 BroadcastServer = item["broadcastServer"]
                 swf_url = 'http://xhamsterlive.com/assets/cams/components/ui/Player/player.swf?bgColor=2829099&isModel=false&version=1.5.892&bufferTime=1&camFPS=30&camKeyframe=15&camQuality=85&camWidth=640&camHeight=480'
                 Url = 'rtmp://b-eu10.stripcdn.com:1935/%s?sessionHash=%s&domain=xhamsterlive.com playpath=%s swfUrl=%s pageUrl=http://xhamsterlive.com/cams/%s live=1 ' % (BroadcastServer, sessionHash, ID, swf_url, Name) 
                 Url = 'rtmp://b-eu10.stripcdn.com:1935/%s?sessionHash=%s&domain=xhamsterlive.com playpath=%s swfVfy=%s pageUrl=http://xhamsterlive.com/cams/%s live=1 ' % (BroadcastServer, sessionHash, ID, swf_url, Name) 
                 if ID == url: 
                    return urlparser.decorateUrl(Url, {'Referer': 'https://xhamsterlive.com/cams/'+Name, 'iptv_livestream': True}) 
           except Exception:
              printExc()
           return ''

        if parser == 'http://www.cliphunter.com':
           host = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3'
           header = {'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'} 
           query_data = { 'url': url, 'header': header, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              return ''
           #printDBG( 'Host listsItems data: '+data )
           url = re.findall('"url":"(.*?)"}', data, re.S)
           if url:
              url = url[-1]
              url = url.replace('\u0026', '.').replace(r"\/",r"/")
              if url.startswith('http'): return url
           url = re.findall('"url":"(.*?)"}', data, re.S)
           if url:
              url = url[-1]
              url = url.replace('\u0026', '.')
              translation_table = {
                 'm': 'a', 'b': 'b', 'c': 'c', 'i': 'd', 'd': 'e', 'g': 'f', 'a': 'h',
                 'z': 'i', 'y': 'l', 'n': 'm', 'l': 'n', 'f': 'o', 'v': 'p', 'x': 'r',
                 'r': 's', 'q': 't', 'p': 'u', 'e': 'v',
                 '$': ':', '&': '.', '(': '=', '^': '&', '=': '/',
              }
              url = ''.join(translation_table.get(c, c) for c in url) 
              return url
           else: return ''

        if parser == 'http://www.redtube.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'redtube.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return ''
           #printDBG( 'Elemek listaja: '+data )
           result = self.cm.ph.getDataBeetwenMarkers(data, 'mp4","videoUrl":"', '","remote":true}],"', False) [1]
           allUrl = result.replace("/api","/").replace("\/","/")
           printDBG( 'Result eredmenye: '+allUrl )
           
           sts, data = self.get_Page(allUrl)
           if not sts: return ''
           printDBG( 'Lekerve: '+data )
           #hlsUrl = self.cm.ph.getAllItemsBeetwenMarkers(data, 'videoUrl":"', '"},{"' False)
           hlsUrl = self.cm.ph.getDataBeetwenMarkers(data, 'videoUrl":"', '"},{"', False) [1]
           videoUrl = hlsUrl.replace("\/","/")
           printDBG( 'Ez a vege: '+videoUrl )
           return videoUrl
          
        if parser == 'http://www.tube8.com/embed/':
           return self.getResolvedURL(url.replace(r"embed/",r""))
        
        if parser == 'http://www.pornhub.com/embed/':
           return self.getResolvedURL(url.replace(r"embed/",r"view_video.php?viewkey="))

        if parser == 'http://www.tube8.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'tube8.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return ''
           #printDBG( 'Host getResolvedURL data: '+data )
           videoUrl = self.cm.ph.getSearchGroups(data, '''quality_720p['"]:['"]([^"^']+?)['"]''')[0] 
           if not videoUrl: videoUrl = self.cm.ph.getSearchGroups(data, '''quality_480p['"]:['"]([^"^']+?)['"]''')[0] 
           return videoUrl.replace('\/','/') 

        if parser == 'http://www.4tube.com':
           COOKIEFILE = os_path.join(GetCookieDir(), '4tube.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           if url.startswith('https://www.4tube.com'):
              self.HTTP_HEADER['Origin'] = 'https://www.4tube.com'
           elif url.startswith('https://www.fux.com'):
              self.HTTP_HEADER['Origin'] = 'https://www.fux.com'
           elif url.startswith('https://www.pornerbros.com'):
              self.HTTP_HEADER['Origin'] = 'https://www.pornerbros.com'
           elif url.startswith('https://www.porntube.com'):
              self.HTTP_HEADER['Origin'] = 'https://www.porntube.com'
           self.HTTP_HEADER['Referer'] = url

           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           domena = url.split('/')[2].replace ('www.','')
           printDBG( 'Host domain: '+domena )

           videoID = re.findall('data-id="(\d+)".*?data-quality="(\d+)"', data, re.S)
           try:
              init = self.cm.ph.getSearchGroups(data, '''window.INITIALSTATE\s*?=\s*?['"]([^"^']+?)['"]''', 1, True)[0] 
              init = urllib.unquote(base64.b64decode(init))
              #printDBG( 'Host listsItems init: '+init )
              try:
                 result = byteify(simplejson.loads(init)["page"])
              except Exception:
                 printExc()
                 result = byteify(simplejson.loads(data))
              videoID = result["video"]["mediaId"]
              info = {}
              res = ''
              for item in result["video"]["encodings"]:
                 res += str(item["height"]) + "+"
              res.strip('+')
              posturl = "https://token.%s/0000000%s/desktop/%s" % (domena, videoID, res)
              printDBG( 'Host getResolvedURL posturl: '+posturl )
              sts, data = self.get_Page(posturl)
              if not sts: return ''
              printDBG( 'Host getResolvedURL posturl data1: '+data )
              videoUrl = re.findall('token":"(.*?)"', data, re.S)
              if videoUrl: return videoUrl[-2]     
           except Exception:
              printExc()
           if videoID:
              res = ''
              for x in videoID:
                  res += x[1] + "+"
              res.strip('+')
              posturl = "https://token.%s/0000000%s/desktop/%s" % (domena, videoID[-1][0], res)
              printDBG( 'Host getResolvedURL posturl: '+posturl )
              sts, data = self.get_Page(posturl)
              if not sts: return ''
              printDBG( 'Host getResolvedURL posturl data2: '+data )
              videoUrl = re.findall('token":"(.*?)"', data, re.S)
              if videoUrl: return videoUrl[-2]                 
              else: return ''
           return ''

        if parser == 'http://hotmovs.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'hotmovs.cookie')
           host = "Mozilla/5.0 (Linux; U; Android 4.1.1; en-us; androVM for VirtualBox ('Tablet' version with phone caps) Build/JRO03S) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30"
           header = {'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}   
           try: data = self.cm.getURLRequestData({ 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           printDBG( 'Host getResolvedURL data: '+data )
           videoPage = self.cm.ph.getSearchGroups(data, '''var video_url=['"]([^"^']+?)['"]''')[0] 
           hash = self.cm.ph.getSearchGroups(data, '''/get_file/(\d+/[^"^']+?)/''')[0] 
           printDBG( 'Host getResolvedURL videoPage: '+videoPage )
           if videoPage:
              decoder = "decrypt=function(_0xf4bdx6) {"\
                 "var _0xf4bdx7 = '',"\
                 "    _0xf4bdx8 = 0;"\
                 "/[^\u0410\u0412\u0421\u0415\u041cA-Za-z0-9\.\,\~]/g ['exec'](_0xf4bdx6) && console['log']('error decoding url');"\
                 "_0xf4bdx6 = _0xf4bdx6['replace'](/[^\u0410\u0412\u0421\u0415\u041cA-Za-z0-9\.\,\~]/g, '');"\
                 "do {"\
                 "var _0xf4bdx9 = '\u0410\u0412\u0421D\u0415FGHIJKL\u041CNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~' ['indexOf'](_0xf4bdx6['charAt'](_0xf4bdx8++)),"\
                 "_0xf4bdxa = '\u0410\u0412\u0421D\u0415FGHIJKL\u041CNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~' ['indexOf'](_0xf4bdx6['charAt'](_0xf4bdx8++)),"\
                 "_0xf4bdxb = '\u0410\u0412\u0421D\u0415FGHIJKL\u041CNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~' ['indexOf'](_0xf4bdx6['charAt'](_0xf4bdx8++)),"\
                 "_0xf4bdxc = '\u0410\u0412\u0421D\u0415FGHIJKL\u041CNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~' ['indexOf'](_0xf4bdx6['charAt'](_0xf4bdx8++)),"\
                 "_0xf4bdx9 = _0xf4bdx9 << 2 | _0xf4bdxa >> 4,"\
                 "_0xf4bdxa = (_0xf4bdxa & 15) << 4 | _0xf4bdxb >> 2,"\
                 "_0xf4bdxd = (_0xf4bdxb & 3) << 6 | _0xf4bdxc,"\
                 "_0xf4bdx7 = _0xf4bdx7 + String['fromCharCode'](_0xf4bdx9);"\
                 "64 != _0xf4bdxb && (_0xf4bdx7 += String['fromCharCode'](_0xf4bdxa));"\
                 "64 != _0xf4bdxc && (_0xf4bdx7 += String['fromCharCode'](_0xf4bdxd))"\
                 "} while (_0xf4bdx8 < _0xf4bdx6['length']);;"\
                 "return unescape(_0xf4bdx7)"\
                 "};" 
              js = decoder + "\n" + "vidurl = decrypt('"+videoPage+"');"  
              printDBG( 'Host getResolvedURL js: '+js )
              urls = js_execute( js+ '\nfor (n in this){print(n+"="+this[n]+";");}')
              videoUrl = self.cm.ph.getSearchGroups(urls['data'], '''vidurl=([^"^']+?);''')[0] 
              printDBG( 'Host hash: '+hash )
              printDBG( 'Host videoUrl.split4: '+videoUrl.split('/')[-6] )
              printDBG( 'Host videoUrl.split5: '+videoUrl.split('/')[-5] )

              if hash: videoUrl = videoUrl.replace(videoUrl.split('/')[-6]+'/'+videoUrl.split('/')[-5],hash)
              if videoUrl: return videoUrl
              if videoPage.startswith('http'): return videoPage

           videoUrl = self.cm.ph.getSearchGroups(data, '''file\':\s['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           return urllib2.unquote(videoUrl)

        if parser == 'https://www.txxx.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'txxx.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'txxx.cookie', 'txxx.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           videoUrl = re.search('video_url":"([^"]+)', data).group(1)
           replacemap = {'M':'\u041c', 'A':'\u0410', 'B':'\u0412', 'C':'\u0421', 'E':'\u0415', '=':'~', '+':'.', '/':','}
           for key in replacemap:
               videoUrl = videoUrl.replace(replacemap[key], key)
           videoUrl = base64.b64decode(videoUrl)
           if videoUrl.startswith('//'): videoUrl = 'https:' + videoUrl
           if videoUrl.startswith('/'): videoUrl = 'https://txxx.com' + videoUrl
           return urlparser.decorateUrl(videoUrl, {'Referer': url})

        if parser == 'http://www.youporn.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'youporn.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           self.defaultParams['header']['Referer'] = url
           sts, data = self.get_Page(url)
           if not sts: return ''
           result = self.cm.ph.getSearchGroups(data, '''"videoUrl":['"]([^'"]+?)['"]''')[0].replace('&amp;','&').replace(r"\/",r"/")
           allUrl = result.replace("/api","https://www.youporn.com/api")
           #printDBG( 'Ezt talaltam: '+allUrl )
           sts, data = self.get_Page(allUrl)         
           #printDBG( 'Lekerve: '+data )
           hlsUrl = self.cm.ph.getDataBeetwenMarkers(data, 'videoUrl":"', '","', False) [1]
           videoUrl = hlsUrl.replace("\/","/").replace('\u0026', '&')
           #printDBG( 'Ez a vege: '+videoUrl )
           return videoUrl
           

        # make by 12asdfg12
        def ssut51(str):
            str = re.sub(r'\D', '', str)
            sut = 0
            for i in range(0, len(str)):
                sut += int(str[i])
            return sut

        if parser == 'https://yourporn.sexy':
           for x in range(1, 99): 
              COOKIEFILE = os_path.join(GetCookieDir(), 'yourporn.cookie')
              self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
              self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE, 'return_data': True}
              self.defaultParams['header']['Origin'] = 'https://sxyprn.com'
              sts, data = self.getPage(url, 'yourporn.cookie', 'sxyprn.com', self.defaultParams)
              if not sts: return ''
              #printDBG( 'Host listsItems data: '+str(data) )
              videoUrl = self.cm.ph.getSearchGroups(data, '''data-vnfo=['"].*?:['"]([^"^']+?)['"]''')[0].replace(r"\/",r"/")
              if videoUrl:
                 printDBG( 'Host listsItems videoUrl: '+videoUrl )
                 if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
                 if videoUrl.startswith('/'): videoUrl = 'https://sxyprn.com' + videoUrl
                 try:
                    match = re.search('src="(/js/main[^"]+)"', data, re.DOTALL | re.IGNORECASE)
                    if match.group(1).startswith('/'): result = 'https://sxyprn.com' + match.group(1)
                    sts, jsscript = self.getPage(result, 'yourporn.cookie', 'sxyprn.com', self.defaultParams)
                    replaceint = re.search(r'tmp\[1\]\+= "(\d+)";', jsscript, re.DOTALL | re.IGNORECASE).group(1)
                    videoUrl = videoUrl.replace('/cdn/', '/cdn%s/' % replaceint)
                 except:
                    if '/cdn/' in videoUrl: videoUrl = videoUrl.replace('/cdn/','/cdn'+str(self.yourporn)+'/')
                 videoUrl = urlparser.decorateUrl(videoUrl, {'Referer': url, 'Origin': 'https://sxyprn.com'}) 
                 tmp = videoUrl.split('/')
                 a = str(int(tmp[-3]) - ssut51(re.sub(r'\D', '', tmp[-2])) - ssut51(re.sub(r'\D', '', tmp[-1])))
                 if int(a)>0: 
                    tmp[-3] = a
                 else: 
                    tmp[-3] = str(int(tmp[-3])-101)
                 videoUrl = '/'.join(tmp)
              self.defaultParams['max_data_size'] = 0
              sts, data = self.getPage(videoUrl, 'yourporn.cookie', 'sxyprn.com', self.defaultParams)
              if not sts: return ''
              if not 'sxyprn' in data.meta['url']: return data.meta['url']
           return ''

        if parser == 'https://www.playvids.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'playvids.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'playvids.cookie', 'playvids.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+str(data) )
           videoUrl = self.cm.ph.getSearchGroups(data, '''hls-src720=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if ''==videoUrl: videoUrl = self.cm.ph.getSearchGroups(data, '''hls-src480=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if ''==videoUrl: videoUrl = self.cm.ph.getSearchGroups(data, '''hls-src360=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              return self.FullUrl(videoUrl)

           videoUrl = self.cm.ph.getSearchGroups(data, '''src720=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              return self.FullUrl(videoUrl)
           videoUrl = self.cm.ph.getSearchGroups(data, '''src480=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              return self.FullUrl(videoUrl)
           videoUrl = self.cm.ph.getSearchGroups(data, '''src360=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              return self.FullUrl(videoUrl)
           return ''

        if parser == 'http://www.tubewolf.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'tubewolf.cookie')
           for x in range(1, 10): 
              self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
              self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
              sts, data = self.get_Page(url)
              if not sts: return ''
              printDBG( 'Host listsItems data: '+data )
              data = self.cm.ph.getDataBeetwenMarkers(data, '<video id', '</video>', False)[1]
              videoUrl = re.findall('<source\ssrc="(.*?)"', data, re.S)
              if videoUrl:
                 return videoUrl[-1]

        if parser == 'https://streamate.com':
            COOKIEFILE = os_path.join(GetCookieDir(), 'streamate.cookie')
            url = 'https://streamate.com/blacklabel/hybrid/?name={}&lang=en&manifestUrlRoot=https://sea1c-ls.naiadsystems.com/sea1c-edge-ls/80/live/s:'.format(url)
            query_data = { 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True }
            try:
                data = self.cm.getURLRequestData(query_data)
            except Exception as e:
                printExc()
                printDBG( 'Host listsItems query error url:'+url )
                return ''
            printDBG( 'Host listsItems data: '+data )
            url =  self.cm.ph.getSearchGroups(data, '''data-manifesturl=['"]([^"^']+?)['"]''')[0] 
            header = {'Referer': 'https://streamate.com', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
            query_data = { 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True }
            try:
                data = self.cm.getURLRequestData(query_data)
            except Exception as e:
                printExc()
                printDBG( 'Host listsItems query error url:'+url )
                return ''
            printDBG( 'Host listsItems data2: '+data )
            try:
                videoinfo = simplejson.loads(data)
                videoUrl = videoinfo['formats']['mp4-hls']['manifest']
                videoUrl = urlparser.decorateUrl(videoUrl, {'Referer': 'https://streamate.com', 'iptv_livestream': True}) 
                if '.m3u8' in videoUrl:
                    if self.cm.isValidUrl(videoUrl): 
                        tmp = getDirectM3U8Playlist(videoUrl)
                        for item in tmp:
                            printDBG( 'Host listsItems valtab: '  +str(item))
                            return item['url']
                return videoUrl
            except Exception as e:
                printExc()
            return ''

        if parser == 'http://www.youjizz.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'youjizz.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return
           #printDBG( 'Host listsItems data: '+data )

           #host = 'iPhone'
           #header = {'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'X-Requested-With':'XMLHttpRequest'}   
           #try: data = self.cm.getURLRequestData({ 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           #except:
           #   printDBG( 'Host getResolvedURL query error url: '+url )
           #   return ''
           #printDBG( 'Host getResolvedURL data: '+data )
           videoPage = self.cm.ph.getSearchGroups(data, '''"quality":"1080","filename":['"]([^"^']+?)['"]''')[0].replace('\/','/')
           if videoPage:
              if videoPage.startswith('//'): videoPage = 'http:' + videoPage
              return videoPage.replace("&amp;","&")
           videoPage = self.cm.ph.getSearchGroups(data, '''"quality":"720","filename":['"]([^"^']+?)['"]''')[0].replace('\/','/')
           if videoPage:
              if videoPage.startswith('//'): videoPage = 'http:' + videoPage
              return videoPage.replace("&amp;","&")
           videoPage = self.cm.ph.getSearchGroups(data, '''"quality":"480","filename":['"]([^"^']+?)['"]''')[0].replace('\/','/')
           if videoPage:
              if videoPage.startswith('//'): videoPage = 'http:' + videoPage
              return videoPage.replace("&amp;","&")
           videoPage = self.cm.ph.getSearchGroups(data, '''"quality":"360","filename":['"]([^"^']+?)['"]''')[0].replace('\/','/')
           if videoPage:
              if videoPage.startswith('//'): videoPage = 'http:' + videoPage
              return videoPage.replace("&amp;","&") 
           videoPage = self.cm.ph.getSearchGroups(data, '''"quality":"288","filename":['"]([^"^']+?)['"]''')[0].replace('\/','/')
           if videoPage:
              if videoPage.startswith('//'): videoPage = 'http:' + videoPage
              return videoPage.replace("&amp;","&") 
           videoPage = self.cm.ph.getSearchGroups(data, '''"quality":"270","filename":['"]([^"^']+?)['"]''')[0].replace('\/','/')
           if videoPage:
              if videoPage.startswith('//'): videoPage = 'http:' + videoPage
              return videoPage.replace("&amp;","&")
           videoPage = self.cm.ph.getSearchGroups(data, '''"filename":['"]([^"^']+?)['"]''')[0].replace('\/','/')
           if videoPage:
              if videoPage.startswith('//'): videoPage = 'http:' + videoPage
              return videoPage.replace("&amp;","&")
           videoPage = self.cm.ph.getSearchGroups(data, '''<source src=['"]([^"^']+?)['"]''')[0] 
           if videoPage:
              if videoPage.startswith('//'): videoPage = 'http:' + videoPage
              return videoPage.replace("&amp;","&")

           error = self.cm.ph.getDataBeetwenMarkers(data, '<p class="text-gray">', '</p>', False)[1]
           if error:
              SetIPTVPlayerLastHostError(_(error))
              return []
           return ''

        if parser == 'https://www.ashemaletube.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'ASHEMALETUBE.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE, 'return_data': True}
           sts, data = self.getPage(url, 'ASHEMALETUBE.cookie', 'ashemaletube.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           if 'sources: ' in data:
              try:
                 sources = self.cm.ph.getDataBeetwenMarkers(data, 'sources: ', ']', False)[1]
                 result = byteify(simplejson.loads(sources+']'))
                 for item in result:
                    if str(item["desc"])=='720p' and str(item["active"])=='true': return str(item["src"])
                    if str(item["desc"])=='480p' and str(item["active"])=='true': return str(item["src"])
                    if str(item["desc"])=='360p' and str(item["active"])=='true': return str(item["src"])
              except Exception as e:
                 printExc()
           videoUrl = self.cm.ph.getSearchGroups(data, '''source src=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return videoUrl 

           if 'To watch this video please' in data:
              SetIPTVPlayerLastHostError(_(' Login Protected.'))
              return []
           return ''

        if parser == 'http://www.pornhub.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornhub.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self._getPage(url, self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           try:
              match = re.compile(r"""quality_([0-9]{3,4})p\s*=(?:"|')?([^'";]+)(?:"|')?;""", re.DOTALL | re.IGNORECASE).findall(data)
              match = sorted(match, key=lambda x: int(x[0]), reverse=True)
              videolink = match[0][1]
              if "/*" in videolink:
                 videolink = re.sub(r"/\*[^/]+/", "", videolink).replace("+","")
                 linkparts = re.compile(r"(\w+)", re.DOTALL | re.IGNORECASE).findall(videolink)
                 for part in linkparts:
                    partval = re.compile(part+'="(.*?)";', re.DOTALL | re.IGNORECASE).findall(data)[0]
                    partval = partval.replace('" + "','')
                    videolink = videolink.replace(part, partval)
              videoUrl = videolink.replace(" ","")
              printDBG( 'Host videoUrl: '+videoUrl )
              if videoUrl: return strwithmeta(videoUrl, {'Referer':url})
           except Exception:
              printExc()  

           videoPage = self.cm.ph.getSearchGroups(data, '''"quality":"720","videoUrl":['"]([^"^']+?)['"]''')[0] 
           if videoPage: return videoPage.replace('\/','/')
           videoPage = self.cm.ph.getSearchGroups(data, '''"quality":"480","videoUrl":['"]([^"^']+?)['"]''')[0] 
           if videoPage: return videoPage.replace('\/','/')
           videoPage = self.cm.ph.getSearchGroups(data, '''"quality":"240","videoUrl":['"]([^"^']+?)['"]''')[0] 
           if videoPage: return videoPage.replace('\/','/')
           try:
              #js = re.findall('(var flashvars_(?:\d+).*?)loadScriptUniqueId', data, re.S)
              js = re.findall('type="text/javascript">.*?(var\sflashvars.*?)</script>', data, re.S)
              #js = self.cm.ph.getDataBeetwenMarkers(data, 'var flashvars_', 'loadScriptUniqueId', False)[1]
              printDBG( 'Host data js: '+js[0] )
              if js:
                 urls = js_execute( js[0].replace('playerObjList.', '')+ '\nfor (n in this){print(n+"="+this[n]+";");}')
                 videoPage = self.cm.ph.getSearchGroups(urls['data'], '''media_[0-9]=([^;]+?1080P[^;]+?);''')[0] 
                 if videoPage: return videoPage
                 videoPage = self.cm.ph.getSearchGroups(urls['data'], '''media_[0-9]=([^;]+?720P[^;]+?);''')[0] 
                 if videoPage: return videoPage
                 videoPage = self.cm.ph.getSearchGroups(urls['data'], '''media_[0-9]=([^;]+?480P[^;]+?);''')[0] 
                 if videoPage: return videoPage
                 videoPage = self.cm.ph.getSearchGroups(urls['data'], '''media_[0-9]=([^;]+?240P[^;]+?);''')[0] 
                 if videoPage: return videoPage
           except Exception:
              printExc()
              embed = re.search('"embedCode":"<iframe src=."(.*?)"', data, re.S)
              if embed:
                 url = embed.group(1).replace('\/','/').replace('\\','')
                 printDBG( 'Host data embed: '+url )
                 sts, data = self._getPage(url, self.defaultParams)
                 if not sts: return ''
                 printDBG( 'Host listsItems data: '+data )
                 videoPage = re.findall('quality_720p":"(.*?)"', data, re.S)
                 if videoPage: return videoPage[0].replace('\/','/')
                 videoPage = re.findall('quality_480p":"(.*?)"', data, re.S)
                 if videoPage: return videoPage[0].replace('\/','/')
           return ''

        if parser == 'https://chaturbate.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'chaturbate.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER}
           for x in range(1, 3): 
              sts, data = self.get_Page(url)
              if not sts: return
              printDBG( 'Host listsItems data: '+str(data) )
              if '/auth/login/' in self.cm.meta['url']:
                 SetIPTVPlayerLastHostError(_(' PRIVATE.'))
              if 'Room is currently offline' in data:
                 SetIPTVPlayerLastHostError(_(' OFFLINE.'))
              host = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.18) Gecko/20110621 Mandriva Linux/1.9.2.18-0.1mdv2010.2 (2010.2) Firefox/3.6.18'
              videoPage = self.cm.ph.getSearchGroups(data, '''<source src=['"]([^"^']+?)['"]''')[0] 
              if not videoPage: 
                 data = data.replace(r'\u0022','"').replace(r'\u002D','-')
                 videoPage = self.cm.ph.getSearchGroups(data, '''hls_source":\s*['"]([^"^']+?)['"]''')[0] 
              try:
                 item = []
                 videoUrl = videoPage.replace('&amp;','&')
                 videoUrl = urlparser.decorateUrl(videoUrl, {'Referer': url, 'User-Agent':host}) 
                 tmp = getDirectM3U8Playlist(videoUrl, checkExt=True, variantCheck=True, checkContent=True, sortWithMaxBitrate=99999999)
                 for item in tmp:
                    printDBG( 'Host listsItems valtab1: '  +str(item))
                 if self.format4k:
                    return tmp[0]['url']
                 else:
                    if tmp[0]['height']<=1080 : return tmp[0]['url']
                    if tmp[1]['height']<=1080 : return tmp[1]['url']
                    if tmp[2]['height']<=1080 : return tmp[2]['url']
              except Exception:
                 printExc()
           return ''
  
        if parser == 'https://www.mydirtyhobby.to':
           COOKIEFILE = os_path.join(GetCookieDir(), 'mydirtyhobby.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self._getPage(url, self.defaultParams)
           if not sts: return 
           printDBG( 'Host listsItems data: '+str(data) )
           videoPage = self.cm.ph.getSearchGroups(data, '''<iframe src=['"]([^"^']+?)['"]''', 1, True)[0] 
           if videoPage: 
              videoPage = urlparser.decorateUrl(videoPage, {'Referer': url})
              return self.getResolvedURL(videoPage)
           if "eval(function(p,a,c,k,e,d)" in data:
              printDBG( 'Host resolveUrl packed' )
              packed = re.compile('>eval\(function\(p,a,c,k,e,d\)(.+?)</script>', re.DOTALL).findall(data)
              if packed:
                 data = packed[-1]
              else:
                 return ''
              printDBG( 'Host data4: '+str(data) )
              try:
                 videoUrl = unpackJSPlayerParams(data, TEAMCASTPL_decryptPlayerParams, 0, True, True) 
                 printDBG( 'OK4: ')
              except Exception: pass 
              printDBG( 'Host videoUrl: '+str(videoUrl) )
              videoPage = self.cm.ph.getSearchGroups(str(videoUrl), '''sources:\[['"]([^"^']+?)['"]''')[0] 
              printDBG( 'Host videoPage: '+str(videoPage) )
              if videoPage: return videoPage
           return ''

        if parser == 'https://www.tnaflix.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'tnaflix.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return 
           printDBG( 'Host listsItems data: '+str(data) )
           vid = self.cm.ph.getSearchGroups(data, '''data-vid=['"]([^"^']+?)['"]''')[0]
           nk =  self.cm.ph.getSearchGroups(data, '''data-nk=['"]([^"^']+?)['"]''')[0]
           vk =  self.cm.ph.getSearchGroups(data, '''data-vk=['"]([^"^']+?)['"]''')[0]
           xml = 'https://cdn-fck.tnaflix.com/tnaflix/%s.fid?key=%s&VID=%s&nomp4=1&catID=0&rollover=1&startThumb=31&embed=0&utm_source=0&multiview=0&premium=1&country=0user=0&vip=1&cd=0&ref=0&alpha' % (vk, nk, vid) 
           sts, data = self.get_Page(xml, self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+str(data) )
           videoPage = re.findall('<videoLink>.*?//(.*?)(?:]]>|</videoLink>)', data, re.S)
           if videoPage: return 'http://' + videoPage[-1]

           videoUrl = self.cm.ph.getSearchGroups(data, '''download href=['"]([^"^']+?)['"]''')[0] 
           if not videoUrl: videoUrl = self.cm.ph.getSearchGroups(data, '''"contentUrl" content=['"]([^"^']+?)['"]''')[0] 
           if videoUrl.startswith('//'): videoUrl = 'https:' + videoUrl
           videoUrl = urlparser.decorateUrl(videoUrl, {'Referer': url})
           if videoUrl: return videoUrl
           return ''

        if parser == 'https://www.empflix.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'empflix.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return 
           printDBG( 'Host listsItems data: '+str(data) )
           vid = self.cm.ph.getSearchGroups(data, '''data-vid=['"]([^"^']+?)['"]''')[0]
           nk =  self.cm.ph.getSearchGroups(data, '''data-nk=['"]([^"^']+?)['"]''')[0]
           vk =  self.cm.ph.getSearchGroups(data, '''data-vk=['"]([^"^']+?)['"]''')[0]
           xml = 'https://cdn-fck.empflix.com/empflix/%s-1.fid?key=%s&VID=%s&nomp4=1&catID=0&rollover=1&startThumb=31&embed=0&utm_source=0&multiview=0&premium=1&country=0user=0&vip=1&cd=0&ref=0&alpha' % (vk, nk, vid)
           sts, data = self.get_Page(xml, self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+str(data) )
           videoPage = re.findall('<videoLink>.*?//(.*?)(?:]]>|</videoLink>)', data, re.S)
           if videoPage: return 'http://' + videoPage[-1]

           videoUrl = self.cm.ph.getSearchGroups(data, '''download href=['"]([^"^']+?)['"]''')[0]
           if not videoUrl: videoUrl = self.cm.ph.getSearchGroups(data, '''"contentUrl" content=['"]([^"^']+?)['"]''')[0] 
           if videoUrl.startswith('//'): videoUrl = 'https:' + videoUrl
           videoUrl = urlparser.decorateUrl(videoUrl, {'Referer': url})
           if videoUrl: return videoUrl
           return ''

        if parser == 'http://www.moviefap.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'moviefap.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           self.USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'
           self.HEADER = {'User-Agent': self.USER_AGENT, 'DNT':'1', 'Accept': 'text/html'}
           self.defaultParams = {'header':dict(self.HEADER)}
           self.defaultParams['header']['Referer'] = url
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return 
           printDBG( 'Host listsItems data: '+str(data) )
           xml = self.cm.ph.getSearchGroups(data, '''flashvars.config.*?//([^"^']+?)['"]''')[0]
           if not xml: xml = self.cm.ph.getSearchGroups(data, '''name="config".*?//([^"^']+?)['"]''')[0] 
           if xml:
              videoUrl = "https://" + xml
              sts, data = self.get_Page(videoUrl, self.defaultParams)
              if not sts: return 
              printDBG( 'Host listsItems data2: '+str(data) )
              url = re.findall('<videoLink>.*?//(.*?)(?:]]>|</videoLink>)', data, re.S)
              if url:
                 return "http://" + url[-1].replace('&amp;','&')  
           return ''

        if parser == 'https://www.pinflix.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'pinflix.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE, 'return_data': True}
           sts, data = self.getPage(url, 'pinflix.cookie', 'pinflix.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+str(data) )
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source[^>]+?src=['"]([^"^']+?)['"]''')[0].replace('\/','/')
           if not videoUrl: videoUrl = self.cm.ph.getSearchGroups(data, '''"720p":['"]([^"^']+?)['"]''')[0].replace('\/','/')
           if not videoUrl: videoUrl = self.cm.ph.getSearchGroups(data, '''"480p":['"]([^"^']+?)['"]''')[0].replace('\/','/')
           if not videoUrl: videoUrl = self.cm.ph.getSearchGroups(data, '''"360p":['"]([^"^']+?)['"]''')[0].replace('\/','/')
           if videoUrl.startswith('/'): videoUrl = 'https://www.pinflix.com' + videoUrl
           self.defaultParams['max_data_size'] = 0
           sts, data = self.getPage(videoUrl, 'pinflix.cookie', 'pinflix.com', self.defaultParams)
           if not sts: return ''
           return data.meta['url']

        if parser == 'http://www.pornhd.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornhd.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE, 'return_data': True}
           sts, data = self.getPage(url, 'pornhd.cookie', 'pornhd.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+str(data) )
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source[^>]+?src=['"]([^"^']+?)['"]''')[0].replace('\/','/')
           if not videoUrl: videoUrl = self.cm.ph.getSearchGroups(data, '''"1080p":['"]([^"^']+?)['"]''')[0].replace('\/','/')
           if not videoUrl: videoUrl = self.cm.ph.getSearchGroups(data, '''"720p":['"]([^"^']+?)['"]''')[0].replace('\/','/')
           if not videoUrl: videoUrl = self.cm.ph.getSearchGroups(data, '''"480p":['"]([^"^']+?)['"]''')[0].replace('\/','/')
           if not videoUrl: videoUrl = self.cm.ph.getSearchGroups(data, '''"360p":['"]([^"^']+?)['"]''')[0].replace('\/','/')
           if videoUrl.startswith('/'): videoUrl = 'https://www.pornhd.com' + videoUrl
           self.defaultParams['max_data_size'] = 0
           sts, data = self.getPage(videoUrl, 'pornhd.cookie', 'pornhd.com', self.defaultParams)
           if not sts: return ''
           return data.meta['url']

        if parser == 'http://www.adulttvlive.net':
           COOKIEFILE = os_path.join(GetCookieDir(), 'adulttv.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'adulttv.cookie', 'adulttv.net', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data1: '+data )

           videoUrl = self.cm.ph.getSearchGroups(data, '''src=['"](https://adult-channels.com/channels/[^"^']+?)['"]''')[0] 
           if not videoUrl: videoUrl = self.cm.ph.getSearchGroups(data, '''src=['"](https://www.adulttvlive.net[^"^']+?embed/)['"]''')[0] 

           sts, data = self.getPage(videoUrl, 'adulttv.cookie', 'adulttv.net', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data2: '+data )
           if 'porndig' in data:
              videoUrl = self.cm.ph.getSearchGroups(data, '''src=['"]([^"^']+?)['"]''')[0] 
              return self.getResolvedURL(videoUrl)

           if 'unescape' in data:
              data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'eval(', ');', False)
              try:
                 ddata = ''
                 for idx in range(len(data)):
                    tmp = data[idx].split('+')
                    for item in tmp:
                       item = item.strip()
                       if item.startswith("'") or item.startswith('"'):
                          ddata += self.cm.ph.getSearchGroups(item, '''['"]([^'^"]+?)['"]''')[0]
                       else:
                          tmp2 = re.compile('''unescape\(['"]([^"^']+?)['"]''').findall(item)
                          for item2 in tmp2:
                             ddata += urllib.unquote(item2)
                
                 printDBG('Host listsItems ddata2: '+ddata)
                
                 funName = self.cm.ph.getSearchGroups(ddata, '''function\s*([^\(]+?)''')[0].strip()
                 sp      = self.cm.ph.getSearchGroups(ddata, '''split\(\s*['"]([^'^"]+?)['"]''')[0]
                 modStr  = self.cm.ph.getSearchGroups(ddata, '''\+\s*['"]([^'^"]+?)['"]''')[0] 
                 modInt  = int( self.cm.ph.getSearchGroups(ddata, '''\+\s*(-?[0-9]+?)[^0-9]''')[0] )
                
                 ddata =  self.cm.ph.getSearchGroups(ddata, '''document\.write[^'^"]+?['"]([^'^"]+?)['"]''')[0]
                 data  = ''
                 tmp   = ddata.split(sp)
                 ddata = urllib.unquote(tmp[0])
                 k = urllib.unquote(tmp[1] + modStr)
                 for idx in range(len(ddata)):
                    data += chr((int(k[idx % len(k)]) ^ ord(ddata[idx])) + modInt)
                      
                 printDBG('host data2: '+data)
                
                 if 'rtmp://' in data:
                    rtmpUrl = self.cm.ph.getDataBeetwenMarkers(data, '&source=', '&', False)[1]
                    if rtmpUrl == '':
                       rtmpUrl = self.cm.ph.getSearchGroups(data, r'''['"](rtmp[^"^']+?)['"]''')[0]
                    return rtmpUrl
                 elif '.m3u8' in data:
                    file = self.cm.ph.getSearchGroups(data, r'''['"](http[^"^']+?\.m3u8[^"^']*?)['"]''')[0]
                    if file == '': file = self.cm.ph.getDataBeetwenMarkers(data, 'src=', '&amp;', False)[1]
                    return file
              except Exception:
                 printExc()
           videoUrl = self.cm.ph.getSearchGroups(data, '''<iframe[^>]+?src=['"]([^"^']+?)['"]''')[0] 
           if not videoUrl:
              link = self.cm.ph.getSearchGroups(data, '''streamer":['"]([^"^']+?)['"]''')[0].replace(r"\/",r"/")
              return 'http://www.filmon.com' + link
           if not videoUrl: return ''
           sts, data = self.getPage(videoUrl, 'adulttv.cookie', 'adulttv.net', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data3: '+data )
           videoUrl = self.cm.ph.getSearchGroups(data, '''sources:\[\{file:['"]([^"^']+?)['"]''', 1, True)[0] 
           if not videoUrl: videoUrl = self.cm.ph.getSearchGroups(data, '''source:['"]([^"^']+?)['"]''', 1, True)[0] 
           if not videoUrl: videoUrl = self.cm.ph.getSearchGroups(data, '''file:['"]([^"^']+?)['"]''', 1, True)[0] 
           return videoUrl

        if parser == 'https://www.balkanjizz.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'balkanjizz.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source src=['"]([^"^']+?)['"]''', 1, True)[0]
           if videoUrl.startswith('/'): data = 'https://www.balkanjizz.com' + videoUrl
           return data

        if parser == 'https://pornorussia.tv':
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornorussia.cookie')
           for x in range(1, 10): 
              sts, data = self.getPage(url, 'pornorussia.cookie', 'pornorussia.tv', self.defaultParams)
              if not sts: return ''
              #printDBG( 'Host listsItems data: '+data )
              videoUrl = self.cm.ph.getSearchGroups(data, '''<source src=['"]([^"^']+?)['"]''', 1, True)[0]
              if videoUrl: return urlparser.decorateUrl(videoUrl, {'Referer': url, 'User-Agent':self.USER_AGENT})
           return ''

        if parser == 'https://www.letmejerk.com':
           for x in range(1, 10): 
              COOKIEFILE = os_path.join(GetCookieDir(), 'letmejerk.cookie')
              self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
              self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
              self.defaultParams['header']['Referer'] = url
              sts, data = self.getPage(url, 'letmejerk.cookie', 'letmejerk.com', self.defaultParams)
              if not sts: return ''
              #printDBG( 'Host listsItems data1: '+data )
              file = str(self.cm.ph.getAllItemsBeetwenMarkers(data, '<script', '</script>'))
              tmp = file.split('|')
              post = ''
              for item in tmp:
                 item = item.strip()
                 if item.endswith("="): post = item
                 if item.startswith("eX"): post = item
                 if 'IWh0dHB' in item: post = item
              #printDBG( 'Host post:%s' % base64.b64decode(post) )
              #printDBG( 'Host post:%s' % base64.b64decode(post)[1:] )
              #printDBG( 'Host post:%s' % base64.b64decode(post)[:len(post)] )
              postdata = {'id' : url.split('/')[4]} 
              self.defaultParams['header']['X-Requested-With'] = 'XMLHttpRequest'
              self.defaultParams['header']['Host'] = 'letmejerk.com'
              sts, data = self.getPage('https://letmejerk.com/load/video/'+post+'/', 'letmejerk.cookie', 'letmejerk.com', self.defaultParams, postdata)
              if not sts: return ''
              printDBG( 'Host listsItems data2: '+data )
              videoUrl = self.cm.ph.getSearchGroups(data, '''<source\ssrc=['"]([^"^']+?)['"]''', 1, True)[0]
              poster = self.cm.ph.getSearchGroups(videoUrl, '''(@[^"^']+?#)''', 1, True)[0]
              videoUrl = videoUrl.replace(poster,'')

              if 'm3u8' in videoUrl: 
                 videoUrl = urlparser.decorateUrl(videoUrl, {'Referer': url, "Origin": "https://letmejerk.com"})
                 tmp = getDirectM3U8Playlist(videoUrl, checkContent=True, sortWithMaxBitrate=999999999)
                 for item in tmp:
                    return item['url']

              HTTP_HEADER = {'Accept-Encoding': 'gzip, deflate', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'} 
              defaultParams = {'header':HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
              defaultParams['header']['Referer'] = url
              defaultParams['max_data_size'] = 0
              defaultParams['header']['Host'] = videoUrl.split('/')[2]
              #defaultParams['header']['User-Agent'] = ua
              defaultParams['header']['Accept'] = "video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5"
              defaultParams['header']['Range'] = "bytes=0-" 
              defaultParams['header']['Referer'] = url
              defaultParams['ignore_http_code_ranges'] = []
              sts, data = self.getPage(videoUrl, 'letmejerk.cookie', 'letmejerk.com', defaultParams)
              #if not sts: return ''
              try:
                 if data.meta['location']: return self.FullUrl(data.meta['location'])
              except Exception: 
                 printExc() 
           return videoUrl 

        if parser == 'https://www.gotporn.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'gotporn.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE, 'return_data': True}
           sts, data = self.getPage(url, 'gotporn.cookie', 'gotporn.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+str(data) )
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source src=['"]([^"^']+?)['"]''')[0].replace('\/','/')
           if videoUrl.startswith('/'): videoUrl = 'https://www.gotporn.com' + videoUrl
           self.defaultParams['max_data_size'] = 0
           sts, data = self.getPage(videoUrl, 'gotporn.cookie', 'gotporn.com', self.defaultParams)
           if not sts: return ''
           return data.meta['url']

        if parser == 'https://www.analdin.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'analdin.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE, 'return_data': True}
           sts, data = self.getPage(url, 'analdin.cookie', 'analdin.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+str(data) )
           videoUrl = self.cm.ph.getSearchGroups(data, '''video_url:\s*['"]([^"^']+?)['"]''')[0].replace('\/','/')
           if videoUrl.startswith('/'): videoUrl = 'https://www.analdin.com' + videoUrl
           self.defaultParams['max_data_size'] = 0
           sts, data = self.getPage(videoUrl, 'analdin.cookie', 'analdin.com', self.defaultParams)
           if not sts: return ''
           return data.meta['url']

        if parser == 'https://www.pornomenge.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornomenge.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'pornomenge.cookie', 'pornomenge.com', self.defaultParams)
           if not sts: return ''
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source\ssrc=['"]([^"^']+?)['"]''')[0] 
           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           return videoUrl

        if parser == 'https://www.koloporno.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'koloporno.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'koloporno.cookie', 'koloporno.com', self.defaultParams)
           if not sts: return ''
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source\ssrc=['"]([^"^']+?)['"]''')[0] 
           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           return videoUrl

        if parser == 'http://www.sunporno.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'sunporno.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           videoPage = re.findall('video src="(.*?)"', data, re.S)   
           if videoPage:
              printDBG( 'Host videoPage:'+videoPage[0])
              return urlparser.decorateUrl(videoPage[0], {'Referer': url})
           return ''

        if parser == 'https://mini.zbiornik.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'zbiornikmini.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source src=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           return urllib2.unquote(videoUrl)

        if parser == 'http://dato.porn':
           #if not 'embed' in url:
           #   url = 'https://datoporn.co/embed-%s-658x400.html' % url.split('/')[-1]
           USER_AGENT = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/37.0.2062.120 Chrome/37.0.2062.120 Safari/537.36'
           COOKIEFILE = os_path.join(GetCookieDir(), 'datoporn.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE, 'return_data': True}
           sts, data = self.getPage(url, 'datoporn.cookie', 'datoporn.co', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+str(data) )
           license_code = self.cm.ph.getSearchGroups(data, '''license_code\s*?:\s*?['"]([^"^']+?)['"]''')[0]
           videoUrl = self.cm.ph.getSearchGroups(data, '''video_alt_url\s*?:\s*?['"]([^"^']+?)['"]''')[0]
           if 'login' in videoUrl or ''==videoUrl: videoUrl = self.cm.ph.getSearchGroups(data, '''video_url\s*?:\s*?['"]([^"^']+?)['"]''')[0]
           printDBG( 'Host license_code: %s' % license_code )
           printDBG( 'Host video_url: %s' % videoUrl )		   
           if 'function/0/' in videoUrl:
              videoUrl = decryptHash(videoUrl, license_code, '16')
           return urlparser.decorateUrl(videoUrl, {'Referer': url, 'User-Agent': USER_AGENT}) 

           if "eval(function(p,a,c,k,e,d)" in data:
              printDBG( 'Host resolveUrl packed' )
              packed = re.compile('>eval\(function\(p,a,c,k,e,d\)(.+?)</script>', re.DOTALL).findall(data)
              if packed:
                 packed = packed[-1]
              else:
                 return ''
              printDBG( 'Host data4: '+str(packed) )
              try:
                 videoPage = unpackJSPlayerParams(packed, TEAMCASTPL_decryptPlayerParams, 0, True, True) 
                 printDBG( 'OK4: ')
              except Exception: pass 
              printDBG( 'Host videoPage: '+str(videoPage) )
              videoUrl = ph.search(videoPage, '''file:['"]([^'^"]+?)['"]''')[0]
              if not videoUrl: videoUrl = ph.search(videoPage, '''src:['"]([^'^"]+?)['"]''')[0]
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              videoUrl = urlparser.decorateUrl(videoUrl, {'User-Agent': USER_AGENT, 'Referer': url})
              if 'm3u8' in videoUrl:
                 tmp = getDirectM3U8Playlist(videoUrl, checkContent=True, sortWithMaxBitrate=999999999)
                 for item in tmp:
                    videoUrl = item['url']
              return videoUrl
           videoUrl = self.cm.ph.getSearchGroups(data, '''src: ['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl: return videoUrl
           videoUrl = self.cm.ph.getSearchGroups(data, '''file:['"]([^"^']+?\.mp4)['"]''')[0].replace('&amp;','&')
           if videoUrl: return videoUrl
           videoUrl = self.cm.ph.getSearchGroups(data, '''file:['"]([^"^']+?\.m3u8)['"]''')[0].replace('&amp;','&')
           if videoUrl: return videoUrl
           if 'File Not Found' in data: 
              SetIPTVPlayerLastHostError(_(' File Not Found.'))
              return []
           if 'File is awaiting for moderation' in data: 
              SetIPTVPlayerLastHostError(_(' File is awaiting for moderation.'))
              return []
           return ''

        if parser == 'http://porn720.net':
           COOKIEFILE = os_path.join(GetCookieDir(), 'porn720.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE, 'return_data': True}
           sts, data = self.getPage(url, 'porn720.cookie', 'porn720.org', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+str(data) )
           videoUrl = self.cm.ph.getSearchGroups(data, '''<iframe[^>]+?src=['"]([^"^']+?)['"]''')[0] 
           if videoUrl:
              return self.getResolvedURL(self.FullUrl(videoUrl))
           videoUrl = re.compile('<source src="(.+?)"', re.DOTALL).findall(data)
           if videoUrl:
              videoUrl = urlparser.decorateUrl(videoUrl[-1], {'User-Agent': self.USER_AGENT, 'Referer': url}) 
              self.defaultParams['max_data_size'] = 0
              sts, data = self.getPage(videoUrl, 'porn720.cookie', 'porn720.org', self.defaultParams)
              if not sts: return ''
              return data.meta['url']

           videoUrl = self.cm.ph.getSearchGroups(data, '''720p['"]:['"]([^"^']+?)['"]''')[0] 
           if videoUrl:
              return urlparser.decorateUrl(videoUrl, {'User-Agent': self.USER_AGENT, 'Referer': url}) 
           videoUrl = self.cm.ph.getSearchGroups(data, '''480p['"]:['"]([^"^']+?)['"]''')[0] 
           if videoUrl:
              return urlparser.decorateUrl(videoUrl, {'User-Agent': self.USER_AGENT, 'Referer': url}) 
           return ''

        if parser == 'https://fapset.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'fapset.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return ''
           printDBG( 'Host  data: '+data )
           videoUrl = self.cm.ph.getSearchGroups(data, '''<iframe[^>]+?src=['"]([^"^']+?)['"]''')[0] 
           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           return self.getResolvedURL(videoUrl)

        if parser == 'http://www.filmyporno.tv':
           COOKIEFILE = os_path.join(GetCookieDir(), 'filmyporno.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return ''
           match = re.findall('source src="(.*?)"', data, re.S)
           if match: return match[0]
           else: return ''

        if parser == 'https://daftsex.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'daftsex.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           self.defaultParams['header']['Referer'] = parser
           sts, data = self.get_Page(url)
           if not sts: return ''

           #printDBG( 'Host  data: '+data )
           videoUrl = self.cm.ph.getSearchGroups(data, '''<iframe[^>]+?src=['"](https://da[^"^']+?)['"]''')[0] 
           sts, data2 = self.get_Page(videoUrl)
           if not sts: return ''
           printDBG( 'Host  data2: '+data2 )
           server = self.cm.ph.getSearchGroups(data2, '''server:\s*?['"]([^"^']+?)['"]''')[0] 
           printDBG( 'Host  server1:%s' % server )
           s = list(server)
           printDBG( 'Host  server list:%s' % s )
           s.reverse()
           printDBG( 'Host  server list2:%s' % s )
           server = base64.b64decode(str(''.join(s)))
           printDBG( 'Host  server2:%s' % server)
           try:
              try:
                 match = re.compile('id: "([^"]+)_([^"]+)".+:"(\d+)\.([^"]+)"}', re.DOTALL | re.IGNORECASE).findall(data2)[0]
                 (id1, id2, res, extra) =  match
                 video =  id1 + '/' + id2 + '/' + res + '.mp4?extra=' + extra
                 printDBG( 'Host  video: '+video )
                 return 'https://' + server + '/videos/' + video
              except Exception: 
                 printExc()
              try:
                 match = re.compile('id: "([^"]+)_([^"]+)".+"(\d+)"\:"([^"]+)"}', re.DOTALL | re.IGNORECASE).findall(data2)[0] 
                 (id1, id2, res, extra) =  match
                 video =  id1 + '/' + id2 + '/' + res + '.mp4?extra=' + extra
                 printDBG( 'Host  video: '+video )
                 return 'https://' + server + '/videos/' + video
              except Exception: 
                 printExc()
           except Exception: 
              printExc()
           return ''

        if parser == 'https://videobin.co':
            baseUrl = strwithmeta(url)
            referer = baseUrl.meta.get('Referer', '')
            self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
            if referer != '': self.HTTP_HEADER['Referer'] = referer
            COOKIEFILE = os_path.join(GetCookieDir(), 'videobin.cookie')
            self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
            sts, data = self.get_Page(url)
            if not sts: return ''
            printDBG( 'Host  data: %s' % data )
            data = self.cm.ph.getDataBeetwenMarkers(data, 'sources:', ']', False)[1]
            data = re.compile('"(http[^"]+?)"').findall(data)
            for videoUrl in data:
                if videoUrl.split('?')[0].endswith('m3u8'):
                    printDBG( 'Host  videoUrl: %s' % videoUrl )
                    #if self.cm.isValidUrl(videoUrl): 
                    #    videoUrl = urlparser.decorateUrl(videoUrl, {'Referer': referer}) 
                    #    tmp = getDirectM3U8Playlist(videoUrl, checkContent=True, sortWithMaxBitrate=999999999)
                    #    for item in tmp:
                    #        printDBG( 'Host listsItems valtab: '  +str(item))
                    #        return item['url']
                elif videoUrl.split('?')[0].endswith('mp4'):
                    printDBG( 'Host  videoUrl: %s' % videoUrl )
                    videoUrl = urlparser.decorateUrl(videoUrl, {'Referer': referer, 'User-Agent': self.USER_AGENT}) 
                    return videoUrl
            return ''

        if parser == 'https://lovehomeporn.com/':
           COOKIEFILE = os_path.join(GetCookieDir(), 'lovehomeporn.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           self.defaultParams['header']['Referer'] = parser
           sts, data = self.get_Page(url)
           if not sts: return ''
           printDBG( 'Host  data: '+data )
           id = self.cm.ph.getSearchGroups(data, '''video_id\s*=\s*['"]([^"^']+?)['"]''')[0] 
           videoUrl = "https://lovehomeporn.com/media/nuevo/config.php?key=%s" % id
           sts, data = self.get_Page(videoUrl)
           if not sts: return ''
           printDBG( 'Host  data2: '+data )
           videoUrl = ph.search(data, '''<file>([^>]+?)<''')[0].replace('&amp;','&')
           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           return urlparser.decorateUrl(videoUrl, {'Referer': url}) 

        if parser == 'http://www.pornrabbit.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornrabbit.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'pornrabbit.cookie', 'pornrabbit.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host data: '+data )
           videoUrl = self.cm.ph.getDataBeetwenMarkers(data, 'content="                ', '                      "/>', False) [1]
           printDBG( 'Ezt talaltam: '+videoUrl )
           return videoUrl
           

        if parser == 'https://www.eroprofile.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'eroprofile.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source src=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           return urlparser.decorateUrl(videoUrl, {'Referer': url}) 

        if parser == 'http://www.absoluporn.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'absoluporn.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source src=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           return urlparser.decorateUrl(videoUrl, {'Referer': url}) 

        if parser == 'https://www.amateurcool.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'amateurcool.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'amateurcool.cookie', 'amateurcool.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source src=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           return urlparser.decorateUrl(videoUrl, {'Referer': url}) 

        if parser == 'https://mangovideo':
           COOKIEFILE = os_path.join(GetCookieDir(), 'mangovideo.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           license_code = self.cm.ph.getSearchGroups(data, '''license_code\s*?:\s*?['"]([^"^']+?)['"]''')[0]
           videoUrl = self.cm.ph.getSearchGroups(data, '''video_url\s*?:\s*?['"]([^"^']+?)['"]''')[0]
           printDBG( 'Host license_code: %s' % license_code )
           printDBG( 'Host video_url: %s' % videoUrl )		   
           if 'function/0/' in videoUrl:
              videoUrl = decryptHash(videoUrl, license_code, '16')
           return urlparser.decorateUrl(videoUrl, {'Referer': url, 'User-Agent': self.HTTP_HEADER['User-Agent']}) 

        if parser == 'http://anybunny.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'anybunny.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'anybunny.cookie', 'anybunny.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           videoPage = self.cm.ph.getAllItemsBeetwenMarkers(data, '<iframe', '</iframe>')
           for item in videoPage:
              if 'exoclick' in item: continue
              printDBG( 'Host  videoPage: '+item )
              videoUrl = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''')[0] 
           if ''== videoUrl:
              videoUrl = self.cm.ph.getSearchGroups(data, '''source src=['"]([^"^']+?)['"]''')[0] 
              if 'm3u8' in videoUrl:
                 tmp = getDirectM3U8Playlist(videoUrl, checkContent=True, sortWithMaxBitrate=999999999)
                 for item in tmp:
                    return item['url']
              else:
                 return strwithmeta(videoUrl, {'Referer': url, 'User-Agent': self.USER_AGENT})

           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           sts, data = self.get_Page(videoUrl)
           if not sts: return ''
           printDBG( 'Host  data2: '+data )
           self.domains = ['vartuc.com', "azblowjobtube.com"]
           try:
              js_link = re.compile("src='(/kt_player/.*?)'", re.DOTALL | re.IGNORECASE).search(data).group(1)
           except Exception: 
              printExc()
              videoUrl = self.cm.ph.getSearchGroups(data, '''source src=['"]([^"^']+?)['"]''')[0] 
              printDBG( 'Host  videoUrl: '+videoUrl )

           js_path = 'https://' + self.domains[0] + js_link + '&ver=x'
           sts, data = self.getPage(js_path, 'anybunny.cookie', 'anybunny.com', self.defaultParams)
           js = data.split(";")
           js = [line for line in js if (line.startswith("gh") or line.startswith("irue842")) and '=' in line and '(' not in line and ')' not in line]
           js = "\n".join(js)
           printDBG( 'Host  js: %s' % js )
           urls = js_execute( js+ '\nfor (n in this){print(n+"="+this[n]+";");}')
           videoUrl = self.cm.ph.getSearchGroups(urls['data'], '''src=['"]([^"^']+?)['"]''')[0] 
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return strwithmeta(videoUrl, {'Referer': url, 'User-Agent': self.USER_AGENT})
           return ''

        if parser == 'https://hqporner.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'hqporner.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'hqporner.cookie', 'hqporner.com', self.defaultParams)
           if not sts: return ''
           if 'page not found' in data:
              SetIPTVPlayerLastHostError(_(' Oops, page not found!'))
              return []
           printDBG( 'Host listsItems data: '+data )
           videoUrl = self.cm.ph.getSearchGroups(data, '''<iframe[^>]+?src=['"]([^"^']+?)['"]''')[0] 
           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           sts, data = self.get_Page(videoUrl)
           if not sts: return ''
           printDBG( 'Host  data2: '+data )
           p1080 = ''
           p720 = ''
           p360 = ''
           p240 = ''
           subData = data.split('<source')
           if len(subData): del subData[0]
           if subData:
              for item in subData:
                 src = self.cm.ph.getSearchGroups(item, '''['"](//[^"^']+?)['"]''')[0].replace('\\','')
                 if '1080' in item: 
                    if src.startswith('//'): src = 'https:' + src
                    p1080 = src
                 if '720' in item: 
                    if src.startswith('//'): src = 'https:' + src
                    p720 = src
                 if '360' in item: 
                    if src.startswith('//'): src = 'https:' + src
                    p360 = src
                 if '240' in item: 
                    if src.startswith('//'): src = 'https:' + src
                    p240 = src
              if p1080: return p1080
              if p720: return p720
              if p360: return p360
              if p240: return p240
           subData = self.cm.ph.getDataBeetwenMarkers(data, 'var srca', ']', False)[1].split('}')
           if subData:
              for item in subData:
                 label   = self.cm.ph.getSearchGroups(item, 'label:\s*?"([^"]+?)"')[0]
                 src     = self.cm.ph.getSearchGroups(item, 'file:\s*?"([^"]+?)"')[0]
                 if '1080' in label: 
                    if src.startswith('//'): src = 'https:' + src
                    p1080 = src
                 if '720' in label: 
                    if src.startswith('//'): src = 'https:' + src
                    p720 = src
                 if '360' in label: 
                    if src.startswith('//'): src = 'https:' + src
                    p360 = src
                 if '240' in label: 
                    if src.startswith('//'): src = 'https:' + src
                    p240 = src
              if p1080: return p1080
              if p720: return p720
              if p360: return p360
              if p240: return p240
           videoUrl = re.compile("<source src='([^']+)'", re.DOTALL | re.IGNORECASE).findall(data)
           if videoUrl:
              videoUrl = videoUrl[0]
              if videoUrl.startswith('//'): videoUrl = 'https:' + videoUrl
              return videoUrl
           videoUrl = re.compile("<script type='text/javascript' src='([^']+)'></script>", re.DOTALL | re.IGNORECASE).findall(data)
           if videoUrl:
              videoUrl = videoUrl[-1]
              sts, data = self.get_Page(videoUrl)
              if not sts: return ''
              printDBG( 'Host  data2: '+data )
              videoUrl = re.compile('file": "([^"]+)"', re.DOTALL | re.IGNORECASE).findall(data)
              videoUrl = videoUrl[-1]
              if videoUrl.startswith('//'):
                 videoUrl = 'https:' + videoUrl
              return videoUrl
           videoUrl = re.compile('file": "([^"]+)"', re.DOTALL | re.IGNORECASE).findall(data)
           if videoUrl:
              videoUrl = videoUrl[-1]
              if videoUrl.startswith('//'): videoUrl = 'https:' + videoUrl
              return videoUrl
           return ''

        if parser == 'https://www.naked.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'naked.cookie')
           UA = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/37.0.2062.120 Chrome/37.0.2062.120 Safari/537.36"
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': False, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'naked.cookie', 'naked.com', self.defaultParams)
           if not sts: return ''
           modelname = self.cm.meta['url'].split('=')[-1]
           id = ''
           host = ''
           data = data.replace('\\','')
           printDBG( 'Host listsItems data: '+data )
           data = data.split('<div class="live clearfix')
           if len(data): del data[0]
           for item in data:
              id = self.cm.ph.getSearchGroups(item, '''data-model-id=['"]([^"^']+?)['"]''')[0] 
              host = self.cm.ph.getSearchGroups(item, '''data-video-host=['"]([^"^']+?)['"]''')[0] 
              if modelname == self.cm.ph.getSearchGroups(item, '''data-model-seo-name=['"]([^"^']+?)['"]''', 1, True)[0]: 
                 if 'multi-user-private' in item: 
                    SetIPTVPlayerLastHostError(_(' Private Show.'))
                    return []
                 break
           videoUrl = 'https://manifest.vscdns.com/manifest.m3u8?key=nil&provider=highwinds&host='+host+'&model_id='+id+'&secure=true&prefix=amlst&youbora-debug=1'
           PHPSESSID = self.cm.getCookieItem(COOKIEFILE, 'PHPSESSID')
           videoUrl = urlparser.decorateUrl(videoUrl, {'Referer': self.cm.meta['url'], 'Cookie':'PHPSESSID=%s' % PHPSESSID, 'User-Agent': UA, 'iptv_livestream':True, 'Origin':'https://www.naked.com'})
           tmp = getDirectM3U8Playlist(videoUrl, checkContent=True, sortWithMaxBitrate=999999999)
           for item in tmp:
              return item['url']
           return ''

        if parser == 'https://www.pornrewind.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornrewind.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           videoUrl = self.cm.ph.getSearchGroups(data, '''video_url:\s*['"]([^"^']+?)['"]''')[0] 
           return videoUrl

        if parser == 'https://spankbang.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'spankbang.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE, 'return_data': True}
           sts, data = self.getPage(url, 'spankbang.cookie', 'spankbang.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+str(data) )
           videoid = self.cm.ph.getSearchGroups(data, '''data-videoid=['"]([^"^']+?)['"]''')[0]
           streamkey = self.cm.ph.getSearchGroups(data, '''data-streamkey=['"]([^"^']+?)['"]''')[0]
           sb_csrf_session = self.cm.getCookieItem(COOKIEFILE,'sb_csrf_session')
           api = 'https://spankbang.com/api/videos/stream'
           postdata = {'id' : streamkey, 'data': 0, 'sb_csrf_session': sb_csrf_session} 
           self.defaultParams['header']['X-Requested-With'] = 'XMLHttpRequest'
           self.defaultParams['header']['X-CSRFToken'] = sb_csrf_session
           sts, data = self.getPage(api, 'spankbang.cookie', 'spankbang.com', self.defaultParams, postdata)
           if not sts: return ''
           printDBG( 'Host listsItems data2: '+data )
           try:
              if data.startswith('{'): data = '['+data+']'
              result = byteify(simplejson.loads(data))
              for item in result:
                 try:
                    if str(item["stream_url_1080p"]) : return self.cm.getFullUrl(str(item["stream_url_1080p"][0]))
                    if str(item["stream_url_720p"]) : return self.cm.getFullUrl(str(item["stream_url_720p"][0]))
                    if str(item["stream_url_480p"]) : return self.cm.getFullUrl(str(item["stream_url_480p"][0]))
                    if str(item["stream_url_320p"]) : return self.cm.getFullUrl(str(item["stream_url_320p"][0]))
                    if str(item["stream_url_240p"]) : return self.cm.getFullUrl(str(item["stream_url_240p"][0]))
                 except Exception as e:
                    printExc()
                 try:
                    if str(item["1080p"]) != '[]': return self.cm.getFullUrl(str(item["1080p"][0]))
                    if str(item["720p"])  != '[]': return self.cm.getFullUrl(str(item["720p"][0]))
                    if str(item["480p"])  != '[]': return self.cm.getFullUrl(str(item["480p"][0]))
                    if str(item["320p"])  != '[]': return self.cm.getFullUrl(str(item["320p"][0]))
                    if str(item["240p"])  != '[]': return self.cm.getFullUrl(str(item["240p"][0]))
                 except Exception as e:
                    printExc()
           except Exception as e:
              printExc()
           return ''

        if parser == 'https://upstream.to':
           COOKIEFILE = os_path.join(GetCookieDir(), 'upstream.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE, 'return_data': True}
           sts, data = self.getPage(url, 'upstream.cookie', 'upstream.to', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+str(data) )
           videoUrl = ph.search(data, '''file:['"]([^'^"]+?)['"]''')[0]
           return videoUrl

        if parser == 'https://prostream.to':
           COOKIEFILE = os_path.join(GetCookieDir(), 'prostream.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE, 'return_data': True}
           sts, data = self.getPage(url, 'prostream.cookie', 'prostream.to', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+str(data) )
           if "eval(function(p,a,c,k,e,d)" in data:
              printDBG( 'Host resolveUrl packed' )
              packed = re.compile('>eval\(function\(p,a,c,k,e,d\)(.+?)</script>', re.DOTALL).findall(data)
              if packed:
                 packed = packed[-1]
              else:
                 return ''
              try:
                 videoPage = unpackJSPlayerParams(packed, TEAMCASTPL_decryptPlayerParams, 0, True, True) 
              except Exception: pass 
              printDBG( 'Host videoPage: '+str(videoPage) )
              videoUrl = ph.search(videoPage, '''file:['"]([^'^"]+?)['"]''')[0]
              if not videoUrl: videoUrl = ph.search(videoPage, '''sources:\[['"]([^'^"]+?)['"]''')[0]
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return videoUrl 
           return ''

        if parser == 'https://www.cumlouder.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'cumlouder.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'cumlouder.cookie', 'cumlouder.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source src=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           return urlparser.decorateUrl(videoUrl, {'Referer': url})

        if parser == 'https://pornone.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornone.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'pornone.cookie', 'pornone.com', self.defaultParams)
           printDBG( 'Elemek: '+data )
           
           videoUrl = self.cm.ph.getDataBeetwenMarkers(data, ' /> <source src="', '" type="video/mp4"', False)[1]
           printDBG( 'Ezt talaltam: '+videoUrl )
           return videoUrl
  
        if parser == 'http://sexu.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'sexu.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           videoUrl = self.cm.ph.getSearchGroups(data, '''downloadUrl":['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return urlparser.decorateUrl(videoUrl, {'Referer': 'http://sexu.com/'})
           videoUrl = re.findall('"file":"(.*?\.mp4)"', data, re.S)
           if videoUrl:
              return urlparser.decorateUrl(videoUrl[-1], {'Referer': 'http://sexu.com/'}) 
           videoUrl = self.cm.ph.getSearchGroups(data, '''"src":['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return urlparser.decorateUrl(videoUrl, {'Referer': 'http://sexu.com/'}) 
 
        if parser == 'http://www.amateurporn.net':
           COOKIEFILE = os_path.join(GetCookieDir(), 'amateurporn.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           license_code = self.cm.ph.getSearchGroups(data, '''license_code\s*?:\s*?['"]([^"^']+?)['"]''')[0]
           videoUrl = self.cm.ph.getSearchGroups(data, '''video_url\s*?:\s*?['"]([^"^']+?)['"]''')[0]
           printDBG( 'Host license_code: %s' % license_code )
           printDBG( 'Host video_url: %s' % videoUrl )
           if license_code and videoUrl:
              if 'function/0/' in videoUrl:
                 videoUrl = decryptHash(videoUrl, license_code, '16')
              return urlparser.decorateUrl(videoUrl, {'Referer': url}) 
           videoUrl = self.cm.ph.getSearchGroups(data, '''<iframe[^>]+?src=['"]([^"^']+?)['"]''')[0] 
           if videoUrl:
              return self.getResolvedURL(self.FullUrl(videoUrl))
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source[^>]+?src=['"]([^"^']+?mp4)['"]''')[0] 
           if videoUrl:
              return self.FullUrl(videoUrl)
           videoUrl = self.cm.ph.getSearchGroups(data, '''file:\s*?['"]([^"^']+?mp4)['"]''')[0] 
           if videoUrl:
              return self.FullUrl(videoUrl)
           return ''

        if parser == 'http://www.hdporn.net':
           COOKIEFILE = os_path.join(GetCookieDir(), 'hdporn.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return
           printDBG( 'Host listsItems data: '+data )
           match = re.findall('source src="(.*?)"', data, re.S)
           if match: return match[0]
           else: return ''

        if parser == 'http://pornicom.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornicom.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return ''
           #printDBG( 'Host data:%s' % data )
           data2 = self.cm.ph.getDataBeetwenMarkers(data, 'var flashvars', '}', False)[1]
           if data2: 
              printDBG( 'Host data2:%s' % data2 )
              return self.cm.ph.getSearchGroups(data2, '''video_url:\s*?['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           videoPage = self.cm.ph.getSearchGroups(data, '''file: ['"]([^"^']+?)['"]''')[0] 
           if videoPage: 
              printDBG( 'Host data file:%s' % videoPage )
              return videoPage
           return ''

        if parser == 'http://www.porn00.org':
           COOKIEFILE = os_path.join(GetCookieDir(), 'porn00.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'porn00.cookie', 'porn00.org', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           license_code = self.cm.ph.getSearchGroups(data, '''license_code\s*?:\s*?['"]([^"^']+?)['"]''')[0]
           videoUrl = self.cm.ph.getSearchGroups(data, '''video_alt_url\s*?:\s*?['"]([^"^']+?)['"]''')[0]
           if 'login' in videoUrl or ''==videoUrl: videoUrl = self.cm.ph.getSearchGroups(data, '''video_url\s*?:\s*?['"]([^"^']+?)['"]''')[0]
           printDBG( 'Host license_code: %s' % license_code )
           printDBG( 'Host video_url: %s' % videoUrl )
           if 'function/0/' in videoUrl:
              videoUrl = decryptHash(videoUrl, license_code, '16')
           return urlparser.decorateUrl(videoUrl, {'Referer': url}) 

        if parser == 'https://porngo.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'porngo.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'porngo.cookie', 'porngo.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           videoUrl = self.FullUrl(self.cm.ph.getSearchGroups(data, '''<source[^>]+?src=['"]([^"^']+?)['"]''')[0])
           if videoUrl:
              return urlparser.decorateUrl(videoUrl, {'Referer': url}) 
           return ''

        if parser == 'https://porndoe.com':
           host = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
           COOKIEFILE = os_path.join(GetCookieDir(), 'porndoe.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return ''
           printDBG( 'Linkekhez: '+data )
           videoUrl = self.cm.ph.getDataBeetwenMarkers(data, 'contentUrl" content="', '" />', False)[1]
           #if '240p-400.mp4?' in videoUrl: videoUrl = videoUrl.replace('240p-400.mp4?', '480p-1000.mp4?burst=16080k&rate=268k&')
           #videoPage = self.FullUrl(self.cm.ph.getDataBeetwenMarkers(data, 'embedURL" content="', '"/>', False)[1]
           #id = self.cm.ph.getDataBeetwenMarkers(data, '"id": "', '"'[1]

           #videoUrl= 'https://porndoe.com/service/index?device=desktop&page=video&id='+id

           #sts, data = self.get_Page(videoUrl, self.defaultParams)
           #if not sts: return ''
           #printDBG( 'Host listsItems data2: '+data )
           #try:
            #  data = self.cm.ph.getDataBeetwenMarkers(data, '"sources":', '}},', False)[1]
             # if data.startswith('{'): data = '['+data+'}]'
              #printDBG( 'Host listsItems data3: '+data )
              #result = byteify(simplejson.loads(data))
              #for item in result:
               #  try:
                #    if str(item["720"]["url"]) : return strwithmeta(str(item["720"]["url"]), {'Referer': url}) 
                #    if str(item["480"]["url"]) : return strwithmeta(str(item["480"]["url"]), {'Referer': url})
                #    if str(item["240"]["url"]) : return strwithmeta(str(item["240"]["url"]), {'Referer': url})
                 #except Exception as e:
                  #  printExc()
           #except Exception as e:
            #  printExc()
           #sts, data = self.get_Page(videoPage, self.defaultParams)
           #if not sts: return ''
           #printDBG( 'Host listsItems data4: '+data )
           #try:
            #  data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<source', '>')
             # for item in data:
              #   printDBG( 'Host item: '+str(item) )
              #videoUrl = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0]
              #if videoUrl: return strwithmeta(videoUrl, {'Referer': url})
           #except Exception as e:
            #  printExc()
           return videoUrl

        if parser == 'https://hdsite.net':
           COOKIEFILE = os_path.join(GetCookieDir(), 'hdsite.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           license_code = self.cm.ph.getSearchGroups(data, '''license_code\s*?:\s*?['"]([^"^']+?)['"]''')[0]
           videoUrl = self.cm.ph.getSearchGroups(data, '''video_url\s*?:\s*?['"]([^"^']+?)['"]''')[0]
           videoUrl = self.cm.ph.getSearchGroups(data, '''video_url\s*?:\s*?['"]([^"^']+?)['"]''')[0]
           printDBG( 'Host license_code: %s' % license_code )
           printDBG( 'Host video_url: %s' % videoUrl )
           if 'function/0/' in videoUrl:
              videoUrl = decryptHash(videoUrl, license_code, '16')
           return urlparser.decorateUrl(videoUrl, {'Referer': url, 'User-Agent': self.HTTP_HEADER['User-Agent']})

        if parser == 'https://p720.net':
           COOKIEFILE = os_path.join(GetCookieDir(), 'p720.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           if 'hdsite.net/embed/' in data:
              videoUrl = self.FullUrl(self.cm.ph.getSearchGroups(data, '''<iframe[^>]+?src=['"]([^"^']+?)['"]''')[0])
              return self.getResolvedURL(videoUrl)
           if not 'mp4' in data: SetIPTVPlayerLastHostError('LOGIN REQUIRED')
           license_code = self.cm.ph.getSearchGroups(data, '''license_code\s*?:\s*?['"]([^"^']+?)['"]''')[0]
           videoUrl = self.cm.ph.getSearchGroups(data, '''video_url\s*?:\s*?['"]([^"^']+?)['"]''')[0]
           printDBG( 'Host license_code: %s' % license_code )
           printDBG( 'Host video_url: %s' % videoUrl )
           if 'function/0/' in videoUrl:
              videoUrl = decryptHash(videoUrl, license_code, '16')
           return urlparser.decorateUrl(videoUrl, {'Referer': url, 'User-Agent': self.HTTP_HEADER['User-Agent']})

        if parser == 'https://www.extremetube.com':
            COOKIEFILE = os_path.join(GetCookieDir(), 'extremetube.cookie')
            self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
            self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
            sts, data = self.get_Page(url)
            if not sts: return ''
            printDBG( 'Host listsItems data: '+data )
            videoPage = re.findall('"quality_\d+p":"(.*?)"', data, re.S) 
            if videoPage:
                url = videoPage[-1].replace('\/','/') 
                return self.FullUrl(url)
            return '' 

        if parser == 'http://xhamster.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'xhamster.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           videoUrl = self.FullUrl(self.cm.ph.getSearchGroups(data, '''1080p['"]:['"]([^'"]+?)['"]''')[0]).replace('&amp;','&').replace(r"\/",r"/")
           if videoUrl: 
              return strwithmeta(videoUrl, {'Referer': url})
           videoUrl = self.FullUrl(self.cm.ph.getSearchGroups(data, '''720p['"]:['"]([^'"]+?)['"]''')[0]).replace('&amp;','&').replace(r"\/",r"/")
           if videoUrl: 
              return strwithmeta(videoUrl, {'Referer': url})
           videoUrl = self.FullUrl(self.cm.ph.getSearchGroups(data, '''480p['"]:['"]([^'"]+?)['"]''')[0]).replace('&amp;','&').replace(r"\/",r"/")
           if videoUrl: 
              return strwithmeta(videoUrl, {'Referer': url})
           videoUrl = self.FullUrl(self.cm.ph.getSearchGroups(data, '''240p['"]:['"]([^'"]+?)['"]''')[0]).replace('&amp;','&').replace(r"\/",r"/")
           if videoUrl: 
              return strwithmeta(videoUrl, {'Referer': url})
           videoUrl = self.FullUrl(self.cm.ph.getSearchGroups(data, '''144p['"]:['"]([^'"]+?)['"]''')[0]).replace('&amp;','&').replace(r"\/",r"/")
           if videoUrl: 
              return strwithmeta(videoUrl, {'Referer': url})
           return ''

        if parser == 'https://anyporn.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'anyporn.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'anyporn.cookie', 'anyporn.com', self.defaultParams)
           if not sts: return ''
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<source', '>')
           for item in data:
              videoUrl = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           return strwithmeta(videoUrl, {'Referer': url})

        if parser == 'https://anon-v.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'anon-v.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'anon-v.cookie', 'anon-v.com', self.defaultParams)
           if not sts: return ''
           license_code = self.cm.ph.getSearchGroups(data, '''license_code\s*?:\s*?['"]([^"^']+?)['"]''')[0]
           videoUrl = self.cm.ph.getSearchGroups(data, '''video_url\s*?:\s*?['"]([^"^']+?)['"]''')[0]
           printDBG( 'Host license_code: %s' % license_code )
           printDBG( 'Host video_url: %s' % videoUrl )
           if 'function/0/' in videoUrl:
              videoUrl = decryptHash(videoUrl, license_code, '16')
           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           return urlparser.decorateUrl(videoUrl, {'Referer': url})

        if parser == 'https://www.sleazyneasy.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'sleazyneasy.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'sleazyneasy.cookie', 'sleazyneasy.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           license_code = self.cm.ph.getSearchGroups(data, '''license_code\s*?:\s*?['"]([^"^']+?)['"]''')[0]
           videoUrl = self.cm.ph.getSearchGroups(data, '''video_url\s*?:\s*?['"]([^"^']+?)['"]''')[0]
           printDBG( 'Host license_code: %s' % license_code )
           printDBG( 'Host video_url: %s' % videoUrl )
           if 'function/0/' in videoUrl:
              videoUrl = decryptHash(videoUrl, license_code, '16')
           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           return urlparser.decorateUrl(videoUrl, {'Referer': self.cm.meta['url']})

        if parser == 'https://javhoho.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'javhoho.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'javhoho.cookie', 'javhoho.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           videoUrl = self.cm.ph.getSearchGroups(data, '''['"](https://upstream.to[^"^']+?)['"]''')[0]
           if not videoUrl: videoUrl = self.cm.ph.getSearchGroups(data, '''['"](https://www.fembed.com[^"^']+?)['"]''')[0]
           return self.getResolvedURL(videoUrl)

        if parser == 'https://forcedcelebs.net':
           COOKIEFILE = os_path.join(GetCookieDir(), 'forcedcelebs.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           videoPage = self.cm.ph.getSearchGroups(data, '''<iframe[^>]+?src=['"]([^"^']+?)['"]''')[0] 
           if videoPage.startswith('//'): videoPage = 'http:' + videoPage
           return self.getResolvedURL(videoPage)

        if parser == 'https://www.yourupload.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'yourupload.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+data )
           videoUrl = self.cm.ph.getSearchGroups(data, '''file\s*:\s*['"]([^"^']+?)['"]''')[0] 
           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           videoUrl = urlparse.urljoin(url, videoUrl) 
           self.defaultParams['max_data_size'] = 0
           sts, data = self.get_Page(videoUrl, self.defaultParams)
           if not sts: return ''
           return strwithmeta(self.cm.meta['url'], {'User-Agent': self.HTTP_HEADER['User-Agent'], 'Referer': url})  #

        

        if parser == 'https://familyporn.tv':
           COOKIEFILE = os_path.join(GetCookieDir(), 'familyporn.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           license_code = self.cm.ph.getSearchGroups(data, '''license_code\s*?:\s*?['"]([^"^']+?)['"]''')[0]
           videoUrl = self.cm.ph.getSearchGroups(data, '''video_alt_url\s*?:\s*?['"]([^"^']+?)['"]''')[0]
           if videoUrl=='': videoUrl = self.cm.ph.getSearchGroups(data, '''video_url\s*?:\s*?['"]([^"^']+?)['"]''')[0]
           printDBG( 'Host license_code: %s' % license_code )
           printDBG( 'Host video_url: %s' % videoUrl )
           if 'function/0/' in videoUrl:
              videoUrl = decryptHash(videoUrl, license_code, '16')
           return urlparser.decorateUrl(videoUrl, {'Referer': url, 'User-Agent': self.HTTP_HEADER['User-Agent']})

        if parser == 'https://bitporno.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'bitporno.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.HTTP_HEADER['Referer'] = url
           self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.get_Page(url, self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+data )
           videoUrl = self.cm.ph.getSearchGroups(data, '''file:\s*?['"]([^"^']+?)['"]''')[0]
           videoUrl = urlparser.decorateUrl(videoUrl, {'Referer': url, 'User-Agent': self.HTTP_HEADER['User-Agent'], 'iptv_livestream':True, 'Origin':'https://bitporno.com'})
           printDBG( 'Ezt talaltam: '+videoUrl )
           if videoUrl.startswith('/m3u8'): videoUrl = 'https://www.bitporno.com' + videoUrl
           return videoUrl

##########################################################################################################################
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        try:
           data = self.cm.getURLRequestData(query_data)
           printDBG( 'Host getResolvedURL data: '+data )
        except:
           printDBG( 'Host getResolvedURL query error' )
           return videoUrl

        if parser == 'file: ':
           return self.cm.ph.getSearchGroups(data, '''file: ['"]([^"^']+?)['"]''')[0] 

        if parser == "0p'  : '":
           videoPage = re.findall("0p'  : '(http.*?)'", data, re.S)   
           if videoPage:
              return videoPage[-1]
           return ''

        if parser == 'source src="':
           videoPage = re.findall('source src="(http.*?)"', data, re.S)   
           if videoPage:
              return videoPage[-1]
           return ''

        if parser == "video_url: '":
           videoPage = re.findall("video_url: '(.*?).'", data, re.S)   
           if videoPage:
              printDBG( 'Host videoPage:'+videoPage[0])
              return videoPage[0]
           return ''

        if parser == 'videoFile="':
           videoPage = re.findall('videoFile="(.*?)"', data, re.S)   
           if videoPage:
              printDBG( 'Host videoPage:'+videoPage[0])
              return videoPage[0]
           return ''

        if parser == 'http://www.ah-me.com':
           videoUrl = ph.search(data, '''<video\ssrc=['"]([^'^"]+?)['"]''')[0]
           return urlparser.decorateUrl(videoUrl, {'Referer': url})

        if parser == 'http://www.nuvid.com':
           videoUrl = re.search("http://www.nuvid.com/video/(.*?)/.+", url, re.S)
           if videoUrl:
              xml = 'http://m.nuvid.com/video/%s' % videoUrl.group(1)
              try:    data = self.cm.getURLRequestData({'url': xml, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True})
              except: 
                 printDBG( 'Host getResolvedURL query error xml' )
                 return ''
              #printDBG( 'Host data json: '+data )
              videoPage = re.findall('source src="(.*?)"', data, re.S)   
              if videoPage:
                 return videoPage[0]
           return ''

        if parser == 'http://www.wankoz.com':
           videoPage = re.findall("'video_html5_url']='(.*?).'", data, re.S)   
           if videoPage:
              printDBG( 'Host videoPage:'+videoPage[0])
              return videoPage[0]
           return ''

        if parser == 'https://alpha.tnaflix.com':
           videoPage = re.findall('"embedUrl" content="(.*?)"', data, re.S)   
           if videoPage:
              printDBG( 'Host videoPage:'+videoPage[0])
              return 'http:'+videoPage[0]
           return ''

        if parser == 'http://www.faphub.xxx':
           videoPage = re.findall("url: '(.*?)'", data, re.S)   
           if videoPage:
              printDBG( 'Host videoPage:'+videoPage[0])
              return videoPage[0]
           return ''
   
        if parser == 'http://www.proporn.com':
           videoPage = re.findall('source src="(.*?)"', data, re.S)   
           if videoPage:
              printDBG( 'Host videoPage:'+videoPage[0])
              return videoPage[0]
           return ''
   
        if parser == 'http://www.xnxx.com':
           videoUrl = self.cm.ph.getSearchGroups(data, '''VideoUrlHigh\(['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return urllib2.unquote(videoUrl)
           videoUrl = self.cm.ph.getSearchGroups(data, '''VideoUrlLow\(['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return urllib2.unquote(videoUrl)
           videoUrl = self.cm.ph.getSearchGroups(data, '''VideoHLS\(['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return urllib2.unquote(videoUrl)
           videoUrl = re.search('flv_url=(.*?)&', data, re.S)
           if videoUrl: return decodeUrl(videoUrl.group(1))
           return ''

        if parser == 'http://www.xvideos.com':
           videoUrl = re.search("setVideoUrlHigh\('(.*?)'", data, re.S)
           if videoUrl: return decodeUrl(videoUrl.group(1))
           videoUrl = re.search('flv_url=(.*?)&', data, re.S)
           if videoUrl: return decodeUrl(videoUrl.group(1))
           return ''

        if parser == 'http://embed.redtube.com':
           videoPage = re.findall('sources:.*?":"(.*?)"', data, re.S)
           if videoPage:
              link = videoPage[-1].replace(r"\/",r"/")
              if link.startswith('//'): link = 'http:' + link 
              return link
           return ''

        if parser == 'http://www.eporner.com':
           data = self.cm.ph.getDataBeetwenMarkers(data, '<div class="dloaddivcol">', '</div>', False) [1]
           printDBG( 'Ez a lista: ' + data)
           videoID = self.cm.ph.getAllItemsBeetwenMarkers(data, ':<a href="', '" >Download', False)
           for i in videoID:
               videoID[videoID.index(i)] = "http://www.eporner.com" + str(i)
           return videoID[-1]
               
        if parser == 'http://www.pornhub.com/embed/':
           match = re.findall("container.*?src.*?'(.*?)'", data, re.S)
           if match: return match[0]
           return ''
        
        if parser == 'http://m.tube8.com':
           match = re.compile('<div class="play_video.+?<a href="(.+?)"', re.DOTALL).findall(data)
           return match[0]

        if parser == 'http://m.pornhub.com':
           match = re.compile('<div class="play_video.+?<a href="(.+?)"', re.DOTALL).findall(data)
           return match[0]

        if parser == 'http://www.dachix.com':
           videoPage = self.cm.ph.getSearchGroups(data, '''<source src=['"]([^"^']+?)['"]''')[0] 
           if videoPage:
              return urllib2.unquote(videoPage) 
           return ''

        if parser == 'http://www.drtuber.com':
           params = re.findall('params\s\+=\s\'h=(.*?)\'.*?params\s\+=\s\'%26t=(.*?)\'.*?params\s\+=\s\'%26vkey=\'\s\+\s\'(.*?)\'', data, re.S)
           if params:
              for (param1, param2, param3) in params:
                 hash = hashlib.md5(param3 + base64.b64decode('UFQ2bDEzdW1xVjhLODI3')).hexdigest()
                 url = '%s/player_config/?h=%s&t=%s&vkey=%s&pkey=%s&aid=' % ("http://www.drtuber.com", param1, param2, param3, hash)
                 query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
                 try:
                    data = self.cm.getURLRequestData(query_data)
                 except:
                    printDBG( 'Host listsItems query error' )
                    printDBG( 'Host listsItems query error url: '+url )
                 #printDBG( 'Host listsItems data: '+data )
                 url = re.findall('video_file>.*?(http.*?)\]\]><\/video_file>', data, re.S)
                 if url:
                    url = str(url[0])
                    url = url.replace("&amp;","&")
                    printDBG( 'Host listsItems url: '+url )
                    return url
           return ''

        if parser == 'http://www.el-ladies.com':
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source[^>]+?src=['"]([^"^']+?)['"]''')[0].replace('&amp;','&') 
           if videoUrl:
              return self.FullUrl(videoUrl)
           videoPage = re.findall(',file:\'(.*?)\'', data, re.S)  
           if videoPage:
              return videoPage[0]
           return ''

        if parser == 'http://sexylies.com':
           videoPage = re.search('source\stype="video/mp4"\ssrc="(.*?)"', data, re.S) 
           if videoPage:
              return videoPage.group(1)
           return ''

        if parser == 'http://www.eskimotube.com':
           videoPage = re.search('color=black.*?href=(.*?)>', data, re.S) 
           if videoPage:
              return videoPage.group(1)
           return ''

        if parser == 'http://www.porn5.com':
           videoPage = re.findall('p",url:"(.*?)"', data, re.S) 
           if videoPage:
              return videoPage[-1]
           return ''

        if parser == 'http://www.pornyeah.com':
           videoPage = re.findall('settings=(.*?)"', data, re.S)
           if not videoPage: return ''
           xml = videoPage[0]
           printDBG( 'Host getResolvedURL xml: '+xml )
           try:    data = self.cm.getURLRequestData({'url': xml, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True})
           except: 
                   printDBG( 'Host getResolvedURL query error xml' )
                   return videoUrl
           videoPage = re.findall('defaultVideo:(.*?);', data, re.S)
           if videoPage: return videoPage[0]
           return ''

        if parser == 'http://rusporn.tv':
           videoUrl = self.cm.ph.getSearchGroups(data, '''video_alt_url: ['"]([^"^']+?)['"]''')[0] 
           if videoUrl: return videoUrl
           videoUrl = self.cm.ph.getSearchGroups(data, '''video_url: ['"]([^"^']+?)['"]''')[0] 
           if videoUrl: return videoUrl
           return ''

        if parser == 'http://www.pornpillow.com':
           videoPage = re.findall("'file': '(.*?)'", data, re.S)   
           if videoPage:
              return videoPage[0]
           return ''

        if parser == 'http://www.thumbzilla.com':
           
           fetchurl = self.cm.ph.getDataBeetwenMarkers(data, 'defaultQuality":false,"format":"hls","videoUrl":"', '","quality"', False) [1]
           fetchurl = fetchurl.replace(r"\/",r"/")
           if fetchurl.startswith('//'): fetchurl = 'http:' + fetchurl
           printDBG( 'Ezt talaltam: '+fetchurl )
           return fetchurl 
           

        if parser == 'https://vidlox.tv':
           parse = re.search('sources.*?"(http.*?)"', data, re.S) 
           if parse: return parse.group(1).replace('\/','/')
           return ''

        if parser == 'http://xxxkingtube.com':
           parse = re.search("File = '(http.*?)'", data, re.S) 
           if parse: return parse.group(1).replace('\/','/')
           return ''

        if parser == 'http://pornsharing.com':
           parse = re.search('btoa\("(http.*?)"', data, re.S) 
           if parse: return parse.group(1).replace('\/','/')
           return ''

        if parser == 'http://pornxs.com':
           parse = re.search('config-final-url="(http.*?)"', data, re.S) 
           if parse: return parse.group(1).replace('\/','/')
           return ''

        if parser == 'http://www.flyflv.com':
           parse = re.search('fileUrl="(http.*?)"', data, re.S) 
           if parse: return parse.group(1).replace('\/','/')
           return ''

        if parser == 'http://www.yeptube.com':
           videoUrl = re.search('video_id = "(.*?)"', data, re.S)
           if videoUrl:
              xml = 'http://www.yeptube.com/player_config_json/?vid=%s&aid=0&domain_id=0&embed=0&ref=&check_speed=0' % videoUrl.group(1)
              try:    data = self.cm.getURLRequestData({'url': xml, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True})
              except: 
                 printDBG( 'Host getResolvedURL query error xml' )
                 return ''
              #printDBG( 'Host data json: '+data )
              videoPage = re.search('"hq":"(http.*?)"', data, re.S)   
              if videoPage: return videoPage.group(1).replace('\/','/')
              videoPage = re.search('"lq":"(http.*?)"', data, re.S)   
              if videoPage: return videoPage.group(1).replace('\/','/')
           return ''

        if parser == 'http://vivatube.com':
           videoUrl = re.search('video_id = "(.*?)"', data, re.S)
           if videoUrl:
              xml = 'http://vivatube.com/player_config_json/?vid=%s&aid=0&domain_id=0&embed=0&ref=&check_speed=0' % videoUrl.group(1)
              try:    data = self.cm.getURLRequestData({'url': xml, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True})
              except: 
                 printDBG( 'Host getResolvedURL query error xml' )
                 return ''
              #printDBG( 'Host data json: '+data )
              videoPage = re.search('"hq":"(http.*?)"', data, re.S)   
              if videoPage: return videoPage.group(1).replace('\/','/')
              videoPage = re.search('"lq":"(http.*?)"', data, re.S)   
              if videoPage: return videoPage.group(1).replace('\/','/')
           return ''

        if parser == 'http://www.tubeon.com':
           videoUrl = re.search('video_id = "(.*?)"', data, re.S)
           if videoUrl:
              xml = 'http://www.tubeon.com/player_config_json/?vid=%s&aid=0&domain_id=0&embed=0&ref=&check_speed=0' % videoUrl.group(1)
              try:    data = self.cm.getURLRequestData({'url': xml, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True})
              except: 
                 printDBG( 'Host getResolvedURL query error xml' )
                 return ''
              #printDBG( 'Host data json: '+data )
              videoPage = re.search('"hq":"(http.*?)"', data, re.S)   
              if videoPage: return videoPage.group(1).replace('\/','/')
              videoPage = re.search('"lq":"(http.*?)"', data, re.S)   
              if videoPage: return videoPage.group(1).replace('\/','/')
           return ''

        if parser == 'http://www.yuvutu.com':
           match = re.findall('iframe src="(.*?)"', data, re.S)
           if match: 
              url = 'http://www.yuvutu.com'+match[0]
              query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
              try:
                 data = self.cm.getURLRequestData(query_data)
              except:
                 printDBG( 'Host listsItems query error url: '+url )
              #printDBG( 'Host listsItems data: '+data )
              url = re.findall('file: "(.*?)"', data, re.S)
              if url: 
                 videoUrl = url[-1]
                 return videoUrl
           return ''

        if parser == 'https://www.realgfporn.com':
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source\ssrc=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return videoUrl
           videoUrl = self.cm.ph.getSearchGroups(data, '''file: ['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return videoUrl

        if parser == 'http://www.homemoviestube.com':
           videoUrl = self.cm.ph.getSearchGroups(data, '''value="settings=([^"^']+?)['"]''')[0]
           if videoUrl:
              query_data = { 'url': videoUrl, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
              try:
                 data = self.cm.getURLRequestData(query_data)
              except:
                 printDBG( 'Host listsItems query error url: '+url )
              #printDBG( 'Host listsItems data: '+data )
              return self.cm.ph.getSearchGroups(data, '''flvMask:([^"^']+?);''')[0]
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source src=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return videoUrl
           return ''

        if parser == 'https://porndig.com':
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source\ssrc=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           if '.m3u8' in videoUrl:
              if self.cm.isValidUrl(videoUrl): 
                 tmp = getDirectM3U8Playlist(videoUrl)
                 for item in tmp:
                    printDBG( 'Host listsItems valtab: '  +str(item))
                 return item['url']
           if 'sources": ' in data:
              try:
                 sources = self.cm.ph.getDataBeetwenMarkers(data, 'sources": ', ']', False)[1]
                 result = byteify(simplejson.loads(sources+']'))
                 for item in result:
                    try:
                       if str(item["label"])=='720p': return str(item["src"]).replace('\/','/')
                    except Exception as e:
                       printExc()
                    try:
                       if str(item["label"])=='480p': return str(item["src"]).replace('\/','/')
                    except Exception as e:
                       printExc()
                    try:
                       if str(item["label"])=='360p': return str(item["src"]).replace('\/','/')
                    except Exception as e:
                       printExc()
                    try:
                       if str(item["label"])=='240p': return str(item["src"]).replace('\/','/')
                    except Exception as e:
                       printExc()
              except Exception as e:
                 printExc()
           return videoUrl

        if parser == 'http://hentaigasm.com':
           videoUrl = self.cm.ph.getSearchGroups(data, '''file: ['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           return urllib2.unquote(videoUrl)

        if parser == 'https://www.katestube.com':
           data2 = self.cm.ph.getDataBeetwenMarkers(data, 'var flashvars', '}', False)[1]
           if data2: return self.cm.ph.getSearchGroups(data2, '''['"](https://www.katestube.com/get_file[^"^']+?)['"]''')[0].replace('&amp;','&')
           data2 = self.cm.ph.getDataBeetwenMarkers(data, 'sources:', ']', False)[1]
           if data2: return self.cm.ph.getSearchGroups(data, '''src:\s['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           videoUrl = self.cm.ph.getSearchGroups(data, '''file: ['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return urllib2.unquote(videoUrl)
           videoUrl = self.cm.ph.getSearchGroups(data, '''['"](https://www.katestube.com/get_file[^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              return urllib2.unquote(videoUrl)
           return ''

        if parser == 'https://www.pornoxo.com':
           videoUrl = self.cm.ph.getSearchGroups(data, '''"file":['"]([^"^']+?)['"]''')[0].replace('\/','/')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return urllib2.unquote(videoUrl)
           videoUrl = self.cm.ph.getSearchGroups(data, '''file\':\s['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return urllib2.unquote(videoUrl)
           videoUrl = self.cm.ph.getSearchGroups(data, '''filefallback\':\s['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return urllib2.unquote(videoUrl)
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source\ssrc=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return urllib2.unquote(videoUrl)
           videoUrl = self.cm.ph.getSearchGroups(data, '''file:\s['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return urllib2.unquote(videoUrl)

        if parser == 'http://sexkino.to':
           videoUrl = re.findall('<iframe.*?src="(.*?)"', data, re.S)
           if videoUrl:
              return self.getResolvedURL(videoUrl[-1])

        if parser == 'https://momxxxfun.com':
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source src=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return urlparser.decorateUrl(videoUrl, {'Referer': 'https://momxxxfun.com'}) 

        videoUrls = []
        urlSupport = self.up.checkHostSupport( url )
        if 1 == urlSupport:
            retTab = self.up.getVideoLinkExt( url )
            videoUrls.extend(retTab)
            printDBG("Video url[%s]" % videoUrls)
            if videoUrls:
                for item in videoUrls:
                    if item['url']: return item['url']

        printDBG( 'Host getResolvedURL end' )
        return videoUrl





############################################
# functions for host
############################################
def decodeUrl(text):
	text = text.replace('%20',' ')
	text = text.replace('%21','!')
	text = text.replace('%22','"')
	text = text.replace('%23','&')
	text = text.replace('%24','$')
	text = text.replace('%25','%')
	text = text.replace('%26','&')
	text = text.replace('%2B','+')
	text = text.replace('%2F','/')
	text = text.replace('%3A',':')
	text = text.replace('%3B',';')
	text = text.replace('%3D','=')
	text = text.replace('&#x3D;','=')
	text = text.replace('%3F','?')
	text = text.replace('%40','@')
	return text

def decodeHtml(text):
	text = text.replace('&auml;','ä')
	text = text.replace('\u00e4','ä')
	text = text.replace('&#228;','ä')
	text = text.replace('&oacute;','ó')
	text = text.replace('&eacute;','e')
	text = text.replace('&aacute;','a')
	text = text.replace('&ntilde;','n')

	text = text.replace('&Auml;','Ä')
	text = text.replace('\u00c4','Ä')
	text = text.replace('&#196;','Ä')
	
	text = text.replace('&ouml;','ö')
	text = text.replace('\u00f6','ö')
	text = text.replace('&#246;','ö')
	
	text = text.replace('&ouml;','Ö')
	text = text.replace('\u00d6','Ö')
	text = text.replace('&#214;','Ö')
	
	text = text.replace('&uuml;','ü')
	text = text.replace('\u00fc','ü')
	text = text.replace('&#252;','ü')
	
	text = text.replace('&Uuml;','Ü')
	text = text.replace('\u00dc','Ü')
	text = text.replace('&#220;','Ü')
	
	text = text.replace('&szlig;','ß')
	text = text.replace('\u00df','ß')
	text = text.replace('&#223;','ß')
	
	text = text.replace('&amp;','&')
	text = text.replace('&quot;','\"')
	text = text.replace('&quot_','\"')

	text = text.replace('&gt;','>')
	text = text.replace('&apos;',"'")
	text = text.replace('&acute;','\'')
	text = text.replace('&ndash;','-')
	text = text.replace('&bdquo;','"')
	text = text.replace('&rdquo;','"')
	text = text.replace('&ldquo;','"')
	text = text.replace('&lsquo;','\'')
	text = text.replace('&rsquo;','\'')
	text = text.replace('&#034;','\'')
	text = text.replace('&#038;','&')
	text = text.replace('&#039;','\'')
	text = text.replace('&#39;','\'')
	text = text.replace('&#160;',' ')
	text = text.replace('\u00a0',' ')
	text = text.replace('&#174;','')
	text = text.replace('&#225;','a')
	text = text.replace('&#233;','e')
	text = text.replace('&#243;','o')
	text = text.replace('&#8211;',"-")
	text = text.replace('\u2013',"-")
	text = text.replace('&#8216;',"'")
	text = text.replace('&#8217;',"'")
	text = text.replace('#8217;',"'")
	text = text.replace('&#8220;',"'")
	text = text.replace('&#8221;','"')
	text = text.replace('&#8222;',',')
	text = text.replace('&#x27;',"'")
	text = text.replace('&#8230;','...')
	text = text.replace('\u2026','...')
	text = text.replace('&#41;',')')
	text = text.replace('&lowbar;','_')
	text = text.replace('&rsquo;','\'')
	text = text.replace('&lpar;','(')
	text = text.replace('&rpar;',')')
	text = text.replace('&comma;',',')
	text = text.replace('&period;','.')
	text = text.replace('&plus;','+')
	text = text.replace('&num;','#')
	text = text.replace('&excl;','!')
	text = text.replace('&#039','\'')
	text = text.replace('&semi;','')
	text = text.replace('&lbrack;','[')
	text = text.replace('&rsqb;',']')
	text = text.replace('&nbsp;','')
	text = text.replace('&#133;','')
	text = text.replace('&#4','')
	text = text.replace('&#40;','')

	text = text.replace('&atilde;',"'")
	text = text.replace('&colon;',':')
	text = text.replace('&sol;','/')
	text = text.replace('&percnt;','%')
	text = text.replace('&commmat;',' ')
	text = text.replace('&#58;',':')

	return text	

############################################
# functions for pornhub
############################################
def decrypt(ciphertext, password, nBits):
    printDBG( 'decrypt begin ' )
    blockSize = 16
    if not nBits in (128, 192, 256): return ""
    ciphertext = base64.b64decode(ciphertext)
#    password = password.encode("utf-8")

    nBytes = nBits//8
    pwBytes = [0] * nBytes
    for i in range(nBytes): pwBytes[i] = 0 if i>=len(password) else ord(password[i])
    key = Cipher(pwBytes, KeyExpansion(pwBytes))
    key += key[:nBytes-16]

    counterBlock = [0] * blockSize
    ctrTxt = ciphertext[:8]
    for i in range(8): counterBlock[i] = ord(ctrTxt[i])

    keySchedule = KeyExpansion(key)

    nBlocks = int( math.ceil( float(len(ciphertext)-8) / float(blockSize) ) )
    ct = [0] * nBlocks
    for b in range(nBlocks):
        ct[b] = ciphertext[8+b*blockSize : 8+b*blockSize+blockSize]
    ciphertext = ct

    plaintxt = [0] * len(ciphertext)

    for b in range(nBlocks):
        for c in range(4): counterBlock[15-c] = urs(b, c*8) & 0xff
        for c in range(4): counterBlock[15-c-4] = urs( int( float(b+1)/0x100000000-1 ), c*8) & 0xff

        cipherCntr = Cipher(counterBlock, keySchedule)

        plaintxtByte = [0] * len(ciphertext[b])
        for i in range(len(ciphertext[b])):
            plaintxtByte[i] = cipherCntr[i] ^ ord(ciphertext[b][i])
            plaintxtByte[i] = chr(plaintxtByte[i])
        plaintxt[b] = "".join(plaintxtByte)

    plaintext = "".join(plaintxt)
 #   plaintext = plaintext.decode("utf-8")
    return plaintext

Sbox = [
    0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
    0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
    0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
    0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
    0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
    0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
    0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
    0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
    0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
    0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
    0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
    0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
    0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
    0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
    0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
    0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16
]

Rcon = [
    [0x00, 0x00, 0x00, 0x00],
    [0x01, 0x00, 0x00, 0x00],
    [0x02, 0x00, 0x00, 0x00],
    [0x04, 0x00, 0x00, 0x00],
    [0x08, 0x00, 0x00, 0x00],
    [0x10, 0x00, 0x00, 0x00],
    [0x20, 0x00, 0x00, 0x00],
    [0x40, 0x00, 0x00, 0x00],
    [0x80, 0x00, 0x00, 0x00],
    [0x1b, 0x00, 0x00, 0x00],
    [0x36, 0x00, 0x00, 0x00]
]

def Cipher(input, w):
    printDBG( 'cipher begin ' )
    Nb = 4
    Nr = len(w)/Nb - 1

    state = [ [0] * Nb, [0] * Nb, [0] * Nb, [0] * Nb ]
    for i in range(0, 4*Nb): state[i%4][i//4] = input[i]

    state = AddRoundKey(state, w, 0, Nb)

    for round in range(1, Nr):
        state = SubBytes(state, Nb)
        state = ShiftRows(state, Nb)
        state = MixColumns(state, Nb)
        state = AddRoundKey(state, w, round, Nb)

    state = SubBytes(state, Nb)
    state = ShiftRows(state, Nb)
    state = AddRoundKey(state, w, Nr, Nb)

    output = [0] * 4*Nb
    for i in range(4*Nb): output[i] = state[i%4][i//4]
    return output

def SubBytes(s, Nb):
    printDBG( 'subbytes begin ' )
    for r in range(4):
        for c in range(Nb):
            s[r][c] = Sbox[s[r][c]]
    return s

def ShiftRows(s, Nb):
    printDBG( 'shiftrows begin ' )
    t = [0] * 4
    for r in range (1,4):
        for c in range(4): t[c] = s[r][(c+r)%Nb]
        for c in range(4): s[r][c] = t[c]
    return s

def MixColumns(s, Nb):
    printDBG( 'mixcolumns begin ' )
    for c in range(4):
        a = [0] * 4
        b = [0] * 4
        for i in range(4):
            a[i] = s[i][c]
            b[i] = s[i][c]<<1 ^ 0x011b if s[i][c]&0x80 else s[i][c]<<1
        s[0][c] = b[0] ^ a[1] ^ b[1] ^ a[2] ^ a[3]
        s[1][c] = a[0] ^ b[1] ^ a[2] ^ b[2] ^ a[3]
        s[2][c] = a[0] ^ a[1] ^ b[2] ^ a[3] ^ b[3]
        s[3][c] = a[0] ^ b[0] ^ a[1] ^ a[2] ^ b[3]
    return s

def AddRoundKey(state, w, rnd, Nb):
    printDBG( 'addroundkey begin ' )
    for r in range(4):
        for c in range(Nb):
            state[r][c] ^= w[rnd*4+c][r]
    return state

def KeyExpansion(key):
    printDBG( 'keyexpansion begin ' )
    Nb = 4
    Nk = len(key)/4
    Nr = Nk + 6

    w = [0] * Nb*(Nr+1)
    temp = [0] * 4

    for i in range(Nk):
        r = [key[4*i], key[4*i+1], key[4*i+2], key[4*i+3]]
        w[i] = r

    for i in range(Nk, Nb*(Nr+1)):
        w[i] = [0] * 4
        for t in range(4): temp[t] = w[i-1][t]
        if i%Nk == 0:
            temp = SubWord(RotWord(temp))
            for t in range(4): temp[t] ^= Rcon[i/Nk][t]
        elif Nk>6 and i%Nk == 4:
            temp = SubWord(temp)
        for t in range(4): w[i][t] = w[i-Nk][t] ^ temp[t]
    return w

def SubWord(w):
    printDBG( 'subword begin ' )
    for i in range(4): w[i] = Sbox[w[i]]
    return w

def RotWord(w):
    printDBG( 'rotword begin ' )
    tmp = w[0]
    for i in range(3): w[i] = w[i+1]
    w[3] = tmp
    return w

def encrypt(plaintext, password, nBits):
    printDBG( 'encrypt begin ' )
    blockSize = 16
    if not nBits in (128, 192, 256): return ""
#    plaintext = plaintext.encode("utf-8")
#    password  = password.encode("utf-8")
    nBytes = nBits//8
    pwBytes = [0] * nBytes
    for i in range(nBytes): pwBytes[i] = 0 if i>=len(password) else ord(password[i])
    key = Cipher(pwBytes, KeyExpansion(pwBytes))
    key += key[:nBytes-16]

    counterBlock = [0] * blockSize
    now = datetime.datetime.now()
    nonce = time.mktime( now.timetuple() )*1000 + now.microsecond//1000
    nonceSec = int(nonce // 1000)
    nonceMs  = int(nonce % 1000)

    for i in range(4): counterBlock[i] = urs(nonceSec, i*8) & 0xff
    for i in range(4): counterBlock[i+4] = nonceMs & 0xff

    ctrTxt = ""
    for i in range(8): ctrTxt += chr(counterBlock[i])

    keySchedule = KeyExpansion(key)

    blockCount = int(math.ceil(float(len(plaintext))/float(blockSize)))
    ciphertxt = [0] * blockCount

    for b in range(blockCount):
        for c in range(4): counterBlock[15-c] = urs(b, c*8) & 0xff
        for c in range(4): counterBlock[15-c-4] = urs(b/0x100000000, c*8)

        cipherCntr = Cipher(counterBlock, keySchedule)

        blockLength = blockSize if b<blockCount-1 else (len(plaintext)-1)%blockSize+1
        cipherChar = [0] * blockLength

        for i in range(blockLength):
            cipherChar[i] = cipherCntr[i] ^ ord(plaintext[b*blockSize+i])
            cipherChar[i] = chr( cipherChar[i] )
        ciphertxt[b] = ''.join(cipherChar)

    ciphertext = ctrTxt + ''.join(ciphertxt)
    ciphertext = base64.b64encode(ciphertext)

    return ciphertext

def urs(a, b):
    printDBG( 'urs begin ' )
    a &= 0xffffffff
    b &= 0x1f
    if a&0x80000000 and b>0:
        a = (a>>1) & 0x7fffffff
        a = a >> (b-1)
    else:
        a = (a >> b)
    return a

############################################
# functions for beeg.com
############################################
def decrypt_key(key, a):
    printDBG( 'beeg_salt= '+a)
    e = urllib.unquote_plus(key).decode("utf-8")
    o = ''.join([
        chr(ord(e[n]) - ord(a[n % len(a)]) % 21)
        for n in range(len(e))])
    return ''.join(split(o, 3)[::-1])
	
def split(o, e):
    def cut(s, x):
        n.append(s[:x])
        return s[x:]
    n = []
    r = len(o) % e
    if r > 0:
        o = cut(o, r)
    while len(o) > e:
        o = cut(o, e)
    n.append(o)
    return n
############################################
# functions for eporner
############################################
def calc_hash(s):
    return ''.join((encode_base_n(int(s[lb:lb + 8], 16), 36) for lb in range(0, 32, 8)))

def encode_base_n(num, n, table=None):
    FULL_TABLE = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if not table:
        table = FULL_TABLE[:n]

    if n > len(table):
        raise ValueError('base %d exceeds table length %d' % (n, len(table)))

    if num == 0:
        return table[0]

    ret = ''
    while num:
        ret = table[num % n] + ret
        num = num // n
    return ret
############################################
# functions for myfreecam
############################################
vs_str={}
vs_str[0]="PUBLIC"
vs_str[2]="AWAY"
vs_str[12]="PVT"
vs_str[13]="GROUP"
vs_str[90]="CAM OFF"
vs_str[127]="OFFLINE"
vs_str[128]="TRUEPVT"

def fc_decode_json(m):
	try:
		m = m.replace('\r', '\\r').replace('\n', '\\n')
		return simplejson.loads(m[m.find("{"):].decode("utf-8","ignore"))
	except:
		return simplejson.loads("{\"lv\":0}")

def read_model_data(m):
	global CAMGIRLSERVER
	global CAMGIRLCHANID
	global CAMGIRLUID
	printDBG("INFO  - "+str(m))
	usr = ''
	msg = fc_decode_json(m)
	try:
		sid=msg['sid']
		level  = msg['lv']
	except:
		printDBG ("errr reply ... We're fucked ..")
		return

	vs     = msg['vs']
	usr    = msg['nm']

	if vs == 2:
		printDBG ("%s is %s" % (usr, vs_str[vs]))
		SetIPTVPlayerLastHostError(_(vs_str[vs]))
		return []
	if vs == 12:
		printDBG ("%s is %s" % (usr, vs_str[vs]))
		SetIPTVPlayerLastHostError(_(vs_str[vs]))
		return []
	if vs == 13:
		printDBG ("%s is %s" % (usr, vs_str[vs]))
		SetIPTVPlayerLastHostError(_(vs_str[vs]))
		return []
	if vs == 90:
		printDBG ("%s is %s" % (usr, vs_str[vs]))
		SetIPTVPlayerLastHostError(_(vs_str[vs]))
		return []
	if vs == 127:
		printDBG ("%s is %s" % (usr, vs_str[vs]))
		SetIPTVPlayerLastHostError(_(vs_str[vs]))
		return []
	if vs == 128:
		printDBG ("%s is %s" % (usr, vs_str[vs]))
		SetIPTVPlayerLastHostError(_(vs_str[vs]))
		return []

	CAMGIRLUID    = msg['uid']
	CAMGIRLCHANID = msg['uid'] + 100000000
	camgirlinfo=msg['m']
	flags  = camgirlinfo['flags']
	u_info=msg['u']

	try:
		CAMGIRLSERVER = u_info['camserv']
		printDBG ("Video Server : %d Channel Id : %d  Model id : %d " %(CAMGIRLSERVER, CAMGIRLCHANID, CAMGIRLUID))
		SetIPTVPlayerLastHostError(str(CAMGIRLSERVER))
#		with open('/tmp/title', 'w') as titleFile:  
#			titleFile.write(str(CAMGIRLSERVER))
#		if CAMGIRLSERVER >= 3000:
#			SetIPTVPlayerLastHostError(str(CAMGIRLSERVER))
#			CAMGIRLSERVER = 0
#			return []
#			CAMGIRLSERVER = CAMGIRLSERVER - 1000
#		elif CAMGIRLSERVER >= 1500:
#			SetIPTVPlayerLastHostError(str(CAMGIRLSERVER))
#			CAMGIRLSERVER = 0
#			return []
#			CAMGIRLSERVER = CAMGIRLSERVER - 800
#		elif CAMGIRLSERVER >= 800:
#			CAMGIRLSERVER = CAMGIRLSERVER - 500
		if vs != 0:
			CAMGIRLSERVER = 0
	except KeyError:
		CAMGIRLSERVER=0

	truepvt = ((flags & 8) == 8)

	buf=usr+" =>"
	try:
		if truepvt == 1:
			buf+=" (TRUEPVT)"
		else:
			buf+=" ("+vs_str[vs]+")"
	except KeyError:
		pass
	printDBG ("%s  Video Server : %d Channel Id : %d  Model id : %d " %(buf, CAMGIRLSERVER, CAMGIRLCHANID, CAMGIRLUID))

def myfreecam_start(url, xchat):
	global CAMGIRL
	global CAMGIRLSERVER
	global CAMGIRLUID
	global CAMGIRLCHANID
	CAMGIRL= url
	CAMGIRLSERVER = 0
	libsPath = GetPluginDir('libs/')
	import sys
	sys.path.insert(1, libsPath)
	import websocket
	printDBG("Connecting to Chat Server:")
	try:
		host = "ws://"+xchat+".myfreecams.com:8080/fcsl"
		printDBG("Chat Server..."+host)
		ws = websocket.create_connection(host)
		ws.send("hello fcserver\n\0")
		ws.send("1 0 0 20071025 0 guest:guest\n\0")
	except:
		printDBG ("We're fucked ...")
		return ''
	rembuf=""
	quitting = 0
	try:
		while quitting == 0:
			sock_buf =  ws.recv()
			sock_buf=rembuf+sock_buf
			rembuf=""
			while True:
				hdr=re.search (r"(\w+) (\w+) (\w+) (\w+) (\w+)", sock_buf)
				if bool(hdr) == 0:
					break
				fc = hdr.group(1)
				mlen   = int(fc[0:4])
				fc_type = int(fc[4:])
				msg=sock_buf[4:4+mlen]
				if len(msg) < mlen:
					rembuf=''.join(sock_buf)
					break
				msg=urllib.unquote(msg)
				if fc_type == 1:
					ws.send("10 0 0 20 0 %s\n\0" % CAMGIRL)
				elif fc_type == 10:
					read_model_data(msg)
					quitting=1
				sock_buf=sock_buf[4+mlen:]
				if len(sock_buf) == 0:
					break
	except:
		printDBG ("WebSocket Error")
		return ''
	ws.close()
	if CAMGIRLSERVER != 0:
		#Url="http://video"+str(CAMGIRLSERVER)+".myfreecams.com:1935/NxServer/ngrp:mfc_"+str(CAMGIRLCHANID)+".f4v_mobile/playlist.m3u8" #+'?nc='+str(int(time_time()*1000))  #+str(datetime.now()) #str(time_time()).encode('utf-8')
		#Url="http://video"+str(CAMGIRLSERVER)+".myfreecams.com:1935/NxServer/mfc_"+str(CAMGIRLCHANID)+".f4v_aac/playlist.m3u8" #320x240
		Url="https://video"+str(CAMGIRLSERVER)+".myfreecams.com/NxServer/ngrp:mfc_"+str(CAMGIRLCHANID)+".f4v_mobile/playlist.m3u8?nc=0.5863279394620062" #+str(random.random())
		printDBG("Camgirl - "+CAMGIRL)
		printDBG("Url  - "+Url)
		return Url
	else:
		printDBG ("No video server ... _|_ ")
		return ''

# decrypt function/0/
def decryptHash(videoUrl, licenseCode, hashRange):
    result = ''
    videoUrlPart = videoUrl.split('/')
    hash = videoUrlPart[7][:2*int(hashRange)]
    nonConvertHash = videoUrlPart[7][2*int(hashRange):]
    seed = calcSeed(licenseCode, hashRange)
    if (seed != '' and hash !=''):
        for k in range(len(hash)-1, -1, -1):
            l = k
            for m in range(k,len(hash)):
                l += int(seed[m])
            l = l % len(hash)
            n = ''
            for o in range(0, len(hash)):
                n = n + hash[l] if o == k else n + hash[k] if o == l else n + hash[o]
            hash = n
        videoUrlPart[7] = hash + nonConvertHash
        videoUrlPart.pop(0)
        videoUrlPart.pop(0)        
        result = '/'.join(videoUrlPart)   
    return result        


def calcSeed(licenseCode, hashRange):
    f = licenseCode.replace('$', '').replace('0', '1')
    j = int(len(f) / 2)
    k = int(f[:len(f)-j])
    l = int(f[j:])
    g = abs(l - k)
    fi = 4*g
    i = int(int(hashRange) / 2 + 2)
    m = ''
    for g2 in range (0,j+1):
        for h in range (1,5):
            n =  int(licenseCode[g2 + h]) + int(str(fi)[g2])
            if n>=i:
                n -= i	
            m = m + str(n)
    return m 