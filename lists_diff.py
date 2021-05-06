#!/usr/bin/python3

import sys
import os.path
import getopt

def usage(prg_name, code):
	print("Usage: ", prg_name, "-b <base file> -n <new_file> [-o <out_dir>]")
	return code
	

if len (sys.argv) < 3:
	sys.exit(usage(sys.argv[0], 1))


out_dir = "."
base_file = ""
new_file = ""
short_options = "b:n:o:"


try:
	arguments, values = getopt.getopt(sys.argv[1:], short_options)
except getopt.error as err:
    # Output error, and return with an error code
    print (str(err))
    sys.exit(usage(sys.argv[0], 2))


for arg, value in arguments:
	if arg == "-b":
		base_file = value
	elif arg == "-n":
		new_file = value
	elif arg == "-o":
		out_dir = value

if not base_file:
	print("Error: base file is not specified")
	sys.exit(usage(sys.argv[0], 3))


if not new_file:
	print("Error: new file is not specified")
	sys.exit(usage(sys.argv[0], 3))


base_file_ar = []
with open(base_file, "r") as bfh:
	for line in bfh:
		if not line.startswith('#'):
			base_file_ar.append(line.strip())
#			print(line.strip())


new_file_ar = []
with open(new_file, "r") as nfh:
	for line in nfh:
		if not line.startswith('#'):
			new_file_ar.append(line.strip())
#			print(line.strip())


new_channels = set(new_file_ar) - set(base_file_ar)
deleted_channels = set(base_file_ar) - set(new_file_ar)

print("New channels: ", len(new_channels))
#for chan in sorted(new_channels):
#	print(chan)

print("Deleted channels: ", len(deleted_channels))
#for chan in sorted(deleted_channels):
#	print(chan)


path_items = os.path.split(base_file)

file_name, ext = os.path.splitext(path_items[1])

new_list_file_name = file_name + "_new" + ext
if path_items[0]:
	new_list_file_name = path_items[0] + "/" + new_list_file_name

if out_dir:
	new_list_file_name = out_dir + "/" + new_list_file_name

with open(new_list_file_name, "w") as outfile:
	outfile.write("\n".join(sorted(new_channels)))

#print(new_list_file_name)

del_list_file_name = file_name + "_deleted" + ext
if path_items[0]:
	del_list_file_name = path_items[0] + "/" + del_list_file_name

if out_dir:
	del_list_file_name = out_dir + "/" + del_list_file_name

with open(del_list_file_name, "w") as outfile:
	outfile.write("\n".join(sorted(deleted_channels)))



