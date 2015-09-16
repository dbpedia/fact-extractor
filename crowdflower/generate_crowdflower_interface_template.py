#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import re
import argparse
import sys

# header with sentence
HEADER = '''<blockquote style="text-align:center">{{sentence}}</blockquote>
<hr />

<div class="row">
'''

# closing row div
FOOTER = "</div>"

# token block template
TOKEN_TEMPLATE = '''
    <!-- BEGIN token %(question_num)d -->
    {%% if %(token_field)s != 'No data available' %%}
    <div class="span2">
        <cml:radios label="{{%(token_field)s}}" class="rando" name="{{%(token_field)s}}" validates="required" gold="true">
            <cml:radio label="Nessuno"></cml:radio>
            %(fe_blocks)s
        </cml:radios>
    </div>
    {%% endif %%}
    <!-- END token %(question_num)d -->
'''

# fe block template
FE_TEMPLATE = '''
          {%% if %(fe_field)s != 'No data available' %%}
          <cml:radio label="{{%(fe_field)s}}"></cml:radio>
          {%% endif %%}'''


def generate_crowdflower_interface_template(input_csv, output_html=None):
    """ Generate CrowFlower interface template based on input data spredsheet

    :param file input_csv: CSV file with the input data
    :param output_html: File in which to write the output or None to return it as str
    :type output_html: file or None
    :return: The HTML interface if output_html is None otherwise None
    """
    # Get the filed names of the input data spreadsheet
    sheet = csv.DictReader(input_csv)
    fields = sheet.fieldnames
    # Get "fe_name[0-9][0-9]" fields
    fe_fields = [f for f in fields if re.match(r'fe_name[0-9]{2}$', f)]
    # Get "fe[0-9][0-9]" fields
    token_fields = [f for f in fields if re.match(r'fe[0-9]{2}$', f)]
    # Generate fe blocks for every token field
    fe_blocks = []
    for fe_field in fe_fields:
        fe_blocks.append(FE_TEMPLATE % {'fe_field': fe_field})
    crowdflower_interface_template = HEADER
    # Generate fe_name blocks(question blocks) for every fe_name field
    for idx, token_field in enumerate(token_fields):
        dic = {'question_num': idx+1, 'token_field': token_field}
        # Add fe blocks into template
        dic['fe_blocks'] = ''.join(fe_blocks)
        # Add current fe_name block or question block into template
        crowdflower_interface_template += (TOKEN_TEMPLATE % dic)

    crowdflower_interface_template += FOOTER
    if output_html is None:
        return crowdflower_interface_template
    else:
        output_html.write(crowdflower_interface_template)


def create_cli_parser():
    """ Create the cli parameters' parser"""
    parser = argparse.ArgumentParser()
    parser.add_argument('input_csv', type=argparse.FileType('r'),
                        help='CSV file containing the CrowdFlower data spreadsheet')
    parser.add_argument('output_html', type=argparse.FileType('w'),
                        help='html file to store the produced html template')
    return parser


if __name__ == '__main__':
    parser = create_cli_parser()
    args = parser.parse_args()
    sys.exit(generate_crowdflower_interface_template(args.input_csv, args.output_html))
