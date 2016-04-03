####################################################################################################
#                                                                                                  #
#                                      JavHiHi Plex Channel                                        #
#                                                                                                  #
####################################################################################################
import messages
import bookmarks
from updater import Updater
from DumbTools import DumbKeyboard
from DumbTools import DumbPrefs

TITLE = L('title')
PREFIX = '/video/javhihi'
BASE_URL = 'http://javhihi.com'

ICON = 'icon-default.png'
ICON_BM = 'icon-bookmarks.png'
ICON_BM_ADD = 'icon-add-bookmark.png'
ICON_BM_REMOVE = 'icon-remove-bookmark.png'
ICON_STAR = 'icon-pornstar.png'
ICON_CAT = 'icon-category.png'
ICON_LIKE = 'icon-like.png'
ICON_RECENT = 'icon-recent.png'
ICON_VIDEO = 'icon-video.png'
ICON_VIEWS = 'icon-views.png'
ART = 'art-default.jpg'

MC = messages.NewMessageContainer(PREFIX, TITLE)
BM = bookmarks.Bookmark(TITLE, PREFIX, ICON_BM_ADD, ICON_BM_REMOVE)

####################################################################################################
def Start():
    HTTP.CacheTime = CACHE_1HOUR

    ObjectContainer.title1 = TITLE
    ObjectContainer.art = R(ART)

    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)

    InputDirectoryObject.art = R(ART)

    VideoClipObject.art = R(ART)

####################################################################################################
@handler(PREFIX, TITLE, thumb=ICON, art=ART)
def MainMenu():
    """Setup Main Menu, Includes Updater"""

    oc = ObjectContainer(title2=TITLE, no_cache=True)
    mhref = '/movie'

    Updater(PREFIX + '/updater', oc)

    oc.add(DirectoryObject(
        key=Callback(DirectoryList, title='Most Recent', href='%s?sort=published' %mhref, page=1),
        title='Most Recent', thumb=R(ICON_RECENT)
        ))
    oc.add(DirectoryObject(
        key=Callback(SortList, title='Most Viewed', href=mhref),
        title='Most Viewed', thumb=R(ICON_VIEWS)
        ))
    oc.add(DirectoryObject(
        key=Callback(SortList, title='Top Rated', href=mhref),
        title='Top Rated', thumb=R(ICON_LIKE)
        ))
    oc.add(DirectoryObject(
        key=Callback(CategoryList), title='Categories', thumb=R(ICON_CAT)
        ))
    oc.add(DirectoryObject(
        key=Callback(SortListC, title='Pornstars', href='/pornstar'),
        title='Pornstars', thumb=R(ICON_STAR)
        ))

    oc.add(DirectoryObject(key=Callback(MyBookmarks), title='My Bookmarks', thumb=R(ICON_BM)))

    if Client.Product in DumbPrefs.clients:
        DumbPrefs(PREFIX, oc, title='Preferences', thumb=R('icon-prefs.png'))
    else:
        oc.add(PrefsObject(title='Preferences', thumb=R('icon-prefs.png')))

    if Client.Product in DumbKeyboard.clients:
        DumbKeyboard(PREFIX, oc, Search, dktitle='Search', dkthumb=R('icon-search.png'))
    else:
        oc.add(InputDirectoryObject(
            key=Callback(Search), title='Search', summary='Search JavHiHi',
            prompt='Search for...', thumb=R('icon-search.png')
            ))

    return oc

