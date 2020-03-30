# CHATBOT TWITCH CHANNEL POINTS OVERLAY

Adds an overlay alert for when someone redeems channel point rewards

[![See Channel Point Alert In Action](https://img.youtube.com/vi/KZXxJbsw70U/0.jpg)](https://www.youtube.com/watch?v=KZXxJbsw70U)


## REQUIREMENTS

- Install [StreamLabs Chatbot](https://streamlabs.com/chatbot)
- [Enable Scripts in StreamLabs Chatbot](https://github.com/StreamlabsSupport/Streamlabs-Chatbot/wiki/Prepare-&-Import-Scripts)
- [Microsoft .NET Framework 4.7.2 Runtime](https://dotnet.microsoft.com/download/dotnet-framework/net472) or later

## INSTALL

- Download the latest zip file from [Releases](https://github.com/camalot/chatbot-channelpointsoverlay/releases/latest)
- Right-click on the downloaded zip file and choose `Properties`
- Click on `Unblock`  
[![](https://i.imgur.com/YoUi7UCl.png)](https://i.imgur.com/YoUi7UC.png)  
  > **NOTE:** If you do not see `Unblock`, the file is already unblocked.
- In Chatbot, Click on the import icon on the scripts tab.  
  ![](https://i.imgur.com/16JjCvR.png)
- Select the downloaded zip file
- Right click on `Twitch Team` row and select `Insert API Key`. Click yes on the dialog.  
[![](https://i.imgur.com/AWmtHKFl.png)](https://i.imgur.com/AWmtHKF.png)  

## CONFIGURATION

Make sure the script is enabled  
[![](https://i.imgur.com/mJMVOY2l.png)](https://i.imgur.com/mJMVOY2.png)  

Click on the script in the list to bring up the configuration.

### GENERAL SETTINGS  

[![](https://i.imgur.com/ONYDhxNl.png)](https://i.imgur.com/ONYDhxN.png)  

| ITEM | DESCRIPTION | DEFAULT | 
| ---- | ----------- | ------- | 
| `Channel Points Name` | The name of your channel points | `Points` |  
| `Ignore Fulfillment` | Will only show for items that have been `UNFULFILLED` | `true` |  
| `Minimum Reward Cost` | The minimum reward points that have to be redeemed to trigger the alert | `` |  
| `Duration (seconds)` | The time, in seconds, to show the alert | `5` |
| `OPEN OVERLAY IN BROWSER` | Opens the url in your browser for testing | |  
| `SEND TEST ALERT` | Sends a test event to the overlay | |



### AUTHENTICATION

[![](https://i.imgur.com/TypKtxAl.png)](https://i.imgur.com/TypKtxA.png)  

| ITEM | DESCRIPTION | DEFAULT | 
| ---- | ----------- | ------- | 
| `Twitch OAuth` | Your Twitch OAuth Token. | `""` |  
| `GET OAUTH TOKEN` | Opens the page to get the token |  |

### TRANSITIONS

[![](https://i.imgur.com/kaBWgI7l.png)](https://i.imgur.com/kaBWgI7.png)  

| ITEM | DESCRIPTION | DEFAULT | 
| ---- | ----------- | ------- | 
| `In Transition` | The animation when the alert shows | `slideInRight` |  
| `In Attention Animation` | An attention animation after it enters | `pulse` |
| `Out Transition` | The animation when the alert exits | `slideOutRight` |  
| `Out Attention Animation` | An attention animation before it exits. | `pulse` |

### STYLE

[![](https://i.imgur.com/1a6tPP0l.png)](https://i.imgur.com/1a6tPP0.png)  

| ITEM | DESCRIPTION | DEFAULT | 
| ---- | ----------- | ------- | 
| `Alert Border Radius` | The percentage of curve to add to the corners. | `0` |  
| `Alert Border Width (px)` | The width of the border to put around the alert box. | `0` |  
| `Alert Border Color` | The border color around the alert box. | `TRANSPARENT` |  
| `Opacity` | 0 = Fully Transparent. 100 = Fully Opaque. | `100` |
| `Use Reward Background Color` | If true, it will use the colors of the reward; otherwise, it will use the `Alert Background Color` | `false` |
| `Alert Background Color` | The color of the alert background | `TRANSPARENT` |
| `Font Name` | The font to use. Select custom to enter a name from `Adobe Edge Fonts` | `days-one` |
| `Custom Font Name` | The name of the `Adobe Edge Font` | |


### TEXT STYLE

[![](https://i.imgur.com/XBAm2kT.png)](https://i.imgur.com/XBAm2kT.png)  

| ITEM | DESCRIPTION | DEFAULT | 
| ---- | ----------- | ------- | 
| `Title Font Size (em)` | The size of the reward title. | `1` |  
| `Title Color` | The color of the reward title | `rgba(240, 240, 240, 1)` |
| `Title Stroke Color` | The color of the reward title stroke | `TRANSPARENT` |
| `Title Stroke Width (px)` | The width of the reward title stroke | `0` |  
| `Name Font Size (em)` | The size of the username label. | `1` |  
| `Name Color` | The color of the username label | `rgba(240, 240, 240, 1)` |
| `Name Stroke Color` | The color of the username label stroke | `TRANSPARENT` |
| `Name Stroke Width (px)` | The width of the username label stroke | `0` |  
| `Show Prompt Message` | If checked, the prompt message will display. | `true` |  
| `Prompt Font Size (em)` | The size of the reward prompt. | `1` |  
| `Prompt Color` | The color of the reward prompt | `rgba(240, 240, 240, 1)` |
| `Prompt Stroke Color` | The color of the reward prompt stroke | `TRANSPARENT` |
| `Prompt Stroke Width (px)` | The width of the reward prompt stroke | `0` |  
| `Show Prompt Response Message` | If checked, the prompt message response will display. | `true` |  
| `Message Font Size (em)` | The size of the reward prompt response. | `1` |  
| `Message Color` | The color of the reward prompt response | `rgba(240, 240, 240, 1)` |
| `Message Stroke Color` | The color of the reward prompt response stroke | `TRANSPARENT` |
| `Message Stroke Width (px)` | The width of the reward prompt response stroke | `0` |  

### INFORMATION  

[![](https://i.imgur.com/MKxaCXLl.png)](https://i.imgur.com/MKxaCXL.png)  

| ITEM | DESCRIPTION | 
| ---- | ----------- | 
| `Donate` | If you feel like supporting, you can click this |  
| `Follow Me On Twitch` | You can follow me on twitch. |  
| `Open Readme` | Opens this document |  
| `Check for Updates` | Updates this script. |  
| `Save Settings` | Save the settings. |  



## SCRIPT UPDATER

> **NOTE:** You must launch from within Streamlabs Chatbot. 

The application will open, and if there is an update it will tell you. You click on the `Download & Update` button. 

> **NOTE:** Applying the update will close down Streamlabs Chatbot. It will reopen after the update is complete.

[![](https://i.imgur.com/hfNMfvJl.png)](https://i.imgur.com/hfNMfvJ.png)

## OVERLAY SETUP IN OBS / SLOBS 

- Add a new `Browser Source` in OBS / SLOBS  
[![](https://i.imgur.com/TAMQkeql.png)](https://i.imgur.com/TAMQkeq.png)
- Set as a `Local File` and choose the `overlay.html` in the `ChannelPointsAlertOverlay` script directory. You can easily get to the script directory location from right clicking on `Channel Points Alert Overlay` in Chatbot and choose `Open Script Folder`.
- Set the `width` and `height` to the resolution of your `Base (Canvas) Resolution`. 
- Add any additional custom CSS that you would like to add.
- Check both `Shutdown source when not visible` and `Refresh browser when scene becomes active`.  
[![](https://i.imgur.com/nouqPh0l.png)](https://i.imgur.com/nouqPh0.png)
