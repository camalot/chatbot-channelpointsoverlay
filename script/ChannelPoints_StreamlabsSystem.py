# -*- coding: utf-8 -*-
#---------------------------------------
#   Import Libraries
#---------------------------------------
import sys
import clr
import json
import codecs
import os
import re
import random
import datetime
import glob
import time
import threading
import shutil
import tempfile
import urllib
from HTMLParser import HTMLParser
import argparse
import logging
from logging.handlers import TimedRotatingFileHandler

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

clr.AddReferenceToFileAndPath(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "./libs/ChannelPointMonitor.dll"))
import ChannelPointMonitor

#---------------------------------------
#   [Required] Script Information
#---------------------------------------
ScriptName = "Channel Points Alert Overlay"
Website = "http://darthminos.tv"
Description = "An Alert Overlay For Twitch Channel Point Rewards"
Creator = "DarthMinos"
Version = "1.0.0-snapshot"
Repo = "camalot/chatbot-channelpointsoverlay"
ReadMeFile = "https://github.com/" + Repo + "/blob/develop/README.md"

UIConfigFile = os.path.join(os.path.dirname(__file__), "UI_Config.json")
SettingsFile = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "settings.json")

ScriptSettings = None
Initialized = False
Listener = None
ChannelId = None
Logger = None

class Settings(object):
    """ Class to hold the script settings, matching UI_Config.json. """

    def __init__(self, settingsfile=None):
        """ Load in saved settings file if available else set default values. """
        defaults = self.DefaultSettings(UIConfigFile)
        try:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
                settings = json.load(f, encoding="utf-8")
            self.__dict__ = Merge(defaults, settings)
        except Exception as ex:
            if Logger:
                Logger.error(str(ex))
            else:
                Parent.Log(ScriptName, str(ex))
            self.__dict__ = defaults

    def DefaultSettings(self, settingsfile=None):
        defaults = dict()
        with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
            ui = json.load(f, encoding="utf-8")
        for key in ui:
            if 'value' in ui[key]:
                try:
                    defaults[key] = ui[key]['value']
                except:
                    if key != "output_file":
                        if Logger:
                            Logger.warn("DefaultSettings(): Could not find key {0} in settings".format(key))
                        else:
                            Parent.Log(ScriptName, "DefaultSettings(): Could not find key {0} in settings".format(key))
        return defaults
    def Reload(self, jsonData):
        """ Reload settings from the user interface by given json data. """
        if Logger:
            Logger.debug("Reload Settings")
        else:
            Parent.Log(ScriptName, "Reload Settings")
        self.__dict__ = Merge(self.DefaultSettings(UIConfigFile), json.loads(jsonData, encoding="utf-8"))

class StreamlabsLogHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            message = self.format(record)
            Parent.Log(ScriptName, message)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

def GetLogger():
    log = logging.getLogger(ScriptName)
    log.setLevel(logging.DEBUG)

    sl = StreamlabsLogHandler()
    sl.setFormatter(logging.Formatter("%(funcName)s(): %(message)s"))
    sl.setLevel(logging.INFO)
    log.addHandler(sl)

    fl = TimedRotatingFileHandler(filename=os.path.join(os.path.dirname(
        __file__), "info"), when="w0", backupCount=8, encoding="utf-8")
    fl.suffix = "%Y%m%d"
    fl.setFormatter(logging.Formatter(
        "%(asctime)s  %(funcName)s(): %(levelname)s: %(message)s"))
    fl.setLevel(logging.INFO)
    log.addHandler(fl)

    if ScriptSettings.DebugMode:
        dfl = TimedRotatingFileHandler(filename=os.path.join(os.path.dirname(
            __file__), "debug"), when="h", backupCount=24, encoding="utf-8")
        dfl.suffix = "%Y%m%d%H%M%S"
        dfl.setFormatter(logging.Formatter(
            "%(asctime)s  %(funcName)s(): %(levelname)s: %(message)s"))
        dfl.setLevel(logging.DEBUG)
        log.addHandler(dfl)

    log.debug("Logger initialized")
    return log