####################################################################################################
@route(PREFIX + '/sortlist')
def SortList(title, href):
    """
    Create sub list
    Most Viewed, Top Rated
    """

    sort = {
        'Most Viewed': {
            'All Time': 'view', 'Daily': 'viewday', 'Weekly': 'viewweek', 'Monthly': 'viewmonth'},
        'Top Rated': {
            'All Time': 'like', 'Daily': 'likeday', 'Weekly': 'likeweek', 'Monthly': 'likemonth'}
        }

    oc = ObjectContainer(title2=title)
    s = title.split('/')[-1].strip()

    for k in sorted(sort[s].keys()):
        t = k if k == title else '%s / %s' %(title, k)
        if ('Pornstar' in title) and (not 'Search' in title):
            oc.add(DirectoryObject(
                key=Callback(PornstarList,
                    title=t, href='%s%ssort=%s&direction=desc' %(href, ('&' if '?' in href else '?'), sort[s][k]),
                    page=1),
                title=k
                ))
        else:
            oc.add(DirectoryObject(
                key=Callback(DirectoryList,
                    title=t, href='%s%ssort=%s' %(href, ('&' if '?' in href else '?'), sort[s][k]),
                    page=1),
                title=k
                ))

    return oc

####################################################################################################
@route(PREFIX + '/categorylist')
def CategoryList():
    """Setup Category List"""

    oc = ObjectContainer(title2='Categories')

    html = HTML.ElementFromURL(BASE_URL)
    for a in html.xpath('//div[starts-with(@class, "categories-wrapper")]//a'):
        href = a.get('href')
        href = href if href.startswith('/') else '/' + href
        name = a.text.strip()
        oc.add(DirectoryObject(
            key=Callback(SortListC, title='Category / %s' %name, href=href),
            title=name, summary='%s Genre List ' %name
            ))

    return oc

####################################################################################################
@route(PREFIX + '/sortlist/c')
def SortListC(title, href, search=False):

    oc = ObjectContainer(title2=title)

    if search:
        oc.add(DirectoryObject(
            key=Callback(DirectoryList, title='%s / Relevance' %title, href=href, page=1),
            title='Relevance'
            ))

    if ('Pornstar' in title) and (search == False):
        oc.add(DirectoryObject(
            key=Callback(PornstarList,
                title='%s / Most Recent' %title,
                href='%s?sort=id&direction=desc' %href,
                page=1),
            title='Most Recent'
            ))
    else:
        oc.add(DirectoryObject(
            key=Callback(DirectoryList,
                title='%s / Most Recent' %title,
                href='%s%ssort=published' %(href, ('&' if search else '?')),
                page=1),
            title='Most Recent'
            ))

    sort_list = ['Most Viewed', 'Top Rated']
    for s in sort_list:
        oc.add(DirectoryObject(
            key=Callback(SortList, title='%s / %s' %(title, s), href=href), title=s
            ))

    return oc

####################################################################################################
@route(PREFIX + '/search')
def Search(query=''):
    """Search JavHiHi"""

    query = query.strip()
    href = '/movie?q=%s' %String.Quote(query, usePlus=True)
    title = 'Search / %s' %query

    return SortListC(title, href, True)

####################################################################################################
@route(PREFIX + '/bookmark/list')
def MyBookmarks():
    """
    Setup Bookmark Main Menu.
    Seperate by Pornstar and Video
    """

    bm = Dict['Bookmarks']
    if not bm:
        return MC.message_container('Bookmarks', 'Bookmark List Empty')

    oc = ObjectContainer(title2='My Bookmarks', no_cache=True)

    for key in sorted(bm.keys()):
        if len(bm[key]) == 0:
            del Dict['Bookmarks'][key]
            Dict.Save()
        else:
            oc.add(DirectoryObject(
                key=Callback(BookmarksSub, category=key),
                title=key, summary='Display Pornstar Bookmarks',
                thumb=R('icon-%s.png' %key.lower())
                ))

    if len(oc) > 0:
        return oc
    else:
        return MC.message_container('Bookmarks', 'Bookmark List Empty')

