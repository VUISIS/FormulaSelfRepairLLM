from config import cfg
import json

FILE = "../training.json"


def convert_json(file):
    """read in JSON file which is of the format
[
    {
        "instruction": "Explain why this model is solvable",
        "input": "domain SymbolicMinAll\n{\n  A ::= new (x : Integer).\n  B ::= new (x : Integer).\n\n  minVal ::= (x : Integer).\n\n  goodA :- a is A, a.x < 10.\n  goodB :- b is B, b.x > 20.\n\n  minVal(x) :- a is A, b is B, x = minAll(a.x,{a.x, b.x}), x : Integer.\n  \n  goodModel :- m is minVal, m.x < 5.\n\n  conforms goodModel.\n}\n\npartial model pm of SymbolicMinAll\n{\n  a is A(x).\n  b is B(y).\n}\n, A(0) B(0) minVal(0)",
        "output": "This model can be solved because of the conformity of the following rules goodModel.\nA rule goodA is derived because these constraints are satisfied a is A, a.x < 10\nA rule goodB is derived because these constraints are satisfied b is B, b.x > 20\nA rule minVal(x) is derived because these constraints are satisfied a is A, b is B, x = minAll(a.x,{a.x, b.x}), x : Integer\nA rule goodModel is derived because these constraints are satisfied m is minVal, m.x < 5\n"
    },
    {
        "instruction": "Explain why this model is solvable",
        "input": "domain relaxedCoconut\n{\n  jovialDailies ::= new (x : Integer).\n  tenseLevel ::= new (x : Integer).\n\n  brownPoset ::= (x : Integer).\n\n  Cold :- a is jovialDailies, a.x < 17.\n  lazyPhrase :- b is tenseLevel, b.x < 16.\n\n  brownPoset(x) :- a is jovialDailies, b is tenseLevel, x = minAll(a.x,{a.x, b.x}), x : Integer.\n  \n  Abstract :- m is brownPoset, m.x <= 94.\n\n  conforms Abstract.\n}\n\npartial model Happy of relaxedCoconut\n{\n  a is jovialDailies(x).\n  b is tenseLevel(y).\n}\n, jovialDailies(0) tenseLevel(0) brownPoset(0)",
        "output": "This model can be solved because of the conformity of the following rules Abstract.\nA rule Cold is derived because these constraints are satisfied a is jovialDailies, a.x < 17\nA rule lazyPhrase is derived because these constraints are satisfied b is tenseLevel, b.x < 16\nA rule brownPoset(x) is derived because these constraints are satisfied a is jovialDailies, b is tenseLevel, x = minAll(a.x,{a.x, b.x}), x : Integer\nA rule Abstract is derived because these constraints are satisfied m is brownPoset, m.x <= 94\n"
    },
    ]

    create a new file called finetune.json which is off the format
    [
    {
        "prompt" : "Explain why the following model delimited by ``` is solvable:\n```<code>```,
        "completion" : "same as output"
    }
    ]
    """
    with open(file, 'r') as infile:
        data = json.load(infile)

    # Prepare the output data in the desired format
    output_data = []
    for item in data:
        prompt = f"{item['instruction']}.\n The model code is written below, delimited by ```. \n\n ```{item['input']}```"
        completion = item['output']

        output_item = {"prompt": prompt, "completion": completion}
        output_data.append(output_item)

    # Write the output data to the finetune.json file
    with open("../finetune.json", "w") as outfile:
        json.dump(output_data, outfile, indent=4)


def print_data(data):
    # with open(file, 'r') as infile:
    #     data = json.load(infile)

    print("Instruction: " + data["instruction"])
    print("Input: " + data["input"])
    print("Output: " + data["output"])


# convert_json(FILE)

# read_json(FILE, 5)

print_data(    {
        "instruction": "Explain why this model is not solvable",
        "input": "domain inverseOctagon\n{\n  snowyBranch ::= new (x : Integer).\n  Brownian ::= new (x : Integer).\n\n  chromaticChangeset ::= (x : Integer).\n\n  crunchySkill :- a is snowyBranch, a.x > 78.\n  matteBog :- b is Brownian, b.x > 66.\n\n  chromaticChangeset(x) :- a is snowyBranch, b is Brownian, x = max(a.x, b.x).\n  \n  jollyException :- m is chromaticChangeset, m.x < 34.\n  \n  conforms crunchySkill.\n  conforms matteBog.\n  conforms jollyException.\n}\n\npartial model Orthogonal of inverseOctagon\n{\n  a is snowyBranch(x).\n  b is Brownian(y).\n}\n,inverseOctagon.jollyExceptioninverseOctagon.crunchySkill",
        "output": "This model cannot be solved because it requires the conformity of the following rules crunchySkill, matteBog, jollyException.\nA crunchySkill exists only if the following constraints are satisfied a is snowyBranch, a.x > 78\nA matteBog exists only if the following constraints are satisfied b is Brownian, b.x > 66\nA chromaticChangeset(x) exists only if the following constraints are satisfied a is snowyBranch, b is Brownian, x = max(a.x, b.x)\nA jollyException exists only if the following constraints are satisfied m is chromaticChangeset, m.x < 34\n"
    })