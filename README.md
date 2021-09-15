# AnnoPI
Dodatak za softver Annovar

Projekat se sastoji od sledecih datoteka:

**AnnoPI** folder sadrži datoteke potrebne za pokretanje aplikacije:
-AnnoPI.py - glavni program

Ontologijske datoteke za GO i HPO u slucaju da korisnik  ne preuzima najsvežije verzije:
-goa_human_gaf.gz (GO)
-genes_to_phenotypes.txt (HPO)

Datoteke sa trenutno prikupljenim podacima za tooltips:
-Output Gene.txt
-Output GO-Data.txt
-Output HPO-Data.txt 

-Folder *js* koji sadrži neophodne JavaScript biblioteke
-scriptFile.js - datoteka koja omogućava selekciju, izvoz, sortiranje, pretragu

-go-icon.png
-hpo-icon.png
-cssFile.css

**srb-hwe.vcf** - primer ulazne datoteke

--------------------------------------

AnnoPI je program napisan u Python-u. Primer pokretanja programa je:
python AnnoPI.py -g goUrl -h hpoUrl -d vcfInputFilename

gde su -g i -h opcioni parametri koje korisnik zadaje u nameri da preuzme najnovije verzije datoteka sa opisom ontologija GO i HPO
ukoliko ih ne navede, program koristi lokalne verzije datoteka

vcfInputFileName argument predstavlja putanju do .vcf datoteke koja predstavlja ulazni podatak za Annovar
