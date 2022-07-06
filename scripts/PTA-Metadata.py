# %%
import os,glob,re
from pathlib import Path
import json
import xmltodict
import datetime
import pandas as pd
from lxml import etree
from rdflib import Graph, URIRef
from rdflib.namespace import RDFS

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
# # pta_data

# %%
def load_metadata(files_path):
    '''Load all CTS metadata files from files_path'''
    data_path = os.path.expanduser(files_path)
    textgroups = glob.glob(data_path, recursive=True)
    metadata_dict = []
    for textgroup in textgroups:
        metadata = Path(textgroup).glob('__cts__.xml')
        works = list(Path(textgroup).rglob('__cts__.xml'))
        workgroup_dict = {}
        listworks = []
        for file in metadata:
            with open(file) as file_open:
                meta_dict = xmltodict.parse(file_open.read(), dict_constructor=dict)
                workgroup_dict["textgroup"] = meta_dict
            for file in works[1:]:
                with open(file) as file_open:
                    meta_dict = xmltodict.parse(file_open.read(), dict_constructor=dict)
                    listworks.append(meta_dict)
                    workgroup_dict["works"] = listworks
            metadata_dict.append(workgroup_dict)
    return metadata_dict

# %% [markdown]
# ## Write files

# %%
data = load_metadata("~/Dokumente/projekte/pta_data/data/*")

# %%
# Write to file
with open('/home/stockhausen/Dokumente/projekte/pta_metadata/pta_data.json', 'w') as fout:
# Ergebnisse werden in eine json-Datei geschrieben
    json.dump(data, fout, indent=4, ensure_ascii=False)

# %% [markdown]
# ### Authors

# %%
# Get data for author LOD files
authors = []
for entry in data:
    this_entry = {}
    this_entry["urn"] = "https://pta.bbaw.de/text/"+entry["textgroup"]["ti:textgroup"]["@urn"]
    try:
        this_entry["gnd"] = entry["textgroup"]["ti:textgroup"]["cpt:structured-metadata"]["gnd:gndIdentifier"]
        this_entry["wd"] = entry["textgroup"]["ti:textgroup"]["cpt:structured-metadata"]["wd:Item"]
        authors.append(this_entry)
    except:
        pass

# %%
# CSV: GND, Wikidata, Link to author page
df = pd.DataFrame(authors)
df = df[['gnd', 'wd', 'urn']]
#df.drop(['person_id','other_ids','urns','new_urns'], axis=1, inplace=True)
#df.replace("", float("NaN"), inplace=True)
#df.dropna(subset=['WIKIDATA', 'GND'], how="all", inplace=True)
# write to csv
df.to_csv('/home/stockhausen/Dokumente/projekte/pta_metadata/LOD/pta_authors.csv', index=False, header=['GND-ID','Wikidata-Entity','URN'])

# %%
# GND BEACON for authors index
df = pd.DataFrame(authors)
df.drop(['wd'], axis=1, inplace=True)
df = df[['gnd', 'urn']]
file_path = write_beacon_file("http://d-nb.info/gnd/","pta_authors_gnd","Alle mit GND-ID versehenen Autoren")
df.to_csv(file_path, header=None, index=None, sep='|', mode='a')

# %%
# WIKIDATA BEACON for authors index
df = pd.DataFrame(authors)
df.drop(['gnd'], axis=1, inplace=True)
df = df[['wd', 'urn']]
file_path = write_beacon_file("https://www.wikidata.org/wiki/","pta_authors_wikidata","Alle mit WIKIDATA-ID versehenen Autoren")
df.to_csv(file_path, header=None, index=None, sep='|', mode='a')

# %%
filename = "/home/stockhausen/Dokumente/projekte/pta_metadata/LOD/pta_authors_gnd"
formats = ["xml","ttl","json-ld"]
g = Graph()
for entry in authors:
    gnd = URIRef("http://d-nb.info/gnd/"+entry["gnd"])
    urn = URIRef(entry["urn"])
    g.add((gnd, RDFS.seeAlso, urn))
for format in formats:
    g.serialize(format=format,destination=filename+"."+format)

# %%
filename = "/home/stockhausen/Dokumente/projekte/pta_metadata/LOD/pta_authors_wikidata"
formats = ["xml","ttl","json-ld"]
g = Graph()
for entry in authors:
    gnd = URIRef("https://www.wikidata.org/wiki/"+entry["wd"])
    urn = URIRef(entry["urn"])
    g.add((gnd, RDFS.seeAlso, urn))
for format in formats:
    g.serialize(format=format,destination=filename+"."+format)

# %% [markdown]
# ## Works

