#!/usr/bin/env python
# coding: utf-8

# In[1]:


import time
import urllib.request
from urllib.request import urlopen
from optparse import OptionParser
import requests, zipfile, io
import gzip
import io
import re
import getopt
import sys
import os


little = -1

urlGo = ''#'http://current.geneontology.org/annotations/goa_human.gaf.gz'
#urlGo = 'http://ftp.ebi.ac.uk/pub/databases/GO/goa/HUMAN/goa_human.gaf.gz'
#urlHpo = 'http://compbio.charite.de/jenkins/job/hpo.annotations/lastBuild/artifact/util/annotation/genes_to_phenotype.txt'
#urlHpo = 'http://compbio.charite.de/jenkins/job/hpo.annotations.monthly/lastSuccessfulBuild/artifact/annotation/ALL_SOURCES_ALL_FREQUENCIES_genes_to_phenotype.txt'
urlHpo = ''#'https://ci.monarchinitiative.org/view/hpo/job/hpo.annotations/lastSuccessfulBuild/artifact/rare-diseases/util/annotation/genes_to_phenotype.txt'

pathAnnovar = ''

try:
    #opts, args = getopt.getopt(sys.argv[1:],"h:i:o",['ifile','ofile'])
	#opts, args = getopt.getopt(sys.argv,'i:o:',['ifile','ofile'])
	opts, args = getopt.getopt(sys.argv,'g:h:',['go','hpo'])
	counter = 0
	for arg in args:
		if arg in ("-g", "--go"):
			urlGo = args[counter+1]
		elif arg in ("-h", "--hpo"):
			urlHpo = args[counter+1]
		elif arg in ("-d", "--vcfInputFileName"):
			pathAnnovar = args[counter+1]
		counter = counter+1
        #elif opt in ("-s", "--short"):
            #little = arg
except getopt.GetoptError:
	print ('some mistake')
	sys.exit(2)

if (pathAnnovar == ''):
	pathAnnovar = input('Please insert path for Annovar input file:')


isExist = os.path.isfile(pathAnnovar)
if (isExist == False):
	print('Annovar input data is not valid. . .')
	sys.exit(1)


outputAnnovar = pathAnnovar[pathAnnovar.rfind("/")+1:pathAnnovar.rfind(".vcf")]
outputName = outputAnnovar + ".hg19_multianno"
print('Preparing ontology files. . . ')

filenameGO = "goa_human.gaf.gz"
if urlGo != '':
	try:
		urllib.request.urlretrieve(urlHpo, os.getcwd() + '\\' + filenameGO)
		print ('GO file has been downloaded')
	except:
		print("Couldn\'t download file, local file will be used")

filenameHpo = 'genes_to_phenotype.txt'
if urlHpo != '':
	try:
		urllib.request.urlretrieve(urlHpo, os.getcwd() + '\\' + filenameHpo)
		print ('HPO file has been downloaded')
	except:
		print("Couldn\'t download file, local file will be used")

print ('Ontology files have been prepared')

output = open("output.txt", "r+")

start = time.time()

from urllib.request import urlopen
import json

def extractGOInfo(go):
    urlGo = 'https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/' + str(go) + '/complete'
    data = urlopen(urlGo).read()#.decode('utf-8')
    json_data = json.loads(data)
    return json_data["results"][0]['name'] + '|' + json_data["results"][0]['definition']['text']


from urllib.request import urlopen
import json

def extractHPOInfo(hpo):
    urlHpo = 'https://hpo.jax.org/api/hpo/term/' + str(hpo) #HP:0002123'
    data = urlopen(urlHpo).read().decode('utf-8')
    json_data = json.loads(data)
    #json_data["details"]['name'] + '|' + 
    return json_data["details"]['definition']

from urllib.request import urlopen
import json
import urllib.request


def checkConnection(url):
    try:
        urllib.request.urlopen(url)
        return True
    except:
        return False

def extractGeneInfo(geneId):
    
    urlGene = 'https://www.uniprot.org/uniprot/' + str(geneId) + '.txt'#'O14764' #geneId
    
    if checkConnection(urlGene):
        data = urlopen(urlGene).read().decode('utf-8')
        #json_data = json.loads(data)
        
        #print (data)
        geneDescriptionStart = data.find("RecName: Full") + len("RecName: Full") + 1
        geneDescriptionEnd = data.find(";", geneDescriptionStart)
        geneDes = data[geneDescriptionStart:geneDescriptionEnd]
        
        return geneDes
    
    return geneId


