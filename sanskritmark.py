# This Python file uses the following encoding: utf-8
# Author - Dr. Dhaval patel - drdhaval2785@gmail.com - www.sanskritworld.in
# Written for Sanskrit Hindi translation tool for Nripendra Pathak's Ph.D.
# XML database of verbs taken from sanskrit.inria.fr site of Gerard Huet. For sample, please see SL_roots.xml
# Date - 21 August 2015
# Version - 1.0.0
from lxml import etree
from io import StringIO, BytesIO
import re
import transcoder
import codecs
import datetime

def printtimestamp():
	return datetime.datetime.now()

# Parsing the XMLs.
print "Parsing of XMLs started at", printtimestamp()
roots = etree.parse('SL_roots.xml')
nouns = etree.parse('SL_nouns.xml')
adverbs = etree.parse('SL_adverbs.xml')
final = etree.parse('SL_final.xml')
parts = etree.parse('SL_parts.xml')
pronouns = etree.parse('SL_pronouns.xml')
filelist = [roots, nouns, adverbs, final, parts, pronouns]
#filelist = [parts]
print "Parsing of XMLs completed at", printtimestamp()
#print "Will notify after every 100 words analysed."

# first members of a compound
def firstmemberlist():
	global final
	iic = final.xpath('/forms/f/iic')
	iip = final.xpath('/forms/f/iip')
	iiv = final.xpath('/forms/f/iiv')
	firstmemberlist = [member.getparent().get('form') for member in iic]
	firstmemberlist += [member.getparent().get('form') for member in iip]
	firstmemberlist += [member.getparent().get('form') for member in iiv]
	return firstmemberlist
firstmembers = firstmemberlist()

# second member
def secondmemberlist():
	global nouns, parts
	n = nouns.xpath('/forms/f')
	p = parts.xpath('/forms/f')
	secondmemberlist = [member.get('form') for member in n]
	secondmemberlist += [member.get('form') for member in p]
	return secondmemberlist
secondmembers = secondmemberlist()
#print "Starting analysis at", printtimestamp()
def compoundupasargatrial(inputform):
	global firstmembers, secondmembers
	#print inputform
	sandhidata = [('+A','a+a'),('+A','a+A'),('+A','A+a'),('+A','A+A'),('+I','i+i'),('+I','i+I'),('+I','I+i'),('+I','I+I'),('+U','u+u'),('+U','u+U'),('+U','U+u'),('+U','U+U'),('+F','f+f'),('+e','e+a'),('+e','a+i'),('+e','A+i'),('+e','a+I'),('+e','A+I'),
				  ('+o','o+a'),('+o','a+u'),('+o','A+u'),('+o','a+I'),('+o','A+U'),('+E','a+e'),('+E','A+e'),('+E','a+E'),('+E','A+E'),('+O','a+o'),('+O','A+o'),('+O','a+O'),('+O','A+O'),('+y','i+'),('+y','I+'),('+v','u+'),('+v','U+'),]
	outputlist = [inputform]
	for i in range(1,len(inputform)):
		outputlist.append(inputform[:i]+"+"+inputform[i:])
	outputlist1 = []
	for inputword in outputlist:
		for (mem1, mem2) in sandhidata:
			if mem1 in inputword:
				outputlist1.append(inputword.replace(mem1, mem2))
	outputlist = outputlist + outputlist1
	outputlist = list(set(outputlist))
	out1 = []
	for words in outputlist:
		wordsplit = words.split('+')
		if wordsplit[0] in firstmembers and wordsplit[1] in secondmembers:
			out1.append("+".join(wordsplit))
	print out1
compoundupasargatrial('nIlotpalasya')

