#!/usr/bin/python
#
#  Copyright (C) 2013 eNovance SAS <licensing@enovance.com>
#  Author: Erwan Velu  <erwan@enovance.com>
#
#  The license below covers all files distributed with fio unless otherwise
#  noted in the file itself.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License version 2 as
#  published by the Free Software Foundation.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import os
import fnmatch
import sys
import getopt
import re
import math

def find_file(path, pattern):
	fio_data_file=[]
	# For all the local files
	for file in os.listdir(path):
	    # If the file math the regexp
	    if fnmatch.fnmatch(file, pattern):
		# Let's consider this file
		fio_data_file.append(file)

	return fio_data_file

def generate_gnuplot_math_script(title,gnuplot_output_filename,mode,unit):
	f=open("mymath",'a')
        f.write("call \'math.gpm\' \'%s' \'%s\' \'\' \'%s\' \'%s\' \'%s\'\n" % (title,gnuplot_output_filename,gnuplot_output_filename,mode,unit))
	f.close()

def compute_math(fio_data_file, title,gnuplot_output_filename,mode,item_unit):
	global_min=[]
	global_max=[]
	cumulated_file=open(gnuplot_output_filename+'.cumulated', 'w')
	average_bp_host_file=open(gnuplot_output_filename+'.average_bp_host', 'w')
	average_bp_stream_file=open(gnuplot_output_filename+'.average_bp_stream', 'w')
	average_cpu_host_file=open(gnuplot_output_filename+'.average_cpu_host', 'w')
	average_network_per_cpu_percent_file=open(gnuplot_output_filename+'.average_network_per_cpu_percent', 'w')
	stddev_between_hosts_file=open(gnuplot_output_filename+'.stddev_bp_between_hosts', 'w')
	stddev_between_streams_file=open(gnuplot_output_filename+'.stddev_between_streams', 'w')

	cumulated_file.write('%s bandwidth\n' % item_unit)
	average_bp_host_file.write('%s bandwidth\n' % item_unit)
	average_bp_stream_file.write('%s bandwidth\n' % item_unit)
	average_cpu_host_file.write('%s cpu_percent\n' % item_unit)
	average_network_per_cpu_percent_file.write('%s bandwidth\n' % item_unit)
	stddev_between_hosts_file.write('%s bandwidth\n' % item_unit)
	stddev_between_streams_file.write('%s bandwidth\n' % item_unit)
	for file in fio_data_file:
		shall_break = False
		f=open(file,'r')
		m = re.search('(?<=.output.).*', file)
		if not m:
			continue
		else:
			item=int(m.group(0))
		while True:
			current_line=[]
			s=f.readline()
			if not s:
				shall_break=True
				break;
			current_line.append(s);

			if shall_break == True:
				break

			last_time = -1
			for line in current_line:
				n = re.search('(.*) : (.*)', line)
				if (n and n.group(1) and n.group(2)):
					if ("Cumulated bandwidth" in n.group(1)):
						cumulated_file.write('%d %s\n' % (item, n.group(2)))
					elif ("Average bandwidth / host" in n.group(1)):
						average_bp_host_file.write('%d %s\n' % (item, n.group(2)))
					elif ("Average bandwidth / stream" in n.group(1)):
						average_bp_stream_file.write('%d %s\n' % (item, n.group(2)))
					elif ("Average cpu load / host" in n.group(1)):
						average_cpu_host_file.write('%d %s\n' % (item, n.group(2)))
					elif ("Average network bandwidth / %cpu" in n.group(1)):
						average_network_per_cpu_percent_file.write('%d %s\n' % (item, n.group(2)))
					elif ("Standard deviation between host" in n.group(1)):
						if "Mbps" in n.group(2):
							stddev_between_hosts_file.write('%d %s\n' % (item, n.group(2)))
					elif ("Standard deviation between streams" in n.group(1)):
						stddev_between_streams_file.write('%d %s\n' % (item, n.group(2)))
		f.close()

	cumulated_file.close()
	average_bp_host_file.close()
	average_bp_stream_file.close()
	average_cpu_host_file.close()
	average_network_per_cpu_percent_file.close()
	stddev_between_hosts_file.close()
	stddev_between_streams_file.close()
	try:
		os.remove('mymath')
	except:
		True

	generate_gnuplot_math_script("Cumulated Bandwidth"+title,gnuplot_output_filename+'.cumulated',"Bandwidth in Mbits/sec",item_unit)
	generate_gnuplot_math_script("Average Bandwidth per Host"+title,gnuplot_output_filename+'.average_bp_host',"Bandwidth in Mbits/sec",item_unit)
	generate_gnuplot_math_script("Average Bandwidth per Stream"+title,gnuplot_output_filename+'.average_bp_stream',"Bandwidth in Mbits/sec",item_unit)
	generate_gnuplot_math_script("Average CPU per Host"+title,gnuplot_output_filename+'.average_cpu_host',"CPU %",item_unit)
	generate_gnuplot_math_script("Average Network Bandwidth per CPU %"+title,gnuplot_output_filename+'.average_network_per_cpu_percent',"Mbits/CPU %",item_unit)
	generate_gnuplot_math_script("Standard Deviation of Bandwidth"+title,gnuplot_output_filename+'.stddev_bp_between_hosts',"Bandwidth in Mbits/sec",item_unit)
	generate_gnuplot_math_script("Standard Deviation of Bandwidth Between Hosts"+title,gnuplot_output_filename+'.stddev_bp_between_hosts',"Bandwidth in Mbits/sec",item_unit)
	generate_gnuplot_math_script("Standard Deviation of Bandwidth Between Streams"+title,gnuplot_output_filename+'.stddev_between_streams',"Bandwidth in Mbits/sec",item_unit)

