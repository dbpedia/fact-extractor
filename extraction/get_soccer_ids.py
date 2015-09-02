import requests
import click

ENDPOINT = 'http://%s.dbpedia.org/sparql'
QUERY = 'SELECT ?id WHERE { ?s a dbpedia-owl:SoccerPlayer ; dbpedia-owl:wikiPageID ?id . } OFFSET %d LIMIT 1000'


@click.command()
@click.argument('outfile', type=click.File('w'))
@click.option('--lang', default='it')
def main(outfile, lang):
    """ gets all the wikipedia ids of pages about soccer players """
    ids = []
    finished = False
    offset = 0
    while not finished:
        url = ENDPOINT % lang
        query = QUERY % offset
        r = requests.get(url, params={'query': query, 'format': 'text/csv'})
        lines = r.content.split('\n')
        ids += lines[1:-1]
        finished = len(lines) < 1001
        offset += 1000
    ids.sort()
    outfile.write('\n'.join(ids))


if __name__ == '__main__':
    main()
