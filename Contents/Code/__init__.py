# -*- coding: utf-8 -*-
VIDEO_PREFIX = "/video/pluzz"

NAME = L('Title')

# make sure to replace artwork with what you want
# these filenames reference the example files in
# the Contents/Resources/ folder in the bundle
ART  = 'art-default.jpg'
ICON = 'icon-default.png'

####################################################################################################
import zipfile
import os
try:
  from cStringIO import StringIO
except:
  from StringIO import StringIO

def Start():
    ## make this plugin show up in the 'Video' section
    ## in Plex. The L() function pulls the string out of the strings
    ## file in the Contents/Strings/ folder in the bundle
    ## see also:
    ##  http://dev.plexapp.com/docs/mod_Plugin.html
    ##  http://dev.plexapp.com/docs/Bundle.html#the-strings-directory
    Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, NAME, ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    ## set some defaults so that you don't have to
    ## pass these parameters to these object types
    ## every single time
    ## see also:
    ##  http://dev.plexapp.com/docs/Objects.html
    MediaContainer.title1 = NAME
    MediaContainer.viewGroup = "List"
    MediaContainer.art = R(ART)
    DirectoryItem.thumb = R(ICON)
    VideoItem.thumb = R(ICON)
    
    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = "Mozilla/5.0 (Windows NT 5.1; rv:15.0) Gecko/20100101 Firefox/15.0.1"



#### the rest of these are user created functions and
#### are not reserved by the plugin framework.
#### see: http://dev.plexapp.com/docs/Functions.html for
#### a list of reserved functions above

@route('/video/pluzz/update')
def Update():
    Log.Debug("Retrieving FranceTelevisions webservices from http://webservices.francetelevisions.fr/catchup/flux/flux_main.zip")
    flux_zip = HTTP.Request("http://webservices.francetelevisions.fr/catchup/flux/flux_main.zip")
    flux_zip.load()
    fp = StringIO(flux_zip.content)
    zfile = zipfile.ZipFile(fp,'r')
    catalogs = [ json_file for json_file in zfile.namelist() if not json_file.startswith('guide_tv_') ]
    for json in catalogs: 
	Log.Debug("Found %s" % json)
	Data.Save(json, zfile.read(json))

    return MessageContainer(
        "Update",
	"Update completed successfully"
    )

#
# Example main menu referenced in the Start() method
# for the 'Video' prefix handler
#

def VideoMainMenu():
    # Container acting sort of like a folder on
    # a file system containing other things like
    # "sub-folders", videos, music, etc
    # see:
    #  http://dev.plexapp.com/docs/Objects.html#MediaContainer
    Log.Debug("Main menu - Updating")
    Update()
    
    Log.Debug("Loading main menu")
    dir = MediaContainer(viewGroup="InfoList")

    # see:
    #  http://dev.plexapp.com/docs/Objects.html#DirectoryItem
    #  http://dev.plexapp.com/docs/Objects.html#function-objects
    dir.Append(
        Function(
            DirectoryItem(
                CategoriesMenu,
                "Categories",
                subtitle="subtitle",
                summary="Afficher les émissions par catégories",
                thumb=R(ICON),
                art=R(ART)
            )
        )
    )
    dir.Append(
        Function(
            DirectoryItem(
                ChainesMenu,
                "Chaînes",
                subtitle="subtitle",
                summary="Afficher les émissions par chaînes",
                thumb=R(ICON),
                art=R(ART)
            )
        )
    )
    dir.Append(
        Function(
            DirectoryItem(
                MostWatched,
                "Les + regardés",
                subtitle="subtitle",
                summary="Afficher les émissions les plus regardées",
                thumb=R(ICON),
                art=R(ART)
            )
        )
    )
    dir.Append(
        Function(
            DirectoryItem(
                ShowMenu,
                "Par programmes",
                subtitle="subtitle",
                summary="Rangement par programmes",
                thumb=R(ICON),
                art=R(ART)
            )
        )
    )
    dir.Append(
        Function(
            DirectoryItem(
                DateMenu,
                "Par date",
                subtitle="subtitle",
                summary="Rangement par date",
                thumb=R(ICON),
                art=R(ART)
            )
        )
    )
    dir.Append(
        Function(
            DirectoryItem(
                Refresh,
                "Actualiser",
                subtitle="subtitle",
                summary="Actualiser le contenu",
                thumb=R(ICON),
                art=R(ART)
            )
        )
    )


    # ... and then return the container
    return dir

