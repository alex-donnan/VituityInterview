import argparse
import shutil
import src.parse_hl7 as hl7
import sys
import os

argParser = argparse.ArgumentParser()
argParser.add_argument('-i', '--intake', type=str, help="The directory path to check for incoming HL7 files.")
argParser.add_argument('-a', '--archive', type=str, help="Optional: The directory path to archive a CSV.")
argParser.add_argument('-s', '--specification', type=str, help="Optional: The file path for the HL7 specification JSON file.")
argParser.add_argument('-v', '--version', type=str, help="Optional: The intended HL7 version, defaults to 2.3.")
argParser.add_argument('-r', '--required', type=bool, help="Optional: Sets the parser to only use required fields from the specification.")

if __name__ == "__main__":
	args = argParser.parse_args()
	if args.intake == None:
		print('Intake file directory is required.')
	else:
		if len(os.listdir(args.intake)) > 0:
			archive = './Archive/' if args.archive == None else args.archive
			specification = './src/hl7_spec.json' if args.specification == None else arg.specification
			for file in os.listdir(args.intake):
				if file.split('.')[-1] in ('txt', 'hl7'):
					output = hl7.to_csv(os.path.join(args.intake, file), archive, specification, args.version, args.required)
					if output:
						shutil.move(f'{args.intake}{file}', f'{archive}/Original/{file}')
						print(f'{file} processing complete, please view CSV file in {archive}/Modified/')
				else:
					shutil.move(f'{args.intake}{file}', f'{archive}/Original/{file}')
					print(f'{file} not processed, moved to {archive}/Original/')
		else:
			print(f'No files in intake.')