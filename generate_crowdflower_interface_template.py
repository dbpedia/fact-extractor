#!/usr/bin/env python
# encoding: utf-8

import csv
import re
import argparse
import sys

# crowdflower interface template header
HEADER = '''<!-- BEGIN sentence -->
<h2 style="text-align:center">{{lu}}</h2>
<br />
<blockquote style="text-align:center">{{sentence}}</blockquote>
<!-- END sentence -->

<hr />

<div class="row">
'''

FOOTER = "</div>"

# token block template
TOKEN_TEMPLATE = '''
    <!-- BEGIN token %(question_num)d -->
    {%% if %(fe_field)s != 'No data available' %%}
    <div class="span2">
        <cml:radios label="{{%(fe_field)s}}" class="rando" name="{{%(fe_field)s}}" validates="required" gold="true">
            <cml:radio label="Nessuno"></cml:radio>
            %(fe_blocks)s
        </cml:radios>
    </div>
    {%% endif %%}
    <!-- END token %(question_num)d -->
'''

# fe block template
FE_TEMPLATE = '''
          {%% if %(fe_name_field)s != 'No data available' %%}
          <cml:radio label="{{%(fe_name_field)s}}"></cml:radio>
          {%% endif %%}'''

# type block template
# TYPE_TEMPLATE = '''
#         {%% if %(type_field)s != 'No data available' %%}
#         <li>{{%(type_field)s}}</li>
#         {%% endif %%}'''


def generate_crowdflower_interface_template(input_csv, output_html=None):
    """ Generate CrowFlower interface template based on input data spredsheet """
    # Get the filed names of the input data spreadsheet
    sheet = csv.DictReader(input_csv)
    fields = sheet.fieldnames
    # Get "fe_name[0-9]" fields
    fe_name_fields = [f for f in fields if re.match('fe_name[0-9]{2}$', f)]
    # Get "fe[0-9]" fields
    fe_fields = [f for f in fields if re.match('fe[0-9]{2}$', f)]
    # Generate fe blocks for every fe filed
    fe_blocks = []
    for fe_name_field in fe_name_fields:
        fe_blocks.append(FE_TEMPLATE % {'fe_name_field': fe_name_field})
    crowdflower_interface_template = HEADER
    # Generate fe_name blocks(question blocks) for every fe_name field
    for idx, fe_field in enumerate(fe_fields):
        dic = {'question_num': idx+1, 'fe_field': fe_field}
        # Add fe blocks into template
        dic['fe_blocks'] = ''.join(fe_blocks)
        
        # # Get "typeK_[0-9]" fields for correspongding "fe_nameK" field
        # type_fields = [f for f in fields if re.match('type%d_[0-9]$' % idx, f)]
        # # Generate type blocks for every type field
        # type_blocks = []
        # for type_field in type_fields:
        #     type_blocks.append(TYPE_TEMPLATE % {'type_field': type_field})
        # # Generate type predicates for all type fields
        # type_predicates = ["%s != 'No data available'" % type_field for type_field in type_fields]
        # # Add type blocks into template
        # dic['type_blocks'] = ''.join(type_blocks)
        # Add type predicates into template
        # dic['type_predicates'] = ' and '.join(type_predicates)
        
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
