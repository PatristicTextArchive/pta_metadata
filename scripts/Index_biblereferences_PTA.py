# %%
import os,glob,re
import csv,json
from bs4 import BeautifulSoup
from lxml import etree
import pandas as pd
import subprocess
# load capitains
from MyCapytain.resources.texts.local.capitains.cts import CapitainsCtsText
from MyCapytain.resolvers.cts.local import CtsCapitainsLocalResolver
from MyCapytain.common.constants import Mimetypes, XPATH_NAMESPACES
from lxml.etree import tostring
# convert to rdf
from rdflib import Graph, URIRef
from rdflib.namespace import RDFS

# %% [markdown]
# # Add biblical references to index file, enriched with quoted text in standard editions (LXX, NA) or with links to online resources (Hexapla, Vg)

# %% [markdown]
# ## Functions

# %%
# Concordance Grc
abbrev_grc = "LXX:Gn, LXX:Ex, LXX:Lv, LXX:Num, LXX:Dt, LXX:Jos, LXX:Judg, LXX:Rt, LXX:1Sa, LXX:2Sa, LXX:1Ko, LXX:2Ko, LXX:1Chr, LXX:2Chr, LXX:3Esr, LXX:Esr, LXX:Est, LXX:Jdt, LXX:Tob, LXX:1Mak, LXX:2Mak, LXX:3Mak, LXX:4Mak, LXX:Ps, LXX:Oden, LXX:Prov, LXX:Eccl, LXX:Song, LXX:Job, LXX:Wis, LXX:Sir, LXX:PsSal, LXX:Hos, LXX:Am, LXX:Mi, LXX:Joel, LXX:Ob, LXX:Jon, LXX:Nah, LXX:Hab, LXX:Zeph, LXX:Hag, LXX:Sach, LXX:Mal, LXX:Is, LXX:Jr, LXX:Bar, LXX:Lam, LXX:EpistJer, LXX:Hes, LXX:Sus, LXX:Sus-LXX, LXX:Dn, LXX:Dn-LXX, LXX:Bel, LXX:Bel-LXX, NA:Mt, NA:Mk, NA:Lk, NA:Jn, NA:Act, NA:Rom, NA:1Cor, NA:2Cor, NA:Gal, NA:Eph, NA:Phil, NA:Col, NA:1Th, NA:2Th, NA:1Tim, NA:2Tim, NA:Tt, NA:Phm, NA:Heb, NA:Jak, NA:1P, NA:2P, NA:1Jn, NA:2Jn, NA:3Jn, NA:Jud, NA:Rev".split(", ")
ptaids_grc = "pta9999.pta001.pta-grc1, pta9999.pta002.pta-grc1, pta9999.pta003.pta-grc1, pta9999.pta004.pta-grc1, pta9999.pta005.pta-grc1, pta9999.pta006.pta-grc1, pta9999.pta007.pta-grc1, pta9999.pta008.pta-grc1, pta9999.pta009.pta-grc1, pta9999.pta010.pta-grc1, pta9999.pta011.pta-grc1, pta9999.pta012.pta-grc1, pta9999.pta013.pta-grc1, pta9999.pta014.pta-grc1, pta9999.pta016.pta-grc1, pta9999.pta017.pta-grc1, pta9999.pta020.pta-grc1, pta9999.pta021.pta-grc1, pta9999.pta022.pta-grc1, pta9999.pta023.pta-grc1, pta9999.pta024.pta-grc1, pta9999.pta025.pta-grc1, pta9999.pta026.pta-grc1, pta9999.pta031.pta-grc1, pta9999.pta032.pta-grc1, pta9999.pta033.pta-grc1, pta9999.pta034.pta-grc1, pta9999.pta035.pta-grc1, pta9999.pta036.pta-grc1, pta9999.pta037.pta-grc1, pta9999.pta038.pta-grc1, pta9999.pta039.pta-grc1, pta9999.pta040.pta-grc1, pta9999.pta041.pta-grc1, pta9999.pta042.pta-grc1, pta9999.pta043.pta-grc1, pta9999.pta044.pta-grc1, pta9999.pta045.pta-grc1, pta9999.pta046.pta-grc1, pta9999.pta047.pta-grc1, pta9999.pta048.pta-grc1, pta9999.pta049.pta-grc1, pta9999.pta050.pta-grc1, pta9999.pta051.pta-grc1, pta9999.pta052.pta-grc1, pta9999.pta053.pta-grc1, pta9999.pta054.pta-grc1, pta9999.pta055.pta-grc1, pta9999.pta056.pta-grc1, pta9999.pta059.pta-grc1, pta9999.pta060.pta-grc1, pta9999.pta060.pta-grc2, pta9999.pta061.pta-grc1, pta9999.pta061.pta-grc2, pta9999.pta062.pta-grc1, pta9999.pta062.pta-grc2, pta9999.pta063.pta-grc1, pta9999.pta064.pta-grc1, pta9999.pta065.pta-grc1, pta9999.pta066.pta-grc1, pta9999.pta067.pta-grc1, pta9999.pta068.pta-grc1, pta9999.pta069.pta-grc1, pta9999.pta070.pta-grc1, pta9999.pta071.pta-grc1, pta9999.pta072.pta-grc1, pta9999.pta073.pta-grc1, pta9999.pta074.pta-grc1, pta9999.pta075.pta-grc1, pta9999.pta076.pta-grc1, pta9999.pta077.pta-grc1, pta9999.pta078.pta-grc1, pta9999.pta079.pta-grc1, pta9999.pta080.pta-grc1, pta9999.pta081.pta-grc1, pta9999.pta082.pta-grc1, pta9999.pta083.pta-grc1, pta9999.pta084.pta-grc1, pta9999.pta085.pta-grc1, pta9999.pta086.pta-grc1, pta9999.pta087.pta-grc1, pta9999.pta088.pta-grc1, pta9999.pta089.pta-grc1".split(", ")

