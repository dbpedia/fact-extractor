import yaml
import re

class DateNormalizer:
    def __init__(self):
        with open('regexes.yml') as f:
            specs = yaml.load(f)

        self.meta = specs.pop('__meta__')
        basic_r = {name: pattern for name, pattern in self.meta.iteritems()}

        self.regexes = {}
        for category, regexes in specs.iteritems():
            regexes = sum((x.items() for x in regexes), [])
            self.regexes[category] = [(re.compile(pattern.format(**basic_r)), result)
                                      for pattern, result in regexes]

    def normalize(self, expression):
        for category, regexes in self.regexes.iteritems():
            for regex, result in regexes:
                match = regex.search(expression)
                if match:
                    return self._process_match(regex, result, match, category)
        else:
            return None


    def _process_match(self, regex, result, match, category):
        if category == 'time':
            match = match.groupdict().get('match')
            if not match:
                return result
            # convert month to two digits number
            months = self.meta['month'][1:-1].split('|')
            match = re.sub(self.meta['month'], string=match,
                           repl=lambda m: '%02d' % (1 + months.index(m.group(0))))
            match = '-'.join(reversed(match.split(' ')))  # '14 09 2010' --> 2010-09-14
            return result.format(match=match)

        elif category == 'duration':
            y1, y2= match.groupdict().get('y1'), match.groupdict().get('y2')
            if y1 and y2:
                duration = int(y2) - int(y1)
                return result.format(match=str(duration))

            match = match.groupdict().get('match')
            if not match:
                return result
            digit = re.search(self.meta['lit_digit'], match)
            if digit:
                num = self.meta['lit_digit'][1:-1].split('|').index(digit.group(0))
                return result.format(match=num if num > 0 else 1)
            else:
                return result.format(match=match)


if __name__ == '__main__':
    with open('tests.yml') as f:
        test_cases = yaml.load(f)

    d = DateNormalizer()
    for text, expected in test_cases.iteritems():
        result = d.normalize(text)
        if result != expected:
            print 'expected %s but got %s on %s' % (expected, result, text)
