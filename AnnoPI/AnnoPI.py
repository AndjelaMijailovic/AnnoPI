#!/usr/bin/env python
# coding: utf-8

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

urlGo = '' #'http://current.geneontology.org/annotations/goa_human.gaf.gz'
urlHpo = '' #'https://ci.monarchinitiative.org/view/hpo/job/hpo.annotations/lastSuccessfulBuild/artifact/rare-diseases/util/annotation/genes_to_phenotype.txt'

pathAnnovar = ''

try:
	opts, args = getopt.getopt(sys.argv,'g:h:d:',['go','hpo','vcfInputFileName'])
	counter = 0
	for arg in args:
		if arg in ("-g", "--go"):
			urlGo = args[counter+1]
		elif arg in ("-h", "--hpo"):
			urlHpo = args[counter+1]
		elif arg in ("-d", "--vcfInputFileName"):
			pathAnnovar = args[counter+1]
		counter = counter+1
except getopt.GetoptError:
	print ('some mistake')
	sys.exit(2)

if (pathAnnovar == ''):
	pathAnnovar = input('Please insert path for Annovar input file:')


isExist = os.path.isfile(pathAnnovar)
if (isExist == False):
	print('Annovar input data is not valid. . .')
	sys.exit(1)


outputAnnovarFile = pathAnnovar[pathAnnovar.rfind("/")+1:pathAnnovar.rfind(".vcf")]
if outputAnnovarFile.find(".vcf") != -1:
	outputName = outputAnnovarFile + ".hg19_multianno.txt"
else:
	outputName = pathAnnovar
print('Preparing ontology files. . . ')

filenameGO = "data/goa_human.gaf.gz"
if urlGo != '':
	try:
		urllib.request.urlretrieve(urlHpo, os.getcwd() + '\\' + filenameGO)
		print ('GO file has been downloaded')
	except:
		print("Couldn\'t download file, local file will be used")

filenameHpo = 'data/genes_to_phenotype.txt'
if urlHpo != '':
	try:
		urllib.request.urlretrieve(urlHpo, os.getcwd() + '\\' + filenameHpo)
		print ('HPO file has been downloaded')
	except:
		print("Couldn\'t download file, local file will be used")

print ('Ontology files have been prepared')


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
def getGOdata(filename, noGoGenes):
	#print ('Getting Gene and GO Data. . .')
	#start = time.time()
    geneGO = {}
    goTooltips = {}
    geneInfo = {}
    geneTooltipsProcessed = []
    goTooltipsProcessed = []
    
	#print ('Start collecting current genes')
    with open("data/Output Gene.txt", "r+") as outputGenesRead:
        for line in outputGenesRead:
            if line.find("->") != -1:
                line = line.replace("->", "-&gt;")
            delimiter = line.find("|")
            geneOutput = line[:delimiter-1]
            if geneOutput not in geneInfo :
                geneInfo[geneOutput] = line[delimiter+2:-1]
		#print('End collecting current genes -> ' + str(len(geneInfo)))
	
	#print ('Start collecting current GO function')
    with open("data/Output GO-Data.txt", "r") as outputGOsRead:
        for line in outputGOsRead:
            goOutput = line[:10].strip()
			
            if goOutput not in goTooltips:
                goTooltips[goOutput] = line[13:-1]#13+goEnd]
        #print('End collecting current GO functions -> ' + str(len(goTooltips)))

    print('Gene and GO Data processing. . .')
    with gzip.open(filename, 'rb') as goaHuman, open("data/Output GO-Data.txt", "a+") as outputGOsRead, open("data/Output Gene.txt", "a+") as outputGenesRead, open("GeneJSMap.js", "w+") as geneJS, open("GOtooltipJS.js", "w+") as goTooltipJS:
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
                    
        for key in noGoGenes:
            if key not in geneTooltipsProcessed and key in geneInfo:
                geneTooltipsProcessed.append(key)
                geneJS.write("geneMap.set(\""+ key + "\",\"" + geneInfo[key] + "\");\n" )   
    print('Gene and GO Data have been collected')
    return geneGO, geneInfo


