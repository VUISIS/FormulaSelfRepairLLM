import argparse
from formula_agent import agent_executor
from prompts import QUERY_PROMPT
def main():
    parser = argparse.ArgumentParser(description='Description of your program.')

    parser.add_argument('--code', required=True, help='Your FORMULA code that you want to try fixing')
    parser.add_argument('--output', required=True, help='A sample of the output of the FORMULA interpreter for your code')
    parser.add_argument('--additional_details', help='Optional: Add any additional prompting details when calling the LLM')

    args = parser.parse_args()

    query = QUERY_PROMPT.format(code=args.code, interpreter_output=args.output)
    if args.additional_details:
        query += f"\n\nHere are some additional details to keep in mind when trying to figure \
out what is wrong with the code:\n\n{args.additional_details}"

    # agent_executor.run(query)
    print(query)



if __name__ == "__main__":
    main()