# function findwordform searches in the XML file for line which matches the wordform we are interested in. e.g. findwordform("BavAmi","SL_roots.xml") would find all lines of XML file which have word form "Bavati".
def findwordform(inputform):
	#print "importing filelist for findwordform started at", printtimestamp()
	global filelist
	#print "importing filelist for findwordform ended at", printtimestamp()
	outputlist = []
	for file in filelist:
		tree = file
		xpathname = '/forms/f[@form="' + inputform + '"]' # Defined the xpath to search
		#print "xpath parsing for findwordform started at", printtimestamp() # After speed analysis, this function is the most time expensive. It takes around 0.10 sec per word form.
		r = tree.xpath(xpathname) # Created a list 'r' whose members are lines of XML file which correspond to the word form 'inputform'
		#print "xpath parsing for findwordform ended at", printtimestamp()
		for member in r:
			outputlist.append(etree.tostring(member).strip()) # Created a string out of element tree. strip() removes unnecessary white spaces around the string.
	#print "findwordform completed at", printtimestamp()
	if len(outputlist) == 0:
		return "????"
	else:
		return "|".join(outputlist)

# function converttodevanagari is used to translate the short forms used by Gerard Huet to their Sanskrit Devanagari counterpart.
def converttodevanagari(attributeslist):
	# Abbreviations used by Gerard.
	gerardwords = ['nom', 'acc', 'ins', 'dat', 'abl', 'gen', 'loc', 'voc', 'mas', 'fem', 'neu', 'dei', 'sg', 'du', 'pl', 'fst', 'snd', 'trd', 'iic', 'iiv', 'iip', 'avyaya', 'na', 'uf', 'conj']
	# Their counterparts in Sanskrit
	devawords =   ['प्रथमा', 'द्वितीया', 'तृतीया', 'चतुर्थी', 'पञ्चमी', 'षष्ठी', 'सप्तमी', 'संबोधन', 'पुंल्लिङ्ग', 'स्त्रीलिङ्ग', 'नपुंसकलिङ्ग', 'सङ्ख्या', 'एकवचन', 'द्विवचन', 'बहुवचन', 'प्रथमपुरुष', 'मध्यमपुरुष', 'उत्तमपुरुष', 'समासपूर्वपद', 'सहायकधातुपूर्व', 'कृदन्तपूर्वपद', 'अव्यय', '', 'अव्यय', '']
	outputlist = [] # initiated a blank list.
	for member in attributeslist:
		alist = [] # initiated a blank list.
		for mem1 in member:
			alist.append(devawords[gerardwords.index(mem1)]) # appended the Devanagari words for Gerard's abbreviations.
		outputlist.append(alist) # appended alist to outputlist
	return outputlist # returned outputlist which has everything converted to Sanskrit in Devanagari.

