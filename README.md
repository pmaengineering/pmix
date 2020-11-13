# PMIX: Questionnaire Language Utilities

A mixed bag of PMA2020 utilities. There are several functionalities all based
on working with spreadsheets. The main features are the following:

* [Analytics](#analytics)
* [Borrow](#borrow)
* [Cascade](#cascade)
* [Numbering](#numbering)
* [Renumber](#renumber)
* [Workbook](#workbook)
* [XlsDiff](#xlsdiff)

Formerly [`qlang`](https://github.com/jkpr/qlang), this package has been renamed and expanded to provide new
functionality and new command-line tools. The command line tools are described after installation.

This version requires Python 3 or later. Python 2 is not supported.


# Installation

This package is on PyPI! Run:

```
python3 -m pip install pmix
```

For developers, to install the bleeding edge from Github, run:

```
python3 -m pip install https://github.com/pmaengineering/pmix/zipball/master
```

# Development set up

Clone this repo

```
git clone https://github.com/pmaengineering/pmix.git
```

Set up a virtual environment

```
cd pmix
python3 -m venv env
```

Activate the virtual environment and install [`pip-tools`](https://github.com/jazzband/pip-tools)

```
source env/bin/activate
python -m pip install pip-tools
```

_Optional:_ Recompile `requirements-dev.txt` and `requirements.txt`

```
pip-compile requirements-dev.in
pip-compile
```

Sync the installed packages in the environment to the compiled requirements

```
pip-sync requirements-dev.txt requirements.txt
```

# Analytics

Usage

```
python3 -m pmix.analytics FILE1 [FILE2 ...]
```

creates a JSON file describing the prompts and fields for analytics.

# Borrow
The purpose of the Pmix *Borrow* module use to assist with translation
management of ODK forms. It is especially useful for merging translations from
one file into another.

## Command Line Usage
This module is called with

```
python3 -m pmix.borrow
```

and it does two things. Without the `-m` argument, it simply creates a
translation dictionary. The source string is in the first column, and the
target languages are in the subsequent columns. With the `-m` argument,
it creates a translation dictionary and then merges those translations into
the file specified by `-m`.

## Examples

1) Without `-m`,

```
python3 -m pmix.borrow FILE1 [FILE2 ...]
```

creates a translation dictionary from `FILE1 [FILE2 ...]`.

2) With `-m`,

```
python3 -m pmix.borrow -m TARGET FILE1 [FILE2 ...]
```

creates a translation dictionary from `FILE1 [FILE2 ...]` and then merges into `TARGET`.

In both examples, a default output filename is used, but one can be specified with the `-o` argument.

## The Input File
The input file can be 1 of 2 kinds:
1. A standard ODK file.
2. A raw translations file.

A raw translations file has the following form, using English and French as
examples:

| text::English | text::Français | ... | text::<language *n*\> |
| --- | --- | --- | --- |
| Hello! | Bonjour! | ... | <"Hello!" in language *n*\> |

## Diverse translations

There are a set of command-line options to work with diverse translations.

- `-D` This option, used without argument, means if text has diverse translations, do not borrow it. Only has effect with `-m`
- `-C CORRECT` This option marks a file as correct. Fill in `CORRECT` with a path to a source file. Its translations are given precedence over others. If there is only one input file, and it is correct, then there is no need to mark it correct because nothing can override it.
- `d DIVERSE` Give a language found in the forms for `DIVERSE`. This option is used without `-m`. It creates a file with only strings that have diverse translations in the supplied language from the source files.

---

## The Output File
A resultant file with merged translations has the following possible highlighting:

- ![#ffd3b6](https://placehold.it/15/ffd3b6/000000?text=+) *Orange* if the source and the translation are the same.
- ![#9acedf](https://placehold.it/15/9acedf/000000?text=+) *Blue* if the new translation changes the old translation.
- ![#d3d3d3](https://placehold.it/15/d3d3d3/000000?text=+) *Grey* if the new translation fills in a previously missing translation (blank cell).
- ![#85ca5d](https://placehold.it/15/85ca5d/000000?text=+) *Green* if the translation is not found in the TranslationDict, but there is a pre-existing translation.
- ![#ffaaa5](https://placehold.it/15/ffaaa5/000000?text=+) *Red* if translation is not found and there is no pre-existing translation.
- ![#fffa81](https://placehold.it/15/fffa81/000000?text=+) *Yellow* if using the `-D` option, shows strings that have diverse translations without inserting them.
- ![#ffffff](https://placehold.it/15/ffffff/000000?text=+) *No highlight* if the translation is the same as the pre-existing translation.

# Cascade

Usage

```
python3 -m pmix.cascade FILE
```

creates a new Excel spreadsheet after converting geographic identifiers from wide format to tall format.

# Numbering

Use the numbering mini-language and create question numbers for an ODK survey.

```
python3 -m pmix.numbering FILE
```

The program then looks for a column entitled "N" in the "survey" worksheet. It creates numbers based off of the
directives there and adds them to label columns.

# Renumber

Does bulk find / replace in an XLSForm.
Takes a renumber file and an XLSForm as input and writes an Excel file. 
The renumber file should be an Excel file with renumbering rules on the first tab.
Each row should use the first two columns (no need for a header). 
The first column is what is the "find" and the second column is the "replace" in a traditional find/replace setup.

Example:

| Col. A | Col. B |
| --- | --- |
| 109 | 101 |
| 113 | 102 |

This replaces all occurrences of `109` with `101` and replaces all occurrences of `113` with `102`.

The result is an Excel file with the following highlighting.


* ![#FFD3B9](https://placehold.it/15/FFD3B6/000000?text=+) *Orange/Peach* -- Cells that have text that match the "find" column, but that text is not changed with the replace. A `201` to `201` find/replace rule is valid.  
* ![#FFF78E](https://placehold.it/15/FFFA81/000000?text=+) *Light Yellow* -- Cells that were changed with a find/replace rule.

On the command line use 

```
python3 -m pmix.renumber path/to/xlsform.xlsx path/to/renumber/file.xlsx
```


# Workbook

There following features are offered:

1. Convert a worksheet to CSV with UTF-8 encoding and UNIX-style newlines.

```
python3 -m pmix.workbook FILE -c SHEET
```

2. Remove all trailing and leading whitespace from all text cells

```
python3 -m pmix.workbook FILE -w
```

# XlsDiff
A utility for showing the differences between two Excel files.

```
python3 -m pmix.xlsdiff FILE1 FILE2 --excel
```

The above command creates a new Excel file, creating a new version of `FILE2` 
with highlighting to show differences.

![#ff0000](https://placehold.it/15/ff0000/000000?text=+) *Red* -- Rows and columns that are duplicate so are not compared  
![#FFD3B9](https://placehold.it/15/FFD3B9/000000?text=+) *Orange/Peach* -- Rows and columns that are in the marked up file (`FILE2`), but not in the other  
![#FFF78E](https://placehold.it/15/FFF78E/000000?text=+) *Light Yellow* -- Cells that are different between the the two files  
![#00ff00](https://placehold.it/15/00ff00/000000?text=+) *Green* -- Rows that are in a changed order  

![XlsDiff](static/xlsdiff_output.png)

## Options
| Short Flag | Long Flag | Description |
|:-----------|:----------|:------------|
| -h | --help | Show this help message and exit. |
| -r | --reverse | Reverse the order of the base file and the new file for processing. |
| -s | --simple | Do a simple diff instead of the default ODK diff. |
| -e | --excel | Path to write Excel output. If flag is given with no argument then default out path is used. If flag is omitted, then write text output to STDOUT.|

# Bugs

Submit bug reports on the Github repository's issue tracker at [https://github.com/pmaengineering/pmix/issues](https://github.com/pmaengineering/pmix/issues).

---


# PMIX: Utilitaires de langue du questionnaire

Un mélange d'utilitaires PMA2020. Il y a plusieurs fonctionnalités toutes basées
sur le travail avec des feuilles de calcul. Les principales caractéristiques sont les suivantes:


* [Analytics](#analytics-1)
* [Borrow](#borrow-1)
* [Cascade](#cascade-1)
* [Numbering](#numbering-1)
* [Workbook](#workbook-1)
* [XlsDiff](#xlsdiff-1)


Anciennement [`qlang`](https://github.com/jkpr/qlang), ce package a été renommé et développé pour offrir de nouvelles fonctionnalités et de nouveaux outils de ligne de commande. Les outils de ligne de commande sont décrits après l'installation.

Cette  version nécessite Python 3 et plus . Python 2 est obsolete.


# Installation

Ce package est sur PyPI! Exécutez:

```
python3 -m pip install pmix
```

Pour les développeurs. Pour installer à partir de Github, exécutez:

```
python3 -m pip install https://github.com/pmaengineering/pmix/zipball/master
```

# Analytics

Usage

```
python3 -m pmix.analytics FILE1 [FILE2 ...]
```

crée un fichier JSON décrivant les invites et les champs pour analytics.


# Borrow

Le module Pmix *Borrow* utilisé pour faciliter la gestion de la traduction
des formulaires ODK. Il est particulièrement utile pour la fusion de traductions d’
un fichier dans un autre.

## Utilisation de la ligne de commande
Ce module est exécuté  avec

```
python3 -m pmix.borrow
```
et il fait deux choses. Sans l'argument `-m`, il crée simplement un
dictionnaire de traduction. La chaîne source est dans la première colonne et la
les langues cibles sont dans les colonnes suivantes. Avec l'argument `-m`,
il crée un dictionnaire de traduction puis fusionne ces traductions en
le fichier spécifié par `-m


## Exemples

1) Sans `-m`,

```
python3 -m pmix.borrow  FILE1 [FILE2 ...]
```

crée un dictionnaire de traduction à partir de `FILE1 [FILE2 ...]`.

2) Avec `-m`,

```
python3 -m pmix.borrow -m TARGET FILE1 [FILE2 ...]
``` 

crée un dictionnaire de traduction à partir de `FILE1 [FILE2 ...]` et fusionne ensuite dans `TARGET`.

Dans les deux exemples, un nom de fichier par défaut est utilisé, mais vous pouvez en spécifier un avec l'argument `-o`.

## Le fichier d'entrée
Le fichier d'entrée peut être d'un des 2 types suivants:
1. Un fichier ODK standard.
2. Un fichier de traduction brut.

Un fichier de traduction brut se présente sous la forme suivante, en anglais et en français
exemples:


| text::English | text::Français | ... | text::<language *n*\> |
| --- | --- | --- | --- |
| Hello! | Bonjour! | ... | <"Hello!" in language *n*\> |

## Diverse traductions

l existe un ensemble d’options de lignes de commande permettant de travailler avec différentes traductions.

- `-D` Cette option, utilisée sans argument, signifie que si le texte a plusieurs traductions, ne l'empruntez pas. N'a d'effet qu'avec `-m`
- `-C CORRECT` Cette option marque un fichier comme correct. Remplissez `CORRECT` avec un chemin d'accès à un fichier source. Ses traductions ont la priorité sur les autres. S'il n'y a qu'un seul fichier d'entrée et qu'il est correct, il n'est pas nécessaire de le marquer comme correct, car rien ne peut le remplacer.
- `-d DIVERSE` Identifie une langue trouvée dans les formulaires pour` DIVERSE`. Cette option est utilisée sans `-m`. Il crée un fichier avec uniquement des chaînes contenant diverses traductions dans la langue fournie à partir des fichiers source.

---

## Le fichier de sortie

Un fichier résultant avec des traductions fusionnées présente la mise en évidence suivante:

- ![# ffd3b6](https://placehold.it/15/ffd3b6/000000?text=+) *Orange* si la source et la traduction sont identiques.
- ![# 9acedf](https://placehold.it/15/9acedf/000000?text=+) *Bleu* si la nouvelle traduction modifie l'ancienne traduction.
- ![# d3d3d3](https://placehold.it/15/d3d3d3/000000?text=+) *Gris* si la nouvelle traduction remplit une traduction précédemment manquante (cellule vide).
- ![# 85ca5d](https://placehold.it/15/85ca5d/000000?text=+) *Vert* si la traduction ne se trouve pas dans TranslationDict, mais qu'il existe une traduction préexistante.
- ![# ffaaa5](https://placehold.it/15/ffaaa5/000000?text=+) *Rouge* si la traduction n'est pas trouvée et qu'il n'y a pas de traduction préexistante.
- ![# fffa81](https://placehold.it/15/fffa81/000000?text=+) *Jaune* si l’utilisation de l'option `-D`, affiche des chaînes contenant diverses traductions sans les insérer.
- ![#ffffff](https://placehold.it/15/ffffff/000000?text=+) *Pas de surbrillance* si la traduction est identique à la traduction existante.



# Cascade

Usage

```
python3 -m pmix. Fichier cascade
```

crée une nouvelle feuille de calcul Excel après avoir converti les identifiants géographiques du format large au format grand.

```
python3 -m pmix. Fichier en cascade
```

crée une nouvelle feuille de calcul Excel après avoir converti les identifiants géographiques du format large au format grand.

# Numérotation

Utilisez le mini-language de numbering et créez des numéros de question pour une enquête ODK.

```
python3 -m pmix.numbering FILE
```

Le programme recherche ensuite une colonne intitulée "N" dans la feuille de calcul "survey". Il crée des nombres basés sur le directives là-bas et les ajoute pour étiqueter les colonnes.


# Workbook

Les fonctionnalités suivantes sont offertes:

1. Convertir une feuille de calcul au format CSV avec codage UTF-8  et effectue des retours à la ligne de style UNIX.

```
python3 -m pmix.workbook FILE -c SHEET
```

2. Supprimer tous les espaces de début et de fin de toutes les cellules de texte

```
python3 -m pmix.workbook FILE -w
```

# XlsDiff

Un utilitaire pour montrer les différences entre deux fichiers Excel.

```
python3 -m pmix.xlsdiff FILE1 FILE2 —excel
```

La commande ci-dessus crée un nouveau fichier Excel, créant une nouvelle version de `FILE2`
avec mise en évidence pour montrer les différences.

* ![# ff0000](https://placehold.it/15/ff0000/000000?text=+) *Red* - Les lignes et les colonnes en double ne sont donc pas comparées.
* ![# FFD3B9](https://placehold.it/15/FFD3B9/000000?text=+) *Orange / Peach* - Les lignes et les colonnes se trouvent dans le fichier marqué (`FILE2`), mais pas dans L'autre
* ![# FFF78E](https://placehold.it/15/FFF78E/000000?text=+) *Light Yellow* - Cellules différentes entre les deux fichiers
* ![#00ff00](https://placehold.it/15/00ff00/000000?text=+) *Green* - Lignes dans un ordre modifié

![XlsDiff](static/xlsdiff_output.png)

## Options
| Drapeau court | Drapeau long | Description |
| ----------- | ---------- | ------------ |
| -h | --help | Afficher ce message d'aide et quitter. |
| -r | --reverse | Inverser l’ordre du fichier de base et du nouveau fichier à traiter. |
| -s | --simple | Faites un simple diff au lieu du diff par défaut ODK. |
| -e | --excel | Générer un ficher sortie Excel. Si flag est donné sans argument, alors le chemin par défaut est utilisé. Si le drapeau (flag) est omis, écrivez la sortie texte dans STDOUT.