def Refresh(sender):
    try:
	Update()	    
    	return MessageContainer(
		"Update",
		"Update completed successfully"
    	)
    except:
    	return MessageContainer(
		"Update",
		"Error while refreshing"
    	)

@route('/video/pluzz/channels')
def ChainesMenu(sender):
    oc = ObjectContainer(title1='ChannelMenu')
    for chaine in ["France1","France2","France3", "France3_Regions","France4","France5","FranceO"]:
	    oc.add(
		DirectoryObject(
			key=Callback(MediaView, ContentType='channel', ContentFilter=chaine.lower(), title = chaine ),
			title=L(chaine),
			summary=L(chaine),
			art=R("%s.png" % chaine.lower()),
			thumb=R("%s.png" % chaine.lower()),
		)
	    )
    return oc

@route('/video/pluzz/categories')
def CategoriesMenu(sender):
    oc = ObjectContainer(title1='CategoriesMenu')
    json_cat = Data.Load('categories.json')
    objects = JSON.ObjectFromString(json_cat, encoding='iso-8859-15')
    for categorie in objects['categories']:
	    clean_categorie_name = String.StripDiacritics(categorie['titre'])
	    clean_accroche = String.StripDiacritics(categorie['accroche'])
	    oc.add(
		DirectoryObject(
			key=Callback(MediaView, ContentType='category', ContentFilter=categorie['titre'], title=clean_categorie_name ),
			title=L(clean_categorie_name),
			summary=L(clean_accroche),
			thumb=R(ICON),
			art=R(ART)
		)
	    )
    return oc

@route('/video/pluzz/date')
def DateMenu(sender):
    oc = ObjectContainer(title1='Par date')
    today = Datetime.Now()
    oneday = Datetime.Delta(days=1)
    dates = [ today - (i * oneday) for i in range(0,7) ]
    for date in dates:
	    oc.add(
		DirectoryObject(
			key=Callback(MediaView, ContentType='date', ContentFilter=date.strftime("%Y-%m-%d"), title='Par date' ),
			title=L(date.strftime("%d/%m/%Y")),
			summary=L('Programme du %s' % date.strftime("%d/%m/%Y")),
			thumb=R(ICON),
			art=R(ART)
		)
	    )
    return oc

@route('/video/pluzz/show')
def ShowMenu(sender):
    oc = ObjectContainer(title1='Par programmes')
    show_list = []
    for chaine in ["France1","France2","France3", "France3_Regions","France4","France5","FranceO"]:
    	json_cat = Data.Load('catch_up_%s.json' % chaine.lower())
    	#objects = JSON.ObjectFromString(json_cat, encoding='iso-8859-15')
    	objects = JSON.ObjectFromString(json_cat, encoding='latin-1')
    	show_list += [ show['titre'] for show in objects['programmes'] if show['titre'] <> '' ]

    for show_name in sorted(set(show_list)):
	    if show_name == '':
		continue
	    #show_name = unicode(show_name, 'latin-1')
	    clean_show_name = String.StripDiacritics(show_name)
	    oc.add(
		DirectoryObject(
			key=Callback(MediaView, ContentType='show', ContentFilter=show_name, title=clean_show_name ),
			title=L(clean_show_name),
			summary=L(clean_show_name),
			thumb=R(ICON),
			art=R(ART)
		)
	    )
    return oc

@route('/video/pluzz/mostwatched')
def MostWatched(sender):
    return MediaView(ContentType='mostwatched', ContentFilter='', title='Les plus vus' )
    

