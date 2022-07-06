# %%
import os,glob,re,unicodedata
import csv,json
from bs4 import BeautifulSoup
from lxml import etree
import pandas as pd
import subprocess
import datetime
# convert to xml
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString
# convert to rdf
from rdflib import Graph, URIRef
from rdflib.namespace import RDFS

# %% [markdown]
# # Add persons and orgs in PTA to index file, enriched with TIPNR and PTA persons data

# %% [markdown]
# ## Functions

# %%
def get_git_revision_short_hash(repo):
    os.chdir(repo)
    return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
# get_git_revision_short_hash("/home/stockhausen/Dokumente/projekte/pta_data/")

# %%
def load_tipnr_wikidata():
    '''
    Load WIKIDATA entities to TIPNR IDs
    '''
    with open('/home/stockhausen/Dokumente/projekte/tipnr_data/tipnr-persons-wikidata.tsv') as wikidata:
        reader = csv.DictReader(wikidata, delimiter='\t')
        contents = []
        for line in reader:
            if line["WIKIDATA_ID"]:
                contents.append(line)
    return contents

# %%
def load_tipnr_data():
    '''
    Load converted TIPNR data from tipnr_data repository and enrich with wikidata IDs
    '''
    with open('/home/stockhausen/Dokumente/projekte/tipnr_data/tipnr_persons.json') as tipnr:
        data = json.load(tipnr)
    wikidata = load_tipnr_wikidata()
    contents = []
    for entry in data:
        person = {}
        try:
            match = next(item for item in wikidata if item["TIPNR_ID"] == entry["unique_name"])
            person = entry
            person["wikidata"] = match["WIKIDATA_ID"]
            contents.append(person)
        except:
            person = entry
            person["wikidata"] = ""
            contents.append(person)
    return contents

# %%
def load_files(files_path):
    '''Load all files from files_path in list of dictionaries with urn, title, body of file'''
    xml_dir = os.path.expanduser(files_path)
    xml_paths = glob.glob(xml_dir)
    xml_paths = [path for path in sorted(xml_paths) if '__cts__' not in path]
    pta_dict = []
    for xml_path in xml_paths:
        file_dict = {}
        short_path = "/".join(xml_path.split("/")[8:])
        urn = "".join(short_path[7:]).split(".xml")[0]
        with open(xml_path) as file_open:
            soup = BeautifulSoup(file_open, 'lxml')
        strip_tags = ['cit', 'ref', 'quote', 'said', 'gap', 'app'] # remove not needed tags to avoid problems
        for tag in strip_tags: 
            for match in soup.find_all(tag):
                match.replaceWithChildren()
        body = soup.find("text")
        title = soup.find('title')
        file_dict["urn"] = urn
        file_dict["title"] = title.text
        file_dict["body"] = body
        pta_dict.append(file_dict)
    return pta_dict

# %%
def extract_all_persons(files_path):
    '''Extract all persons from all files in list of dictionaries with 
    type (biblical, else), key, content and urn + counter of file'''
    file_list = load_files(files_path)
    results = []
    for entry in file_list:
        body = BeautifulSoup(str(entry["body"]), "lxml")
        counter = 0
        for person in body.find_all("persname"):
            counter = counter+1
            pers_entry = {}
            try:
                pers_entry["ID"] = person["key"].strip()
                # Clean up forms of name in text (replace grave accent with acute accent)
                name_intext = person.text.strip().split("\n")[0]
                if " " in name_intext:
                    pers_entry["name"] = name_intext
                else:
                    pers_entry["name"] = unicodedata.normalize("NFKC",unicodedata.normalize("NFKD", name_intext).translate({ord('\N{COMBINING GRAVE ACCENT}'):'\N{COMBINING ACUTE ACCENT}'}))
                pers_entry["urn"] = entry["urn"]+":p"+str(counter)
                results.append(pers_entry)
            except:
                refs = "no ref found"
    return results