# function iter is to iterate over the XML file and get following from a given word form - Base root and attributes
# Default strength is "Full". "deva" converts the output to Devanagari, which is not advisable to use for any other use than testing. 
def iter(wordxml, strength="Full"):
	if wordxml == "????":
		return "????"
	else:
		wordxml = unicode(wordxml) # Converted the word to unicode
		wordwithtags = [] # Empty list
		individualentries = wordxml.split('|')
		for individualentry in individualentries:
			tree = StringIO(individualentry) # Created XML from the worddata
			#print "parsing of iter started at", printtimestamp()
			context = etree.parse(tree) # Parsed the element tree.
			#print "parsing of iter ended at", printtimestamp()
			root = context.getroot() # got the root of element tree e.g. 'f'
			# The next two steps require explanation. In Gerard's XML files, All possible attributes are given as children of 'f'. The last child is always 's' which stores the stem. All other children are the various possible word attributes. Given as 'na' or 'v' etc. Gio
			children = root.getchildren()[:-1] # attributes
			basedata = root.getchildren()[-1] # 's' stem
			basewordslp = basedata.get('stem').strip() # Base word in SLP1 encoding.
			if strength == "deva":
				baseword = transcoder.transcoder_processString(basewordslp,'slp1','deva') # If the user wants output in Devanagari rather than SLP1, this code converts it to Devanagari.
			else:
				baseword = basewordslp # Otherwise in SLP1.
			attributes = [] # An empty list to store attributes.
			for child in children:
				taglist = child.xpath('.//*') # Fetches all elements (abbreviations) of a particular verb / word characteristics.
				output = [child.tag] # The first member of output list is the tag of element 'v', 'na' etc.
				output = output + [ tagitem.tag for tagitem in taglist] # Other tags (abbreviations) and add it to output list.
				# The following section is commented out right now. But it would be needed for situation where we need to konw the gaNa of a verb or 7 kinds of aorist derivation.
				"""if len(child.xpath('.//prs[@gn]')) > 0:
					prsgana = child.xpath('.//prs')[0].get('gn')
					output.append('verbgana')
					output.append(prsgana)
				elif len(child.xpath('.//aor[@gn]')) > 0:
					aorgana = child.xpath('.//aor')[0].get('gn')
					output.append('aoristgana')
					output.append(aorgana)
				elif len(child.xpath('.//inj[@gn]')) > 0:
					injgana = child.xpath('.//inj')[0].get('gn')
					output.append('injunctivegana')
					output.append(injgana)"""
				attributes.append(output) # output list is appended to attributes list.
			if (strength == "deva"):
				outputlist = converttodevanagari(attributes) # Devanagari
			else:
				outputlist = attributes # SLP1
			for member in outputlist:
				wordwithtags.append(baseword + "-" + "-".join(member) ) # Created a list wordwithtags where the first member is baseword and the rest of the members are attributes separated by '-'
		#print "postprocessing of iter ended at", printtimestamp()
		return "|".join(wordwithtags) # If there are more than one possible verb characteristics for a given form, they are shown separated by a '|'

# function analyser analyses all the XML files and gets matching details from all XMLs e.g. 'Bavati' may be a verb form, but it can also be a noun form of 'Bavat' locative singular. Therefore it is needed to traverse all XML files.
def analyser(word, strength="Full"):
	return iter(findwordform(word), strength)

# Functions findrootword and generator are for generating the word form from given attributes and root.
# The approach 
def findrootword(checkedrootword):
	listing = []
	filelist = ['SL_roots.xml', 'SL_nouns.xml', 'SL_adverbs.xml', 'SL_final.xml', 'SL_parts.xml', 'SL_pronouns.xml']
	for datafile in filelist:
		tree = etree.parse(datafile)
		entries = tree.xpath('.//f')
		for entry in entries:
			parts = entry.getchildren()
			s = parts[-1] # Fetched tag 's' till this section.
			if s.get('stem') == checkedrootword: # If the stem is the same as checkedrootword
				children = parts[:-1] # Removed the last because it has only stem data.
				for child in children:
					taglist = child.xpath('.//*')
					output = [ child.tag ] + [ tagitem.tag for tagitem in taglist]
					if output[-1] in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'] and output[-2] in ['verbgana', 'aoristgana', 'injunctivegana']: # Remove the last two data, because they are not part of Gerard's scheme.
						output = output[:-2] 
					output += [ entry.get('form') ] # Added the entered word form at the last.
					listing.append(output) # Added output to listing list
	return listing # Return listing list.

def generator(analysedword, translit="slp1"):
	analysedword = unicode(analysedword) # unicode
	data = re.split('|',analysedword) # There may be cases where the data may have been analysed by our analyser. They would be separated by '|'.
	for datum in data:
		separate = re.split('-', datum) # split the whole string by '-'
		rootword = separate[0] # Base word
		taglist = separate[1:] # attributes
		if taglist[-1] in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'] and taglist[-2] in ['verbgana', 'aoristgana', 'injunctivegana']:
			taglist = taglist[:-2] # Removed artificially added attributes
		datahavingroot = findrootword(rootword) # Created a list of possible items
		outlist = []
		for rootdatum in datahavingroot:
			if set(taglist) < set(rootdatum): # If the tags supplied are a subset of the data from XML file,
				outlist.append(rootdatum[-1]) # Add the word form to outlist
		if translit == "deva":
			return transcoder.transcoder_processString("|".join(outlist),'slp1','deva') # Devanagari
		else:
			return "|".join(outlist) # SLP1