# %%
## merge both lists to dict
concordance = dict(zip(abbrev_grc,ptaids_grc))

# %%
resolver = CtsCapitainsLocalResolver(["/home/stockhausen/Dokumente/projekte/pta_data"])


# %%
# print("{}\t{}".format(text.reference, text.text.replace("\n","")))

# %%
def ctsformat_reference(reference):
    """
    Format reference as CTS reference according to concordance, refurns list of ctsref
    """
    temp = reference.split(":")
    prefix = ":".join(temp[:2])
    chap = temp[2]
    verstemp = ":".join(temp[3:])
    # sequence of verses
    if "-" in verstemp:
        if ":" in verstemp:
            verses = verstemp.split("-")
            chapvers = ".".join(verses[1].split(":"))
            ctsref = ["urn:cts:pta:"+concordance[prefix]+":"+chap+"."+verses[0]+"-"+chapvers]
        elif "." in verstemp:
            verses = verstemp.split("-")
            if "." in verses[0] and "." in verses[1]:
                pointedverse1 = verses[0].split(".")
                pointedverse2 = verses[1].split(".")
                ref0 = chap+"."+pointedverse1[0]
                ref1 = chap+"."+pointedverse1[1]+"-"+chap+"."+pointedverse2[0]
                ref2 = chap+"."+pointedverse2[1]
                ctsref = ["urn:cts:pta:"+concordance[prefix]+":"+ref0,"urn:cts:pta:"+concordance[prefix]+":"+ref1,"urn:cts:pta:"+concordance[prefix]+":"+ref2]
            elif "." in verses[0]:
                pointedverse = verses[0].split(".")
                ref = chap+"."+pointedverse[1]+"-"+chap+"."+verses[1]
                ctsref = ["urn:cts:pta:"+concordance[prefix]+":"+chap+"."+pointedverse[0],"urn:cts:pta:"+concordance[prefix]+":"+ref]
            else:
                pointedverse = verses[1].split(".")
                ref = chap+"."+verses[0]+"-"+chap+"."+pointedverse[0]
                ctsref = ["urn:cts:pta:"+concordance[prefix]+":"+ref,"urn:cts:pta:"+concordance[prefix]+":"+chap+"."+pointedverse[1]]
        else:
            verses = verstemp.split("-")
            ref = chap+"."+verses[0]+"-"+chap+"."+verses[1]
            ctsref = ["urn:cts:pta:"+concordance[prefix]+":"+ref]
    # special case: two separate verses in same chapter, not available in CTS, need to split therefore
    elif "." in verstemp:
        verses = verstemp.split(".")
        ctsref = ["urn:cts:pta:"+concordance[prefix]+":"+chap+"."+verses[0],"urn:cts:pta:"+concordance[prefix]+":"+chap+"."+verses[1]]
    # no verse, only chapter
    elif verstemp == "":
        ctsref = ["urn:cts:pta:"+concordance[prefix]+":"+chap]
    # single verse
    else:
        ref = chap+"."+verstemp
        ctsref = ["urn:cts:pta:"+concordance[prefix]+":"+ref]
    return ctsref

