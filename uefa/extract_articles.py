import click
import json
import codecs
from lxml import etree


@click.command()
@click.argument('uefa_xml', type=click.File('r', 'utf8'))
@click.argument('out_xml', type=click.File('w', 'utf8'))
@click.argument('out_mapping')
@click.option('--debug/--no-debug', default=False)
def main(uefa_xml, out_xml, out_mapping, debug):
    uefa_root = etree.parse(uefa_xml).getroot()

    mapping = {}
    for article in uefa_root.iter('file'):
        id = article.xpath('@id')[0]
        url = article.xpath('head/url/text()')[0]
        title = article.xpath('head/title/text()')[0]
        content = article.xpath('content/text()')[0]
        
        mapping[id] = title
        out_xml.write(u'<doc id="%s" url="%s" title="%s">\n' % (id, url, 
                      title.replace('"', "'")))
        out_xml.write(u'%s\n</doc>\n' % content)

        if debug:
            print '[%s] %s' % (id, title)

    with codecs.open(out_mapping, 'wb', 'utf8') as f:
        json.dump(mapping, f, indent=2)

if __name__ == '__main__':
    main()
