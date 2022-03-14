import gpmf
import gpxpy
import argparse
import os.path
import glob
from datetime import datetime, timedelta

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--path", help="Path to the gps file", default='/Users/fischert/Pictures/HERO10 BLACK/')
parser.add_argument("-i", "--input", help="Input video num", type=str, required=True)
args = parser.parse_args()

# Read the binary stream from the file
gpx = gpxpy.gpx.GPX()
gpx_track = gpxpy.gpx.GPXTrack()
gpx.tracks.append(gpx_track)

for infile in glob.glob(os.path.join(args.path, 'GX*' + args.input + ".MP4")):
    print('Process file ' + infile)
    stream = gpmf.io.extract_gpmf_stream(infile)

    # Extract GPS low level data from the stream
    gps_blocks = gpmf.gps.extract_gps_blocks(stream)

    # Parse low level data into more usable format
    gps_data = list(map(gpmf.gps.parse_gps_block, gps_blocks))
    last_invalid_gps_idx = 0
    for idx, gps_item in enumerate(gps_data):
        if gps_item.precision > 10 or gps_item.fix != 3:
            last_invalid_gps_idx = idx + 1
    print(f'Removing {last_invalid_gps_idx} (out of {len(gps_data)}) invalid GPS points, i.e.  {last_invalid_gps_idx / len(gps_data) * 100:.1f} %')
    print(f'That\'s {(datetime.strptime(gps_data[last_invalid_gps_idx].timestamp, "%Y-%m-%d %H:%M:%S.%f") - datetime.strptime(gps_data[0].timestamp, "%Y-%m-%d %H:%M:%S.%f")).total_seconds()} seconds out of {(datetime.strptime(gps_data[-1].timestamp, "%Y-%m-%d %H:%M:%S.%f") - datetime.strptime(gps_data[0].timestamp, "%Y-%m-%d %H:%M:%S.%f")).total_seconds()} seconds')
    gps_data = gps_data[last_invalid_gps_idx:]

    gpx_track.segments.append(gpmf.gps.make_pgx_segment(gps_data))

outfilename = os.path.join(args.path, args.input + '.gpx')
print('Write gpx to ' + outfilename)
with open(outfilename, 'w') as outfile:
    outfile.write(gpx.to_xml())