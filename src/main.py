import argparse
from formula_agent import agent_executor
from prompts import QUERY_PROMPT

def read_file_content(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def main():
    parser = argparse.ArgumentParser(description='Description of your program.')

    group_code = parser.add_mutually_exclusive_group(required=True)
    group_code.add_argument('--code', help='Your FORMULA code that you want to try fixing')
    group_code.add_argument('--code_file', help='Path to a file containing the FORMULA code')

    group_output = parser.add_mutually_exclusive_group(required=True)
    group_output.add_argument('--output', help='A sample of the output of the FORMULA interpreter for your code')
    group_output.add_argument('--output_file', help='Path to a file containing the output sample')

    parser.add_argument('--additional_details', help='Optional: Add any additional prompting details when calling the LLM')

    args = parser.parse_args()

    if args.code_file:
        code = read_file_content(args.code_file)
    else:
        code = args.code

    if args.output_file:
        output = read_file_content(args.output_file)
    else:
        output = args.output

    query = QUERY_PROMPT.format(code=code, interpreter_output=output)
    if args.additional_details:
        query += f"\n\nHere are some additional details to keep in mind when trying to figure \
out what is wrong with the code:\n\n{args.additional_details}"

    agent_executor.run(query)
    # print(query)

def run_agent_executor(code, output, additional_details):
    query = QUERY_PROMPT.format(code=code, interpreter_output=output)
    if additional_details:
        query += f"\n\nHere are some additional details to keep in mind when trying to figure \
out what is wrong with the code:\n\n{additional_details}"

    agent_executor.run(query)

if __name__ == "__main__":
    main()
