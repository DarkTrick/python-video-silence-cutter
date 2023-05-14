# Created by DarkTrick - 4fb5f723849d32782e723c34bfd132e442d378d7

import subprocess
import tempfile
import sys
import os

def findSilences(filename, dB = -35):
  """
    returns a list:
      even elements (0,2,4, ...) denote silence start time
      uneven elements (1,3,5, ...) denote silence end time

  """
  command = ["ffmpeg","-i",filename,
             "-af","silencedetect=n=" + str (dB) + "dB:d=1",
             "-f","null","-"]
  output = subprocess.run (command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  s = str(output)
  lines = s.split("\\n")
  time_list = []
  for line in lines:
    if ("silencedetect" in line):
        words = line.split(" ")
        for i in range (len(words)):
            if ("silence_start" in words[i]):
              time_list.append (float(words[i+1]))
            if "silence_end" in words[i]:
              time_list.append (float (words[i+1]))
  silence_section_list = list (zip(*[iter(time_list)]*2))

  #return silence_section_list
  return time_list



def getVideoDuration(filename:str) -> float:
  command = ["ffprobe","-i",filename,"-v","quiet",
             "-show_entries","format=duration","-hide_banner",
             "-of","default=noprint_wrappers=1:nokey=1"]

  output = subprocess.run (command, stdout=subprocess.PIPE)
  s = str(output.stdout, "UTF-8")
  return float (s)

def getSectionsOfNewVideo (silences, duration):
  """Returns timings for parts, where the video should be kept"""
  return [0.0] + silences + [duration]


def ffmpeg_filter_getSegmentFilter(videoSectionTimings):
  ret = ""
  for i in range (int (len(videoSectionTimings)/2)):
    start = videoSectionTimings[2*i]
    end   = videoSectionTimings[2*i+1]
    ret += "between(t," + str(start) + "," + str(end) + ")+"
  # cut away last "+"
  ret = ret[:-1]
  return ret

def getFileContent_videoFilter(videoSectionTimings):
  ret = "select='"
  ret += ffmpeg_filter_getSegmentFilter (videoSectionTimings)
  ret += "', setpts=N/FRAME_RATE/TB"
  return ret

def getFileContent_audioFilter(videoSectionTimings):
  ret = "aselect='"
  ret += ffmpeg_filter_getSegmentFilter (videoSectionTimings)
  ret += "', asetpts=N/SR/TB"
  return ret

def writeFile (filename, content):
  with open (filename, "w") as file:
    file.write (str(content))


def ffmpeg_run (file, videoFilter, audioFilter, outfile):
  # prepare filter files
  vFile = tempfile.NamedTemporaryFile (mode="w", encoding="UTF-8", prefix="silence_video")
  aFile = tempfile.NamedTemporaryFile (mode="w", encoding="UTF-8", prefix="silence_audio")

  videoFilter_file = vFile.name #"/tmp/videoFilter" # TODO: replace with tempfile
  audioFilter_file = aFile.name #"/tmp/audioFilter" # TODO: replace with tempfile
  writeFile (videoFilter_file, videoFilter)
  writeFile (audioFilter_file, audioFilter)

  command = ["ffmpeg","-i",file,
              "-filter_script:v",videoFilter_file,
              "-filter_script:a",audioFilter_file,
              outfile]
  subprocess.run (command)

  vFile.close()
  aFile.close()



def cut_silences(infile, outfile, dB = -35):
  print ("detecting silences")
  silences = findSilences (infile,dB)
  duration = getVideoDuration (infile)
  videoSegments = getSectionsOfNewVideo (silences, duration)

  videoFilter = getFileContent_videoFilter (videoSegments)
  audioFilter = getFileContent_audioFilter (videoSegments)

  print ("create new video")
  ffmpeg_run (infile, videoFilter, audioFilter, outfile)

def printHelp():
  print ("Usage:")
  print ("   silence_cutter.py [infile] [optional: outfile] [optional: dB]")
  print ("   ")
  print ("        [outfile]")
  print ("         Default: [infile]_cut")
  print ("   ")
  print ("        [dB]")
  print ("         Default: -30")
  print ("         A suitable value might be around -50 to -35.")
  print ("         The lower the more volume will be defined das 'silent'")
  print ("         -30: Cut Mouse clicks and mouse movent; cuts are very recognizable.")
  print ("         -35: Cut inhaling breath before speaking; cuts are quite recognizable.")
  print ("         -40: Cuts are almost not recognizable.")
  print ("         -50: Cuts are almost not recognizable.")
  print ("              Cuts nothing, if there is background noise.")
  print ("         ")
  print ("")
  print ("Dependencies:")
  print ("          ffmpeg")
  print ("          ffprobe")

def main():
  args = sys.argv[1:]
  if (len(args) < 1):
    printHelp()
    return

  if (args[0] == "--help"):
    printHelp()
    return

  infile = args[0]

  if (not os.path.isfile (infile)):
    print ("ERROR: The infile could not be found:\n" + infile)
    return

  # set default values for optionl arguments
  tmp = os.path.splitext (infile)
  outfile = tmp[0] + "_cut" + tmp[1]
  dB = -30

  if (len(args) >= 2):
    outfile = args[1]

  if (len(args) >= 3):
    dB = args[2]


  cut_silences (infile, outfile, dB)


if __name__ == "__main__":
  main()
