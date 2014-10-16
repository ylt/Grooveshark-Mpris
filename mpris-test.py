from PyQt4 import QtDBus
from PyQt4.QtCore import QCoreApplication, QObject, Q_CLASSINFO, pyqtSlot, pyqtProperty, QTimer
from PyQt4.QtDBus import QDBusConnection, QDBusAbstractAdaptor
import http.client as httplib

#https://github.com/intarstudents/keySharky/wiki/api-server
class keySharky():
	def __init__(self, address):
		self.address = address
	
	def _query(self, path):
		conn = httplib.HTTPConnection(self.address)
		conn.request("GET", path)
		response = conn.getresponse()
		return response.read().decode('utf-8')

	def _parse(self, text):
		lines = text.splitlines(True)
		out = {}
		for line in lines:
			d = line.partition(": ")
			out[d[0]] = d[2].strip()
		return out

	def play(self):
		self._query("/play")
	def stop(self):
		self._query("/stop")
	def previous(self):
		self._query("/previous")
	def next(self):
		self._query("/next")
	def favorite(self):
		self._query("/favorite")
	def remove(self):
		self._query("/remove")
	def voteup(self):
		self._query("/voteup")
	def votedown(self):
		self._query("/votedown")
	def voteclear(self):
		self._query("/voteclear")
	def mute(self):
		self._query("/mute")
	def voldown(self):
		self._query("/voldown")
	def volup(self):
		self._query("/volup")
	def currentSong(self):
		s = self._query("/currentSong")
		return self._parse(s)
	def previousSong(self):
		s = self._query("/previousSong")
		return self._parse(s)
	def nextSong(self):
		s = self._query("/nextSong")
		return self._parse(s)
	def volume(self):
		v = self._query("/volume")
		return self._parse(v) 
	def setVolume(self, volume):
		self._query("/setVolume?%d" % volume)
	def muted(self):
		self._query("/muted")
	def gs_version(self):
		self._query("/gs-version")
	def gs_api_version(self):
		self._query("/gs-api-version")

class MyServer(QObject):
	def __init__(self):
		QObject.__init__(self)
		self.keySharky = keySharky("127.0.0.1:8800")
		self.dbus_main = Mpris2_Main(self)
		self.dbus_player = Mpris2_Player(self, self.keySharky)

class Mpris2_Main(QDBusAbstractAdaptor):
	Q_CLASSINFO("D-Bus Interface", "org.mpris.MediaPlayer2")
	Q_CLASSINFO("D-Bus Introspection",
		'  <interface name="org.mpris.MediaPlayer2">\n'
		'    <property name="CanQuit" type="b" access="read"/>\n'
		'    <property name="CanRaise" type="b" access="read"/>\n'
		'    <property name="HasTrackList" type="b" access="read"/>\n'
		'    <property name="Identity" type="b" access="read"/>\n'
		'    <property name="SupportedUriSchemes" type="b" access="read"/>\n'
		'    <property name="SupportedMimeTypes" type="b" access="read"/>\n'
		'    <method name="quit" />\n'
		'  </interface>\n')
	def __init__(self, parent):
		super().__init__(parent)

	@pyqtProperty(bool)
	def CanQuit(self):
		return False

	@pyqtProperty(bool)
	def CanRaise(self):
		return False

	@pyqtProperty(bool)
	def HasTrackList(self):
		return False

	@pyqtProperty(str)
	def Identity(self):
		return "Grooveshark"

	@pyqtProperty(str)
	def SupportedUriSchemes(self):
		return ""

	@pyqtProperty(str)
	def SupportedMimeTypes(self):
		return ""

	@pyqtSlot()
	def quit(self):
		import sys
		sys.exit(":D")