# %%
# Get data for works LOD files
works = []
for entry in data:
    for item in entry["works"]:
        this_entry = {}
        this_entry["urn"] = "https://pta.bbaw.de/text/"+item["ti:work"]["@urn"]
        cpg = "".join([num for num in item["ti:work"]["cpt:structured-metadata"]["dc:identifier"] if "CPG" in num])
        if cpg:
            cpg = cpg.split(":")[1]
        this_entry["CPG"] = cpg
        bhg = "".join([num for num in item["ti:work"]["cpt:structured-metadata"]["dc:identifier"] if "BHG" in num])
        if bhg:
            bhg = bhg.split(":")[1]
        this_entry["BHG"] = bhg
        pinakes = "".join([num for num in item["ti:work"]["cpt:structured-metadata"]["dc:identifier"] if "Pinakes" in num])
        if pinakes:
            pinakes = pinakes.split(":")[1]
        this_entry["Pinakes-Oeuvre"] = pinakes
        works.append(this_entry)

# %%
# CSV: CPG, BHG, Pinakes-Oeuvre no. link to work page
df = pd.DataFrame(works)
df = df[['CPG', 'BHG', 'Pinakes-Oeuvre','urn']]
#df.drop(['person_id','other_ids','urns','new_urns'], axis=1, inplace=True)
df.replace("", float("NaN"), inplace=True)
df.dropna(subset=['CPG', 'BHG', 'Pinakes-Oeuvre'], how="all", inplace=True)
# write to csv
df.to_csv('/home/stockhausen/Dokumente/projekte/pta_metadata/LOD/pta_works.csv', index=False, header=['CPG no.','BHG no.','Pinakes-Oeuvre no.','URN'])

# %%
# ClaCla (CPG) BEACON for work page
df = pd.DataFrame(works)
df.drop(['BHG','Pinakes-Oeuvre'], axis=1, inplace=True)
df.replace("", float("NaN"), inplace=True)
df.dropna(subset=['CPG'], how="all", inplace=True)
df = df[['CPG', 'urn']]
file_path = write_beacon_file("https://clavis.brepols.net/clacla/OA/link.aspx?clavis=CPG&number=","pta_works_cpg","Alle mit CPG-Nummer versehenen Werke")
df.to_csv(file_path, header=None, index=None, sep='|', mode='a')

# %%
# ClaCla (BHG) BEACON for work page
df = pd.DataFrame(works)
df.drop(['CPG','Pinakes-Oeuvre'], axis=1, inplace=True)
df.replace("", float("NaN"), inplace=True)
df.dropna(subset=['BHG'], how="all", inplace=True)
df = df[['BHG', 'urn']]
file_path = write_beacon_file("https://clavis.brepols.net/clacla/OA/link.aspx?clavis=BHG&number=","pta_works_bhg","Alle mit BHG-Nummer versehenen Werke")
df.to_csv(file_path, header=None, index=None, sep='|', mode='a')

# %%
# Pinakes-Oeuvre BEACON for work page
df = pd.DataFrame(works)
df.drop(['CPG','BHG'], axis=1, inplace=True)
df.replace("", float("NaN"), inplace=True)
df.dropna(subset=['Pinakes-Oeuvre'], how="all", inplace=True)
df = df[['Pinakes-Oeuvre', 'urn']]
file_path = write_beacon_file("https://pinakes.irht.cnrs.fr/notices/oeuvre/","pta_works_pinakes-oeuvre","Alle mit Pinakes-Oeuvre-Nummer versehenen Werke")
df.to_csv(file_path, header=None, index=None, sep='|', mode='a')

# %%
filename = "/home/stockhausen/Dokumente/projekte/pta_metadata/LOD/pta_works_cpg"
formats = ["xml","ttl","json-ld"]
g = Graph()
for entry in works: 
    if entry["CPG"]:
        cpg = URIRef("https://clavis.brepols.net/clacla/OA/link.aspx?clavis=CPG&number="+entry["CPG"].split(";")[0])
        urn = URIRef(entry["urn"])
        g.add((cpg, RDFS.seeAlso, urn))
for format in formats:
    g.serialize(format=format,destination=filename+"."+format)

# %%
filename = "/home/stockhausen/Dokumente/projekte/pta_metadata/LOD/pta_works_bhg"
formats = ["xml","ttl","json-ld"]
g = Graph()
for entry in works:
    if entry["BHG"]:
        gnd = URIRef("https://clavis.brepols.net/clacla/OA/link.aspx?clavis=BHG&number="+entry["BHG"])
        urn = URIRef(entry["urn"])
        g.add((gnd, RDFS.seeAlso, urn))
for format in formats:
    g.serialize(format=format,destination=filename+"."+format)

# %%
filename = "/home/stockhausen/Dokumente/projekte/pta_metadata/LOD/pta_works_pinakes-oeuvre"
formats = ["xml","ttl","json-ld"]
g = Graph()
for entry in works:
    if entry["Pinakes-Oeuvre"]:
        gnd = URIRef("https://pinakes.irht.cnrs.fr/notices/oeuvre/"+entry["Pinakes-Oeuvre"])
        urn = URIRef(entry["urn"])
        g.add((gnd, RDFS.seeAlso, urn))
for format in formats:
    g.serialize(format=format,destination=filename+"."+format)

# %% [markdown]
# # pta_manuscripts

