import requests
import click


QUERY = ('http://{}.dbpedia.org/sparql?default-graph-uri=&query=SELECT+%3Fid%0D%0AWHERE' +
        '+%7B%0D%0A++%3Fs+a+%3Chttp%3A%2F%2Fdbpedia.org%2Fontology%2FSoccerPlayer%3E+' +
        '%3B%0D%0A++++%3Chttp%3A%2F%2Fdbpedia.org%2Fontology%2FwikiPageID%3E+%3Fid+.' +
        '%0D%0A%7D%0D%0AORDER+BY+%3Fid%0D%0ALIMIT+1000%0D%0AOFFSET+{}&format=text%2Fcsv')


@click.command()
@click.argument('outfile', type=click.File('w'))
@click.option('--lang', default='it')
def main(outfile, lang):
    ids = []
    finished = False
    offset = 0
    while not finished:
        url = QUERY.format(lang, offset)
        r = requests.get(url)
        lines = r.content.split('\n')
        ids += lines[1:-1]
        finished = len(lines) < 1001
        offset += 1000

    outfile.write('\n'.join(ids))


if __name__ == '__main__':
    main()
