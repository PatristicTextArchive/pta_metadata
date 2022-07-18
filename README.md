# Patristic Text Archive (Meta-)Data
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6822080.svg)](https://doi.org/10.5281/zenodo.6822080)

This repository contains (meta-)data information used in the frontend of PTA at <https://pta.bbaw.de> and information for Linked Open Data (see folder `LOD`). The scripts used to generate this data are in the folder `scripts`.

## pta_data.json

This file is built from metadata files conforming to the [Capitains guidelines](http://capitains.org/pages/guidelines). It is converted from ` __cts__.xml`-files in the [pta_data-Respository](https://github.com/PatristicTextArchive/pta_data) to json. It contains the metadata for all textgroups, works, and versions of works.

## pta_statistics.json

This file is generated using the [CLTK](https://www.cltk.org) lemmatizer. It contains statistical data on words (and their number of occurences) and lemmata (and their number of occurences) in each work (identified by its urn); currently only the Greek and Latin texts are analyzed. Please note that the [CLTK stopword](Link) list was applied.

## pta_manuscripts.json

The file is built from metadata in the teiHeader of the files in the [pta_manuscripts-Respository](https://github.com/PatristicTextArchive/pta_manuscripts). It contains the metadata for all manuscript descriptions.

## pta_biblereferences.json
This file is built from all annotated biblical references in the PTA and enriched 
- with the text of the biblical quotes from Rahlfs' Septuaginta at <https://pta.bbaw.de/texts/pta9999> (in case of quotes from LXX) 
- with the text of the biblical quotes from SBLGNT at <https://pta.bbaw.de/texts/pta9999> (in case of quotes from the Greek New Testament)
- with links to Fields' edition of Origen's Hexapla at <https://archive.org/details/origenhexapla01unknuoft> and <https://archive.org/details/origenhexapla02unknuoft> (in case of quotes from the Hexapla)
- with links to Weber's/Gryson's edition of the Vulgata at <https://www.bibelwissenschaft.de> (in case of quotes from the Vulgata)

## pta_groups.json

This file is built from the PTA persons registry. Data from these sources is extracted and mashed up for the [group index of PTA](https://pta.bbaw.de/indices).

## pta_persons.json

This file is built from the [TIPNR (Translators Individualised Proper Names with all References)](https://github.com/STEPBible/STEPBible-Data/blob/master/TIPNR%20-%20Translators%20Individualised%20Proper%20Names%20with%20all%20References%20-%20STEPBible.org%20CC%20BY.txt) and from the PTA persons registry. Data from these sources is extracted and mashed up for the [person index of PTA](https://pta.bbaw.de/indices).

## pta_places.json

This file is built from the [Pleiades Gazetteer](https://pleiades.stoa.org/) and the [TIPNR (Translators Individualised Proper Names with all References)](https://github.com/STEPBible/STEPBible-Data/blob/master/TIPNR%20-%20Translators%20Individualised%20Proper%20Names%20with%20all%20References%20-%20STEPBible.org%20CC%20BY.txt). Data from these sources is extracted and mashed up for the [place index of PTA](https://pta.bbaw.de/indices).
