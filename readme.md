# A tool for removing silences from a video

**This tool is made to just work!**

However, at the moment, it's a quick-write. Please report bugs, if you found some.

## Comparison to other tools
As far as my reseach goes, all other tools suck:
- They don't work
- They have huge dependencies
- They have complex dependencies
- Their dependencies don't work
- They store each frame of the video as bitmap file<br> (how can you even think about something like this)


## Dependencies

- python3
- ffmpeg 
- ffprobe

You need to have all of those installed.

**@Windows users**:
Make sure, that the path to `ffmpeg` and `ffprobe` are inside the "path variable". I.e. you can run both commands from the command line like `C:> ffmpeg`.

## How to use

- Easiest command: 
`python3 silence_cutter.py [your video]`

- Show **help** and suggestions: 
`python3 silence_cutter.py --help`

- More Options:
`python3 silence_cutter.py [your video] [outfile] [silence dB border]`


## Bugs

File them directly here on Github. I'll try to fix them as soon as possible.






