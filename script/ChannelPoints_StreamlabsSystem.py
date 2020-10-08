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

SettingsFile = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "settings.json")

ScriptSettings = None
Initialized = False
Listener = None
ChannelId = None

class Settings(object):
    """ Class to hold the script settings, matching UI_Config.json. """

    def __init__(self, settingsfile=None):
        """ Load in saved settings file if available else set default values. """
        try:
            self.PointsName = "Points"
            self.TwitchOAuthToken = ""
            self.IgnoreFulfillment = True
            self.PlaySound = False
            self.InSound = ""
            self.OutSound = ""
            self.InTransition = "slideInRight"
            self.InAttentionAnimation = "pulse"
            self.OutTransition = "slideOutRight"
            self.OutAttentionAnimation = "pulse"
            self.Duration = 5
            self.ImageShape = "circle"
            self.Opacity = 100
            self.TitleColor = "rgba(255,255,255,1)"
            self.TitleStrokeColor = "rgba(0,0,0,0)"
            self.TitleStrokeWidth = 0
            self.NameColor = "rgba(255,255,255,1)"
            self.NameStrokeColor = "rgba(0,0,0,0)"
            self.NameStrokeWidth = 0
            self.PromptColor = "rgba(255,255,255,1)"
            self.PromptStrokeColor = "rgba(0,0,0,0)"
            self.PromptStrokeWidth = 0
            self.ShowPrompt = True
            self.MessageColor = "rgba(255,255,255,1)"
            self.MessageStrokeColor = "rgba(0,0,0,0)"
            self.MessageStrokeWidth = 0
            self.ShowMessage = True
            self.PromptFontSize = 1
            self.TitleFontSize = 1
            self.NameFontSize = 1
            self.MessageFontSize = 1
            self.BorderRadius = 0
            self.BorderWidth = 0
            self.BorderColor = "rgba(0,0,0,0)"
            self.MinimumCost = 0
            self.UseRewardBackgroundColor = True
            self.AlertBackgroundColor = "rgba(0,0,0,0)"
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
                fileSettings = json.load(f, encoding="utf-8")
                self.__dict__.update(fileSettings)

        except Exception as e:
            Parent.Log(ScriptName, str(e))

    def Reload(self, jsonData):
        """ Reload settings from the user interface by given json data. """
        Parent.Log(ScriptName, "Reload Settings")
        fileLoadedSettings = json.loads(jsonData, encoding="utf-8")
        self.__dict__.update(fileLoadedSettings)


def Init():
    global ScriptSettings
    global Initialized
    global Listener
    global ChannelId

    if Initialized:
        Parent.Log(ScriptName, "Skip Initialization. Already Initialized.")
        return
    ChannelId = GetChannelId()
    Parent.Log(ScriptName, "Initialize")
    # Load saved settings and validate values
    ScriptSettings = Settings(SettingsFile)
    SendSettingsUpdate()
    Listener = ChannelPointMonitor.ChannelPointListener(ScriptSettings.TwitchOAuthToken, str(ChannelId))
    if Listener:
        Listener.OnRewardRedeemed += onRewardRedeemed
        Listener.Connect()
    else:
        Parent.Log(ScriptName, "Listener is NONE")
    Initialized = True
    return

def onRewardRedeemed (sender, args):
    #  (ScriptSettings.IgnoreFulfillment and args.Status.upper() == "FULFILLED") or
    if not args.Image:
        return

    itemCost = int(str(args.RewardCost))
    if itemCost <= ScriptSettings.MinimumCost:
        return

    bgColor = ScriptSettings.AlertBackgroundColor or "rgba(0,0,0,0)"
    if ScriptSettings.UseRewardBackgroundColor:
        bgColor = str(args.BackgroundColor)
    
    rewardPayload = self.GetPayloadFromReward(args)
    
    Parent.Log(ScriptName, str(args.DisplayName) + " just redeemed " + str(args.RewardTitle) + " for " + str(args.RewardCost) + " " + ScriptSettings.PointsName + ".")
    dataVal = {
        "displayName" : str(args.DisplayName),
        "pointsName" : ScriptSettings.PointsName,
        "message" : str(args.Message or ""),
        "title" : str(args.RewardTitle),
        "prompt" : str(args.RewardPrompt or ""),
        "cost" : itemCost,
        "status" : str(args.Status),
        "image" : str(args.Image or ""),
        "backgroundColor" : bgColor
    }
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
    Parent.Log(ScriptName, "State Changed: " + str(state))
    if state:
        Init()
    else:
        Unload()
    return

# ---------------------------------------
# [Optional] Reload Settings (Called when a user clicks the Save Settings button in the Chatbot UI)
# ---------------------------------------
def ReloadSettings(jsondata):
    Parent.Log(ScriptName, "Reload Settings")
    # Reload saved settings and validate values
    Unload()
    Init()
    return

def Parse(parseString, user, target, message):
    resultString = parseString or ""
    return resultString

def SendWebsocketData(eventName, payload):
    Parent.Log(ScriptName, "Trigger Event: " + eventName)
    Parent.BroadcastWsEvent(eventName, json.dumps(payload))
    return
def SendSettingsUpdate():
    SendWebsocketData("EVENT_CHANNELPOINTS_SETTINGS", ScriptSettings.__dict__)

def SendRedemptionData(payload):
    SendWebsocketData("EVENT_CHANNELPOINTS_REDEEMED", payload)

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

def GetPayloadFromReward(reward):
    try:
        body = str(reward.RewardPrompt or "")
        payload = json.loads(body)
        return payload
    except Exception as e:
        return None

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
    Parent.Log(ScriptName, libsDir)
    try:
        src_files = os.listdir(libsDir)
        tempdir = tempfile.mkdtemp()
        Parent.Log(ScriptName, tempdir)
        for file_name in src_files:
            full_file_name = os.path.join(libsDir, file_name)
            if os.path.isfile(full_file_name):
                Parent.Log(ScriptName, "Copy: " + full_file_name)
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
        Parent.Log(ScriptName, updater)
        configJson = json.dumps(updaterConfig)
        Parent.Log(ScriptName, configJson)
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

    bgColor = ScriptSettings.AlertBackgroundColor or "rgba(0,0,0,0)"
    if ScriptSettings.UseRewardBackgroundColor:
        bgColor = "rgba(200,0,0,1)"

    SendRedemptionData({
        "displayName" : Parent.GetChannelName(),
        "pointsName" : ScriptSettings.PointsName,
        "message" : "Test Channel Point Redemption",
        "title" : "Test Channel Point Reward",
        "prompt" : "Test Prompt Message",
        "cost" : 500,
        "status" : "UNFULFILLED",
        "image" : "https://static-cdn.jtvnw.net/custom-reward-images/58491861/5b6b1100-88e5-416b-934c-2e9ae2d75c70/b845e0af-0463-4da5-a336-6467b87a595c/custom-4.png",
        "backgroundColor" : bgColor
    })

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