def render_gnuplot():
	print "Running gnuplot Rendering\n"
	try:
		os.system("gnuplot mymath")
	except:
		print "Could not run gnuplot on mymath or mygraph !\n"
		sys.exit(1);

def print_help():
    print 'multidn2fio.py -gh -t <title> -o <outputfile> -p <pattern> -u <unit_name>'
    print
    print '-h --help                           : Print this help'
    print '-p <pattern> or --pattern <pattern> : A pattern in regexp to select fio input files'
    print '-g           or --gnuplot           : Render gnuplot traces before exiting'
    print '-o           or --outputfile <file> : The basename for gnuplot traces'
    print '                                       - Basename is set with the pattern if defined'
    print '-t           or --title <title>     : The title of the gnuplot traces'
    print '                                       - Title is set with the block size detected in fio traces'
    print '-u           or --unit <unit_name>  : The name of the item measured between runs'
    print '                                       - like mtu, rx/tx, ...'
    print 'Example : ./multidn2fio.py -p \'diag_network.output*\' -g -u mtu'

def main(argv):
    mode="Bandwidth (MBits/sec)"
    pattern=''
    title=''
    gnuplot_output_filename='result'
    run_gnuplot=False
    global_search=''
    unit=''

    try:
	    opts, args = getopt.getopt(argv[1:],"gho:t:p:u:")
    except getopt.GetoptError:
	 print_help()
         sys.exit(2)

    for opt, arg in opts:
      if opt in ("-p", "--pattern"):
	 pattern=arg
	 pattern=pattern.replace('\\','')
         gnuplot_output_filename=pattern
         # As we do have some regexp in the pattern, let's make this simpliest
         # We do remove the simpliest parts of the expression to get a clear file name
         gnuplot_output_filename=gnuplot_output_filename.replace('-*-','-')
         gnuplot_output_filename=gnuplot_output_filename.replace('*','-')
         gnuplot_output_filename=gnuplot_output_filename.replace('--','-')
         gnuplot_output_filename=gnuplot_output_filename.replace('.output','')
         # Insure that we don't have any starting or trailing dash to the filename
         gnuplot_output_filename = gnuplot_output_filename[:-1] if gnuplot_output_filename.endswith('-') else gnuplot_output_filename
         gnuplot_output_filename = gnuplot_output_filename[1:] if gnuplot_output_filename.startswith('-') else gnuplot_output_filename
      elif opt in ("-t", "--title"):
         title=arg
      elif opt in ("-u", "--unit"):
         unit=arg
      elif opt in ("-g", "--gnuplot"):
	 run_gnuplot=True
      elif opt in ("-h", "--help"):
	  print_help()
	  sys.exit(1)

    fio_data_file=find_file('.',pattern)
    if len(fio_data_file) == 0:
	    print "No log file found with pattern %s!" % pattern
	    sys.exit(1)

    fio_data_file=sorted(fio_data_file, key=str.lower)
    for file in fio_data_file:
	print 'Selected %s' % file

    compute_math(fio_data_file,title,gnuplot_output_filename,mode,unit)

    if (run_gnuplot==True):
   	render_gnuplot()

    # Cleaning temporary files
    try:
	os.remove('gnuplot_temp_file.*')
    except:
	True

#Main
if __name__ == "__main__":
    sys.exit(main(sys.argv))
