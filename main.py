#!/usr/bin/env python
# -*- coding: utf-8 -*-

from client import LineClient
from curve.ttypes import ContentType
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM
import re

import config

class IRCThread(Thread):
	def __init__(self):
		self.S = socket(AF_INET, SOCK_STREAM)
		self.ready = False
		self.LineSend = None

		Thread.__init__(self)

	def setLineSend(self, lineSend):
		self.LineSend = lineSend

	def run(self):
		self.S.connect((config.IRC_HOST, config.IRC_PORT))
		self.F = self.S.makefile()
		self.send_raw_line("NICK %s" % config.IRC_NICK)
		self.send_raw_line("USER lineircbot 8 * :Line <-> IRC Bot")

		while True:
			line = self.F.readline().strip()
			if line == "":
				break

			token = line.split(" ")

			if token[0] == "PING":
				self.send_raw_line("PONG %s" % token[1])

			elif token[1] == "001":
				self.on_welcome()

			elif token[1] == "PRIVMSG":
				if self.LineSend != None:
					user = re.match(":(.*)!(.*)@(.*)", token[0])
					nick = user.group(1)
					host = user.group(3)

					ircmsg = re.match(":.*!.* PRIVMSG #.* :(.*)", line).group(1)

					if nick in config.IRC_NO_PREFIX:
						linemsg = ircmsg
					else:
						linemsg = "<%s> %s" % (nick, ircmsg)

					self.LineSend.send(linemsg)

	def send_raw_line(self, line):
		self.S.send("%s\r\n" % line)

	def send_message(self, line):
		self.send_raw_line("PRIVMSG %s :%s" % (config.IRC_CHAN, line.replace("\n", "")))

	def on_welcome(self):
		self.send_raw_line("JOIN %s" % config.IRC_CHAN)
		self.ready = True
		print ":: IRC is ready"


class LineSendThread(Thread):
	def __init__(self, token):
		try:
			self.client = LineClient(authToken = token)
		except:
			print ":: Send Login Failed"

		print ":: LineSend is ready"

		self.group = self.client.getGroupById(config.LINE_TARGET_GROUP)
		Thread.__init__(self)

	def setIRC(self, IRC):
		self.IRC = IRC

	def getClient(self):
		return self.client

	def send(self, message):
		self.group.sendMessage(message)

class LineRecvThread(Thread):
	def __init__(self, token):
		try:
			self.client = LineClient(authToken = token)
		except:
			print ":: Recv Login Failed"

		print ":: LineRecv is ready"

		self.idNickCache = {}
		self.IRC = None

		Thread.__init__(self)

	def setIRC(self, IRC):
		self.IRC = IRC

	def run(self):
		while True:
			op_list = []

			for op in self.client.longPoll():
				op_list.append(op)

			for op in op_list:
				sender   = op[0]
				message  = op[2]

				if message.contentType == ContentType.STICKER:
					ver = int(message.contentMetadata["STKVER"])
					pkgid = message.contentMetadata["STKPKGID"]
					stkid = message.contentMetadata["STKID"]
					url = "http://dl.stickershop.line.naver.jp/products/%d/%d/%d/%s/PC/stickers/%s.png" % (ver / 1000000, ver / 1000, ver % 1000, pkgid, stkid)
					msg = "[STICKER] %s" % url
				elif message.contentType == ContentType.IMAGE:
					if config.IMAGE_LOCAL_PREVIEW:
						# upload image to local server
						with open("%s/%s.jpg" % (config.IMAGE_LOCAL_PATH, message.id), "w+") as file_:
							file_.write(message.contentPreview)
						msg = "[IMAGE] %s/%s.jpg" % (config.IMAGE_LOCAL_WEB_PATH, message.id)
					elif config.IMAGE_WEB_PREVIEW:
						# image via line server
						msg = "[IMAGE] " + (config.IMAGE_WEB_PATH % message.id)
					else:
						# no image
						msg = "[IMAGE]";
				elif message.contentType == ContentType.NONE:
					msg = message.text
				else:
					msg = "[UNKNOWN]"

				if sender == None:
					if message.senderId in self.idNickCache:
						senderName = self.idNickCache[message.senderId]
					else:
						senderName = self.client._client.getContact(message.senderId).displayName
						self.idNickCache[message.senderId] = senderName
				else:
					senderName = sender.name

				if senderName in config.LINE_NO_PREFIX:
					ircmsg = msg
				else:
					ircmsg = "<%s> %s" % (senderName, msg)

				for rule in config.LINE_NICK_REPLACE:
					senderName = senderName.replace(rule[0], rule[1])

				if self.IRC != None and self.IRC.ready:
					self.IRC.send_message(ircmsg)

if __name__ == "__main__":
	IRC = IRCThread()
	IRC.daemon = True
	IRC.start()

	LineSend = LineSendThread(config.LINE_AUTH_TOKEN)
	LineSend.daemon = True
	LineSend.start()

	LineRecv = LineRecvThread(config.LINE_AUTH_TOKEN)
	LineRecv.daemon = True
	LineRecv.start()

	IRC.setLineSend(LineSend)
	LineRecv.setIRC(IRC)

	while True:
		pass