@route('/video/pluzz/mediaview')
def MediaView(ContentType, ContentFilter, title):
    Log.Debug("Entering %s" % title)
    Log.Debug("Building JSON content")

    if ContentType == 'channel':
    	json_cat = Data.Load('catch_up_%s.json' % ContentFilter)
    	objects = JSON.ObjectFromString(json_cat, encoding='iso-8859-15')
    	unsorted_json = objects['programmes']
	json = sorted(unsorted_json, key=lambda k: k['date'])
	json.reverse()
    if ContentType == 'category':
	replay_list = []
    	for chaine in ["France1","France2","France3", "France3_Regions","France4","France5","FranceO"]:
    		json_cat = Data.Load('catch_up_%s.json' % chaine.lower())
    		objects = JSON.ObjectFromString(json_cat, encoding='iso-8859-15')
    		replay_list += [ replay for replay in objects['programmes'] if replay['rubrique'] == ContentFilter ]
	unsorted_json = replay_list
	json = sorted(unsorted_json, key=lambda k: k['date'])
	json.reverse()
    if ContentType == 'mostwatched':
	replay_list = []
    	for chaine in ["France1","France2","France3", "France3_Regions","France4","France5","FranceO"]:
    		json_cat = Data.Load('catch_up_%s.json' % chaine.lower())
    		objects = JSON.ObjectFromString(json_cat, encoding='iso-8859-15')
    		replay_list += [ replay for replay in objects['programmes'] ]
	unsorted_json = replay_list
	json = sorted(unsorted_json, key=lambda k: k['nb_vues'])
	json.reverse()
    if ContentType == 'show':
	replay_list = []
    	for chaine in ["France1","France2","France3", "France3_Regions","France4","France5","FranceO"]:
    		json_cat = Data.Load('catch_up_%s.json' % chaine.lower())
    		objects = JSON.ObjectFromString(json_cat, encoding='iso-8859-15')
    		replay_list += [ replay for replay in objects['programmes'] if replay['titre'] == ContentFilter]
	unsorted_json = replay_list
	json = sorted(unsorted_json, key=lambda k: k['date'])
	json.reverse()
    if ContentType == 'date':
	replay_list = []
    	for chaine in ["France1","France2","France3", "France3_Regions","France4","France5","FranceO"]:
    		json_cat = Data.Load('catch_up_%s.json' % chaine.lower())
    		objects = JSON.ObjectFromString(json_cat, encoding='iso-8859-15')
    		replay_list += [ replay for replay in objects['programmes'] if replay['date'] == ContentFilter]
	unsorted_json = replay_list
	json = sorted(unsorted_json, key=lambda k: k['titre'])
	json.reverse()
	
    
    oc = ObjectContainer(title1=title.capitalize())
    for replay in json:
	    if replay['sous_titre'] <> "":
	    	titre	= "%s - %s" % (replay['titre'], replay['sous_titre'])
	    else:
	    	titre	= "%s - %s" % (replay['titre'], replay['date'])
		
	    thumb 	= "http://pluzz.francetv.fr/%s.%s" % (replay['url_image_racine'], replay['extension_image'])
	    video_url 	= "http://medias2.francetv.fr/catchup-mobile%s" % replay['url_video'].encode("utf-8")
	    rating_key 	=  titre.lower().strip()
	    art 	= "http://pluzz.francetv.fr/%s.%s" % (replay['url_image_racine'], replay['extension_image']) 
	    summary 	= replay['accroche']
	    tagline	= replay['date']

	    oc.add(
		VideoClipObject(
			key = Callback(Lookup, title=titre, thumb=thumb, rating_key=rating_key, url=video_url, art=art, summary=summary, tagline=tagline),
			title=L(titre),
			tagline=L(tagline),
			rating_key =  rating_key,
			items = [
                                MediaObject(
                                        parts = [PartObject(key=HTTPLiveStreamURL(Callback(PlayVideo, url=video_url)))]
                                )
			],
			summary=L(summary),
			thumb=Resource.ContentsOfURLWithFallback(url=thumb),
			art=Resource.ContentsOfURLWithFallback(url=art)
		)
	    )
    return oc

@route('/video/pluzz/program')
def Lookup(title, thumb, rating_key, url, art, summary, tagline):
	Log.Debug("Entering Lookup")
	oc = ObjectContainer()
        oc.add(
                VideoClipObject(
                        key 		= Callback(Lookup, title=title, thumb=thumb, rating_key=rating_key, url=url, art=art, summary=summary, tagline=tagline),
                        title 		= title,
                        thumb 		= thumb,
			tagline		= tagline,
                        rating_key 	= rating_key,
			summary		= summary,
			art		= art,
                        items 		= [
                                MediaObject(
                                        parts = [PartObject(key=HTTPLiveStreamURL(Callback(PlayVideo, url=url)))]
                                )
                        ]
                )
        )

        return oc

def PlayVideo(url):
        return Redirect(url)

def CallbackInProgress(sender):
    return MessageContainer(
        "Not implemented",
	"Work in progress. Soyez indulgents."
    )

  
