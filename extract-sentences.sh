# this script extracts short sentences talking about soccer players from the full
# dump of wikipedia

DUMP="../itwiki-latest-pages-articles.xml.bz2"
SOCCER_IDS=../soccer_ids
TOKEN_LIST=resources/tokens.list
SENT_DIR=../sentences
CORPUS_DIR=../corpus
EXTRACT_DIR=../extracted
ALL_ARTS=../all-articles
MAPPING=../mapping.json
MAX_LENGTH=40

mkdir -p "$SENT_DIR" "$CORPUS_DIR" "$EXTRACT_DIR"

echo "extracting the sentences from the dump"
zcat $DUMP | lib/WikiExtractor.py -o $EXTRACT_DIR

echo "merging into a single big file"
find $EXTRACT_DIR/*/* -type f -exec cat '{}' \; > $ALL_ARTS

echo "extracting sentences"
python process_articles.py $SOCCER_IDS $ALL_ARTS $TOKEN_LIST $SENT_DIR $MAPPING
