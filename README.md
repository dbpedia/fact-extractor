# Fact Extractor
Fact Extraction from Wikipedia Text

## Intro
The [DBpedia Extraction Framework](http://dbpedia.org) is pretty much mature when dealing with Wikipedia semi-structured content like infoboxes, links and categories.  
However, unstructured content (typically text) plays the most crucial role, due to the amount of knowledge it can deliver, and few efforts have been carried out to extract structured data out of it.  
For instance, given the [Germany Football Team](http://en.wikipedia.org/wiki/Germany_national_football_team) article, we want to extract a set of meaningful facts and structure them in machine-readable statements.  
The following sentence:
> In Euro 1992, Germany reached the final, but lost 0–2 to Denmark

would produce statements (triples) like:
```
<Germany, defeat, Denmark>
<defeat, score, 0–2>
<defeat, winner, Denmark>
<defeat, competition, Euro 1992>
```

## High-level Workflow
**INPUT** = Wikipedia corpus

### Corpus Analysis
1. Corpus Raw Text Extraction
2. Verb Extraction
3. Verb Ranking

### Unsupervised Fact Extraction
1. Entity Linking
2. Frame Classification
3. Dataset Production

### Supervised Fact Extraction
1. Training Set Creation
2. Classifier Training
3. Frame Classification
4. Dataset Production

## Get Ready
- **Python**, **pip** and **Java** should be there in your machine, aren't they?
- Install all the Python requirements:
```
$ pip install -r requirements.txt
```
- Install the third party dependencies:
    - [TreeTagger](http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/)
    - [libsvm](http://www.csie.ntu.edu.tw/~cjlin/libsvm/)
- Request access to a supported entity linking API:
    - [The Wiki Machine](mailto:giuliano@fbk.eu)
    - [Dandelion API](https://dandelion.eu/accounts/register/?next=/docs/api/datatxt/nex/getting-started/)
- Put your API credentials into a new file `lib/secrets.py` as follows:
```
# For The Wiki Machine
TWM_URL = 'your service URL'
TWM_APPID = 'your app ID'
TWM_APPKEY = 'your app key'

# For Dandelion API
NEX_URL = 'https://api.dandelion.eu/datatxt/nex/v1'
NEX_APPID = 'your app ID'
NEX_APPKEY = 'your app key'
```

## Get Started
Here is how to produce the *unsupervised Italian soccer dataset*:
```
$ wget http://dumps.wikimedia.org/itwiki/latest/itwiki-latest-pages-articles.xml.bz2
$ make extract-pages
$ make extract-soccer
$ make extract-sentences-baseline
$ make unsupervised-run
```
Done!

### Note: Wikipedia Dump Pre-processing
Wikipedia dumps are packaged as XML documents and contain text formatted according to the [Mediawiki markup syntax](https://www.mediawiki.org/wiki/Help:Formatting), with [templates](https://www.mediawiki.org/wiki/Help:Templates) to be transcluded.
To obtain a raw text corpus, we use the [WikiExtractor](https://github.com/attardi/wikiextractor), integrated in a frozen version [here](lib/WikiExtractor.py).

## Development Policy
Contributors should follow the standard team development practices:

1. Branch out of master;
2. Commit **frequently** with **clear** messages;
3. Make a pull request.

## Coding Style
Pull requests not complying to these guidelines will be ignored.
- Use *4 spaces* (soft tab) for indentation;
- Naming conventions
  - use an *underscore* as a word separator (files, variables, functions);
  - constants are *UPPERCASE*;
  - anything else is *lowercase*.
- Use *2* empty lines to separate functions;
- Write docstrings according to *[PEP 287](https://www.python.org/dev/peps/pep-0287/)*, with a special attention to [field lists](http://sphinx-doc.org/domains.html#info-field-lists). IDEs like [PyCharm](https://www.jetbrains.com/pycharm/help/creating-documentation-comments.html) will do the job.

## References
- [FrameNet: A Knowledge Base for Natural Language Processing](http://www.aclweb.org/anthology/W/W14/W14-3001.pdf)
- [Outsourcing FrameNet to the Crowd](http://www.aclweb.org/anthology/P13-2130)
- [Frame Semantics Annotation Made Easy with DBpedia](http://ceur-ws.org/Vol-1030/paper-03.pdf)

## License
The source code is under the terms of the [GNU General Public License, version 3](http://www.gnu.org/licenses/gpl.html).
