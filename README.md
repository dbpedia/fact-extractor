# Fact Extractor
Fact Extraction from Wikipedia Text

## Intro
The DBpedia Extraction Framework is pretty much mature when dealing with Wikipedia semi-structured content like infoboxes, links and categories.  
However, unstructured content (typically text) plays the most crucial role, due to the amount of knowledge it can deliver, and few efforts have been carried out to extract structured data out of it.  
For instance, given the [Germany Football Team](http://en.wikipedia.org/wiki/Germany_national_football_team) article, we want to extract a set of meaningful facts and structure them in machine-readable statements.  
The following sentence:
> In Euro 1992, Germany reached the final, but lost 0–2 to Denmark

would produce statements like:
```
<Germany, defeat, Denmark>
<defeat, score, 0–2>
<defeat, winner, Denmark>
<defeat, competition, Euro 1992>
```

## High-level Workflow + Related Code
**INPUT** = Wikipedia corpus (e.g., [the latest Italian chapter](http://dumps.wikimedia.org/itwiki/latest/itwiki-latest-pages-articles.xml.bz2))

1. Verb Extraction
  1. [Extract raw text from Wikipedia dump](lib/WikiExtractor.py), forked from [this repo](https://github.com/bwbaugh/wikipedia-extractor)
  2. [Extract a sub-corpus based on Wiki IDs](get_soccer_players_articles.py)
  3. [Verb Extraction](extract_verbs.sh)
2. Verb Ranking
  1. [Build a frequency dictionary of lemmas](make_lemma_freq.py)
  2. [TF/IDF-based token ranking](tf_idfize.py), using the TF/IDF module forked from [this repo](https://github.com/hrs/python-tf-idf)
  3. [Lemma ranking based on the token-to-lemma map](compute_stdev_by_lemma.py)
3. Training Set Creation
  1. [Build CrowdFlower input spreadsheet](create_crowdflower_input.py)
4. Frame Classifier Training
  1. [Translate CrowdFlower results into training data format](crowdflower_results_into_training_data.py)
  2. [Train classifier](use_classifier.sh)
5. Frame Extraction

## Requirements
- [TreeTagger](http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/)
- [libsvm](http://www.csie.ntu.edu.tw/~cjlin/libsvm/)
- csplit from [GNU coreutils 8.23](https://www.gnu.org/software/coreutils/) or later

## Warm-up Tasks
See the [issues](../../issues).

## Development Policy
Committers should follow the standard team development practices:

1. Start working on a task
2. Branch out of master
3. Commit **frequently** with **clear** messages
4. Make a pull request

## References
- [FrameNet: A Knowledge Base for Natural Language Processing](http://www.aclweb.org/anthology/W/W14/W14-3001.pdf)
- [Outsourcing FrameNet to the Crowd](http://www.aclweb.org/anthology/P13-2130)
- [Frame Semantics Annotation Made Easy with DBpedia](http://ceur-ws.org/Vol-1030/paper-03.pdf)

## License
The source code is under the terms of the [GNU General Public License, version 2](http://www.gnu.org/licenses/gpl-2.0.html).
