# main.py

from agents import ResumeReaderAgent, ExtractorAgent, ValidatorAgent
import json


def main():
    print("Welcome to the Resume Processing System")

    # Instantiate agents
    reader_agent = ResumeReaderAgent()
    extractor_agent = ExtractorAgent()
    validator_agent = ValidatorAgent()

    # Get the resume file path from the user
    resume_file = input("Enter the path to the resume file: ")

    # Read the resume
    try:
        resume_text = reader_agent.read_resume(resume_file)
        print("\nResume text extracted successfully.")
    except Exception as e:
        print(f"\nError reading resume: {e}")
        return

    # Human Feedback Loop: Allow user to review or edit the extracted text
    print("\n--- Resume Text ---")
    print(resume_text)
    user_input = input("\nWould you like to edit the extracted text? (y/n): ")
    if user_input.lower() == 'y':
        print("\nPlease edit the resume text below. When done, enter 'END' on a new line.")
        edited_text = []
        while True:
            line = input()
            if line.strip().upper() == 'END':
                break
            edited_text.append(line)
        resume_text = '\n'.join(edited_text)

    # Extract entities
    print("\nExtracting entities from resume...")
    extracted_data = extractor_agent.extract_entities(resume_text)
    print("\nEntities extracted successfully.")

    # Human Feedback Loop: Allow user to review or edit the extracted data
    print("\n--- Extracted Data ---")
    print(json.dumps(extracted_data, indent=4))
    user_input = input("\nWould you like to edit the extracted data? (y/n): ")
    if user_input.lower() == 'y':
        print("\nPlease edit the extracted data in JSON format. When done, enter 'END' on a new line.")
        edited_data_lines = []
        while True:
            line = input()
            if line.strip().upper() == 'END':
                break
            edited_data_lines.append(line)
        edited_data_str = '\n'.join(edited_data_lines)
        try:
            extracted_data = json.loads(edited_data_str)
        except json.JSONDecodeError:
            print("\nInvalid JSON format. Using original extracted data.")

    # Validate entities
    print("\nValidating extracted data...")
    validation_result = validator_agent.validate_entities(extracted_data)

    if not validation_result['valid']:
        print("\nValidation Errors:")
        for error in validation_result['errors']:
            print(f"- {error}")
        # Human Feedback Loop: Ask user to correct errors
        user_input = input("\nWould you like to correct the errors? (y/n): ")
        if user_input.lower() == 'y':
            print("\nPlease edit the extracted data in JSON format to correct errors. When done, enter 'END' on a new line.")
            edited_data_lines = []
            while True:
                line = input()
                if line.strip().upper() == 'END':
                    break
                edited_data_lines.append(line)
            edited_data_str = '\n'.join(edited_data_lines)
            try:
                extracted_data = json.loads(edited_data_str)
                # Re-validate
                validation_result = validator_agent.validate_entities(extracted_data)
                if not validation_result['valid']:
                    print("\nValidation errors still present.")
                else:
                    print("\nData validated successfully after corrections.")
            except json.JSONDecodeError:
                print("\nInvalid JSON format. Using original extracted data.")
        else:
            print("\nProceeding with invalid data.")
    else:
        print("\nExtracted data is valid.")

    # Save the data to JSON file
    output_file = 'output.json'
    with open(output_file, 'w') as f:
        json.dump(extracted_data, f, indent=4)
    print(f"\nExtracted data saved to {output_file}")


if __name__ == '__main__':
    main()