def getGOVersion(filename):
    
    version = ""
    
    with gzip.open(filename, 'rb') as goaHuman:
        for line in goaHuman:
            line = line.decode()
            position = line.find("!date-")

            if position == -1:
                continue
            else:
                version = line[17:27]
                break
    return version


#parse goa_human.gaf file with GO info
import time
import re
def getGOdata(filename, outputName):
	print ('------Getting Gene and GO Data-------')
	#start = time.time()
	geneGO = {}
	goTooltips = {}
	geneInfo = {}
	geneTooltipsProcessed = []
	goTooltipsProcessed = []
    
	#print ('Start collecting current genes')
	with open("Output Gene.txt", "r+") as outputGenesRead:
		for line in outputGenesRead:
			if line.find("->") != -1:
				line = line.replace("->", "-&gt;")
			delimiter = line.find("|")
			geneOutput = line[:delimiter-1]
			if geneOutput not in geneInfo :
				geneInfo[geneOutput] = line[delimiter+2:-1]
		#print('End collecting current genes -> ' + str(len(geneInfo)))
	
	#print ('Start collecting current GO function')
	with open("Output GO-Data.txt", "r") as outputGOsRead:
		for line in outputGOsRead:
			goOutput = line[:10].strip()
			
			if goOutput not in goTooltips:
				goTooltips[goOutput] = line[13:-1]#13+goEnd]
        #print('End collecting current GO functions -> ' + str(len(goTooltips)))

	print('---------Gene and GO Data processing---------')
	with gzip.open(filename, 'rb') as goaHuman, open("Output GO-Data.txt", "a+") as outputGOsRead, open("Output Gene.txt", "a+") as outputGenesRead, open("GeneJSMap.js", "w+") as geneJS, open("GOtooltipJS.js", "a+") as goTooltipJS:
		geneJS.write("const geneMap = new Map();\n")
		goTooltipJS.write("const goMap = new Map();\n")
        
		for line in goaHuman:
			line = line.decode()
			if line.find("GO:") == -1:
				continue
			info = re.split(' |\t', line)
			gene = info[2]
			function = "f"
			geneId = info[1]
			go = info[4].strip()

			if go.find("GO") != -1:
				function = ''
				if go in goTooltips:
					function = goTooltips[go]
				else:
					print(go + " - " + function)
					function = extractGOInfo(go)
					goTooltips[go] = function
					outputGOsRead.write(go + ' | ' + function + '\n')

				if gene in geneGO:
					current = [currentGeneInfo[0] for currentGeneInfo in geneGO[gene]]
					if go not in current:
						geneGO[gene].append((go, function, geneId))
                    #geneGO[gene].append((go, functionWhole))
				else:
					geneGO[gene] = [(go, function, geneId)]
                    
				if geneId not in geneInfo:
					geneDescription = extractGeneInfo(geneId)
					geneInfo[geneId] = geneDescription
					outputGenesRead.write(geneId + ' | ' + geneDescription + '\n')

				if gene not in geneTooltipsProcessed:
					geneTooltipsProcessed.append(gene)
					geneJS.write("geneMap.set(\""+ gene + "\",\"" + geneInfo[geneId] + "\");\n" )

				if go not in goTooltipsProcessed:
					goTooltipsProcessed.append(go)
					goTooltipJS.write("goMap.set(\""+ go + "\",\"" + function + "\");\n" )

    #print ("goa_human.gaf data: " + str(len(geneGO.keys())))
    #print ("Gene information: " + str(len(geneInfo.keys())))
	print('--------Gene and GO Data have been collected---------')
    #end = time.time() - start
    #print (str (round(end, 2)))
	return geneGO, geneInfo