# %%
def index_reference(reference):
    """
    Format reference as for index, refurns list of references
    """
    temp = reference.split(":")
    chap = temp[1]+":"+temp[2]
    verstemp = ":".join(temp[3:])
    # sequence of verses
    if "-" in verstemp:
        if ":" in verstemp:
            verses = verstemp.split("-")
            ref = [chap+":"+verses[0]+"-"+verses[1]]
        elif "." in verstemp:
            verses = verstemp.split("-")
            if "." in verses[0] and "." in verses[1]:
                pointedverse1 = verses[0].split(".")
                pointedverse2 = verses[1].split(".")
                ref0 = chap+"."+pointedverse1[0]
                ref1 = chap+"."+pointedverse1[1]+"-"+chap+"."+pointedverse2[0]
                ref2 = chap+"."+pointedverse2[1]
                ref = [ref0,ref1,ref2]
            elif "." in verses[0]:
                pointedverse = verses[0].split(".")
                ref = chap+"."+pointedverse[1]+"-"+chap+"."+verses[1]
                ref = [chap+"."+pointedverse[0],ref]
            else:
                pointedverse = verses[1].split(".")
                ref = [chap+":"+verses[0]+"-"+chap+":"+pointedverse[0],chap+":"+pointedverse[1]]
        else:
            verses = verstemp.split("-")
            ref = [chap+":"+verses[0]+"-"+chap+":"+verses[1]]
    # special case: two separate verses in same chapter, not available in CTS, need to split therefore
    elif "." in verstemp:
        verses = verstemp.split(".")
        ref = [chap+":"+verses[0],chap+":"+verses[1]]
    # no verse, only chapter
    elif verstemp == "":
        ref = [chap]
    # single verse
    else:
        ref = [chap+":"+verstemp]
    return ref

# %%
# print(ctsformat_reference("NA:Act:10-11"))

# %%
def hexapla_reference(reference):    
    """
    handle Hexapla references, uses corresp attrib in form: "Field I 7"
    """
    temp = reference.split(" ")
    if temp[1] == "II":
        volume = "02"
    else:
        volume = "01"
    if "-" in temp[2]:
        page = temp[2].split("-")[0]
    else:
        page = temp[2]
    hexaref = "https://archive.org/details/origenhexapla"+volume+"unknuoft/page/"+page+"/mode/2up"
    return hexaref 

# %%
def vulg_reference(reference):    
    """
    handle Vulgata references, due to no free licence links to Bibelwissenschaft website for Vulgata ed. Weber/Gryson"
    """
    temp = reference.split(":")
    ref = temp[1]+temp[2]+","+temp[3]
    vulgref = "http://www.bibelwissenschaft.de/bibelstelle/"+ref+"/VULG/"
    return vulgref 

# %%
def get_git_revision_short_hash(repo):
    os.chdir(repo)
    return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
# get_git_revision_short_hash("/home/stockhausen/Dokumente/projekte/pta_data/")

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
        strip_tags = ['said', 'gap', 'app'] # remove not needed tags to avoid problems
        for tag in strip_tags: 
            for match in soup.find_all(tag):
                match.replaceWithChildren()
        try:
            body = soup.find("text")
            title = soup.find('title')
            file_dict["urn"] = urn
            file_dict["title"] = title.text
            file_dict["body"] = body
            pta_dict.append(file_dict)
        except:
            print(xml_path)
    return pta_dict

# %%
def extract_all_quotes(files_path):
    '''Extract all persons from all files in list of dictionaries with 
    type (biblical, else), key, content and urn + counter of file'''
    file_list = load_files(files_path)
    results = []
    for entry in file_list:
        body = BeautifulSoup(str(entry["body"]), features="xml")
        counter = 0
        for quote in body.find_all("ref"):
            counter = counter+1
            quote_entry = {}
            try:
                quote_entry["ID"] = quote["cref"]
                quote_entry["urn"] = entry["urn"]+":b"+str(counter)
                try:
                    quote_entry["corresp"] = quote["corresp"]
                except:
                    quote_entry["corresp"] = ""
                results.append(quote_entry)
            except:
                print(quote)
    return results

# %%
def clean(text):
    """Remove superfluous spaces and linebreaks from extracted text"""
    cleaned = re.sub("\n","",text)
    cleaned = re.sub("  "," ",cleaned)
    cleaned = re.sub("\s([.,·]+)","\\1",cleaned)
    return cleaned

