#!/usr/bin/env python
# encoding: utf-8

import csv
import re

# crowdflower interface template header
TEMPLATE_HEADER = '''<!-- BEGIN sentence -->
<h2 style="text-align:center">{{lu}}</h2>
<br />
<blockquote style="text-align:center">{{sentence}}</blockquote>
<!-- END sentence -->

<hr />
'''

# fe_name(question) block template
FE_NAME_TEMPLATE = '''
<!-- BEGIN question %(question_num)d -->
{%% if %(fe_name_field)s != 'No data available' %%}
<div class="row">
  <div class="span5">
    <cml:radios label="{{%(fe_name_field)s}}" class="rando" name="{{%(fe_name_field)s}}" validates="required" gold="true">
          <cml:radio label="Nessuno"></cml:radio>%(fe_blocks)s</cml:radios>
  </div>

  {%% if %(type_predicates)s %%}
  <div class="span5">
    <div class="alert alert-info">
      <h3 style="text-align:center"><i class="icon-info-sign"></i> <span style="color:black">SUGGERIMENTI</span><br />{{fe_name0}} potrebbe essere un:</h3>
      <ul class="inline">%(type_blocks)s</ul>
    </div>
  </div>
  {%% endif %%}

</div>
<hr />
{%% endif %%}
<!-- END question %(question_num)d -->
'''

# fe block template
FE_TEMPLATE = '''
          {%% if %(fe_field)s != 'No data available' %%}
          <cml:radio label="{{%(fe_field)s}}"></cml:radio>
          {%% endif %%}'''

# type block template
TYPE_TEMPLATE = '''
        {%% if %(type_field)s != 'No data available' %%}
        <li>{{%(type_field)s}}</li>
        {%% endif %%}'''

def generate_crowdflower_interface_template(sheet_file_name, template=None):
    """ Generate CrowFlower interface template based on input data spredsheet """
    # Get the filed names of the input data spreadsheet
    with open(sheet_file_name) as sheet_file:
        sheet = csv.DictReader(sheet_file)
        fields = sheet.fieldnames
    # Get "fe_name[0-9]" fields
    fe_name_fields = [f for f in fields if re.match('fe_name[0-9]$', f)]
    # Get "fe[0-9]" fields
    fe_fields = [f for f in fields if re.match('fe[0-9]$', f)]
    # Generate fe blocks for every fe filed
    fe_blocks = []
    for fe_field in fe_fields:
        fe_blocks.append(FE_TEMPLATE % {'fe_field':fe_field})
    crowdflower_interface_template = TEMPLATE_HEADER
    # Generate fe_name blocks(question blocks) for every fe_name field
    for idx, fe_name_field in enumerate(fe_name_fields):
        dic = {'question_num':idx+1, 'fe_name_field':fe_name_field}
        # Add fe blocks into template
        dic['fe_blocks'] = ''.join(fe_blocks)
        # Get "typeK_[0-9]" fields for correspongding "fe_nameK" field
        type_fields = [f for f in fields if re.match('type%d_[0-9]$' % idx, f)]
        # Generate type blocks for every type field
        type_blocks = []
        for type_field in type_fields:
            type_blocks.append(TYPE_TEMPLATE % {'type_field':type_field})
        # Generate type predicates for all type fields
        type_predicates = ["%s != 'No data available'" % type_field for type_field in type_fields]
        # Add type blocks into template
        dic['type_blocks'] = ''.join(type_blocks)
        # Add type predicates into template
        dic['type_predicates'] = ' and '.join(type_predicates)
        # Add current fe_name block or question block into template
        crowdflower_interface_template += (FE_NAME_TEMPLATE % dic)
    if template is None:
        return crowdflower_interface_template
    else:
        with open(template, 'w') as template_file:
            template_file.write(crowdflower_interface_template)

if __name__ == '__main__':
    print generate_crowdflower_interface_template('resources/crowdflower-input.sample', 'tmp.html')