# %%
def enrich_biblpersons_data(file_path):
    '''Enrich extracted data with other data'''
    results = extract_all_persons(file_path)
    df = pd.DataFrame(results)
    allpersons = [{**g.to_dict(orient='list'), **{'ID': k}} for k, g in df.groupby('ID')]
    print("Persons extracted")
    data = load_tipnr_data()
    print("TIPNR data loaded")
    enriched_data = []
    for result in allpersons:
        enriched = {}
        try:
            person = next(item for item in data if item["unique_name"] == result["ID"])
            pers_name = person.get("unique_name").split("_")[0]
            description = person.get("ext_description")
            wikidata = person.get("wikidata", "")
            orig_name_heb = []
            orig_name_grc = []
            refs_OT = []
            refs_NT = []
            link = []
            for item in person.get("subrecord"):
                if "H" in person["subrecord"][item]['Strong']:
                    orig_name = person["subrecord"][item]['orig_name']
                    orig_name_heb.append(orig_name)
                    refs = person["subrecord"][item]['references']
                    refs_OT.append(refs)
                if "G" in person["subrecord"][item]['Strong']:
                    orig_name = person["subrecord"][item]['orig_name']
                    orig_name_grc.append(orig_name)
                    refs = person["subrecord"][item]['references']
                    refs_NT.append(refs)
                this_link = person["subrecord"][item]['link']
                link.append(this_link)
            enriched["person_id"] = result["ID"]
            enriched["other_ids"] = []
            if wikidata:
                other_id = {}
                other_id["WIKIDATA"] = wikidata
                enriched["other_ids"].append(other_id)
            list_names = []
            names = {}
            names["eng"] = pers_name
            names["heb"] = orig_name_heb
            names["grc"] = orig_name_grc
            list_names.append(names)
            enriched["forename"] = list_names
            enriched["addname"] = []
            enriched["surname"] = []
            enriched["floruit"] = ""
            enriched["description"] = description
            enriched["references_OT"] = ",".join(list(set(refs_OT)))
            enriched["references_NT"] = ",".join(list(set(refs_NT)))
            links = []
            for entry in link:
                cleaned = entry.split("=")[-1]
                links.append(cleaned)
            new_link = "https://www.stepbible.org/?q=version=ESV|version=LXX|version=SBLG|text="+pers_name+"*|reference="+";".join(links)        
            enriched["source"] = "TIPNR"
            enriched["link"] = new_link
            enriched["urns"] = list(result["urn"])
            enriched["name_txts"] = list(result["name"])
            enriched_data.append(enriched)
        except:
            pass
    return enriched_data
    

# %%
def load_pta_persons():
    '''Load persons from PTA registry'''
    pta = []
    with open('/home/stockhausen/Dokumente/projekte/pta_catalogues/pta_persons.xml') as file:
            tree = etree.parse(file)
            root = tree.getroot()
            ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
            # title of text
            entries = root.findall('.//tei:person', ns)
            for entry in entries:
                persons = {}
                persons['person_id'] = entry.attrib['{http://www.w3.org/XML/1998/namespace}id']
                list_others = []
                for item in entry.findall('.//tei:idno', ns):
                    others = {}
                    key = item.attrib["type"].replace("#","").upper()
                    others[key] = item.text
                    list_others.append(others)
                persons['other_ids'] = list_others
                list_forenames = []
                for item in entry.findall('.//tei:forename', ns):
                    others = {}
                    key = item.attrib["{http://www.w3.org/XML/1998/namespace}lang"]
                    others[key] = item.text
                    list_forenames.append(others)
                persons['forename'] = list_forenames
                if entry.find('.//tei:surname', ns) is not None:
                    list_surnames = []
                    for item in entry.findall('.//tei:surname', ns):
                        others = {}
                        key = item.attrib["{http://www.w3.org/XML/1998/namespace}lang"]
                        others[key] = item.text
                        list_surnames.append(others)
                    persons['surname'] = list_surnames
                else:
                    persons['surname'] =  []
                if entry.find('.//tei:addName', ns) is not None:
                    list_addnames = []
                    for item in entry.findall('.//tei:addName', ns):
                        others = {}
                        key = item.attrib["{http://www.w3.org/XML/1998/namespace}lang"]
                        others[key] = item.text
                        list_addnames.append(others)
                    persons['addname'] = list_addnames
                else:
                    persons['addname'] =  []
                persons['floruit'] = entry.find('.//tei:floruit', ns).text
                persons['description'] = entry.find('.//tei:p', ns).text
                persons["references_OT"] = []
                persons["references_NT"] = []
                persons["link"] = ""
                try:
                    persons['source'] = entry.attrib["resp"].replace("#","")
                except:
                    persons['source'] = entry.attrib["source"].replace("#","")
                pta.append(persons)
    return pta

