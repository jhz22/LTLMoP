import os
import string
import sys
import argparse
import re
import pocketsphinx as ps

#The framework path should be changed to whatever location it is
#on the user's computer
framework = ''
f0 = open(framework, 'r')
frame = f0.readlines()

#These will change depending on the pocketsphinx installation and
#what language model is currently being used.
hmmd = ''
lmd = ''
dictd = ''

parser = argparse.ArgumentParser()
parser.add_argument('SACR')
stuff = parser.parse_args()

f1 = open(stuff.SACR, 'r')
f2 = open('newcorp.txt','w')
mapname = (stuff.SACR).replace(".txt","_map.txt")
f3 = open(mapname,'w')

sensors = []
actuators = []
customs = []
regions = []

specinfo = f1.readlines()

sensors = specinfo[specinfo.index("SENSORS\n")+1:specinfo.index("ACTUATORS\n")]

actuators = specinfo[specinfo.index("ACTUATORS\n")+1:specinfo.index("CUSTOMS\n")]

customs = specinfo[specinfo.index("CUSTOMS\n")+1:specinfo.index("REGIONS\n")]

regions = specinfo[specinfo.index("REGIONS\n")+1:]

psensors = []
pactuators = []
pcustoms = []
pregions = []

for s in sensors:
	s = s.replace("\n","")
	s2 = s.replace("_"," ")
	psensors.append(s2)
	f3.writelines(s2+","+s+"\n")
	
for a in actuators:
        a = a.replace("\n","")
        a2 = a.replace("_"," ")
        pactuators.append(a2)
        f3.writelines(a2+","+a+"\n")
        
for c in customs:
        c = c.replace("\n","")
        c2 = c.replace("_"," ")
        pcustoms.append(c2)
        f3.writelines(c2+","+c+"\n")
        
for r in regions:
	r = r.replace('\n','')
	rdict = {'1':' one','2':' two','3':' three',
		'4':' four','5':' five','6':' six','7':' seven',
		'8':' eight','9':' nine','0':' zero','_':' ','\n':''}
	robj = re.compile('|'.join(rdict.keys()))
	result = robj.sub(lambda m: rdict[m.group(0)], r)
	pregions.append(result)
	f3.writelines(result+","+r+"\n")
        
f3.close()

props_by_placeholder = {"SENSOR": psensors,

                        "ACTUATOR": pactuators,

                        "REGION": pregions,

                        "CUSTOM": pcustoms}

for line in frame:

    placeholders_to_process = re.findall("|".join(props_by_placeholder.keys()), line)

    current = [line.strip() + "\n"] # for some reason I needed to force the type of newline

    for ph in placeholders_to_process: 

        current = [l.replace(ph, prop, 1) for l in current for prop in props_by_placeholder[ph]]

    f2.writelines(current)

f2.close()

getlm = 'lmbasename=`curl --form formtype=simple --form corpus=@newcorp.txt -L http://www.speech.cs.cmu.edu/cgi-bin/tools/lmtool/run | pcregrep -o "http://.*?.tgz" | xargs curl | tar zxvf - 2>&1 | pcregrep -o "\b\d+\b" | uniq`; for f in $lmbasename.*; do mv "$f" "${f/$lmbasename/langmodel}"; done'
os.system(getlm)
os.system('mkdir current_model; mv langmodel.* current_model/')

total = ''
flag = ''
rec = 'rec -t raw -c 1 -e signed-integer -b 16 -L -r 16000 recording.raw silence 0 1 0:00:03 10%'
lmd = 'current_model/langmodel.lm'
speechRec = ps.Decoder(hmm = hmmd, lm = lmd, dict = dictd)
while flag != 'e':	
	os.system(rec)
	fRaw = open('./recording.raw', 'r')
	speechRec.decode_raw(fRaw)
	result = speechRec.get_hyp()
	print '\nAcceptable text?\n' + result[0] + '\n\n'
	flag = raw_input()
	if flag != 'n':
		total = total + "\n" + result[0]
	
print '\n\n\n'
print '******************'
print 'Hypothesis text:\n'

hyp = open('./temp.txt','w')
hyp.writelines(string.lower(total))
hyp.close()

with open(mapname) as inf:
	replace = "sed '"

	line_words = (line.replace(',','/') for line in inf)

	for words in line_words:
		if len(words)>1:
			replace += 's/' + words.strip() + '/gI;'

        replace = replace[:len(replace)-1];
        replace += "' <temp.txt >hypothesis.txt;rm -f temp.txt"

	os.system(replace)

	os.system("cat hypothesis.txt")
	print '\n'

