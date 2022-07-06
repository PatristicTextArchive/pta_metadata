# %%
import os,glob,re,gzip
import json,jsonlines
from bs4 import BeautifulSoup
import requests
import pandas as pd
from rdflib import Graph, URIRef
from rdflib.namespace import RDFS
# convert to xml
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString
import subprocess
import datetime

# %% [markdown]
# # Add places in PTA to index file

# %% [markdown]
# ## Functions

# %%
def get_git_revision_short_hash(repo):
    os.chdir(repo)
    return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
# get_git_revision_short_hash("/home/stockhausen/Dokumente/projekte/pta_data/")

# %%
def load_pleiades_data():
    '''Load Pleiades data from http://atlantides.org/downloads/pleiades/json/pleiades-places-latest.json.gz if it does not exist yet'''
    if os.path.isfile('pleiades-places-latest.jsonl'):
        contents = open('pleiades-places-latest.jsonl', "r").read() 
    else:
        url = 'http://atlantides.org/downloads/pleiades/json/pleiades-places-latest.json.gz'
        r = requests.get(url, allow_redirects=True)
        with open('pleiades-places-latest.json.gz', 'wb') as f_gzip:
            f_gzip.write(r.content)
        with gzip.open("pleiades-places-latest.json.gz", 'rb') as f_in:
            with jsonlines.open("pleiades-places-latest.jsonl", mode='w', sort_keys=True,compact=True) as f_out:
                places = json.load(f_in)
                for place in places['@graph']:
                    f_out.write(place)
        contents = open('pleiades-places-latest.jsonl', "r").read() 
    data = [json.loads(str(item)) for item in contents.strip().split('\n')]
    return data

# %%
# not used yet
def load_tipnr_data():
    '''
    Load converted TIPNR data from tipnr_data repository
    '''
    with open('/home/stockhausen/Dokumente/projekte/tipnr_data/tipnr_places.json') as tipnr:
        contents = json.load(tipnr)
    return contents

# %%
def load_files(files_path):
    '''Load all files from files_path in list of dictionaries with urn, title, body of file'''
    xml_paths = glob.glob(files_path)
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
def extract_places(files_path):
    '''Extract places from all files in list of dictionaries with 
    urn, title, number of place mentions, number of places, 
    list of places (with Pleiades-ID, context, count of mentions)'''
    file_list = load_files(files_path)
    results = []
    for entry in file_list:
        body = BeautifulSoup(str(entry["body"]), "lxml")
        counter = 0
        for place in body.find_all('placename'):
            counter = counter+1
            place_entry = {}
            try:
                place_entry["ID"] = place["ref"]
                place_entry["name"] = place.text
                new_urn = entry["urn"]+":l"+str(counter)
                place_entry["urn"] = new_urn
                results.append(place_entry)
            except:
                refs = "no ref found"
    return results

# %%
def enrich_data(file_path):
    '''Enrich extracted places with pleiades data'''
    results = extract_places(file_path)
    df = pd.DataFrame(results)
    allplaces = [{**g.to_dict(orient='list'), **{'ID': k}} for k, g in df.groupby('ID')]
    print("Places extracted")
    data = load_pleiades_data()
    print("Pleiades data loaded")
    enriched_data = []
    for result in allplaces:
        enriched = {}
        try:
            location = next(item for item in data if item["uri"] == result["ID"])
            place_name = location.get("title")
            description = location.get("description")
            long,lat = location.get("reprPoint")
            bbox = location.get("bbox")
        except:
            place_name = result["name"]
            location = "empty"
            description= "empty"
            long = "0"
            lat = "0"
            bbox = "empty"
        enriched["ID"] = result["ID"]
        enriched["canonical"] = place_name
        enriched["description"] = description
        enriched["coordinates"] = long,lat
        enriched["bbox"] = bbox
        enriched["urns"] = list(result["urn"])
        enriched["orig_name"] = list(result["name"])
        enriched_data.append(enriched)
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

# %%
# write_beacon_file("http://d-nb.info/gnd/","index_places","Alle mit Pleiades-ID versehenen Datensätze im Ortsregister")

# %% [markdown]
# ## Generate data

# %%
# add files path here
files_path = "/home/stockhausen/Dokumente/projekte/pta_data/data/*/*/*.xml"
this_path = "/".join(files_path.split("/")[:6])
# do the heavy work...
all_places = enrich_data(files_path)
# get current githash
githash = get_git_revision_short_hash(this_path)

# %%
# Write places according to text to file
with open('/home/stockhausen/Dokumente/projekte/pta_metadata/pta_places.json', 'w') as fout:
# Ergebnisse werden in eine json-Datei geschrieben
    json.dump(all_places, fout, indent=4, ensure_ascii=False)

# %%
# convert json2 xml
xml = dicttoxml(all_places, attr_type=False)
dom = parseString(xml)
with open("/home/stockhausen/Dokumente/projekte/pta_catalogues/places_for_exist.xml", 'w') as file_open:
    file_open.write(dom.toprettyxml())

# %% [markdown]
# ## Write data to places LOD files

# %%
# Prepare links, drop unnecessary keys, add link 
min_places = []
for place in all_places:
    entries_to_remove = ('canonical','description','coordinates','bbox','orig_name')
    for k in entries_to_remove:
        place.pop(k, None)
    pleiades_id = place["ID"].split("/")[4]
    index_urn = "https://pta.bbaw.de/place/"+pleiades_id
    new_urns = []
    for urn in place["urns"]:
        this_urn = "https://pta.bbaw.de/text/"+githash+"/urn:cts:pta:"+urn
        new_urns.append(this_urn)
    place["index_urn"] = index_urn    
    place["new_urns"] = new_urns
    min_places.append(place)

# %%
# CSV: Pleiades-URL, Link to mentioning in PTA-Text
df = pd.DataFrame(min_places)
df.drop(['urns','index_urn'], axis=1, inplace=True)
s = df.explode('new_urns')
# write to csv
s.to_csv('/home/stockhausen/Dokumente/projekte/pta_metadata/LOD/pta_places.csv', index=False, header=['Place','mentioned in'])

# %%
# CSV: Pleiades-URL, Link to place in PTA places index
df = pd.DataFrame(min_places)
df.drop(['urns','new_urns'], axis=1, inplace=True)
# write to csv
df.to_csv('/home/stockhausen/Dokumente/projekte/pta_metadata/LOD/pta_place_index.csv', index=False, header=['Place','Place in index'])

# %%
# BEACON for place index
df = pd.DataFrame(min_places)
df.drop(['urns','new_urns'], axis=1, inplace=True)
df["ID"] = df.ID.replace('https://pleiades.stoa.org/places/','', regex=True)
file_path = write_beacon_file("https://pleiades.stoa.org/places/","pta_places","Alle mit Pleiades-ID versehenen Datensätze im Ortsregister")
df.to_csv(file_path, header=None, index=None, sep='|', mode='a')

# %%
filename = "/home/stockhausen/Dokumente/projekte/pta_metadata/LOD/pta_places"
formats = ["xml","ttl","json-ld"]
g = Graph()
for entry in min_places:
    pleiades = URIRef(entry["ID"])
    urn = URIRef(entry["index_urn"])
    g.add((pleiades, RDFS.seeAlso, urn))
for format in formats:
    g.serialize(format=format,destination=filename+"."+format)