class Mpris2_Player(QDBusAbstractAdaptor):
	Q_CLASSINFO("D-Bus Interface", "org.mpris.MediaPlayer2.Player")
	Q_CLASSINFO("D-Bus Introspection",
		'  <interface name="org.mpris.MediaPlayer2.Player">\n'
		'    <property name="PlaybackStatus" type="s" access="read"/>\n'
		'    <property name="Rate" type="d" access="readwrite"/>\n'
		'    <property name="Shuffle" type="b" access="readwrite"/>\n'
		'    <property name="Metadata" type="a{sv}" access="read"/>\n'
		'    <property name="Volume" type="d" access="readwrite"/>\n'
		'    <property name="Position" type="x" access="read"/>\n'
		'    <property name="MinimumRate" type="d" access="read"/>\n'
		'    <property name="MaximumRate" type="d" access="read"/>\n'
		'    <property name="CanGoNext" type="b" access="read"/>\n'
		'    <property name="CanGoPrevious" type="b" access="read"/>\n'
		'    <property name="CanPlay" type="b" access="read"/>\n'
		'    <property name="CanPause" type="b" access="read"/>\n'
		'    <property name="CanSeek" type="b" access="read"/>\n'
		'    <property name="CanControl" type="b" access="read"/>\n'

		'    <method name="Next" />\n'
		'    <method name="Previous" />\n'
		'    <method name="Pause" />\n'
		'    <method name="PlayPause" />\n'
		'    <method name="Stop" />\n'
		'    <method name="Play" />\n'
		'    <method name="Seek">\n'
		'      <arg direction="in" type="x" name="Offset" />\n'
		'    </method>\n'
		'    <method name="SetPosition">\n'
		'      <arg direction="in" type="o" name="TrackId" />\n'
		'      <arg direction="in" type="x" name="Position" />\n'
		'    </method>\n'
		'    <method name="OpenUri">\n'
		'      <arg direction="in" type="s" name="Uri" />\n'
		'    </method>\n'
		'  </interface>\n')

	def PropertiesChanged(self, interface, property, values):
		"""Sends PropertiesChanged signal through sessionBus.
		Args:
			interface: interface name
			property: property name
			values: current property value(s)
		"""
		self.signal.setArguments(
			[interface, {property: values}, []]
		)
		QtDBus.QDBusConnection.sessionBus().send(self.signal)

	def __init__(self, parent, keySharky):
		super().__init__(parent)
		self.keySharky = keySharky

		self.signal = QtDBus.QDBusMessage.createSignal(
			"/org/mpris/MediaPlayer2",
			"org.freedesktop.DBus.Properties",
			"PropertiesChanged"
		)

		self.currentId = 1
		self.track = {}
		#self.prevTrack = {}
		#self.nextTrack = {}

		self.timer = QTimer()
		self.timer.timeout.connect(self.tick)
		self.timer.start(150)
		self.tick()

	def tick(self):
		old = self.track
		current = self.keySharky.currentSong()
		self.track = current

		if "songID" not in old:
			return

		if old["songID"] != current["songID"]:
			self.PropertiesChanged("org.mpris.MediaPlayer2.Player", "Metadata", self.getMetadata())
			self.currentId += 1
		
		if old["position"] != current["position"]:
			self.PropertiesChanged("org.mpris.MediaPlayer2.Player", "Position", self.Position)

		if old["status"] != current["status"]:
			self.PropertiesChanged("org.mpris.MediaPlayer2.Player", "PlaybackStatus", self.PlaybackStatus)
	
	def getTrack(self):
		return self.track

	def getMetadata(self):
		entry = self.track
		meta = {
			"mpris:trackid": self.currentId,
			"mpris:length": int(float(entry["calculatedDuration"])*1000),
			"mpris:artUrl": entry["artURL"],
			"xesam:album": entry["albumName"],
			"xesam:artist": entry["artistName"],
			"xesam:title": entry["songName"],
			"xesam:trackNumber": entry["trackNum"],
			"xesam:userRating": 1 if entry["vote"]==1 or entry["isInLibrary"] == "true" else 0
		}
		return meta
	
	@pyqtProperty(str)
	def PlaybackStatus(self):
		#song = self.keySharky.currentSong()
		#return song["status"]
		status = self.getTrack()["status"]
		return status.title()

	@pyqtProperty(int)
	def Rate(self):
		return 1
	
	#Todo: metadata
	@pyqtProperty("QMap<QString, QVariant>")
	def Metadata(self):
		return self.getMetadata()

	@pyqtProperty(float)
	def Volume(self):
		volume = self.keySharky.volume()
		return float(volume["volume"])/100
	@Volume.setter
	def Volume(self, value):
		self.keySharky.setVolume(value)*100

	@pyqtProperty(int)
	def Position(self):
		return float(self.getTrack()["position"])*1000

	@pyqtProperty(int)
	def MinimumRate(self):
		return 1

	@pyqtProperty(int)
	def MaximumRate(self):
		return 1

	@pyqtProperty(bool)
	def CanGoNext(self):
		song = self.keySharky.nextSong()
		if "songID" in song:
			return True
		return False

	@pyqtProperty(bool)
	def CanGoPrevious(self):
		song = self.keySharky.previousSong()
		if "songID" in song:
			return True
		return False

	#Todo: Can Play
	@pyqtProperty(bool)
	def CanPlay(self):
		song = self.getTrack()
		if "songID" in song:
			return True
		return False
	@pyqtProperty(bool)
	def CanPause(self):
		song = self.getTrack()
		if "songID" in song:
			return True
		return False

	@pyqtProperty(bool)
	def CanSeek(self):
		return True

	@pyqtProperty(bool)
	def CanControl(self):
		return True

	@pyqtSlot()
	def Next(self):
		self.keySharky.next()

	@pyqtSlot()
	def Previous(self):
		self.keySharky.previous()

	@pyqtSlot()
	def Pause(self):
		self.keySharky.play()
	@pyqtSlot()
	def PlayPause(self):
		self.keySharky.play()
	@pyqtSlot()
	def Stop(self):
		self.keySharky.stop()
	@pyqtSlot()
	def Play(self):
		self.keySharky.play()

	@pyqtSlot()
	def Seek(self):
		#"If the CanSeek property is false, this has no effect. "
		pass
	@pyqtSlot()
	def SetPosition(self, trackID, position):
		#"If the CanSeek property is false, this has no effect. "
		pass
	@pyqtSlot()
	def OpenURI(self, uri):
		pass

def start():
	app = QCoreApplication([])
	bus = QDBusConnection.sessionBus()
	server = MyServer()
	bus.registerObject('/org/mpris/MediaPlayer2', server)
	bus.registerService('org.mpris.MediaPlayer2.grooveshark')
	app.exec_()

if __name__ == '__main__':
	start()