from PyQt4 import QtDBus
from PyQt4.QtCore import (QCoreApplication, QObject, Q_CLASSINFO, pyqtSlot,
						  pyqtProperty)
from PyQt4.QtDBus import QDBusConnection, QDBusAbstractAdaptor
import http.client as httplib

#https://github.com/intarstudents/keySharky/wiki/api-server
class keySharky():
	def __init__(self, address):
		self.address = address
	
	def _query(self, path):
		conn = httplib.HTTPConnection(self.address)
		conn.request("GET", path)
		return conn.getresponse()

	def _parse(self, text):
		lines = text.splitLines(true)
		out = {}
		for line in lines:
			d = line.partition(": ")
			out[d[0]] = d[1]
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
		return self_parse(s)
	def previousSong(self):
		self._query("/previousSong")
	def nextSong(self):
		self._query("/nextSong")
	def volume(self):
		self._query("/volume")
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
		self.keySharky = keySharky("localhost:8800")
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
	def __init__(self, parent, keySharky):
		super().__init__(parent)
		self.keySharky = keySharky
	
	@pyqtProperty(str)
	def PlaybackStatus(self):
		song = self.keySharky.currentSong()
		return song.status

	@pyqtProperty(str)
	def Rate(self):
		return 1


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