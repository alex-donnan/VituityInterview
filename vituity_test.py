import argparse
import shutil
import src.parse_hl7 as hl7
import src.billing_report as bill
import sys
import os

argParser = argparse.ArgumentParser()
argParser.add_argument('-i', '--intake', type=str, help="The directory path to check for incoming HL7 files.")
argParser.add_argument('-a', '--archive', type=str, help="Optional: The base directory path for archives.")
argParser.add_argument('-s', '--specification', type=str, help="Optional: The file path for the HL7 specification JSON file.")
argParser.add_argument('-v', '--version', type=str, help="Optional: The intended HL7 version, defaults to 2.3.")
argParser.add_argument('-r', '--required', type=bool, help="Optional: Sets the parser to only use required fields from the specification.")

if __name__ == "__main__":
	'''
	Main - Using the required Intake path, attempts to parse the HL7 files therein.

	Args:
		intake (string): The directory path for intake
		archive (string): The base directory path for archiving
		specification (string): The file path for the HL7 specification file
		version (string): The version of HL7 to use
		required (bool): Sets the output to only provide required fields per the spec file
	'''
	args = argParser.parse_args()
	if args.intake == None:
		print('Intake file directory is required.')
	else:
		if len(os.listdir(args.intake)) > 0:
			archive = './Archive/' if args.archive == None else args.archive
			specification = './src/hl7_spec.json' if args.specification == None else arg.specification

			if not os.path.exists(f'{archive}/Original/'): os.makedirs(f'{archive}/Original/')
			if not os.path.exists(f'{archive}/Modified/'): os.makedirs(f'{archive}/Modified/')
			if not os.path.exists(f'{archive}/Reports/'): os.makedirs(f'{archive}/Reports/')

			for file in os.listdir(args.intake):
				if file.split('.')[-1] in ('csv'):
					hl7_csv = hl7.from_csv(f'{args.intake}/{file}', archive)
					if hl7_csv:
						shutil.move(f'{args.intake}{file}', f'{archive}/Original/{file}')
						print(f'{file} processing complete, please view CSV file in {archive}/Modified/')

			for file in os.listdir(args.intake):
				if file.split('.')[-1] in ('txt'):
					hl7_dict = hl7.to_dict(f'{args.intake}/{file}', specification, args.version, args.required)
					hl7_csv = hl7.to_csv(hl7_dict, archive)
					if hl7_csv:
						shutil.move(f'{args.intake}{file}', f'{archive}/Original/{file}')
						print(f'{file} processing complete, please view CSV file in {archive}/Modified/')

			report_sum = []
			for file in os.listdir(f'{archive}/Modified/'):
				if file.split('.')[-1] in ('csv'):
					if hl7.group_fields(f'{archive}/Modified/{file}', 'patient_name', '"{0}, {1} {2}"', 'patient_last_name', 'patient_first_name', 'patient_middle_name'):
						print(f'Field grouping successfully updated.')
					report_data = hl7.sum_field(f'{archive}/Modified/{file}', 'bill_amount', 'patient_state')
					if report_data != None:
						report_sum += report_data
			
			bill.state_report(f'{archive}/Reports/State_Report.txt', report_sum)
		else:
			print(f'No files in intake.')