# %%
def load_pta_orgs():
    '''Load groups from PTA registry'''
    pta = []
    with open('/home/stockhausen/Dokumente/projekte/pta_catalogues/pta_persons.xml') as file:
            tree = etree.parse(file)
            root = tree.getroot()
            ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
            # title of text
            entries = root.findall('.//tei:org', ns)
            for entry in entries:
                orgs = {}
                orgs['org_id'] = entry.attrib['{http://www.w3.org/XML/1998/namespace}id']
                list_others = []
                for item in entry.findall('.//tei:idno', ns):
                    others = {}
                    key = item.attrib["type"].replace("#","").upper()
                    others[key] = item.text
                    list_others.append(others)
                orgs['other_ids'] = list_others
                list_orgnames = []
                for item in entry.findall('.//tei:orgName', ns):
                    others = {}
                    key = item.attrib["{http://www.w3.org/XML/1998/namespace}lang"]
                    others[key] = item.text
                    list_orgnames.append(others)
                orgs['orgname'] = list_orgnames
                orgs['type'] = entry.attrib["role"]
                event = entry.find('.//tei:event', ns)
                try:
                    orgs['date'] = event.attrib['when']
                except:
                    orgs['date'] = ''
                pta.append(orgs)
    return pta

# %%
def extract_organisations(files_path):
    '''Extract organisations from all files in list of dictionaries with 
    key, content and urn of file'''
    file_list = load_files(files_path)
    results_org = []
    for entry in file_list:
        body = BeautifulSoup(str(entry["body"]), "lxml")
        counter = 0
        for org in body.find_all("orgname",{"key": re.compile("PTA*")}):
            counter = counter+1
            org_entry = {}
            try: 
                org_entry["ID"] = org["key"].strip()
                # Clean up forms of name in text (replace grave accent with acute accent)
                name_intext = org.text.strip().split("\n")[0]
                if " " in name_intext:
                    org_entry["name"] = name_intext
                else:
                    org_entry["name"] = unicodedata.normalize("NFKC",unicodedata.normalize("NFKD", name_intext).translate({ord('\N{COMBINING GRAVE ACCENT}'):'\N{COMBINING ACUTE ACCENT}'}))
                org_entry["urn"] = entry["urn"]+":g"+str(counter)
                results_org.append(org_entry)
            except:
                refs = "no ref found"
    return results_org

# %%
def enrich_persons_data(file_path):
    '''Enrich extracted data with other data'''
    results = extract_all_persons(file_path)
    df = pd.DataFrame(results)
    allpersons = [{**g.to_dict(orient='list'), **{'ID': k}} for k, g in df.groupby('ID')]
    print("Persons extracted")
    data = load_pta_persons()
    print("PTA persons data loaded")
    enriched_data = []
    for result in allpersons:
        try:
            person = {}
            person = next(item for item in data if item["person_id"] == result["ID"])
            person["urns"] = list(result["urn"])
            person["name_txts"] = list(result["name"])
            enriched_data.append(person)
        except:
            pass
    return enriched_data

# %%
def enrich_org_data(file_path):
    '''Enrich extracted data with other data'''
    results = extract_organisations(file_path)
    df = pd.DataFrame(results)
    allpersons = [{**g.to_dict(orient='list'), **{'ID': k}} for k, g in df.groupby('ID')]
    print("Organisations extracted")
    data = load_pta_orgs()
    print("PTA organisation data loaded")
    enriched_data = []
    for result in allpersons:  
        org = {}
        try:
            org = next(item for item in data if item["org_id"] == result["ID"])
            org["urns"] = list(result["urn"])
            org["name_txts"] = list(result["name"])
        except:
            pass
        enriched_data.append(org)
    return enriched_data

