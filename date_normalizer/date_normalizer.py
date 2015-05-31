import yaml
import re

class DateNormalizer:
    def __init__(self):
        with open('regexes.yml') as f:
            specs = yaml.load(f)

        basic_r = {name: pattern for name, pattern in specs['basic'].iteritems()}
        specs.pop('basic')

        self.regexes = {}
        for category, regexes in specs.iteritems():
            self.regexes[category] = [(re.compile(pattern.format(**basic_r)), result)
                                      for pattern, result in regexes.iteritems()]

    def normalize(self, expression):
        for category, regexes in self.regexes.iteritems():
            for regex, result in regexes:
                match = regex.search(expression)
                if match:
                    return result.format(match=match.groupdict().get('match'))
        else:
            return None


if __name__ == '__main__':
    with open('tests.yml') as f:
        test_cases = yaml.load(f)

    d = DateNormalizer()
    for text, expected in test_cases.iteritems():
        result = d.normalize(text)
        assert result == expected, 'expected %s but got %s on %s' % (expected, result, text)
    else:
        print 'All test passed'
