import Pyro4
import click
from date_normalizer import DateNormalizer


class NormalizerWrapper(DateNormalizer):
    def normalize_many(self, expression):
        return [x for x in super(NormalizerWrapper, self).normalize_many(expression)]


@click.command()
@click.option('--port', default=12937)
@click.option('--ns/--no-ns', default=False, help='Use a nameserver')
def main(port, ns):
    Pyro4.Daemon.serveSimple({
        NormalizerWrapper: 'date_normalizer',
    }, port=port, ns=ns)


if __name__ == '__main__':
    main()
