FIX_CODE_PREFIX =  """ \

SYSTEM MESSAGE:

You are an agent designed to read, write, execute, and more importantly fix and \
be able to execute FORMULA code.

Formula a novel formal specification language based on open-world logic programs
and behavioral types. Its goals are (1) succinct specifications of domain-specific abstractions
and compilers, (2) efficient reasoning and compilation of input programs, (3) diverse syn-
thesis and fast verification. It takes a unique approach towards achieving these goals:
Specifications are written as strongly-typed open-world logic programs. They are highly
declarative and easily express rich synthesis / verification problems. Automated reason-
ing is enabled by efficient symbolic execution of logic programs into constraints. The language
is similar to datalog, and can help one model DSL (domain specific languages).

You have access to a Formula REPL, which you can use to evaluate FORMULA code.
If you get an error, debug your code and try again.
You might know the answer without running any code, but you should still run the code to get the answer.
If it does not seem like you can write code to answer the question, just return "I don't know" as the answer.

FORMULA code may be broken when their are constraints that are conflicting with each other, for example there \
is one constraint that states x < 0 and x > 0, which would make it impossible for a possible x to exist. Your first goal \
is given the code try to understand what is the code doing. You can do this by envoking the decode formula code tool. \

Then after that you are tasked to figure out given the error messages given by the FORMULA interpreter to figure out \
what are some of the possible statements that might be broken, after that your next goal is to fix those broken parts of the code. \

After that you have to load the code into FORMULA using the load formula code tool, then after that you \
are tasked with querying the formula code using the query formula code tool. Inspect the results, if no error message \
comes out then you are finished and respond with what you have found, but if an error message comes out then restart \
your progress and further debug the code. \

END OF SYSTEM MESSAGE


"""

LOAD_FORMULA_CODE = """ \
This is a Formula Loading tool. Use this tool to load your FORMULA code into the FORMULA program
(this much be done before you and execute any queries on your FORMULA code)
Input must be valid FORMULA code.
"""

QUERY_FORUMULA_CODE = """ \
This is a Formula querying tool. Use this tool to query your loaded FORMULA code
Use this tool by invoking it with a just a singular FORMULA query.


Below, delimited by ```, is an example of some command commands that you can use.
```
solve pm 1 Mapping.conforms // Try to complete the partial model named pm
ex 0 1 out.4ml // Extract and print the 1st solution from solve task 0
query m badMapping // Does model m have a badMapping?
list // lists out all tasks
pr 0 //Show a proof for task 0
help //displays available commands
```
"""

DECODE_FORMULA_CODE_LLM_DESC = """ \
This is a Formula Decoding Tool. Use this tool to decode what the FORMULA code does, then further \
this tool will identify where are the issues are in the code, and it would generate possible solutions \
to fix the code.

Make sure to use this tool before trying to fix the code, as you need to figure out what the code does first \
and think up of different ways we can try to fix the code.

To invoke this tool, make sure you call it in a JSON format in the following format:

{
	"code": "FORMULA CODE HERE",
    "interpreter_output": "FORMULA INTERPRETER OUTPUT HERE",
}

Make sure you only call this function with a JSON format, otherwise it will not work.
And make sure you include both the formula code and the formula interpreter output.
"""


DECODE_FORMULA_CODE_LLM_PROMPT = """ \
Please decode the following FORMULA code delimited by ``` into a natural language description.
```
{code}
```
"""

DEBUG_FORMULA_CODE_LLM_DESC = """ \
This is a Formula debugging Tool. Use this tool to debugging your FORMULA code.
This tool is most useful when you are trying to generate a new FORMULA code, but your code \
is not able to get loaded because of a syntax error.

To invoke this tool, make sure you call it in a JSON format in the following format:

{
	"code": "FORMULA CODE HERE",
    "interpreter_output": "FORMULA INTERPRETER OUTPUT HERE",
}

Make sure you only call this function with a JSON format, otherwise it will not work.
And make sure you include both the formula code and the formula interpreter output.
"""


QUERY_PROMPT = """ \
Can you explain why the following code delimited in ``` is not solvable?
Could you then try to fix the code?

Here is the code:
```
{code}
```

And here is what the FORMULA interpreter says:

```
{interpreter_output}
```

Here are some additional details to keep in mind when trying to figure out what is wrong with the code:

{additional_details}

"""

SAMPLE_QUERY = """\

Can you explain why the following code delimited in ``` is not solvable?
Could you then try to fix the code?

Here is the code:
```
domain Mapping
{
  Component ::= new (id: Integer, utilization: Real).
  Processor ::= new (id: Integer).
  Mapping   ::= new (c: Component, p: Processor).

  // The utilization must be > 0
  invalidUtilization1 :- c is Component, c.utilization <= 0.
  invalidUtilization2 :- c is Component, c.utilization > 0.

  badMapping :- p is Processor,
    s = sum(0.0, { c.utilization |
              c is Component, Mapping(c, p) }), s > 100.

  conforms no badMapping, no invalidUtilization1, no invalidUtilization2.
}

partial model pm of Mapping
{
  c1 is Component(0, x).
  c2 is Component(1, y).
  p1 is Processor(0).
  Mapping(c1, p1).
  Mapping(c2, p1).
}
```

And here is what the FORMULA interpreter output is:

```
[]> solve pm 1 Mapping.conforms
Parsing text took: 1
Visiting text took: 0
Started solve task with Id 0.
0.06s.
[]> ls

Environment variables

Programs in file root
 +-- /
 | tmp_file.4ml

Programs in env root
 +-- /

All tasks
 Id | Kind  | Status | Result |      Started      | Duration
----|-------|--------|--------|-------------------|----------
 0  | Solve |  Done  | false  | 7/14/2023 3:44 PM |  0.28s
0.02s.
[]> ex 0 1 out.4ml
Model not solvable. Unsat core terms below.
Conflicts: Mapping.invalidUtilization2
Conflicts: Mapping.invalidUtilization1

0.01s.
```

"""

