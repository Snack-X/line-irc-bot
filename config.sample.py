#!/usr/bin/env python
# -*- coding: utf-8 -*-

IRC_HOST = "irc.example.com"
IRC_PORT = 6667
IRC_NICK = "LineIRCBot"
IRC_CHAN = "#line"

LINE_AUTH_TOKEN = ""
LINE_NICK_REPLACE = [
	["nickname", "nick·name"] # prefixed nickname replace rules at IRC
]
LINE_TARGET_GROUP = ""

IRC_NO_PREFIX = ["nickname1", "nickname2"] # these nicknames will not be prefixed at IRC
LINE_NO_PREFIX = ["nickname1"] # these nicknames will not be prefixed at LINE

IMAGE_PREVIEW = True # use image preview with web
IMAGE_LOCAL_PATH = "/home/linepreview/" # server path of LINE's preview images
IMAGE_WEB_PATH = "http://line.example.com/" # web path of LINE's preview images