####################################################################################################
@route(PREFIX + '/bookmark/sub')
def BookmarksSub(category):
    """List Bookmarks Alphabetically"""

    bm = Dict['Bookmarks']
    if not category in bm.keys():
        return MC.message_container('Error',
            '%s Bookmarks list is dirty, or no %s Bookmark list exist.' %(category, category))

    oc = ObjectContainer(title2='My Bookmarks / %s' %category, no_cache=True)

    for bookmark in sorted(bm[category], key=lambda k: k['title']):
        title = bookmark['title']
        thumb = bookmark['thumb']
        url = bookmark['url']
        item_id = bookmark['id']
        duration = bookmark['duration']
        tagline = bookmark['tagline']
        summary = bookmark['summary']
        date = bookmark['date']

        video_info = {
            'id': item_id, 'title': title, 'duration': duration, 'thumb': thumb, 'url': url,
            'tagline': tagline, 'date': date, 'summary': summary, 'category': category
            }

        if category == 'Video':
            oc.add(DirectoryObject(
                key=Callback(VideoPage, video_info=video_info),
                title=title, thumb=thumb
                ))
        elif category == 'Pornstar':
            oc.add(DirectoryObject(
                key=Callback(PornstarSubList, title=title, href=url, pid=item_id, thumb=thumb),
                title=title, thumb=thumb
                ))

    if len(oc) > 0:
        return oc
    else:
        return MC.message_container('Bookmarks', '%s Bookmarks list Empty' %category)

####################################################################################################
@route(PREFIX + '/pornstar/list', page=int)
def PornstarList(title, href, page):
    """Setup Pornstar list"""

    url = BASE_URL + href
    html = HTML.ElementFromURL(url)
    href_next = html.xpath('//li[@class="next"]/a/@href')
    if href_next or (page > 1):
        main_title = '%s / Page %i' %(title, page)
    else:
        main_title = title

    oc = ObjectContainer(title2=main_title)

    for p in html.xpath('//div[@class="pornstar-item"]'):
        a0 = p.xpath('.//a')[0]
        phref = a0.get('href')
        phref = phref if phref.startswith('/') else '/' + phref
        pid = phref.split('/', 2)[2].rsplit('.', 1)[-2]
        pname = a0.get('title')
        thumb = a0.xpath('./img/@src')[0]

        oc.add(DirectoryObject(
            key=Callback(PornstarSubList,
                title='%s / %s' %(title, pname), href=phref, pid=pid, thumb=thumb),
            title=pname, thumb=thumb
            ))

    if href_next:
        nhref = href_next[0]
        nhref = nhref if nhref.startswith('/') else '/' + nhref
        oc.add(NextPageObject(
            key=Callback(PornstarList, title=title, href=nhref, page=page + 1),
            title='Next Page>>'))

    return oc

####################################################################################################
@route(PREFIX + '/pornstar/list/sub')
def PornstarSubList(title, href, pid, thumb):
    """
    Setup Pornstar options
    Videos, Related Pornstars, and Bookmark options
    """

    oc = ObjectContainer(title2=title, no_cache=True)

    oc.add(DirectoryObject(
        key=Callback(DirectoryList, title=title + ' / Videos', href=href, page=1),
        title='Videos', thumb=R('icon-video.png')
        ))

    oc.add(DirectoryObject(
        key=Callback(PornstarList, title=title + ' / Related Pornstars', href=href, page=1),
        title='Related Pornstars', thumb=R('icon-pornstar.png')
        ))

    bm_info = {
            'id': pid, 'title': title.split('/')[-1].strip(), 'duration': 'none',
            'thumb': thumb, 'url': href, 'tagline': 'none', 'date': 'none',
            'summary': 'none', 'category': 'Pornstar'
            }
    BM.add_remove_bookmark(oc, bm_info)

    return oc