#parse file with HPO info
def getHPOdata(filename):
    #phenotypes
    print ('---------HPO Data processing---------')
    geneHpo = {}
    hpoTooltips = {}
    hpoGeneId = {}
    counter = 0
    counter1 = 0
    counter2 = 0
    hpoProcessed = []

    #print('Start collecting current HPO phenotypes')
    with open("Output HPO-Data.txt", "r+") as outputHPOsRead:
        for line in outputHPOsRead:
            hpoOutput = line[:10].strip()
            #hpoEnd = line[13:].find("|")
            if hpoOutput not in hpoTooltips:
                hpoTooltips[hpoOutput] = line[13:-1].replace("\"","")#13+hpoEnd]
        #print('End collecting current HPO phenotypes -> ' + str(len(hpoTooltips)))
    
    with open(filename, "r") as allHpo, open("Output HPO-Data.txt", "a+") as outputHPOsRead, open("HPOtooltipJS.js", "a+") as hpoJS:
        hpoJS.write("const hpoMap = new Map();\n")
        for line in allHpo:

            if line.find("HP:") == -1:
                continue
            info = re.split(' |\t', line)
            #print (info)
            gene = info[1]
            hpo = info[2]
            geneIdHPO = info[0]
            
            phenotype = "p"#extractHPOInfo(hpo)
            if hpo in hpoTooltips:
                phenotype = hpoTooltips[hpo]
            else:
                phenotype = info[3] + ' |' + extractHPOInfo(hpo)
                hpoTooltips[hpo] = phenotype
                #print('made now')
                outputHPOsRead.write(hpo + ' | ' + phenotype + '\n')
            
            if gene in geneHpo:
                currentHpo = [currentGeneInfoH[0] for currentGeneInfoH in geneHpo[gene]]
                if hpo not in currentHpo:
                    geneHpo[gene].append((hpo, phenotype))
            else:
                geneHpo[gene] = [(hpo, phenotype)]
                
            if gene not in hpoGeneId:
                hpoGeneId[gene] = geneIdHPO

            if hpo not in hpoProcessed:
                hpoProcessed.append(hpo)
                hpoJS.write("hpoMap.set(\""+ hpo + "\",\"" + phenotype + "\");\n")

    print('---------HPO Data has been collected-----------')
    return geneHpo, hpoGeneId


#parse info from annotation file
def getVariationsData(fileName):
    
    print ("---------Variations data processing---------")
    variations = {}
    allExonicGenes = ''
    geneInfo = {}

    #annovarGenes = open("annovarGenes.txt", "w+")
    count = 0
    
    with open(fileName, 'r') as varFile:
        for line in varFile:
            pos = line.find("\texonic")
            if pos != -1:
                pos = pos + 1
                
                info = re.split('\t', line)
                currentGene = info[6]
                begin = -1
                chro = info[0]
                startVar = info[1]
                endVar = info[2]
                ref = info[3]
                alt = info[4]
                exonicFunc = info[8]
                if currentGene in variations:
                    variations[currentGene].append((startVar, endVar, ref, alt, exonicFunc, chro))#, geneDetail, exonicFunc))
                else:
                    variations[currentGene] = [(startVar, endVar, ref, alt, exonicFunc, chro)] #geneDetail, exonicFunc)]

    #annovarGenes.write(" ".join(str(g) for g in variations.keys()))
    print("---------Variations data has been collected--------- " + str(len(variations.keys())))
    return variations



