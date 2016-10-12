import os
import sys
import tlsh
import argparse
from datetime import datetime

def compute_tlsh(path):
    with open(path, 'rb') as f:
        data = f.read()
        hs = tlsh.hash(data)
    return hs

def walk(walkdir, hashdict):
   for root, subdirs, files in os.walk(walkdir):
      for f in files:
         path = root + "/" + f
         tlshval = compute_tlsh(path)
         if tlshval != '':
            hashdict[tlshval] = path
   return hashdict

def handle_fuzz_walk(dirname, gauge):
   hashdict = dict()
   cache = dict()

   startTime = datetime.now()
   hashdict = walk(dirname, hashdict)

   for k1, v1 in hashdict.iteritems():
      for k2, v2 in hashdict.iteritems():
         if v1 != v2:
            if v1+v2 not in cache and v2+v1 not in cache:
               score = tlsh.diff(k1, k2)
               cache[v1+v2] = 1
               cache[v2+v1] = 2
               if gauge != 0:
                  if score <= int(gauge):
                     sys.stdout.write('"' + str(score) + '","' + v1 + '","' + v2 + '"\n')
               else:
                  sys.stdout.write('"' + str(score) + '","' + v1 + '","' + v2 + '"\n')

   sys.stderr.write(str(datetime.now() - startTime) + "\n")

def main():

   #parse arguments
   parser = argparse.ArgumentParser(description='Compute all TLSH hashes and compare for a given directory.')
   parser.add_argument('--dir', help='Mandatory: Directory to compute and compare hashes for.')
   parser.add_argument('--gauge', help='Optional: Do not output scores higher than this.')

   #reprint args if not long enough...
   if len(sys.argv)==1:
      parser.print_help()
      sys.exit(1)

   #parse arguments into namespace object to reference later in the script
   global args
   args = parser.parse_args()

   if args.gauge == None:
      args.gauge = 0

   if args.dir:
      handle_fuzz_walk(args.dir, args.gauge)      
   else:
      sys.exit(0)

if __name__ == "__main__":
   main()

