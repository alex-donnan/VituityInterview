import datetime
import json
import re
import os

def to_dict(filename, spec_dir, hl7_version='2.3', required=False):
	'''
	Takes an HL7 file (any format) and converts it into a dictionary,
	based on desired specificaiton.

	Args:
		filename (string): The filename to be processed (not a path)
		spec_dir (string): The path and filename of the HL7 specification JSON
		hl7_version (string): The version number for intended use (default 2.3)
		required (bool): Triggers whether only required fields in the spec are returned (default False)

	Returns:
		dict: The HL7 dictionary generated or None
	'''
	try:
		with open(spec_dir) as json_file:
			spec = json.load(json_file)
	except Exception as ex:
		print(f'Failed to open specification, aborting: {ex}')
		return None

	with open(filename, 'r') as hl7_file:
		del_field = '|'
		del_subfield = '^'
		del_repeat = '~'
		del_escape = '\\'
		del_cmpfield = '&'
		version = hl7_version
		datatype = dict_get(spec, version, 'datatype')
		file_dict = {}

		for ind, segment in enumerate(hl7_file):
			fields = segment.strip().split(del_field)
			if len(fields[0]) > 0: file_dict[fields[0]] = {}

			if fields[0] == 'MSH':
				del_field = segment[3]
				del_subfield = segment[4]
				del_repeat = segment[5]
				del_escape = segment[6]
				del_cmpfield = segment[7]

				fields = ['MSH', del_field] + fields[1:]
				version = fields[12]
				v_spec = spec.get(version, spec.get('2.3'))
				datatype = v_spec.get('datatype')

			for f_ind, field in enumerate(fields):
				if f_ind > 0:
					f_segment = v_spec.get(fields[0]).get(str(f_ind))

					if f_segment != None:
						f_name = f_segment.get('field')
						f_reqd = f_segment.get('required')
						f_type = f_segment.get('datatype')

						if (required and f_reqd) or not required:
							if f_type != None:
								dt_spec = datatype.get(f_type)
								subfields = field.split(del_subfield)
								subdict = {}

								if f_type.startswith('CM_'):
									for s_ind, subfield in enumerate(subfields):
										cmpfields = subfield.split(del_cmpfield)
										subfields[s_ind] = cmpfields

								for s_ind, subfield in enumerate(subfields):
									if dt_spec.get(str(s_ind + 1)):
										subdict[dt_spec.get(str(s_ind + 1))] = subfield

								fields[f_ind] = subdict

							file_dict[fields[0]][f_name] = fields[f_ind]


	return file_dict

def from_csv(input_file, output_dir):
	'''
	Takes a CSV file of patient data and appends it to the respective output file.

	Args:
		input_file (string): The CSV file to parse
		output_dir (string): The path of the output directory

	Returns:
		string: Either the output filename or None

	'''
	try:
		date_now = datetime.datetime.now().strftime('%Y%m%d')
		with open(input_file, 'r') as in_file:
			file_dict = {}
			header = []
			for l_ind, line in enumerate(in_file):
				row = re.split(r',(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)', line.strip())
				if l_ind == 0:
					header = row
					header.append('date_of_service')
					for f_ind, field in enumerate(row):
						file_dict[field] = f_ind
				else:
					hl7_type = row[file_dict['message_type']].split('-')[0]
					output_file = f'{output_dir}/Modified/{hl7_type}_{date_now}_Modified_file.csv'

					append = True if os.path.isfile(output_file) else False
					row_count = 1
					if append:
						with open(output_file, 'r') as out_file:
							row_count = len(out_file.readlines())

					with open(output_file, 'a') as out_file:
						if not append: out_file.write(','.join(header) + '\n')

						row[0] = str(row_count)
						row.append(date_now)

						out_file.write(re.sub(r'"+', '', ','.join(row) + '\n'))
	except Exception as ex:
		print(f'Fatal error converting to CSV format: {ex}')
		return None
	return output_file

