# (Meta-)Data for PTA frontend

This repository contains (meta-)data information used in the frontend of PTA at <https://pta.bbaw.de>.

## pta_data.json

This file is built from metadata files conforming to the [Capitains guidelines](http://capitains.org/pages/guidelines). It is converted from ` __cts__.xml`-files in the [pta_data-Respository](https://github.com/PatristicTextArchive/pta_data) to json. It contains the metadata for all textgroups, works, and versions of works.

## pta_manuscripts.json

The file is built from metadata in the teiHeader of the files in the [pta_manuscripts-Respository](https://github.com/PatristicTextArchive/pta_manuscripts). It contains the metadata for all manuscript descriptions.

## pta_persons.json

This file is built from the [TIPNR (Translators Individualised Proper Names with all References)](https://github.com/STEPBible/STEPBible-Data/blob/master/TIPNR%20-%20Translators%20Individualised%20Proper%20Names%20with%20all%20References%20-%20STEPBible.org%20CC%20BY.txt) and from the PTA persons registry. Data from these sources is extracted and mashed up for the [person index of PTA](https://pta.bbaw.de/indices).

## pta_places.json

This file is built from the [Pleiades Gazetteer](https://pleiades.stoa.org/) and the [TIPNR (Translators Individualised Proper Names with all References)](https://github.com/STEPBible/STEPBible-Data/blob/master/TIPNR%20-%20Translators%20Individualised%20Proper%20Names%20with%20all%20References%20-%20STEPBible.org%20CC%20BY.txt). Data from these sources is extracted and mashed up for the [place index of PTA](https://pta.bbaw.de/indices).
