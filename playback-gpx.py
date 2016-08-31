#!/usr/bin/env python
import sys
import logging
from optparse import OptionParser
import os
import platform
import gpxpy
import gpxpy.gpx
import time
from subprocess import check_output

# python playback-gpx.py -i 1 -r "-r 192.168.56.102" "docs/North On Topanga(1).gpx"
# python playback-gpx.py -i 1 -r "-r 192.168.56.101" "docs/South On Topanga(1).gpx"

# 08/21/2014
# added returnDefaultPath function so the script is more os independent
# added -r option so users can pass extra flags to geanyshell like an ip address
# added ability to pause execution of script with keyboard interrupt

def returnDefaultPath():
    if(platform.system() == 'Linux'):
      return "/usr/bin/genyshell"
    elif(platform.system() == 'Windows'):
      return "C:\Program Files\Genymobile\Genymotion\genyshell.exe"
    elif(platform.system() == 'Darwin'):
      return "/Applications/Genymotion Shell.app/Contents/MacOS/genyshell"

def process_file(path, options):
    logging.info("processing " + path)
    gpx_file = open(path, 'r')
    gpx = gpxpy.parse(gpx_file)

    for track in gpx.tracks:
        print track
        for segment in track.segments:
            for point in segment.points:
                set_point(point, options)
                try:
                  time.sleep(options.interval)
                except KeyboardInterrupt:
                  print '\nPausing...  (Hit ENTER to continue, type quit or exit.)'
                  response = raw_input()
                  if (response == 'quit') or (response == 'exit'):
                    exit()
                  else:
                    continue

    for route in gpx.routes:
        for point in route:
            set_point(point, options)
            time.sleep(options.interval)


def set_point(point, options):
    try:
      logging.info('Point at ({0},{1},{2})'.format(point.latitude, point.longitude, point.elevation))
      logging.debug(check_output([options.command, "-c", "gps setlatitude " + str(point.latitude), options.ipaddress]))
      logging.debug(check_output([options.command, "-c", "gps setlongitude " + str(point.longitude), options.ipaddress]))
      logging.debug(check_output([options.command, "-c", "gps setaltitude " + str(point.elevation), options.ipaddress]))
    except KeyboardInterrupt:
      print '\nPausing...  (Hit ENTER to continue, type quit or exit.)'
      try:
        response = raw_input()
        if (response == 'quit') or (response == 'exit'):
          exit()
        print 'Resuming...'
      except KeyboardInterrupt:
        print 'Resuming...'


if __name__=='__main__':
    usage = "usage: %prog "
    parser = OptionParser(usage=usage,
        description="Read a gpx file and use it to send points to Genymotion emulator at a fixed interval")
    parser.add_option("-d", "--debug", action="store_true", dest="debug")
    parser.add_option("-q", "--quiet", action="store_true", dest="quiet")
    parser.add_option("-i", "--interval", type="int", dest="interval", default="2",
        help="interval between points in seconds, defaults to 2 seconds")
    parser.add_option("-r", "--ip_address", dest="ipaddress",
        help="any extra flags passed to genymotion shell",
        default="")
    parser.add_option("-g", "--genymotion-shell", dest="command",
        help="path to the genyshell command",
        default=returnDefaultPath())
    (options, args) = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if options.debug else
        (logging.ERROR if options.quiet else logging.INFO))

    logging.debug("using genymotion shell at " + options.command)

    for path in args:
        if not os.path.exists(path):
            logging.error(path + " not found")
            continue
        process_file(path, options)
