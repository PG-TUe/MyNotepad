"""
This script converts csv datasets to ARFF format.
In the ARFF format, one needs to know whether features are numeric or categorical - this is done with a simple heuristic, and thus is not always completely accurate.
No support for Data attributes yet.
Categorical attributes should be encoded as numbers
"""
import sys
import math
import numpy
import pandas as pd
import numbers
import arff

input_file = sys.argv[1]
output_file = sys.argv[2]

if '/' in input_file:
	end_of_folder_path = input_file.rfind('/') + 1
else:
	end_of_folder_path = 0

dataset_name = input_file[end_of_folder_path:-4]
dataset = pd.read_csv(input_file, sep='\t')

column_info = []
integer_columns = []
for column in dataset.columns:
	column_values = dataset[column]
	column_is_integer = (all([isinstance(el, numbers.Number) for el in column_values]) and
			     all([math.isnan(el) or float(el).is_integer() for el in column_values]))

	integer_columns.append(column_is_integer)

	if column_is_integer:
		not_nan_values = column_values[~numpy.isnan(column_values)]
		unique_values = numpy.unique(not_nan_values)
		is_categorical = (len(unique_values) <= 10 and column_is_integer)
		if is_categorical:
			data_type_str = [str(int(val)) for val in unique_values]
		else:
			data_type_str = 'INTEGER'
	else:
		data_type_str = 'string' if all([isinstance(val, str) for val in column_values]) else 'NUMERIC'

	column_info.append((column, data_type_str))

arff_dict = {
	'description':  'This ARFF is automatically generated.\n'
			'The data types of attributes are inferred from the data.\n'
		        'In particular this means there is some uncertainty as to whether '
			'an attribute truly is categorical or numerical.\n',
	'relation': dataset_name,
	'attributes': column_info,
	'data': [row for _, row in dataset.iterrows()]
}

with open('{}.arff'.format(dataset_name),'w') as arff_file:
	arff.dump(arff_dict, arff_file)
