##
## Original Picon renderer by Gruffy .. some speedups by Ghost
## XPicons Addon by iMaxxx
## Threaded ActiveXPicons  (downloads missing XPicons from web repository)
## Dynamic Size Addon (Resizes automatically)


from Renderer import Renderer
from enigma import ePixmap,ePicLoad
from Components.AVSwitch import AVSwitch
from Components.Pixmap import Pixmap
from Components.config import config
import os
import urllib2
import traceback
import threading
import shutil
from enigma import iServiceInformation, iPlayableService, iPlayableServicePtr
from Tools.Directories import fileExists, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, resolveFilename

URL_ACTIVEXPICON_API = "http://api-nuevo.open-store.net/?q=get.file&type=9&id="


class XPicon(Renderer):
	searchPaths = ('/media/hdd/XPicons/%s/','/media/usb/XPicons/%s/','/media/cf/XPicons/%s/','/usr/share/enigma2/XPicons/%s/','/media/hdd/XPicon/%s/','/media/usb/XPicon/%s/','/media/cf/XPicon/%s/','/usr/share/enigma2/XPicon/%s/','/usr/share/enigma2/%s/','/media/hdd/%s/','/media/usb/%s/','/media/cf/%s/')

	def __init__(self):
		Renderer.__init__(self)
		self.path = "picon"
		self.nameCache = { }
		self.pngname = ""
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()
		self.PicLoad.PictureData.get().append(self.DecodeXPicon)

	def applySkin(self, desktop, parent):
		attribs = [ ]
		for (attrib, value) in self.skinAttributes:
			if attrib == "path":
				self.path = value
			else:
				attribs.append((attrib,value))
		self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)

	GUI_WIDGET = ePixmap
	
	
	
	def ShowXPicon(self,picPath):
		self.PicLoad.setPara([self.instance.size().width(),self.instance.size().height(),self.Scale[0],self.Scale[1],True, 1, "#ff000000"])
		#self.PicLoad.getThumbnail(picPath,self.instance.size().width(),self.instance.size().height(),True)
		self.PicLoad.startDecode(picPath)
		#print "showing image"
		
	def DecodeXPicon(self, PicInfo = ""):
		#print "decoding piture"
		ptr = self.PicLoad.getData()
		self.instance.setPixmap(ptr)	

	def changed(self, what):
		if self.instance:
			try:
				overwrite = config.plugins.MyMetrix.XPiconsOverwrite.value
			except:
				overwrite = False
			pngname = ""
			if what[0] != self.CHANGED_CLEAR:
				sname = self.source.text
				pos = sname.rfind(':')
				if pos != -1:
					sname = sname[:pos].rstrip(':').replace(':','_')
				pngname = self.nameCache.get(sname, "")
				if pngname == "":
					pngname = self.findPicon(sname)
					if pngname != "":
						self.nameCache[sname] = pngname
						if overwrite:
							self.downloadXPicon(sname)
				else:
					if overwrite:
						self.downloadXPicon(sname)
			if pngname == "": # no picon for service found
				pngname = self.nameCache.get("default", "")
				if pngname == "": # no default yet in cache..
					pngname = self.findPicon("picon_default")
					if pngname == "":
						tmp = resolveFilename(SCOPE_CURRENT_SKIN, "picon_default.png")
						if fileExists(tmp):
							pngname = tmp
						else:
							pngname = resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/picon_default.png")
					self.nameCache["default"] = pngname
				
			if self.pngname != pngname:
				self.pngname = pngname
				self.ShowXPicon(pngname)
				

	def findPicon(self, serviceName):
		try:
			active = config.plugins.MyMetrix.ActiveXPicon.value
		except:
			active = False
		for path in self.searchPaths:
			pngname = (path % self.path) + serviceName + ".png"
			if fileExists(pngname):
				return pngname
		if active:
			self.downloadXPicon(serviceName)
		return ""
	
	def downloadXPicon(self,serviceName):	
		self.thread_downloader = threading.Thread(target=self.downloadXPiconThread, args=(serviceName,))
		self.thread_downloader.daemon = True
		self.thread_downloader.start()
	
	def downloadXPiconThread(self,serviceName):
		try:
			repoId = config.plugins.MyMetrix.XPiconsRepository.value
		except:
			repoId = 611
		try:
			depth = config.plugins.MyMetrix.PiconDepth.value
		except:
			depth = '8bit'
		try:
			width = config.plugins.MyMetrix.PiconSizes.value
		except:
			width = '220:XPicon/picon/'
		if serviceName != "picon_default":
			try:
				for widthItem in width.split(','):
					entry = widthItem.split(':')
					try:
						localPath = config.plugins.MyMetrix.XPiconsPath.value+entry[1]
					except:
						localPath = "/usr/share/enigma2/XPicon/picon/"
					if not os.path.exists(localPath):
						os.makedirs(localPath)
					activeXPiconUrl = URL_ACTIVEXPICON_API+str(repoId)+'&depth='+depth+'&width='+entry[0]+'&file='+serviceName+'.png'
					#print "[ActiveXPicon] Downloading "+serviceName+'.png'
					localFilePath = localPath + serviceName + '.png'
					webFile = urllib2.urlopen(activeXPiconUrl)
					print "Downloading XPicon: "+activeXPiconUrl
					localFile = open(localFilePath, 'w')
					localFile.write(webFile.read())
					webFile.close()
					localFile.close()
					#self.ShowXPicon(localFilePath)
			except Exception, e:
				pass

		
	
