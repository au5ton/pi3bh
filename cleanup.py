#!/usr/bin/env python3

import os
import time
import shutil
import argparse
from pathlib import Path
from datetime import datetime

print(f'''
----------
cleanup.py
{datetime.now()}
''')

# see: https://stackoverflow.com/a/1094933
def sizeof_fmt(num, suffix='B'):
        for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
                if abs(num) < 1024.0:
                        return "%3.1f%s%s" % (num, unit, suffix)
                num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)

parser = argparse.ArgumentParser(description='Cleanup old files that are taking up space')
parser.add_argument('path', type=str, help='Directory location to monitor')
parser.add_argument('--ratio', type=float, default=0.8, help='Percentage (as a ratio 0.0-1.0) that describes when files should start being pruned off.')
parser.add_argument('--dryrun', action='store_true', help='Show which files would be deleted, but don\'t actually delete them.')
args = parser.parse_args()

stat = shutil.disk_usage(args.path)
ratio = stat.used / stat.total

print(f'{round(ratio * 100,2)}% of disk used at {args.path}')
print(f'Ratio limit is set to: {round(args.ratio * 100,2)}%')

if(ratio >= args.ratio):
        print('Usage exceeds limit!')
else:
        print('Usage does not exceed limit. Exiting.')
        exit()


# get array of files in directory
files = [x for x in Path(args.path).iterdir() if x.is_file()]
# sort files by modification date, in ascending order
files = sorted(files, key=lambda x: os.path.getmtime(x.absolute()))

# determine which files should be deleted to maintain ratio
recovery_goal = stat.used - (args.ratio * stat.total)
print(f'Need to recover {sizeof_fmt(recovery_goal)} to maintain ratio of {round(args.ratio * 100,2)}%')

_sumofallfiles = sum([x.stat().st_size for x in files])
if(_sumofallfiles < recovery_goal):
        print(f'Recovery goal is impossible. The files in the following directory don\'t occupy enough space to meet the recovery goal.')
        print(f'Directory: {args.path}')
        print(f'Directory size: {sizeof_fmt(_sumofallfiles)}')
        print(f'Recovery goal: {sizeof_fmt(recovery_goal)}')
        exit()

# while our recovery goal has still not yet been met
to_delete = []
for x in files:
        to_delete_size = sum([x.stat().st_size for x in to_delete])
        if(to_delete_size < recovery_goal):
                to_delete += [x]

print('Staged to delete:')
for x in to_delete:
        print(f'\t - {x.absolute()}')
        print(f'\t   {time.ctime(os.path.getmtime(x.absolute()))}')

if(not args.dryrun):
        for x in to_delete:
                x.unlink()
        print('Staged files were deleted')