def to_csv(dictionary, output_dir):
	'''
	Takes an HL7 dictionary and converts into a CSV.

	Args:
		dictionary (dict): The dictionary to be processed
		output_dir (string): The path of the output directory

	Returns:
		string: Either the output filename or None
	'''

	try:
		hl7_dict = dictionary
		if hl7_dict == None or dict_get(hl7_dict, 'MSH') == '': return None
		hl7_type = hl7_dict['MSH']['message_type']['message_type'][0]

		date_now = datetime.datetime.now().strftime('%Y%m%d')
		output_file = f'{output_dir}/Modified/{hl7_type}_{date_now}_Modified_file.csv'

		append = True if os.path.isfile(output_file) else False
		row_count = 1
		if append:
			with open(output_file, 'r') as out_file:
				row_count = len(out_file.readlines())

		with open(output_file, 'a') as out_file:
			header = [
				'#',
				'id',
				'site_id',
				'service_location',
				'message_type',
				'message_time',
				'message_id',
				'account_number',
				'discharge_disposition',
				'financial_class',
				'patient_first_name',
				'patient_last_name',
				'patient_middle_name',
				'patient_address_1',
				'patient_address_2',
				'patient_city',
				'patient_state',
				'patient_zip',
				'patient_zip4',
				'patient_date_of_birth',
				'patient_deceased_date',
				'patient_sex',
				'patient_ssn',
				'referring_doctor_id',
				'attending_doctor_id',
				'patient_ethnicity',
				'patient_race',
				'patient_language',
				'patient_smoking_status',
				'patient_email_address',
				'patient_cell_phone_area_code',
				'patient_cell_phone_number',
				'patient_marital_status',
				'bill_amount',
				'patient_drivers_license_number',
				'guarantor_first_name',
				'guarantor_last_name',
				'guarantor_middle_name',
				'guarantor_address_1',
				'guarantor_address_2',
				'guarantor_city',
				'guarantor_state',
				'guarantor_zip',
				'date_of_service'
			]
			if not append: out_file.write(','.join(header) + '\n')

			row = []
			row.append(str(row_count))
			row.append(dict_get(hl7_dict, 'PID', 'patient_id', 'id'))
			row.append(dict_get(hl7_dict, 'PV1', 'assigned_patient_location', 'facility'))
			row.append(dict_get(hl7_dict, 'PD1', 'patient_primary_facility', 'id'))
			msg_type = dict_get(hl7_dict, 'MSH', 'message_type', 'message_type')
			event = dict_get(hl7_dict, 'MSH', 'message_type', 'trigger_event')
			if msg_type != '' and event == '':
				row.append(f'{msg_type[0]}')
			elif msg_type != '' and event != '':
				row.append(f'{msg_type[0]}-{event[0]}')
			else:
				row.append('')
			row.append(dict_get(hl7_dict, 'MSH', 'message_datetime'))
			row.append(dict_get(hl7_dict, 'MSH', 'message_control_id'))
			row.append(dict_get(hl7_dict, 'PID', 'patient_account_number', 'id'))
			row.append(dict_get(hl7_dict, 'PV1', 'discharge_disposition'))
			row.append(dict_get(hl7_dict, 'PV1', 'financial_class', 'financial_class'))
			row.append(dict_get(hl7_dict, 'PID', 'patient_name', 'first_name'))
			row.append(dict_get(hl7_dict, 'PID', 'patient_name', 'last_name'))
			row.append(dict_get(hl7_dict, 'PID', 'patient_name', 'middle_name'))
			row.append(dict_get(hl7_dict, 'PID', 'patient_address', 'street_address'))
			row.append(dict_get(hl7_dict, 'PID', 'patient_address', 'street_address2'))
			row.append(dict_get(hl7_dict, 'PID', 'patient_address', 'city'))
			row.append(dict_get(hl7_dict, 'PID', 'patient_address', 'state'))
			row.append(dict_get(hl7_dict, 'PID', 'patient_address', 'zip'))
			row.append('')
			row.append(dict_get(hl7_dict, 'PID', 'patient_birth_datetime'))
			row.append(dict_get(hl7_dict, 'PID', 'patient_death_datetime'))
			row.append(dict_get(hl7_dict, 'PID', 'patient_sex'))
			row.append(dict_get(hl7_dict, 'PID', 'patient_ssn'))
			row.append(dict_get(hl7_dict, 'PV1', 'admitting_doctor', 'id'))
			row.append(dict_get(hl7_dict, 'PV1', 'attending_doctor', 'id'))
			row.append(dict_get(hl7_dict, 'PID', 'ethnic_group'))
			row.append(dict_get(hl7_dict, 'PID', 'race'))
			row.append(dict_get(hl7_dict, 'PID', 'primary_language', 'id'))
			row.append('')
			row.append(dict_get(hl7_dict, 'PID', 'phone_number_home', 'email_address'))
			phone = dict_get(hl7_dict, 'PID', 'phone_number_home', 'telephone_number')
			if phone:
				phone = ''.join(c for c in phone if c.isdigit())
				row.append(phone[0:3])
				row.append(phone[3:])
			else:
				row.append('')
				row.append('')
			row.append(dict_get(hl7_dict, 'PID', 'marital_status'))
			row.append(dict_get(hl7_dict, 'PV1', 'total_charges'))
			row.append(dict_get(hl7_dict, 'PID', 'drivers_license_number', 'drivers_license_number'))
			row.append(dict_get(hl7_dict, 'GT1', 'guarantor_name', 'first_name'))
			row.append(dict_get(hl7_dict, 'GT1', 'guarantor_name', 'last_name'))
			row.append(dict_get(hl7_dict, 'GT1', 'guarantor_name', 'middle_name'))
			row.append(dict_get(hl7_dict, 'GT1', 'guarantor_address', 'street_address'))
			row.append(dict_get(hl7_dict, 'GT1', 'guarantor_address', 'street_address2'))
			row.append(dict_get(hl7_dict, 'GT1', 'guarantor_address', 'city'))
			row.append(dict_get(hl7_dict, 'GT1', 'guarantor_address', 'state'))
			row.append(dict_get(hl7_dict, 'GT1', 'guarantor_address', 'zip'))
			row.append(date_now)

			out_file.write(re.sub(r'"+', '', ','.join(row) + '\n'))
	except Exception as ex:
		print(f'Fatal error converting to CSV format: {ex}')
		return None
	return output_file

