# AnnoPI
Dodatak za softver Annovar

Projekat se sastoji od sledecih datoteka:

--------------------------------------------------------------------
**AnnoPI** folder koji sadrži datoteke potrebne za pokretanje aplikacije:
--------------------------------------------------------------------
-AnnoPI.py - glavni program

**data** folder koji sadrzi:
Ontologijske datoteke za GO i HPO u slučaju da korisnik  ne preuzima najsvežije verzije:
-goa_human_gaf.gz (GO)
-genes_to_phenotypes.txt (HPO)

Datoteke sa trenutno prikupljenim podacima za tooltips:
-Output Gene.txt
-Output GO-Data.txt
-Output HPO-Data.txt 

**js** folder koji sadrži neophodne JavaScript biblioteke kao i  scriptFile.js - datoteku koja omogućava selekciju, izvoz, sortiranje, pretragu

**css** folder koji sadrzi datoteke za css podrsku
**images** folder sa ikonicama


--------------------------------------------------------------------------------------
**srb-hwe.vcf** - primer ulazne .vcf datoteke nad kojom je moguce testirati aplikaciju
---------------------------------------------------------------------------------------


AnnoPI je program napisan u Python-u. Primer pokretanja programa je:
python AnnoPI.py -g goUrl -h hpoUrl -d vcfInputFilename

gde su -g i -h opcioni parametri koje korisnik zadaje u nameri da preuzme najnovije verzije datoteka sa opisom ontologija GO i HPO
ukoliko ih ne navede, program koristi lokalne verzije datoteka

vcfInputFileName argument predstavlja putanju do .vcf datoteke koja predstavlja ulazni podatak za Annovar

Za ispravno pokretanje programa neophodno je da korisnik ima instaliran Perl i Python interpreter
