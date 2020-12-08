# SOUNDS FOLDER

Sound files must be named the same as the Reward on Twitch. 

*Note: characters that are not allowed in file names should be replaced with `_`*

There are 2 types of files that can be used. An audio file, like an `mp3`, `wav`, or `ogg`. Or a text file. The text file contains lines that have just the path, relative to the `Sound Files Path`. It will play a random file from the text file.

## Supported file formats:

- mp3
- wav
- ogg
- txt (this is a special file that allows you to put multiple sound files, and it will randomly play one of them)

## Sounds folder structure:

- `/sounds/`
	- `default-reward.mp3` or `default-reward.txt`
	- `run ad.txt`
		- Play a random file for the reward  
			sample contents of `run ad.txt`:
			```
			sound1.mp3
			sound2.mp3
			sound3.mp3

			``` 
	- `choose operator.mp3`