# %%
def load_manuscripts(files_path):
    '''Load all files from files_path in list of dictionaries with urn, title, body of file'''
    xml_dir = os.path.expanduser(files_path)
    xml_paths = glob.glob(xml_dir)
    metadata_dict = []
    for xml_path in xml_paths:
        file_dict = {}
        meta_dict = {}
        with open(xml_path) as file:
            tree = etree.parse(file)
            root = tree.getroot()
            ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
            # title of text
            title = root.find('.//tei:title', ns)
            msident = root.find('.//tei:msIdentifier', ns).getchildren()
            diktyon = root.find('.//tei:altIdentifier/tei:idno', ns)
            contents = root.findall('.//tei:msContents/tei:msItem[@corresp]', ns)
            try:
                images = root.find('.//tei:surrogates//tei:ref[@type="straighturl"]', ns).attrib["target"]
            except:
                images = ""
            try:
                iif_manifest = root.find('.//tei:surrogates//tei:ref[@type="manifesturl"]', ns).attrib["target"]
            except:
                iiif_manifest = ""
            try:
                origDate = re.sub(r"\s{2,}","",root.find('.//tei:origDate', ns).text)
            except:
                origDate = ""
            
            try:
                origDate_notbefore = root.find('.//tei:origDate', ns).attrib['notBefore-iso']
                origDate_notafter = root.find('.//tei:origDate', ns).attrib['notAfter-iso']
            except:
                origDate_notbefore = ""
                origDate_notafter = ""
            content = [x.attrib['corresp'] for x in contents]
            meta_dict["id"] = root.attrib["{http://www.w3.org/XML/1998/namespace}id"]
            try:
                meta_dict["status"] = root.find('.//tei:revisionDesc', ns).attrib['status']
            except:
                meta_dict["status"] = ""
            meta_dict["diktyon"] = re.sub(r"\s{2,}","",diktyon.text)
            meta_dict["manuscript"] = re.sub(r"\s{2,}","",title.text)
            meta_dict["settlement"] = re.sub(r"\s{2,}","",msident[1].text)
            meta_dict["repository"] = re.sub(r"\s{2,}","",msident[2].text)
            meta_dict["collection"] = re.sub(r"\s{2,}","",msident[3].text)
            meta_dict["idno"] = re.sub(r"\s{2,}","",msident[4].text)
            meta_dict["origDate"] = origDate
            meta_dict["origDate_notbefore"] = origDate_notbefore
            meta_dict["origDate_notafter"] = origDate_notafter
            meta_dict["images"] = images
            meta_dict["iiif_manifest"] = iiif_manifest
            meta_dict["contents"] = content
            metadata_dict.append(meta_dict)
    return metadata_dict

# %%
data = load_manuscripts("~/Dokumente/projekte/pta_manuscripts/data/*.xml")

# %% [markdown]
# ## Write files

# %%
# Write to file
with open('/home/stockhausen/Dokumente/projekte/pta_metadata/pta_manuscripts.json', 'w') as fout:
# Ergebnisse werden in eine json-Datei geschrieben
    json.dump(data, fout, indent=4, ensure_ascii=False)

# %%
# Get data for diktyon LOD files
manuscripts = []
for entry in data:
    this_entry = {}
    this_entry["urn"] = "https://pta.bbaw.de/manuscripts/"+entry["id"]
    try:
        this_entry["diktyon"] = entry["diktyon"]
        manuscripts.append(this_entry)
    except:
        pass

# %%
filename = "/home/stockhausen/Dokumente/projekte/pta_metadata/LOD/pta_manuscripts_diktyon"
formats = ["xml","ttl","json-ld"]
g = Graph()
for entry in manuscripts:
    diktyon = URIRef("https://pinakes.irht.cnrs.fr/notices/cote/"+entry["diktyon"])
    urn = URIRef(entry["urn"])
    g.add((diktyon, RDFS.seeAlso, urn))
for format in formats:
    g.serialize(format=format,destination=filename+"."+format)

# %%
# CSV: Diktyon-ID, Link to manuscripts page
df = pd.DataFrame(manuscripts)
df = df[['diktyon', 'urn']]
#df.drop(['person_id','other_ids','urns','new_urns'], axis=1, inplace=True)
#df.replace("", float("NaN"), inplace=True)
#df.dropna(subset=['WIKIDATA', 'GND'], how="all", inplace=True)
# write to csv
df.to_csv('/home/stockhausen/Dokumente/projekte/pta_metadata/LOD/pta_manuscripts_diktyon.csv', index=False, header=['Diktyon-ID','URN'])

# %%
# Diktyon BEACON for manuscripts
df = pd.DataFrame(manuscripts)
df = df[['diktyon', 'urn']]
file_path = write_beacon_file("https://pinakes.irht.cnrs.fr/notices/cote/","pta_manuscripts_diktyon","Alle mit Diktyon-ID versehenen Handschriften")
df.to_csv(file_path, header=None, index=None, sep='|', mode='a')