#parse file with HPO info
def getHPOdata(filename):
    #phenotypes
    print ('HPO Data processing. . .')
    geneHpo = {}
    hpoTooltips = {}
    hpoGeneId = {}
    hpoProcessed = []

    #print('Start collecting current HPO phenotypes')
    with open("data/Output HPO-Data.txt", "r+") as outputHPOsRead:
        for line in outputHPOsRead:
            hpoOutput = line[:10].strip()
            if hpoOutput not in hpoTooltips:
                hpoTooltips[hpoOutput] = line[13:-1].replace("\"","")#13+hpoEnd]
        #print('End collecting current HPO phenotypes -> ' + str(len(hpoTooltips)))
    
    with open(filename, "r") as allHpo, open("data/Output HPO-Data.txt", "a+") as outputHPOsRead, open("HPOtooltipJS.js", "w+") as hpoJS:
        hpoJS.write("const hpoMap = new Map();\n")
        for line in allHpo:

            if line.find("HP:") == -1:
                continue
            info = re.split(' |\t', line)
            #print (info)
            gene = info[1]
            hpo = info[2]
            geneIdHPO = info[0]
            
            phenotype = "p"
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

    print('HPO Data has been collected')
    return geneHpo, hpoGeneId


#parse info from annotation file
def getVariationsData(fileName):
    
    print ("Variations data processing. . .")
    variations = {}
    allExonicGenes = ''
    geneInfo = {}

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
    print("Variations data has been collected" + str(len(variations.keys())))
    return variations