def group_fields(filename, fieldname, fieldformat, *fields):
	'''
	Utility function that takes a CSV file and concatenates the given fields into a single field.
	Header line is required.

	Args:
		filename (string): The CSV file to be modified
		fieldname (string): The new field name
		format (formatting string): The format for the string object
		*fields (string): The field names to be grouped

	Returns:
		bool: Success or failure
	'''
	try:
		file_dict = {}
		field_ind = -1
		rows = []

		with open(filename, 'r') as file:
			for l_ind, line in enumerate(file):
				row = re.split(r',(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)', line.strip())
				rows.append(row)
				if l_ind == 0:
					for f_ind, field in enumerate(row):
						if field in fields:
							file_dict[field] = f_ind
							field_ind = min(field_ind, f_ind) if field_ind > 0 else f_ind
		
		if len(file_dict) != len(fields):
			print(f'Failed to capture all desired fields, aborting.')
			return False

		with open(filename, 'w') as file:
			for r_ind, row in enumerate(rows):
				field_list = []

				for f_ind, field in enumerate(fields):
					field_list.append(row[file_dict[field]])

				pop_count = 0
				for f_ind, field in enumerate(row):
					if f_ind > field_ind:
						row.pop(f_ind - pop_count)
						pop_count += 1
					if pop_count == len(fields)-1:
						break
				
				if r_ind == 0:
					row[field_ind] = fieldname
				else:
					row[field_ind] = fieldformat.format(*field_list).strip()
				file.write(','.join(row) + '\n')
		return True
	except Exception as ex:
		print(f'Failed to group the desired fields : {ex}')
		return False

def sum_field(filename, fieldname, *fields):
	'''
	Utility function that attempts to summarize a numeric column.
	Additional fields can be returned with the value for extra processing.

	Args:
		filename (string): The CSV file to be modified
		fieldname (string): The fieldname to search and summarize (must be numeric)
		*fields (string): Additional fields to return

	Returns:
		array<dict>: An array of dictionaries with the initial field and associate data
	'''
	try:
		field_index = -1
		row_length = -1
		field_total = 0.0
		file_dict = {}
		field_output = []
		with open(filename, 'r') as file:
			for l_ind, line in enumerate(file):
				row = re.split(r',(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)', line.strip())
				row_length = len(row)
				row_dict = {}
				for f_ind, field in enumerate(row):
					if l_ind == 0:
						if field == fieldname:
							field_index = f_ind
							file_dict[f_ind] = field
						if field in fields:
							file_dict[f_ind] = field
					elif l_ind > 0:
						if f_ind == field_index:
							value = float(field) if field != '' else 0.0
							field_total += value
						if f_ind in file_dict.keys():
							row_dict[file_dict[f_ind]] = field
				if len(row_dict) == len(fields) + 1:
					field_output.append(row_dict)
		return field_output
	except Exception as ex:
		print(f'Failed to summarize the desired field : {ex}')
		return None

def dict_get(dictionary, *keys):
	'''
	Utility function to simplify deep key retrieval.

	Args:
		dictionary (dict): The dictionary to get values from
		*keys (string): The path of key strings to attempt retrieval

	Returns:
		string: The value of the field or an empty string
	'''
	cur_dict = dictionary
	for key in keys:
		try:
			cur_dict = cur_dict[key]
		except KeyError as ke:
			return ''
	return cur_dict
