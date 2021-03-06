#!/usr/bin/env python3

import os
import glob
import math
import sys
import pandas as pd
import csv
import functools
import time

def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['_B', 'KB', 'MB', 'GB', 'TB']:
        if num < 1000.0:
            return "%3.1f%s" % (num, x)
        num /= 1000.0


def file_size(file_path):
  """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)

def timestamp(file_path):
    if (not os.path.isfile(file_path)):
        return '--/--/--_--:--:--'
    return time.strftime('%y/%m/%d_%H:%M:%S', time.gmtime(os.path.getmtime(file_path)))

def left_justified(df):
    formatters = {}
    for li in list(df.columns):
        max = df[li].str.len().max()
        form = "{{:<{}s}}".format(max)
        formatters[li] = functools.partial(str.format, form)
    return df.to_string(formatters=formatters)

glob_verbose=False

def check_tagraw(dir,v):
    count=0
    for i in range(0,72100,5000):
        j=i+4999
        if (j>72100): j=72100
        #name = '{dir}/tags_{i:05}.json'.format(dir=dir,i=j) # tags v1
        name = '{dir}/tags_{i:05}-{j:05}.json'.format(dir=dir,v=v,i=i,j=j)
        if (glob_verbose):
            print(name)
        if os.path.isfile(name):
            count+=1
    return count

def main(options):

    dates=options.dates.split(',')
    hours=options.hours.split(',')
    out=options.output

    df=pd.DataFrame(columns=['avi','mp4','scale4','tagraw','tagmerge','tagclean'])

    def ok(flag, yes='ok', no='NO'):
        return yes if flag else no
    for d in dates:
        df.loc['C02_'+d+'______']=['','','','','','']
        for h in hours:
            name=d+h+'0000'
            vname='C02_'+name

            avifile='/work/rmegret/sfeliciano/Gurabo/*_02_R_'+name+'.avi'
            mpgfile='/work/rmegret/rmegret/videos/Gurabo/C02_'+name+'.mp4'
            scale4file=mpgfile+'.scale4.mp4'

            tagdir0='/work/rmegret/rmegret/tags/C02_'+name
            tagdir='/work/rmegret/rmegret/tags/C02_'+name+'/tagjson'
            tagrawfile='/work/rmegret/rmegret/tags/C02_'+name+'/tagjson/tags_69999.json'
            tagrawfile2='/work/rmegret/rmegret/tags/C02_'+name+'/tagjson/tags_65000-69999.json'
            tagmergefile='/work/rmegret/rmegret/tags/C02_'+name+'/tags-C02_'+name+'-0-72100.json'
            tagcleanfile='/work/rmegret/rmegret/tags/Tags/Tags-C02_'+name+'.json'

            avis = glob.glob(avifile)

            df.set_value(vname, 'avi', ok(len(avis)>0,'avi:ok  ','avi:--  '))
            df.set_value(vname, 'mp4', ok(os.path.isfile(mpgfile), 'mp4:ok  ','mp4:--  '))
            df.set_value(vname, 'scale4', ok(os.path.isfile(scale4file), 'sc4:ok  ','sc4:--  '))
            tagcount=check_tagraw(tagdir,vname)
            df.set_value(vname, 'tagraw',
                  'raw:{count:02}/15{mark} '.format(count=tagcount,mark='*' if tagcount<15 else ' '))
            df.set_value(vname, 'tagmerge', ok(os.path.isfile(tagmergefile),  'mrg:ok  ','mrg:--  '))
            df.set_value(vname, 'tagclean', ok(os.path.isfile(tagcleanfile),  'cln:ok  ','cln:--  '))

            if (len(avis)>0):
                if (os.path.isfile(avis[0])):
                   df.at[vname,'avi'] = 'avi({:1}):'.format(len(avis))+'{:_>8}'.format(file_size(avis[0]))
            if (os.path.isfile(mpgfile)):
            	 df.at[vname,'tagclean'] = 'cln:'+'{:_>8}'.format(file_size(tagcleanfile))

            if (options.timestamps):
                df.at[vname,'tagraw'] = timestamp(tagrawfile2)+'_'+df.at[vname,'tagraw']
                df.at[vname,'tagmerge'] = timestamp(tagmergefile)+'_'+df.at[vname,'tagmerge']
                df.at[vname,'tagclean'] = timestamp(tagcleanfile)+'_'+df.at[vname,'tagclean']
    if (out is not None):
        df.to_csv(out, index_label='video')
        with open(out+'.txt','w') as file:
            file.write(left_justified(df))
            file.write('\n')
    else:
        sys.stdout.write(left_justified(df))
        sys.stdout.write('\n')

if __name__ == '__main__':

    from argparse import ArgumentParser

    # for some reason pylint complains about members being undefined :(
    # pylint: disable=E1101

    parser = ArgumentParser(
        description='List videos and associated results')

    show_default = ' (default %(default)s)'

    parser.add_argument('-o', dest='output', help='output file'+show_default, default=None)

    parser.add_argument('-D', '--dates', dest='dates',  default='',
                        help='Dates to check '+show_default)
    parser.add_argument('-H', '--hours', dest='hours', default='07,08,09,10,11,12,13,14,15,16,17,18',
                        help='Hours to check '+show_default)

    parser.add_argument('-t', '--timestamps', dest='timestamps', action='store_true', help='Show file timestamp')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Increase verbosity')

    options = parser.parse_args()

    glob_verbose = options.verbose

    main(options)