# %%
def write_beacon_file(prefix,filename,description):
    '''
    Generates a BEACON file, cf. https://de.wikipedia.org/wiki/Wikipedia:BEACON
    Prefix = URL of linked entities
    Description like "Alle mit Norm-ID versehenen Datensätze im Personenregister"
    Target is always URL
    '''
    prefix = prefix
    filename = filename
    description = description
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with open("/home/stockhausen/Dokumente/projekte/pta_metadata/LOD/"+filename+"_beacon.txt", 'w') as fout:
        fout.write("#FORMAT: BEACON\n")
        fout.write("#PREFIX: "+prefix+"\n")
        fout.write("#FEED: https://raw.githubusercontent.com/PatristicTextArchive/pta_metadata/main/LOD/"+filename+"_beacon.txt\n")
        fout.write("#NAME: Patristisches Textarchiv (PTA)\n")
        fout.write("#DESCRIPTION: "+description+"\n")
        fout.write("#RELATION: http://www.w3.org/2000/01/rdf-schema#seeAlso\n")
        fout.write("#CONTACT: Dr. Annette von Stockhausen <annette.von_stockhausen@bbaw.de>\n")
        fout.write("#INSTITUTION: Berlin-Brandenburgische Akademie der Wissenschaften\n")
        fout.write("#TIMESTAMP: "+timestamp+"\n")
        fout.write("#UPDATE: monthly\n")
    file_path = "/home/stockhausen/Dokumente/projekte/pta_metadata/LOD/"+filename+"_beacon.txt"
    return file_path

# %% [markdown]
# ## Do conversion

# %%
# add files path here
files_path = "/home/stockhausen/Dokumente/projekte/pta_data/data/*/*/*.xml"
this_path = "/".join(files_path.split("/")[:6])

# %%
persons = enrich_persons_data(files_path)

# %%
bibl_persons = enrich_biblpersons_data(files_path)

# %%
all_persons = persons + bibl_persons

# %%
orgs = enrich_org_data(files_path)

# %%
# get current githash
githash = get_git_revision_short_hash(this_path)

# %% [markdown]
# ## Write to json

# %%
# Write to file
with open('/home/stockhausen/Dokumente/projekte/pta_metadata/pta_persons.json', 'w') as fout:
# Ergebnisse werden in eine json-Datei geschrieben
    json.dump(all_persons, fout, indent=4, ensure_ascii=False)

# %%
# Write to file
with open('/home/stockhausen/Dokumente/projekte/pta_metadata/pta_groups.json', 'w') as fout:
# Ergebnisse werden in eine json-Datei geschrieben
    json.dump(orgs, fout, indent=4, ensure_ascii=False)

# %% [markdown]
# ## Write to xml

# %%
# convert json2 xml
xml = dicttoxml(all_persons, attr_type=False)
final = parseString(xml)
with open("/home/stockhausen/Dokumente/projekte/pta_catalogues/persons_for_exist.xml", 'w') as file_open:
    file_open.write(final.toprettyxml())

# %% [markdown]
# ## Write data to persons LOD files

# %%
# Prepare links, drop unnecessary keys, add link 
min_persons = []
for person in all_persons:
    entries_to_remove = ('forename','surname','addname','floruit','description','references_OT','references_NT','link','source','name_txts')
    for k in entries_to_remove:
        person.pop(k, None)
    index_urn = "https://pta.bbaw.de/person/"+person["person_id"]
    new_urns = []
    for urn in person["urns"]:
        this_urn = "https://pta.bbaw.de/text/"+githash+"/urn:cts:pta:"+urn
        new_urns.append(this_urn)
    try:
        gnd = next(item["GND"] for item in person["other_ids"] if item.get("GND"))
    except:
        gnd = ""
    try:
        wikidata = next(item["WIKIDATA"] for item in person["other_ids"] if item.get("WIKIDATA"))
    except:
        wikidata = ""
    person["GND"] = gnd
    person["WIKIDATA"] = wikidata
    person["index_urn"] = index_urn    
    person["new_urns"] = new_urns
    min_persons.append(person)