def Init():
    global ScriptSettings
    global Initialized
    global Listener
    global ChannelId
    global Logger

    if Initialized:
        Logger.debug("Skip Initialization. Already Initialized.")
        return
    ScriptSettings = Settings(SettingsFile)
    Logger = GetLogger()

    ChannelId = GetChannelId()
    Logger.debug("Initialize Channel Points Overlay Script")
    # Load saved settings and validate values
    SendSettingsUpdate()
    Listener = ChannelPointMonitor.ChannelPointListener(ScriptSettings.TwitchOAuthToken, str(ChannelId))
    if Listener:
        Listener.OnRewardRedeemed += onRewardRedeemed
        Listener.OnLog += onLog
        Listener.Connect()
    else:
        Logger.debug("Listener is NONE")
    Initialized = True
    return

def onLog(sender, args):
    Logger.debug(str(args.Data))

def onRewardRedeemed (sender, args):
    Logger.debug("onRewardRedeemed Triggered")
    #  (ScriptSettings.IgnoreFulfillment and args.Status.upper() == "FULFILLED") or
    if not str(args.Image):
        Logger.debug("Skipped because no image defined")
        return
    itemCost = int(str(args.RewardCost))
    if itemCost <= ScriptSettings.MinimumCost:
        Logger.debug("Skipped because Cost is Below Minimum Cost Setting: {0}/{1}".format(itemCost, str(args.RewardCost)))
        # cost is not high enough
        return
    Logger.debug("After Item Cost Check")
    title = str(args.RewardTitle)
    if ScriptSettings.IgnorePattern and re.match(ScriptSettings.IgnorePattern, title):
        Logger.debug("Skipped because of ignore pattern")
        # matches the ignore pattern
        return
    if ScriptSettings.MatchPattern and not re.match(ScriptSettings.MatchPattern, title): 
        Logger.debug("Skipped because of Must Match Pattern")
        # does not match "must match" pattern
        return
    bgColor = ScriptSettings.AlertBackgroundColor or "rgba(0,0,0,0)"
    Logger.debug("Set Default BG Color: {0}".format(bgColor))
    if ScriptSettings.UseRewardBackgroundColor:
        bgColor = str(args.BackgroundColor)
        Logger.debug("Use Reward Background Color: {0}".format(bgColor))
    else:
        Logger.debug("Not Using Reward Background Color")

    Logger.debug(str(args.DisplayName) + " just redeemed " + title + " for " + str(args.RewardCost) + " " + ScriptSettings.PointsName + ".")
    dataVal = {
        "displayName" : str(args.DisplayName),
        "pointsName" : ScriptSettings.PointsName,
        "message" : str(args.Message or ""),
        "title" : title,
        "prompt" : str(args.RewardPrompt or ""),
        "cost" : itemCost,
        "status" : str(args.Status),
        "image" : str(args.Image or ""),
        "backgroundColor" : bgColor
    }

    # https://github.com/Bare7a/Streamlabs-Chatbot-Scripts/blob/master/SoundPlayer/SoundPlayer_StreamlabsSystem.py
    # Play sound file? 

    if ScriptSettings.EnableSounds:
        LocateSoundFile(title)
    
    SendRedemptionData(dataVal)
    return

def Unload():
    global Initialized
    global Listener
    Initialized = False
    if Listener is not None:
        Listener.OnRewardRedeemed -= onRewardRedeemed
        Listener = None

    return


def Execute(data):
    return


def Tick():
    return


def ScriptToggled(state):
    Logger.debug("State Changed: " + str(state))
    if state:
        Init()
    else:
        Unload()
    return

# ---------------------------------------
# [Optional] Reload Settings (Called when a user clicks the Save Settings button in the Chatbot UI)
# ---------------------------------------
def ReloadSettings(jsondata):
    Logger.debug("Reload Settings")
    # Reload saved settings and validate values
    Unload()
    Init()
    return

def Parse(parseString, user, target, message):
    resultString = parseString or ""
    return resultString

