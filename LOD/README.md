# Linked Open Data

This folder contains information to link to the resources in the [Patristic Text Archive (PTA)](https://pta.bbaw.de). Currently we provide this information as tables in csv-format, as [BEACON](https://gbv.github.io/beaconspec/beacon.html) and as [RDF](https://www.w3.org/RDF/) files (turtle, rdf/xml, JSON-LD).

## Authors of texts in the PTA
using [Gemeinsame Normdatei](http://d-nb.info/gnd/) and [Wikidata](https://www.wikidata.org/)

- `pta_authors.csv` (columns: GND-ID,Wikidata-Entity,URN)
- `pta_authors_gnd_beacon.txt`, `pta_authors_gnd.xml`, `pta_authors_gnd.ttl`, `pta_authors_gnd.json-ld` (all authors in PTA identified by a GND-ID)
- `pta_authors_wikidata_beacon.txt`, `pta_authors_wikidata.xml`, `pta_authors_wikidata.ttl`, `pta_authors_wikidata.json-ld` (all authors in PTA identified by a Wikidata-ID)

## Works in the PTA
using [Clavis Clavium](https://clavis.brepols.net/clacla) and [Pinakes](https://pinakes.irht.cnrs.fr)

- `pta_works.csv` (columns: CPG no.,BHG no.,Pinakes-Oeuvre no.,URN)
- `pta_works_cpg_beacon.txt`, `pta_works_cpg.xml`, `pta_works_cpg.ttl`, `pta_works_cpg.json-ld` (all works in PTA identified by a Clavis Patrum Graecorum number)
- `pta_works_bhg_beacon.txt`, `pta_works_bhg.xml`, `pta_works_bhg.ttl`, `pta_works_bhg.json-ld` (all works in PTA identified by a Bibliographia Hagriographica Graeca number)
- `pta_works_pinakes-oeuvre_beacon.txt`, `pta_works_pinakes-oeuvre.xml`, `pta_works_pinakes-oeuvre.ttl`, `pta_works_pinakes-oeuvre.json-ld` (all works in PTA identified by a Pinakes Oeuvre number)

## Manuscript descriptions in the PTA
using [Pinakes](https://pinakes.irht.cnrs.fr)

- `pta_manuscripts_diktyon.csv` (columns: Diktyon-ID,URN)
- `pta_manuscripts_diktyon_beacon.txt`, `pta_manuscripts_diktyon.xml`, `pta_manuscripts_diktyon.ttl`, `pta_manuscripts_diktyon.json-ld` (all manuscript descriptions identified by a Diktyon-ID)

## Biblical references in the texts of the PTA
Editions used are: Hexapla, LXX = Septuagint, NA = Greek New Testament, Vg = Vulgata

Biblical books are abbreviated as follows: 
- Gn, Ex, Lv, Num, Dt, Jos, Judg, Rt, 1Sa, 2Sa, 1Ko, 2Ko, 1Chr, 2Chr, 3Esr, Esr, Est, Jdt, Tob, 1Mak, 2Mak, 3Mak, 4Mak, Ps, Oden, Prov, Eccl, Song, Job, Wis, Sir, PsSal, Hos, Am, Mi, Joel, Ob, Jon, Nah, Hab, Zeph, Hag, Sach, Mal, Is, Jr, Bar, Lam, EpistJer, Hes, Sus, Dn, Bel
- Mt, Mk, Lk, Jn, Act, Rom, 1Cor, 2Cor, Gal, Eph, Phil, Col, 1Th, 2Th, 1Tim, 2Tim, Tt, Phm, Heb, Jak, 1P, 2P, 1Jn, 2Jn, 3Jn, Jud, Rev

### linking to the texts
- `pta_biblereferences.csv` (columns: Quotation-URL,Edition,Reference)

### linking to the index
- `pta_biblereferences_index.csv` (columns: Edition,Reference,Reference in Index)

## Persons mentioned in texts in the PTA
using [Gemeinsame Normdatei](http://d-nb.info/gnd/) and [Wikidata](https://www.wikidata.org/)

### linking to the texts
- `pta_persons.csv` (columns: GND-ID,Wikidata-Entity,mentioned in)
- `pta_persons_gnd_beacon.txt`, `pta_persons_gnd.xml`, `pta_persons_gnd.ttl`, `pta_persons_gnd.json-ld` (all persons identified by a GND-ID)
- `pta_persons_wikidata_beacon.txt`, `pta_persons_wikidata.xml`, `pta_persons_wikidata.ttl`, `pta_persons_wikidata.json-ld` (all persons identified by a Wikidata-ID)

### linking to the index
- `pta_persons_index.csv` (columns: GND-ID,Wikidata-Entity,Person in index)
- `pta_persons_gnd_index_beacon.txt`, `pta_persons_index_gnd.xml`, `pta_persons_index_gnd.ttl`, `pta_persons_index_gnd.json-ld` (all entries in the persons index identified by a GND-ID)
- `pta_persons_wikidata_index_beacon.txt`, `pta_persons_index_wikidata.xml`, `pta_persons_index_wikidata.ttl`, `pta_persons_index_wikidata.json-ld` (all entries in the persons index identified by a Wikidata-ID)

## Organisations and groups mentioned in texts in the PTA
using [Gemeinsame Normdatei](http://d-nb.info/gnd/) and [Wikidata](https://www.wikidata.org/)

### linking to the texts
- `pta_orgs.csv`(columns: GND-ID,Wikidata-Entity,mentioned in)
- `pta_orgs_gnd_beacon.txt`, `pta_orgs_gnd.xml`, `pta_orgs_gnd.ttl`, `pta_orgs_gnd.json-ld` (all orgs identified by a GND-ID)
- `pta_orgs_wikidata_beacon.txt`, `pta_orgs_wikidata.xml`, `pta_orgs_wikidata.ttl`, `pta_orgs_wikidata.json-ld` (all orgs identified by a Wikidata-ID)

### linking to the index
- `pta_orgs_index.csv` (columns: GND-ID,Wikidata-Entity,Person in index)
- `pta_orgs_gnd_index_beacon.txt`, `pta_orgs_index_gnd.xml`, `pta_orgs_index_gnd.ttl`, `pta_orgs_index_gnd.json-ld` (all entries in the orgs index identified by a GND-ID)
- `pta_orgs_wikidata_index_beacon.txt`, `pta_orgs_index_wikidata.xml`, `pta_orgs_index_wikidata.ttl`, `pta_orgs_index_wikidata.json-ld` (all entries in the orgs index identified by a Wikidata-ID)

## Places mentioned in texts in the PTA
using [Pleiades Gazetteer](https://pleiades.stoa.org/)

### linking to the texts
- `pta_places.csv` (columns: Place,mentioned in)
- `pta_places_beacon.txt`, `pta_places.xml`, `pta_places.ttl`, `pta_places.json-ld` (all places identified by a Pleiades Gazetteer ID)

### linking to the index
- `pta_places_index.csv` (columns: Place,Place in index)
- `pta_places_index_beacon.txt`, `pta_places_index.xml`, `pta_places_index.ttl`, `pta_places_index.json-ld` (all entries in the place index identified by a Pleiades Gazetteer ID)