# %%
# CSV: GND, Wikidata, Link to mentioning in PTA-Text
df = pd.DataFrame(min_persons)
df.drop(['person_id','other_ids','urns','index_urn'], axis=1, inplace=True)
df.replace("", float("NaN"), inplace=True)
df.dropna(subset=['WIKIDATA', 'GND'], how="all", inplace=True)
s = df.explode('new_urns')
# write to csv
s.to_csv('/home/stockhausen/Dokumente/projekte/pta_metadata/LOD/pta_persons.csv', index=False, header=['GND-ID','Wikidata-Entity','mentioned in'])

# %%
# CSV: GND, Wikidata, Link to place in PTA persons index
df = pd.DataFrame(min_persons)
df.drop(['person_id','other_ids','urns','new_urns'], axis=1, inplace=True)
df.replace("", float("NaN"), inplace=True)
df.dropna(subset=['WIKIDATA', 'GND'], how="all", inplace=True)
# write to csv
df.to_csv('/home/stockhausen/Dokumente/projekte/pta_metadata/LOD/pta_persons_index.csv', index=False, header=['GND-ID','Wikidata-Entity','Person in index'])

# %%
# GND BEACON for persons index
df = pd.DataFrame(min_persons)
df.drop(['person_id','other_ids','urns','new_urns','WIKIDATA'], axis=1, inplace=True)
df.replace("", float("NaN"), inplace=True)
df.dropna(subset=['GND'], how="all", inplace=True)
file_path = write_beacon_file("http://d-nb.info/gnd/","pta_persons_index_gnd","Alle mit GND-ID versehenen Datensätze im Personenregister")
df.to_csv(file_path, header=None, index=None, sep='|', mode='a')

# %%
# WIKIDATA BEACON for persons index
df = pd.DataFrame(min_persons)
df.drop(['person_id','other_ids','urns','new_urns','GND'], axis=1, inplace=True)
df.replace("", float("NaN"), inplace=True)
df.dropna(subset=['WIKIDATA'], how="all", inplace=True)
file_path = write_beacon_file("https://www.wikidata.org/wiki/","pta_persons_index_wikidata","Alle mit WIKIDATA-ID versehenen Datensätze im Personenregister")
df.to_csv(file_path, header=None, index=None, sep='|', mode='a')

# %%
filename = "/home/stockhausen/Dokumente/projekte/pta_metadata/LOD/pta_persons_index_gnd"
formats = ["xml","ttl","json-ld"]
g = Graph()
for entry in min_persons:
    if entry["GND"]:
        gnd = URIRef("http://d-nb.info/gnd/"+entry["GND"])
        urn = URIRef(entry["index_urn"])
        g.add((gnd, RDFS.seeAlso, urn))
for format in formats:
    g.serialize(format=format,destination=filename+"."+format)

# %%
filename = "/home/stockhausen/Dokumente/projekte/pta_metadata/LOD/pta_persons_index_wikidata"
formats = ["xml","ttl","json-ld"]
g = Graph()
for entry in min_persons:
    if entry["WIKIDATA"]:
        wd = URIRef("https://www.wikidata.org/wiki/"+entry["WIKIDATA"])
        urn = URIRef(entry["index_urn"])
        g.add((wd, RDFS.seeAlso, urn))
for format in formats:
    g.serialize(format=format,destination=filename+"."+format)

# %% [markdown]
# ## Write data to orgs LOD files