def createOutput(fileName, goFile = "data/goa_human.gaf.gz", hpoFile = "data/genes_to_phenotype.txt"):
    
    variations = getVariationsData(fileName)
    geneGO, genes = getGOdata(goFile, variations.keys())
    geneHpo, genesHPO = getHPOdata(hpoFile)
    #print ("Variations: " + str(len(variations.keys())))
    
    outputGenes = []
    outputGos = []
    outputHpos = []
    counterGo = 0
    counterHpo = 0
    counterGene = 0
    
    outputFileName = fileName[fileName.rfind("/")+1:fileName.find('.')] + ".html"
    outputHtml = open(outputFileName, "w+")
    
    print("Generation html output. . .")
    
    outputHtml.write("<!DOCTYPE html>\n")
    outputHtml.write("<html><body><head>")
    outputHtml.write("<script src=\"js/jquery.3.4.1.min.js\"></script>")
    
    #datatable
    outputHtml.write("<script type=\"text/javascript\" src=\"js/jquery.dataTables.js\"></script>\n")
    outputHtml.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"css/jquery.dataTables.css\">\n")
    
    #checkbox
    outputHtml.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"css/select.dataTables.min.css\">")
    outputHtml.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"css/buttons.dataTables.min.css\">")
    outputHtml.write("<script type=\"text/javascript\" src=\"js/dataTables.select.min.js\"></script>")
    
    outputHtml.write("<script type=\"text/javascript\" src=\"js/dataTables.buttons.min.js\"></script>")
    outputHtml.write("<script type=\"text/javascript\" src=\"js/buttons.flash.min.js\"></script>")
    outputHtml.write("<script type=\"text/javascript\" src=\"js/buttons.html5.min.js\"></script>")
    outputHtml.write("<script type=\"text/javascript\" src=\"js/jszip.min.js\"></script>")
    outputHtml.write("<script type=\"text/javascript\" src=\"js/input.js\"></script>")
	#outputHtml.write("<script type=\"text/javascript\" charset=\"utf8\" src=\"https://cdn.rawgit.com/bpampuch/pdfmake/0.1.18/build/pdfmake.min.js\"></script>")
	#outputHtml.write("<script type=\"text/javascript\" charset=\"utf8\" src=\"https://cdn.rawgit.com/bpampuch/pdfmake/0.1.18/build/vfs_fonts.js\"></script>")
  
    #include tippy for tooltip
	#outputHtml.write("<script src=\"https://unpkg.com/@popperjs/core@2/dist/umd/popper.min.js\"></script>")
	#outputHtml.write("<script src=\"https://unpkg.com/tippy.js@6/dist/tippy-bundle.umd.js\"></script>")

    outputHtml.write("<link rel=\"stylesheet\" href=\"css/cssFile.css\">")
    outputHtml.write("<script src='js/scriptFile.js'></script></head>")
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

                allGoColumn = "</td><td><img src=\"images/go-icon.png\"></td>"
                allHpoColumn = "<td><img src=\"images/hpo-icon.png\"></td></tr>\n"
                
                if currentGene in geneGO:
                    values = geneGO[currentGene]
                            
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
                    allGoColumn = "</td><td><a href=\"https://www.ebi.ac.uk/QuickGO/annotations?geneProductId=" + geneId + "\" target=\"_blank\"><img src=\"images/go-icon.png\"></a></td>"	
                            
                outputHtml.write("</td><td>")

                if currentGene in geneHpo:
                    values = geneHpo[currentGene]
                                    
                    currentGeneHpo = len(values)

                    if currentGeneHpo > 10:
                        
                        #no tooltip
                        outputHtml.write(" ".join(str(startURLhpo + e[0] + "\" target=\"_blank\">" + e[0] + "<br/>" + aTagClosed)  for e in geneHpo[currentGene][:10]))# + " ")
                        outputHtml.write(" ".join(str(startURLhpo + e[0] + "\" target=\"_blank\" style=\"display:none\" class=\"noshow\">" + e[0] + "<br/> " +aTagClosed)  for e in geneHpo[currentGene][10:]) + " ") #GO
                    
                    elif currentGeneHpo >=1:
                        
                        #no tooltip
                        outputHtml.write(" <br/>".join(str(startURLhpo + e[0] + "\" target=\"_blank\">" + e[0] + aTagClosed)  for e in geneHpo[currentGene]) + " ") #GO
                        
                    allHpoColumn = "<td><a href=\"https://hpo.jax.org/app/browse/gene/"+ geneIdHpo + "\" target=\"_blank\"><img src=\"images/hpo-icon.png\"></a></td></tr>\n"
				
                outputHtml.write(allGoColumn)
                outputHtml.write(allHpoColumn)

    endOfTable = "<tfoot><tr><th>Chr</th><th>Start</th><th>End</th><th>Ref</th><th>Alt</th><th>Exonic function</th><th>Gene</th><th>GO associations</th><th>HPO annotations</th><th>All GO</th><th>All HPO</th></tr></tfoot></table>"
    outputHtml.write("</tbody>")
    outputHtml.write(endOfTable)
    outputHtml.write("</body><script src=\'GeneJSMap.js\'></script><script src=\'GOtooltipJS.js\'></script><script src=\'HPOtooltipJS.js\'></script></html>")
    print("Output has been generated. . .")


import os, string
import subprocess

def getAnnovarData(pathAnnovar):
	print("Calling annovar. . .")
	
	outputAnnovar = pathAnnovar[pathAnnovar.rfind("/")+1:pathAnnovar.rfind(".vcf")]

	pipe = subprocess.Popen(["perl", "table_annovar.pl" , pathAnnovar, "humandb/", "-buildver", "hg19", "-out", outputAnnovar, "-remove", "-protocol", "refGene", "-operation", "g", "-nastring", ".", "-vcfinput", "-polish"], stdout=subprocess.PIPE)

	(output, err) = pipe.communicate()
	p_status = pipe.wait()

	print ("Annovar has been finished. . .")

if pathAnnovar.find(".vcf") != -1:
	getAnnovarData(pathAnnovar)

createOutput(outputName.replace("\\", "/"))


duration = round(time.time() - start, 2)
print("Execution time: " + str(duration) + "s")


