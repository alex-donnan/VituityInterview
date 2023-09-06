## Vituity Interview Project
#### Alex Donnan
#### Sept. 5, 2023
<hr>

This project intends to demonstrate basic knowledge of HL7 principles and file manipulation with Python.

#### How To Use:
This project was built using Python 3.11.5 but should be compatible with later versions. No non-standard libraries were used.

1. Clone the project into a local directory.
2. From terminal, navigate to the base folder.
	- The original project files already exist in the intake folder `./Intake/`
3. Run the program `vituity_test.py` with a minimum of the required arg `-i`
	- *Other options:*
	- -h, --help
		- Show these options in the terminal.
	- -i, --intake INTAKE
		- The directory path to check for incoming HL7 files.
	- -a, --archive ARCHIVE
	    - Optional: The base directory path for archives.
	- -s, --specification SPECIFICATION
	    - Optional: The file path for the HL7 specification JSON file.
	- -v, --version VERSION
	    - Optional: The intended HL7 version, defaults to 2.3.
	- -r, --required REQUIRED
        - Optional: Sets the parser to only use required fields from the specification.
4. Success confirmation messages should appear regarding file location of modified files and reports.

#### Modification:
The project relies on `hl7_spec.json` found in the `src` folder. Segments and datatypes are explicitly defined for the sake of adding new versions or specifications to the project. The selected specification relies on the `version` number provided (default 2.3).