# %%
# Prepare links, drop unnecessary keys, add link 
min_orgs = []
for org in orgs:
    entries_to_remove = ('orgname','type','date','name_txts')
    for k in entries_to_remove:
        org.pop(k, None)
    index_urn = "https://pta.bbaw.de/group/"+org["org_id"]
    new_urns = []
    for urn in org["urns"]:
        this_urn = "https://pta.bbaw.de/text/"+githash+"/urn:cts:pta:"+urn
        new_urns.append(this_urn)
    try:
        gnd = next(item["GND"] for item in org["other_ids"] if item.get("GND"))
    except:
        gnd = ""
    try:
        wikidata = next(item["WIKIDATA"] for item in org["other_ids"] if item.get("WIKIDATA"))
    except:
        wikidata = ""
    org["GND"] = gnd
    org["WIKIDATA"] = wikidata
    org["index_urn"] = index_urn    
    org["new_urns"] = new_urns
    min_orgs.append(org)

# %%
# CSV: GND, Wikidata, Link to mentioning in PTA-Text
df = pd.DataFrame(min_orgs)
df.drop(['org_id','other_ids','urns','index_urn'], axis=1, inplace=True)
df.replace("", float("NaN"), inplace=True)
df.dropna(subset=['WIKIDATA', 'GND'], how="all", inplace=True)
s = df.explode('new_urns')
# write to csv
s.to_csv('/home/stockhausen/Dokumente/projekte/pta_metadata/LOD/pta_orgs.csv', index=False, header=['GND-ID','Wikidata-Entity','mentioned in'])

# %%
# CSV: GND, Wikidata, Link to place in PTA orgs index
df = pd.DataFrame(min_orgs)
df.drop(['org_id','other_ids','urns','new_urns'], axis=1, inplace=True)
df.replace("", float("NaN"), inplace=True)
df.dropna(subset=['WIKIDATA', 'GND'], how="all", inplace=True)
# write to csv
df.to_csv('/home/stockhausen/Dokumente/projekte/pta_metadata/LOD/pta_orgs_index.csv', index=False, header=['GND-ID','Wikidata-Entity','Person in index'])

# %%
# GND BEACON for orgs index
df = pd.DataFrame(min_orgs)
df.drop(['org_id','other_ids','urns','new_urns','WIKIDATA'], axis=1, inplace=True)
df.replace("", float("NaN"), inplace=True)
df.dropna(subset=['GND'], how="all", inplace=True)
file_path = write_beacon_file("http://d-nb.info/gnd/","pta_orgs_index_gnd","Alle mit GND-ID versehenen Datensätze im Register der Organisationen und Gruppen")
df.to_csv(file_path, header=None, index=None, sep='|', mode='a')

# %%
# WIKIDATA BEACON for orgs index
df = pd.DataFrame(min_orgs)
df.drop(['org_id','other_ids','urns','new_urns','GND'], axis=1, inplace=True)
df.replace("", float("NaN"), inplace=True)
df.dropna(subset=['WIKIDATA'], how="all", inplace=True)
file_path = write_beacon_file("https://www.wikidata.org/wiki/","pta_orgs_index_wikidata","Alle mit WIKIDATA-ID versehenen Datensätze im Register der Organisationen und Gruppen")
df.to_csv(file_path, header=None, index=None, sep='|', mode='a')

# %%
filename = "/home/stockhausen/Dokumente/projekte/pta_metadata/LOD/pta_orgs_index_gnd"
formats = ["xml","ttl","json-ld"]
g = Graph()
for entry in min_orgs:
    if entry["GND"]:
        gnd = URIRef("http://d-nb.info/gnd/"+entry["GND"])
        urn = URIRef(entry["index_urn"])
        g.add((gnd, RDFS.seeAlso, urn))
for format in formats:
    g.serialize(format=format,destination=filename+"."+format)

# %%
filename = "/home/stockhausen/Dokumente/projekte/pta_metadata/LOD/pta_orgs_index_wikidata"
formats = ["xml","ttl","json-ld"]
g = Graph()
for entry in min_orgs:
    if entry["WIKIDATA"]:
        wd = URIRef("https://www.wikidata.org/wiki/"+entry["WIKIDATA"])
        urn = URIRef(entry["index_urn"])
        g.add((wd, RDFS.seeAlso, urn))
for format in formats:
    g.serialize(format=format,destination=filename+"."+format)



