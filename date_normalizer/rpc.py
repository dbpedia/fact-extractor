""" This module is a RPC interface exposing the date normalizer """
import Pyro4
import click
from date_normalizer import DateNormalizer


class NormalizerWrapper(DateNormalizer):
    """ Wrapper for the date normalizer """

    def normalize_many(self, expression):
        """ Wraps :meth:`date_normalizer.date_normalizer.DateNormalizer.normalize_many`
        because it is not possible to serialize generators

        :param str expression: The expression to serialize
        :return: All the normalized entities
        :rtype: list
        """
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
