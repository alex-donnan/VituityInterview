import datetime
import json
import os

def to_dict(filename, spec_dir, hl7_version='2.3', required=False):
	try:
		with open(spec_dir) as json_file:
			spec = json.load(json_file)
			datatype = spec.get('datatype')
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

def to_csv(filename, output_dir, spec_dir, hl7_version='2.3', required=False):
	try:
		hl7_dict = to_dict(filename, spec_dir, hl7_version, required)
		if hl7_dict == None:
			return None
		hl7_type = hl7_dict['MSH']['message_type']['message_type'][0]

		date_now = datetime.datetime.now().strftime('%Y%m%d')
		output_file = f'{output_dir}/Modified/{hl7_type}_{date_now}_Modified_file.csv'

		append = True if os.path.isfile(output_file) else False
		if append:
			with open(output_file, 'r') as out_file:
				count = len(out_file.readlines())
		else:
			count = 1

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
				'patient_name',
				'patient_street_address',
				'patient_street_address_2',
				'patient_city',
				'patient_state',
				'patient_zip',
				'patient_birth_date',
				'patient_death_date',
				'patient_sex',
				'patient_ssn',
				'referring_doctor',
				'attending_doctor',
				'patient_ethnicity',
				'patient_race',
				'patient_language',
				'patient_email_address',
				'patient_phone_area_code',
				'patient_phone_number',
				'patient_marital_status',
				'bill_amount',
				'patient_drivers_license_number',
				'guarantor_first_name',
				'guarantor_last_name',
				'guarantor_middle_name',
				'guarantor_street_address',
				'guarantor_street_address2',
				'guarantor_city',
				'guarantor_state',
				'guarantor_zip',
				'date_of_service'
			]

			row = []
			row.append(str(count))
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
			patient_first = dict_get(hl7_dict, 'PID', 'patient_name', 'first_name')
			patient_middle = dict_get(hl7_dict, 'PID', 'patient_name', 'middle_name')
			patient_last = dict_get(hl7_dict, 'PID', 'patient_name', 'last_name')
			row.append(f'{patient_last}, {patient_first} {patient_middle}')
			row.append(dict_get(hl7_dict, 'PID', 'patient_address', 'street_address'))
			row.append(dict_get(hl7_dict, 'PID', 'patient_address', 'street_address2'))
			row.append(dict_get(hl7_dict, 'PID', 'patient_address', 'city'))
			row.append(dict_get(hl7_dict, 'PID', 'patient_address', 'state'))
			row.append(dict_get(hl7_dict, 'PID', 'patient_address', 'zip'))
			row.append(dict_get(hl7_dict, 'PID', 'patient_birth_datetime'))
			row.append(dict_get(hl7_dict, 'PID', 'patient_death_datetime'))
			row.append(dict_get(hl7_dict, 'PID', 'patient_sex'))
			row.append(dict_get(hl7_dict, 'PID', 'patient_ssn'))
			row.append(dict_get(hl7_dict, 'PV1', 'admitting_doctor', 'id'))
			row.append(dict_get(hl7_dict, 'PV1', 'attending_doctor', 'id'))
			row.append(dict_get(hl7_dict, 'PID', 'ethnic_group'))
			row.append(dict_get(hl7_dict, 'PID', 'race'))
			row.append(dict_get(hl7_dict, 'PID', 'primary_language', 'id'))
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

			if not append: out_file.write(','.join(header) + '\n')
			out_file.write(','.join(row) + '\n')
	except Exception as ex:
		print(f'Fatal error converting to CSV format: {ex}')
		return None
	return output_file

def dict_get(dictionary, *keys):
	cur_dict = dictionary
	for key in keys:
		try:
			cur_dict = cur_dict[key]
		except KeyError as ke:
			return ''
	return cur_dict
