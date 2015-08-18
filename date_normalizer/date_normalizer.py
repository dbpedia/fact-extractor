import yaml
import re
import os


class DateNormalizer(object):
    """
    find matches in text strings using regular expressions and transforms them
    according to a pattern transformation expression evaluated on the match

    the specifications are given in yaml format and allow to define meta functions
    and meta variables as well as the pattern and transformation rules themselves.

    meta variables will be placed inside patterns which use them in order to
    make writing patterns easier. meta variables will be available to use from
    inside the meta functions too as a dictionary named meta_vars

    a pattern transformation expression is an expression which will be evaluated
    if the corresponding regular expression matches. the pattern transformation
    will have access to all the meta functions and meta variables defined and
    to a variable named 'match' containing the regex match found
    """

    def __init__(self):
        path = os.path.join(os.path.dirname(__file__), 'regexes.yml')
        with open(path) as f:
            specs = yaml.load(f)

        self._meta_init(specs)
        basic_r = {name: pattern for name, pattern in self.meta_vars.iteritems()}

        self.regexes = {}
        for category, regexes in specs.iteritems():
            regexes = sum((x.items() for x in regexes), [])
            self.regexes[category] = [(re.compile(pattern.replace(' ', '\\s+') \
                                                         .format(**basic_r),
                                                  re.IGNORECASE), result)
                                      for pattern, result in regexes]

    def _meta_init(self, specs):
        """ reads the meta variables and the meta functions from the specification """
        self.meta_vars = specs.pop('__meta_vars__')

        # compile meta functions in a dictionary
        self.meta_funcs = {}
        for f in specs.pop('__meta_funcs__'):
            exec f in self.meta_funcs

        # make meta variables available to the meta functions just defined
        self.meta_funcs['__builtins__']['meta_vars'] = self.meta_vars

        self.globals = self.meta_funcs
        self.globals.update(self.meta_vars)

    def normalize_one(self, expression):
        """ find the first matching part in the given expression """
        expression = expression.lower()
        for category, regexes in self.regexes.iteritems():
            for regex, transform in regexes:
                match = regex.search(expression)
                if match:
                    return self._process_match(category, transform, match)
        else:
            return (-1, -1), None, None

    def normalize_many(self, expression):
        """ find all the matching entities in the given expression expression """
        expression = expression.lower()
        for category, regexes in self.regexes.iteritems():
            for regex, transform in regexes:
                for match in regex.finditer(expression):
                    yield self._process_match(category, transform, match)

    def _process_match(self, category, transform, match):
        result = eval(transform, self.globals, {'match': match})
        return match.span(), category, result


if __name__ == '__main__':
    from pprint import pprint
    with open('tests.yml') as f:
        test_cases = yaml.load(f)

    d = DateNormalizer()
    for text, expected in test_cases.iteritems():
        position, category, result = d.normalize_one(text)
        if result != expected:
            print 'expected %s but got %s on %s' % (expected, result, text)

    print 'All tests run'