def SendWebsocketData(eventName, payload):
    if Logger:
        Logger.debug("Trigger Event: " + eventName)
    Parent.BroadcastWsEvent(eventName, json.dumps(payload))
    return
def SendSettingsUpdate():
    SendWebsocketData("EVENT_CHANNELPOINTS_SETTINGS", ScriptSettings.__dict__)

def SendRedemptionData(payload):
    SendWebsocketData("EVENT_CHANNELPOINTS_REDEEMED", payload)

def LocateSoundFile(rewardId):
    if not ScriptSettings.EnableSounds:
        Logger.debug("no sound: not enabled")
        return
    if os.path.isabs(ScriptSettings.SoundsPath):
        soundsPath = ScriptSettings.SoundsPath
    else:
        soundsPath = os.path.abspath(os.path.join(os.path.dirname(__file__), ScriptSettings.SoundsPath))

    if not os.path.exists(soundsPath):
        Logger.debug("Sounds path '{0}' does not exist.".format(soundsPath))
        return

    safeName = safeFileName(rewardId)
    Logger.debug("looking for {0}".format(safeName))
    soundFile = None
    foundFile = False

    # Find the text file
    textFile = os.path.join(soundsPath, "{0}.txt".format(safeName))
    if os.path.exists(textFile):
        randomLine = getRandomLineFromFile(textFile)
        soundFile = os.path.join(soundsPath, randomLine)
        foundFile = os.path.exists(soundFile)
    else:
        extensions = ["mp3", "wav", "ogg"]
        for ext in extensions:
            fullFile = os.path.join(soundsPath, "{0}.{1}".format(safeName, ext))
            if os.path.exists(fullFile) and not foundFile:
                foundFile = True
                soundFile = fullFile

    if not foundFile and ScriptSettings.EnableDefaultSound:
        defaultFile = os.path.join(soundsPath, ScriptSettings.SoundDefault)
        if os.path.exists(defaultFile):
            if defaultFile.endswith(".txt"):
                randomLine = getRandomLineFromFile(defaultFile)
                soundFile = os.path.join(soundsPath, randomLine)
                foundFile = os.path.exists(soundFile)
            else:
                foundFile = True
                soundFile = defaultFile

    if foundFile:
        # should there be a cooldown for the sound play?
        Logger.debug("playing {0}".format(soundFile))
        Parent.PlaySound(soundFile, ScriptSettings.SoundVolume)

def getRandomLineFromFile(filename):
    r = random.Random(random.seed())
    lines = list(open(filename))
    r.shuffle(lines)
    randomLine = r.choice(lines).rstrip()
    return randomLine

def safeFileName(filename):
    keepcharacters = (' ','.','_')
    return "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()

def str2bool(v):
    if not v:
        return False
    return stripQuotes(v).strip().lower() in ("yes", "true", "1", "t", "y")

def urlEncode(v):
    return urllib.quote(v)

def stripQuotes(v):
    r = re.compile(r"^[\"\'](.*)[\"\']$", re.U)
    m = r.search(v)
    if m:
        return m.group(1)
    return v


def Merge(source, destination):
    """
    >>> a = { 'first' : { 'all_rows' : { 'pass' : 'dog', 'number' : '1' } } }
    >>> b = { 'first' : { 'all_rows' : { 'fail' : 'cat', 'number' : '5' } } }
    >>> merge(b, a) == { 'first' : { 'all_rows' : { 'pass' : 'dog', 'fail' : 'cat', 'number' : '5' } } }
    True
    """
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            Merge(value, node)
        elif isinstance(value, list):
            destination.setdefault(key, value)
        else:
            if key in destination:
                pass
            else:
                destination.setdefault(key, value)

    return destination

def TriggerRewardCommand(name, payload):
    pass

def random_line(filename):
    with open(filename) as f:
        lines = f.readlines()
        return random.choice(lines).strip()

def GetChannelId():
    resp = Parent.GetRequest("https://decapi.me/twitch/id/" + Parent.GetChannelName(), headers={})
    obj = json.loads(json.loads(resp)['response'])
    return str(obj)