#print generator('Davala-sg-mas-abl', 'deva')

# devangaridisplay and translator functions are created for Nripendra Pathak, so that he may provide necessary data for extending the code.
# function devanagaridisplay will show the attribute list from XML files in a format which a traditional Sanskrit scholar may understand easily.
def devanagaridisplay(word):
	if len(word) > 1:
		if word[-1] == 'H':
			word = word[:-1]+"s" # A word ending with a visarga are converted to sakArAnta, because this is how Gerard has stored his data.
		elif word[-1] == 'M':
			word = word[:-1]+"m"
	# If there are tags which are not enumerated here, they can be added as and when there is a need.
	database = [('v-cj-prim', 'प्राथमिक'),
				('v-cj-ca', 'णिजन्त'),
				('v-cj-int', 'यङन्त'),
				('v-cj-des', 'सन्नन्त'),
				('sys-prs-md-pr', 'लट्'),
				('sys-prs-md-ip', 'लोट्'),
				('sys-prs-md-op', 'विधिलिङ्'),
				('sys-prs-md-im', 'लङ्'),
				('sys-pas-md-pr', 'लट्-कर्मणि'),
				('sys-pas-md-ip', 'लोट्-कर्मणि'),
				('sys-pas-md-op', 'विधिलिङ्-कर्मणि'),
				('sys-pas-md-im', 'लङ्-कर्मणि'),
				('sys-tp-fut', 'लृट्'),
				('sys-tp-prf', 'लिट्'),
				('sys-tp-aor', 'लुङ्'),
				('sys-tp-inj', 'आगमाभावयुक्तलुङ्'),
				('sys-tp-cnd', 'लृङ्'),
				('sys-tp-ben', 'आशीर्लिङ्'),
				('sys-pef', 'लुट्'),
				('np-sg', 'एकवचन'),
				('np-du', 'द्विवचन'),
				('np-pl', 'बहुवचन'),
				('fst', 'उत्तमपुरुष'),
				('snd', 'मध्यमपुरुष'),
				('trd', 'प्रथमपुरुष'),
				('na-nom', 'प्रथमा'),
				('na-voc', 'संबोधन'),
				('na-acc', 'द्वितीया'),
				('na-ins', 'तृतीया'),
				('na-dat', 'चतुर्थी'),
				('na-abl', 'पञ्चमी'),
				('na-gen', 'षष्ठी'),
				('na-loc', 'सप्तमी'),
				('sg', 'एकवचन'),
				('du', 'द्विवचन'),
				('pl', 'बहुवचन'),
				('mas', 'पुंल्लिङ्ग'),
				('fem', 'स्त्रीलिङ्ग'),
				('neu', 'नपुंसकलिङ्ग'),
				('dei', 'सङ्ख्या'),
				('uf', 'अव्यय'),
				('ind', 'क्रियाविशेषण'),
				('interj', 'उद्गार'),
				('parti', 'निपात'),
				('prep', 'चादि'),
				('conj', 'संयोजक'),
				('tasil', 'तसिल्'),
				('vu-cj-prim', 'अव्ययधातुरूप-प्राथमिक'),
				('vu-cj-ca', 'अव्ययधातुरूप-णिजन्त'),
				('vu-cj-int', 'अव्ययधातुरूप-यङन्त'),
				('vu-cj-des', 'अव्ययधातुरूप-सन्नन्त'),
				('iv-inf','तुमुन्'),
				('iv-abs','क्त्वा'),
				('iv-per','per'),
				('ab-cj-prim', 'क्त्वा-प्राथमिक'),
				('ab-cj-ca', 'क्त्वा-णिजन्त'),
				('ab-cj-int', 'क्त्वा-यङन्त'),
				('ab-cj-des', 'क्त्वा-सन्नन्त'),
				('kr-cj-prim-no', 'प्राथमिक'),
				('kr-cj-ca-no', 'णिजन्त'),
				('kr-cj-int-no', 'यङन्त'),
				('kr-cj-des-no', 'सन्नन्त'),
				('kr-vb-no', ''),
				('ppp', 'कर्मणिभूतकृदन्त'),
				('ppa', 'कर्तरिभूतकृदन्त'),
				('pprp', 'कर्मणिवर्तमानकृदन्त'),
				('ppr-para', 'कर्तरिवर्तमानकृदन्त-परस्मै'),
				('ppr-atma', 'कर्तरिवर्तमानकृदन्त-आत्मने'),
				('ppft-para', 'पूर्णभूतकृदन्त-परस्मै'),
				('ppft-atma', 'पूर्णभूतकृदन्त-आत्मने'),
				('pfutp', 'कर्मणिभविष्यत्कृदन्त'),
				('pfut-para', 'कर्तरिभविष्यत्कृदन्त-परस्मै'),
				('pfut-atma', 'कर्तरिभविष्यत्कृदन्त-आत्मने'),
				('gya', 'य'),
				('iya', 'ईय'),
				('tav', 'तव्य'),
				('para', 'कर्तरि'),
				('atma', 'कर्तरि'),
				('pass', 'कर्मणि'),
				('pa', 'कृदन्त'),
				('iic', 'समासपूर्वपदनामपद'),
				('iip', 'समासपूर्वपदकृदन्त'),
				('iiv', 'समासपूर्वपदधातु'),
				]
	#print "analysis of word started", printtimestamp()
	datafetched = analyser(word)
	#print "analysis of word ended", printtimestamp()
	if datafetched == "????":
		return "????"
	else:
		individual = datafetched.split("|")
		outputlist = []
		for ind in individual:
			split = ind.split('-')
			root = split[0].decode('utf-8')
			#root = root.split('#')[0]
			root = transcoder.transcoder_processString(root, "slp1", "deva")
			output = "-".join(split[1:])
			output = output.decode('utf-8')
			for member in database:
				output = re.sub(member[0], member[1].decode('utf-8'), output) # Changed attributes strings with their Sanskrit Devanagari counterparts.
			output = transcoder.transcoder_processString(output, "slp1", "deva") # This code creates some issue in windows setting. Therefore not converting to Devanagari right now. Will do that later.
			outputlist.append(root + "-" + output)
		#print "Postprocessing of word ended", printtimestamp()
		return "|".join(outputlist)


#print devanagaridisplay("aMSakatas")

def convertfromfile(inputfile,outputfile):
	f = codecs.open(inputfile, 'r', 'utf-8')
	data = f.readlines()
	f.close()
	g = codecs.open(outputfile, 'w', 'utf-8')
	for datum1 in data:
		datum1 = datum1.strip()
		datum1 = transcoder.transcoder_processString(datum1, "deva", "slp1")
		dat = re.split('(\W+)',datum1)
		for i in xrange(len(dat)):
			datum = dat[i].strip()
			if i % 2 == 0 and i != len(dat):
				#print "analysis of word started", printtimestamp()
				x = devanagaridisplay(datum)
				#print "analysis of word ended", printtimestamp()
				g.write(transcoder.transcoder_processString(datum, "slp1", "deva")+"("+x+")")
				print transcoder.transcoder_processString(datum, "slp1", "deva")+"("+x+")",
				#print "wrote to the file", printtimestamp()
			else:
				g.write(transcoder.transcoder_processString(dat[i], "slp1", "deva"))
				print transcoder.transcoder_processString(dat[i], "slp1", "deva"),
		g.write('\n')
		print
	g.close()
	
#convertfromfile('sanskritinput.txt','hindioutput.txt')