# %%
def enrich_referencetexts(files_path):
    """"Enrich references with quotes from Bible text in PTA (Rahlfs, SBLGNT)"""
    quotes = extract_all_quotes(files_path)
    df = pd.DataFrame(quotes)
    allquotes = [{**g.to_dict(orient='list'), **{'ID': k}} for k, g in df.groupby('ID')]
    print("All biblical references extracted")
    results = []
    for quote in allquotes:
        #print(quote)
        extended = {}
        extended["ID"] = quote["ID"]
        extended["urn"] = quote["urn"]
        extended["edition"] = quote["ID"].split(":")[0]
        extended["book"] = quote["ID"].split(":")[1]
        extended["reference"] = ":".join(quote["ID"].split(":")[2:])
        extended["chapter"] = quote["ID"].split(":")[2]
        try:
            vers = quote["ID"].split(":")[3]
            if "." in vers:
                extended["versFrom"] = vers.split(".")[0]
                extended["versTo"] = vers.split(".")[1]
            elif "-" in vers:
                extended["versFrom"] = vers.split("-")[0]
                extended["versTo"] = vers.split("-")[1]
            else:
                extended["versFrom"] = vers
                extended["versTo"] = ""
        except:
            # only chapter, no verse
            extended["versFrom"] = ""
            extended["versTo"] = ""
        if "LXX" in quote["ID"] or "NA" in quote["ID"]:
            extended["CTS"] = ctsformat_reference(quote["ID"])
            list = []
            for cts in extended["CTS"]:
                prefix,reference = cts.rsplit(":", 1)
                try:
                    resolved = resolver.getTextualNode(prefix,subreference=reference)
                    text = resolved.export(Mimetypes.PLAINTEXT, exclude=["tei:rdg"])
                    list.append(clean(text))
                except:
                    print("Error: "+quote["ID"]+" not found")
                extended["text"] = " … ".join(list)
        elif "Hexapla" in quote["ID"]:
            try:
                extended["link"] = hexapla_reference("".join(set(quote["corresp"])))
            except:
                print(quote["ID"])
        elif "Vg" in quote["ID"]:
            try:
                extended["link"] = vulg_reference(quote["ID"])
            except:
                print(quote["ID"])
        else:
            print(quote["ID"])
        results.append(extended)
    return results

# %% [markdown]
# ## Do conversion
# 

# %%
# add files path here
files_path = "/home/stockhausen/Dokumente/projekte/pta_data/data/pta0001/pta001/*.xml"
this_path = "/".join(files_path.split("/")[:6])

# %%
quotes_enriched = enrich_referencetexts(files_path)

# %%
""""Reformat list of dicts to dict with ID as key"""
biblequotes = {item['ID']:item for item in quotes_enriched}


# %%
# get current githash
githash = get_git_revision_short_hash(this_path)

# %% [markdown]
# ## Write to json

# %%
with open('/home/stockhausen/Dokumente/projekte/pta_metadata/pta_biblereferences.json', 'w') as fout:
    json.dump(biblequotes, fout, indent=4, ensure_ascii=False)

# %% [markdown]
# ## Write data to biblereferences LOD files
# 
# At the moment only csv is provided.
# 
# Beacon, rdf only possible, if biblical references can be refered to by URL. (One option could be https://www.bibelwissenschaft.de...)
# 

# %%
# Prepare links, drop unnecessary keys, add link 
min_references = []
for reference in quotes_enriched:
    new_ids = index_reference(reference["ID"])
    index_urns = []
    for new_id in new_ids:
        index_urn = "https://pta.bbaw.de/biblical-reference/"+new_id
        index_urns.append(index_urn)
    new_urns = []
    for urn in reference["urn"]:
        this_urn = "https://pta.bbaw.de/text/"+githash+"/urn:cts:pta:"+urn
        new_urns.append(this_urn)
    reference["new_ids"] = new_ids
    reference["index_urns"] = index_urns    
    reference["new_urns"] = new_urns
    entries_to_remove = ('ID','edition','book','reference','chapter','versFrom','versTo','link','CTS','text')
    for k in entries_to_remove:
        reference.pop(k, None)
    min_references.append(reference)


# %%
# CSV: Link to quotation in PTA-Text, Biblical reference
df = pd.DataFrame(min_references)
df.drop(['urn','index_urns'], axis=1, inplace=True)
df.replace("", float("NaN"), inplace=True)
s = df.explode('new_urns')
s = s.explode('new_ids')
s = s[['new_urns','new_ids']]
# write to csv
s.to_csv('/home/stockhausen/Dokumente/projekte/pta_metadata/LOD/pta_biblereferences.csv', index=False, header=['Quotation-URL','Reference'])


# %%
# CSV: Biblical reference, Link to PTA-Bible-Index
df = pd.DataFrame(min_references)
df.drop(['urn','new_urns'], axis=1, inplace=True)
df.replace("", float("NaN"), inplace=True)
s = df.explode('index_urns')
s = s.explode('new_ids')
s = s[['new_ids','index_urns']]
# write to csv
s.to_csv('/home/stockhausen/Dokumente/projekte/pta_metadata/LOD/pta_biblereferences_index.csv', index=False, header=['Reference','Reference in Index'])