def createOutput(fileName, outputName, goFile = "goa_human.gaf.gz", hpoFile = "genes_to_phenotype.txt"):
    
	geneGO, genes = getGOdata(goFile, outputName)
	geneHpo, genesHPO = getHPOdata(hpoFile)
	variations = getVariationsData(fileName + ".txt")
	#print ("Variations: " + str(len(variations.keys())))
    
	outputGenes = []
	outputGos = []
	outputHpos = []
	counterGo = 0
	counterHpo = 0
	counterGene = 0
    
	outputFileName = fileName[:fileName.find('.')] + ".html"
	outputHtml = open(outputFileName, "w+")
    
	outputHtml.write("<!DOCTYPE html>\n")
	outputHtml.write("<html><body><head>")
	outputHtml.write("<script src=\"https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js\"></script>")
    
    #datatable
	outputHtml.write("<script type=\"text/javascript\" charset=\"utf8\" src=\"https://cdn.datatables.net/1.10.20/js/jquery.dataTables.js\"></script>\n")
	outputHtml.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"https://cdn.datatables.net/1.10.20/css/jquery.dataTables.css\">\n")
    
    #checkbox
	outputHtml.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"https://cdn.datatables.net/select/1.3.1/css/select.dataTables.min.css\">")
	outputHtml.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"https://cdn.datatables.net/buttons/1.7.0/css/buttons.dataTables.min.css\">")
	outputHtml.write("<script type=\"text/javascript\" charset=\"utf8\" src=\"https://cdn.datatables.net/select/1.3.1/js/dataTables.select.min.js\"></script>")
    
	outputHtml.write("<script type=\"text/javascript\" charset=\"utf8\" src=\"https://cdn.datatables.net/buttons/1.7.0/js/dataTables.buttons.min.js\"></script>")
	outputHtml.write("<script type=\"text/javascript\" charset=\"utf8\" src=\js/buttons.flash.min.js\"></script>")
	outputHtml.write("<script type=\"text/javascript\" charset=\"utf8\" src=\js/buttons.html5.min.js\"></script>")
	outputHtml.write("<script type=\"text/javascript\" charset=\"utf8\" src=\"https://cdnjs.cloudflare.com/ajax/libs/jszip/2.5.0/jszip.min.js\"></script>")
	outputHtml.write("<script type=\"text/javascript\" charset=\"utf8\" src=\"js/input.js\"></script>")
	#outputHtml.write("<script type=\"text/javascript\" charset=\"utf8\" src=\"https://cdn.rawgit.com/bpampuch/pdfmake/0.1.18/build/pdfmake.min.js\"></script>")
	#outputHtml.write("<script type=\"text/javascript\" charset=\"utf8\" src=\"https://cdn.rawgit.com/bpampuch/pdfmake/0.1.18/build/vfs_fonts.js\"></script>")
  
    #include tippy for tooltip
	#outputHtml.write("<script src=\"https://unpkg.com/@popperjs/core@2/dist/umd/popper.min.js\"></script>")
	#outputHtml.write("<script src=\"https://unpkg.com/tippy.js@6/dist/tippy-bundle.umd.js\"></script>")

	outputHtml.write("<link rel=\"stylesheet\" href=\"cssFile.css\">")
	outputHtml.write("<script src='scriptFile.js'></script></head>")
	outputHtml.write("")
	outputHtml.write("<div style=\"text-align:center\"><span id=\"headingTop\" style=\"font-size:26px;\">Function and phenotype terms associated with human exonic variations</span><br />")
	outputHtml.write("<span id = \"goHpoVersion\" style=\"font-size:18px\">GO version: " + getGOVersion(goFile) +". <br /> HPO version: #1271 Mar 27, 2020</span></div>")
	outputHtml.write("<div id=\"firstXrows\"><label for=\"numberOfRows\">Select first</label> <input type=\"number\" id=\"rowsNumber\" name=\"numberOfRows\" style=\"width:50px\" min = 1> rows</div>")
   
	outputHtml.write("<div id=\"showXYfunctions\">Show  <select id=\"showXFunctions\"><option value=\"10\">10</option><option value=\"20\">20</option><option value=\"30\">30</option><option value=\"all\">all</option></select>functions</div>")
	outputHtml.write("<div class=\"dataTables_length\"></div>")
	outputHtml.write("<table id=\"annotationTable\" class=\"display cell-border\" style=\"text-align:center\">")
	outputHtml.write("<thead><tr>")
	outputHtml.write("<th>Chr</th><th>Start</th><th>End</th><th>Ref</th><th>Alt</th><th>Exonic function</th><th>Gene</th><th>GO associations</th><th>HPO annotations</th><th>All GO</th><th>All HPO</th></tr></thead><tbody>")
    
	startURL = "<a href=\"https://www.ebi.ac.uk/QuickGO/term/"
	startURLhpo = "<a href=\"https://hpo.jax.org/app/browse/term/"
	aTagOpen = "<a"
	aTagClosed = "</a>"

	counterExonic = 0
	counterNrnaExonic = 0
	counterNo = 0
	counter = 0
	allExonicGenes = ""
    #list of all gene IDs for Uniprot convert
    
	for currentGene in variations:
		if allExonicGenes.find(currentGene) == -1 and currentGene in variations:
            #goNo, hpoNo, ncRna = False
            
			if currentGene not in outputGenes:
				outputGenes.append(currentGene)
                                
			allExonicGenes = allExonicGenes + currentGene
            
			for j in range (0, len(variations[currentGene])):
				outputHtml.write("<tr><td>") #first column for checkbox or not
				val = -1                                   

                #column chr
				outputHtml.write(variations[currentGene][j][5] + "</td><td>")
                
                #columns start, end, ref, alt
				for i in range(0, 5):
					outputHtml.write(variations[currentGene][j][i] + "</td><td>")
                
                #no tooltip
				outputHtml.write("<span class=\"g\">" + currentGene + "</span></td><td>")

                #column gene

				allGoColumn = "</td><td><img src=\"go-icon.png\"></td>"
				allHpoColumn = "<td><img src=\"hpo-icon.png\"></td></tr>\n"
                
				if currentGene in geneGO:
					values = geneGO[currentGene]
                    #for g in values:
                        #if g not in outputGos:
                            #outputGos.append(g)
                            
					currentGeneGo = len(values)
                   
					if currentGeneGo > 10:
                        
                        #no tooltip
						outputHtml.write(" ".join(str(startURL + e[0] + "\" target=\"_blank\">" + e[0] + "<br/>" + aTagClosed) for e in values[:10]) + "") #GO
						outputHtml.write(" ".join(str(startURL + e[0] + "\" target=\"_blank\" style=\"display:none\">" + e[0] + "<br/>" +aTagClosed)  for e in values[10:]) + "") #GO
                        
					elif currentGeneGo >= 1:
                        
                        #no tooltip
						outputHtml.write(" ".join(str(startURL + e[0] + "\" target=\"_blank\">" + e[0] + "<br/> " + aTagClosed) for e in values[:9]) + " ") #GO
                        
					geneId = str(values[0][2])
					geneIdHpo = genesHPO[currentGene] if currentGene in genesHPO else ""
					allGoColumn = "</td><td><a href=\"https://www.ebi.ac.uk/QuickGO/annotations?geneProductId=" + geneId + "\" target=\"_blank\"><img src=\"go-icon.png\"></a></td>"
										
				#else:
					#noGo.write(" " + currentGene)
                            
				outputHtml.write("</td><td>")

				if currentGene in geneHpo:
					values = geneHpo[currentGene]
                    #for v in values:
                        #if v not in outputHpos:
                            #outputHpos.append(v)
                                    
					currentGeneHpo = len(values)
                    #counterHpo = counterHpo + currentGeneHpo
					if currentGeneHpo > 10:
                        #outputHtml.write(" ".join(str(startURLhpo + e[0] + "\" data-tippy-content=\""+ e[1] + "\" target=\"_blank\">" + e[0] + "<br/>" + aTagClosed)  for e in geneHpo[currentGene][:10]))# + " ")
                        #outputHtml.write(" ".join(str(startURLhpo + e[0] + "\" data-tippy-content=\""+ e[1] + "\" target=\"_blank\" style=\"display:none\" class=\"noshow\">" + e[0] + "<br/> " +aTagClosed)  for e in geneHpo[currentGene][10:]) + " ") #GO
                        #outputHtml.write(" ".join(str(startURLhpo + e +"\" target=\"_blank\" style=\"display:none\">" + e + "<br /> " +aTagClosed) for e in geneHpo[currentGene][5:]))
                        
                        #no tooltip
						outputHtml.write(" ".join(str(startURLhpo + e[0] + "\" target=\"_blank\">" + e[0] + "<br/>" + aTagClosed)  for e in geneHpo[currentGene][:10]))# + " ")
						outputHtml.write(" ".join(str(startURLhpo + e[0] + "\" target=\"_blank\" style=\"display:none\" class=\"noshow\">" + e[0] + "<br/> " +aTagClosed)  for e in geneHpo[currentGene][10:]) + " ") #GO
                    
					elif currentGeneHpo >=1:
                        #outputHtml.write(" <br/>".join(str(startURLhpo + e[0] + "\" data-tippy-content=\"" + e[1] + "\" target=\"_blank\">" + e[0] + aTagClosed)  for e in geneHpo[currentGene]) + " ") #GO
                        
                        #no tooltip
						outputHtml.write(" <br/>".join(str(startURLhpo + e[0] + "\" target=\"_blank\">" + e[0] + aTagClosed)  for e in geneHpo[currentGene]) + " ") #GO
                        
                #outputHtml.write("</td><td><a href=\"https://www.ebi.ac.uk/QuickGO/annotations?geneProductId=" + geneGO[currentGene][0][2] if currentGene in geneGO else "" + "\" target=\"_blank\"><img src=\"go-icon.png\" style=\"width:50px; height:50px\"></a></td><td><a href=\"https://hpo.jax.org/app/browse/gene/"+  +"\" target=\"_blank\"><img src=\"hpo-icon.png\" style=\"width:50px; height:50px\"></a></td></tr>\n")
					allHpoColumn = "<td><a href=\"https://hpo.jax.org/app/browse/gene/"+ geneIdHpo + "\" target=\"_blank\"><img src=\"hpo-icon.png\"></a></td></tr>\n"
				
				outputHtml.write(allGoColumn)
				outputHtml.write(allHpoColumn)
                #counter = counter + 1
	endOfTable = "<tfoot><tr><th>Chr</th><th>Start</th><th>End</th><th>Ref</th><th>Alt</th><th>Exonic function</th><th>Gene</th><th>GO associations</th><th>HPO annotations</th><th>All GO</th><th>All HPO</th></tr></tfoot></table>"
	outputHtml.write("</tbody>")
	outputHtml.write(endOfTable)
	outputHtml.write("</body><script src=\'GeneJSMap.js\'></script><script src=\'GOtooltipJS.js\'></script><script src=\'HPOtooltipJS.js\'></script></html>")
    #print ("Different genes: " +str(len(outputGenes)))
    #print ("All genes: " + str(counter))
    #print ("Different GO functions: " + str(len(outputGos)))
    #print ("All GO functions: " + str(counterGo))
    #print ("Different HPO functions: " + str(len(outputHpos)))
    #print ("All HPO functions: " + str(counterHpo))