def OpenScriptUpdater():
    currentDir = os.path.realpath(os.path.dirname(__file__))
    chatbotRoot = os.path.realpath(os.path.join(currentDir, "../../../"))
    libsDir = os.path.join(currentDir, "libs/updater")
    Logger.debug(libsDir)
    try:
        src_files = os.listdir(libsDir)
        tempdir = tempfile.mkdtemp()
        Logger.debug( tempdir)
        for file_name in src_files:
            full_file_name = os.path.join(libsDir, file_name)
            if os.path.isfile(full_file_name):
                Logger.debug("Copy: " + full_file_name)
                shutil.copy(full_file_name, tempdir)
        updater = os.path.join(tempdir, "ApplicationUpdater.exe")
        updaterConfigFile = os.path.join(tempdir, "update.manifest")
        repoVals = Repo.split('/')
        updaterConfig = {
            "path": os.path.realpath(os.path.join(currentDir, "../")),
            "version": Version,
            "name": ScriptName,
            "requiresRestart": True,
            "kill": [],
            "execute": {
                "before": [{
                    "command": "cmd",
                    "arguments": [ "/c", "del /q /f /s *" ],
                    "workingDirectory": "${PATH}\\${FOLDERNAME}\\Libs\\updater\\",
                    "ignoreExitCode": True,
                    "validExitCodes": [ 0 ]
                }],
                "after": []
            },
            "application": os.path.join(chatbotRoot, "Streamlabs Chatbot.exe"),
            "folderName": os.path.basename(os.path.dirname(os.path.realpath(__file__))),
            "processName": "Streamlabs Chatbot",
            "website": Website,
            "repository": {
                "owner": repoVals[0],
                "name": repoVals[1]
            }
        }
        Logger.debug(updater)
        configJson = json.dumps(updaterConfig)
        Logger.debug(configJson)
        with open(updaterConfigFile, "w+") as f:
            f.write(configJson)
        os.startfile(updater)
        return
    except OSError as exc:  # python >2.5
        raise
    return


def OpenFollowOnTwitchLink():
    os.startfile("https://twitch.tv/DarthMinos")
    return


def OpenReadMeLink():
    os.startfile(ReadMeFile)
    return


def OpenWordFile():
    os.startfile(WordFile)
    return


def OpenPaypalDonateLink():
    os.startfile("https://paypal.me/camalotdesigns/10")
    return
def OpenGithubDonateLink():
    os.startfile("https://github.com/sponsors/camalot")
    return
def OpenTwitchDonateLink():
    os.startfile("http://twitch.tv/darthminos/subscribe")
    return

def SendTestAlert():
    Logger.debug("Send Test Alert")
    bgColor = ScriptSettings.AlertBackgroundColor or "rgba(0,0,0,0)"
    if ScriptSettings.UseRewardBackgroundColor:
        bgColor = "rgba(200,0,0,1)"
    rewardTitle = "Test Channel Point Reward"
    SendRedemptionData({
        "displayName" : Parent.GetChannelName(),
        "pointsName" : ScriptSettings.PointsName,
        "message" : rewardTitle,
        "title" : "Test Channel Point Reward",
        "prompt" : "Test Prompt Message",
        "cost" : 500,
        "status" : "UNFULFILLED",
        "image" : "https://static-cdn.jtvnw.net/custom-reward-images/58491861/5b6b1100-88e5-416b-934c-2e9ae2d75c70/b845e0af-0463-4da5-a336-6467b87a595c/custom-4.png",
        "backgroundColor" : bgColor
    })
    Logger.debug("trigger soundfile")
    LocateSoundFile(rewardTitle)

def OpenOverlayInBrowser():
    # ?layer-name=" + urlEncode(ScriptName) + "&layer-width=1920&layer-height=1080
    os.startfile(os.path.realpath(os.path.join(
        os.path.dirname(__file__), "overlay.html")))
    return

def OpenOAuthRequestInBrowser():
    os.startfile("https://twitchapps.com/tmi/")
    return
def OpenDiscordLink():
    os.startfile("https://discord.com/invite/vzdpjYk")
    return