####################################################################################################
@route(PREFIX + '/directory/list', page=int)
def DirectoryList(title, href, page):
    """List Videos by page"""

    url = BASE_URL + href

    html = HTML.ElementFromURL(url)

    href_next = html.xpath('//a[contains(@class, "movie-next-page")]/@href')
    if href_next or (page > 1):
        main_title = '%s / Page %i' %(title, page)
    else:
        main_title = title

    oc = ObjectContainer(title2=main_title)

    for v in html.xpath('//div[@class="video-item"]'):
        a0 = v.xpath('.//a')[0]
        vhref = a0.get('href')
        vhref = vhref if vhref.startswith('/') else '/' + vhref
        vid = vhref.split('.')[-2]
        name = a0.get('title')
        thumb = a0.xpath('./img/@src')[0]

        duration = v.xpath('.//span[@class="duration"]/text()')[0]

        p = v.xpath('.//p')[0]
        for s in p.xpath('./span/text()'):
            if 'views' in s:
                views = s
            elif 'likes' in s:
                likes = s
            else:
                date = s
        tagline = 'Likes: %s | Views: %s' %(likes.split(' ')[0], views.split(' ')[0])

        video_info = {
            'id': vid, 'title': name, 'duration': duration, 'thumb': thumb, 'url': vhref,
            'tagline': tagline, 'date': date
            }

        oc.add(DirectoryObject(key=Callback(VideoPage, video_info=video_info), title=name, thumb=thumb))

    if href_next:
        nhref = href_next[0]
        nhref = nhref if nhref.startswith('/') else '/' + nhref
        oc.add(NextPageObject(
            key=Callback(DirectoryList, title=title, href=nhref, page=page + 1),
            title='Next Page>>'))

    if len(oc) > 0:
        return oc
    else:
        return MC.message_container('Videos', 'Video List Empty')

####################################################################################################
@route(PREFIX + '/videopage', video_info=dict)
def VideoPage(video_info):
    """
    Video Sub Page
    Includes Similar Videos and Bookmark Option
    """

    bm = Dict['Bookmarks']
    url = BASE_URL + video_info['url']
    html = HTML.ElementFromURL(url)
    header = None
    message = None
    duration = video_info['duration']
    summary = video_info['summary'] if 'summary' in video_info.keys() else None
    error = False
    match = BM.bookmark_exist(item_id=video_info['id'], category='Video')
    video_info.update({'category': 'Video', 'summary': summary})
    if match:
        error = html.xpath('//meta[@content="Erros"]')
        if error:
            header = video_info['title']
            message = 'This video is no longer available.'

    oc = ObjectContainer(title2=video_info['title'], header=header, message=message, no_cache=True)

    if not error:
        duration = None
        summary = video_info['summary']
        genres = []
        tags = []
        for md in html.xpath('//div[@class="box movie-detail"]'):
            p0 = md.xpath('./p')[0].text_content().strip()
            dur = Regex('Duration\:\ (\d+)(.+)').search(p0)
            duration = int(dur.group(1).strip()) * (60000 if 'min' in dur.group(2) else 3600000)

            summary = md.xpath('./p')[1].text_content().strip()
            genres = md.xpath('//ul[@class="links links-categories"]/li/a/text()')
            tags = md.xpath('//ul[@class="links links-tags"]/li/a/text()')

        video_info.update({'duration': str(duration), 'summary': summary})

        oc.add(VideoClipObject(
            title=video_info['title'],
            source_title='JavHiHi',
            tagline=video_info['tagline'],
            originally_available_at=Datetime.ParseDate(video_info['date']),
            year=int(Datetime.ParseDate(video_info['date']).year),
            summary=summary,
            genres=genres,
            tags=tags,
            duration=duration,
            thumb=video_info['thumb'],
            url=url
            ))


    similar_node = html.xpath('//div[@class="video-item"]')
    if similar_node:
        s_thumb = similar_node[0].xpath('.//a/img/@src')[0]
        oc.add(DirectoryObject(
            key=Callback(DirectoryList, title='Suggested Videos', href=video_info['url'], page=1),
            title='Suggested Videos', thumb=s_thumb
            ))

    if not error:
        oc.add(DirectoryObject(
            key=Callback(PornstarList, title='Pornstars', href=video_info['url'], page=1),
            title='Pornstar(s) in Video', thumb=R('icon-pornstar.png')
            ))

    BM.add_remove_bookmark(oc=oc, bm_info=video_info)

    return oc