# In[18]:


import os, string
import subprocess

print("Calling annovar")

#my_cmd = "perl table_annovar.pl example/ex1.avinput humandb/ -buildver hg19 -out myanno -remove -protocol refGene,cytoBand,dbnsfp30a -operation g,r,f -nastring . -csvout -polish -xreffile example/gene_fullxref.txt"
#my_cmd = "perl table_annovar.pl mom/mom.vcf humandb/ -buildver hg19 -out mom -remove -protocol refGene -operation g -nastring . -vcfinput -polish

#my_cmd = "perl table_annovar.pl example/ex1.avinput humandb/ -buildver hg19 -out myanno -remove -protocol refGene,cytoBand,dbnsfp30a -operation g,r,f -nastring . -csvout -polish -xreffile example/gene_fullxref.txt"
#my_cmd = "perl table_annovar.pl mom/mom.vcf humandb/ -buildver hg19 -out mom -remove -protocol refGene -operation g -nastring . -vcfinput -polish

#my_cmd_output = os.popen(my_cmd)

pipe = subprocess.Popen(["perl", "table_annovar.pl" , pathAnnovar, "humandb/", "-buildver", "hg19", "-out", outputAnnovar, "-remove", "-protocol", "refGene", "-operation", "g", "-nastring", ".", "-vcfinput", "-polish"], stdout=subprocess.PIPE)

(output, err) = pipe.communicate()
p_status = pipe.wait()

print ("Annovar has been finished")


# In[19]:


#createOutput("momAll.txt")
#createOutput("dadAll.txt")
#createOutput("sonAll.txt")
#createOutput(nameSon + ".hg19_multianno.txt")
#createOutput(nameDad + ".hg19_multianno.txt")
#createOutput("son" + ".hg19_multianno.txt", "son")
#createOutput("dad" + ".hg19_multianno.txt", "dad")

createOutput(outputName, outputName)
#createOutput("dad" + ".hg19_multianno.txt")


# In[20]:


duration = round(time.time() - start, 2)
print("Execution time: " + str(duration) + "s")

