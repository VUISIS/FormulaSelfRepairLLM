from typing import Any, Dict, Optional

from os.path import abspath

from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
from langchain.chat_models.base import BaseChatModel
from langchain.chains import SequentialChain
from pydantic import (
    BaseModel,
    Extra,
    Field,
    create_model,
    root_validator,
    validate_arguments,
)
from langchain.tools.base import BaseTool
from langchain.utilities import PythonREPL
from prompts import (
    DEBUG_FORMULA_CODE_LLM_DESC,
    DECODE_FORMULA_CODE_LLM_DESC,
    LOAD_FORMULA_CODE,
    QUERY_FORUMULA_CODE,
    DECODE_FORMULA_CODE_LLM_PROMPT,
)
import os
from pythonnet import load
from langchain.memory import ConversationBufferMemory
from langchain import LLMChain, PromptTemplate
from langchain.tools import BaseTool, StructuredTool, Tool, tool
import json

load("coreclr", runtime_config=os.path.abspath("../runtimeconfig.json"))
import clr

process_path = abspath("../CommandLine/CommandLine.dll")

clr.AddReference(os.path.abspath(process_path))

from Microsoft.Formula.CommandLine import CommandInterface, CommandLineProgram
from System.IO import StringWriter
from System import Console

sink = CommandLineProgram.ConsoleSink()
chooser = CommandLineProgram.ConsoleChooser()
ci = CommandInterface(sink, chooser)

sw = StringWriter()
Console.SetOut(sw)
Console.SetError(sw)

if not ci.DoCommand("wait on"):
    raise Exception("Wait on command failed.")

if not ci.DoCommand("unload *"):
    raise Exception("Unload command failed.")


def _LoadFormulaCode(query: str):
    """Use the tool."""

    # Put the query string into a file ./temp.4ml
    with open("./temp.4ml", "w") as f:
        f.write(query)

    # Load the file into the FORMULA program

    if not ci.DoCommand("unload"):
        raise Exception("Unload command failed.")

    if not ci.DoCommand("load ./temp.4ml"):
        raise Exception("Load command failed.")

    output = sw.ToString()
    sw.GetStringBuilder().Clear()

    # if output contains the word "failed" case insensitive return false
    if "failed" in output.lower():
        return f"Failed to load FORMULA code, you probably have an syntax error in your code. Please check your code and try again.\n\nHere is the output from the FORMULA program:\n{output}"

    return "Successfully loaded FORMULA code, you can now query the code using the query formula code tool."


LoadFormulaCode = Tool.from_function(
    func=_LoadFormulaCode, name="LoadFormulaCode", description=LOAD_FORMULA_CODE
)


# class QueryFormulaCode(BaseTool):
#     """A tool for querying FORMULA code"""

#     name = "QueryFormulaCode"
#     description = QUERY_FORUMULA_CODE

#     def _run(
#         self,
#         query: str,
#         run_manager: Optional[CallbackManagerForToolRun] = None,
#     ) -> Any:
#         sw.GetStringBuilder().Clear()
#         if not ci.DoCommand(query):
#             raise Exception("Query command failed.")

#         return sw.ToString()


def _QueryFormulaCode(query: str):
    """Use the tool."""

    sw.GetStringBuilder().Clear()
    if not ci.DoCommand(query):
        raise Exception("Query command failed.")

    output = sw.ToString()
    sw.GetStringBuilder().Clear()

    if "not solvable" in output.lower():
        return f""" \
Your code is not solvable. This means that the code is broken and you need to fix it.
Here was the output from the FORMULA program:

{output}

Make sure to try to regenerate your code, using the DebugFormulaCodeLLM tool if needed, and then re run the program again
using the LoadFormulaCode tool / QueryFormulaCode Formula REPL tools.
"""

    return output


QueryFormulaCode = Tool.from_function(
    func=_QueryFormulaCode, name="QueryFormulaCode", description=QUERY_FORUMULA_CODE
)


class DecodeFormulaCodeLLM(BaseTool):
    """A tool for querying FORMULA code"""

    name = "DecodeFormulaCodeLLM"
    description = DECODE_FORMULA_CODE_LLM_DESC
    llm: BaseChatModel

    def _run(
        self,
        query: str = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs,
    ) -> Any:
        # print(kwargs)

        # parsed_code = json.loads(query)
        parsed_code = kwargs
        code = parsed_code["code"]
        interpreter_output = parsed_code["interpreter_output"]

        code_description_template = """
You are a chatbot who is an expert at programming in Prolog and Formula,
designed to read FORMULA code, understand what the code does. The code is also going to be broken,
and you are tasked with trying to figure out how to fix it.

Your goal is to describe what the code is exactly doing, and what each interpreter output is saying.

Formula a novel formal specification language based on open-world logic programs
and behavioral types. Its goals are (1) succinct specifications of domain-specific abstractions
and compilers, (2) efficient reasoning and compilation of input programs, (3) diverse syn-
thesis and fast verification. It takes a unique approach towards achieving these goals:
Specifications are written as strongly-typed open-world logic programs. They are highly
declarative and easily express rich synthesis / verification problems. Automated reason-
ing is enabled by efficient symbolic execution of logic programs into constraints. The language
is similar to datalog, and can help one model DSL (domain specific languages).

Here is the code and interpreter output delimited by ```

code:
```
{code}
```

interpreter output:
```
{interpreter_output}
```
"""

        code_painpoints_template = """
You are a chatbot who is an expert at programming in Prolog and Formula,
designed to read FORMULA code, understand what the code does. The code is also going to be broken,
and you are tasked with trying to figure out how to fix it.

You will be given the code, the interpreter output, and an example of what the code is doing.
Your goal is to figure out where are all the possible places where the code is broken.


Formula a novel formal specification language based on open-world logic programs
and behavioral types. Its goals are (1) succinct specifications of domain-specific abstractions
and compilers, (2) efficient reasoning and compilation of input programs, (3) diverse syn-
thesis and fast verification. It takes a unique approach towards achieving these goals:
Specifications are written as strongly-typed open-world logic programs. They are highly
declarative and easily express rich synthesis / verification problems. Automated reason-
ing is enabled by efficient symbolic execution of logic programs into constraints. The language
is similar to datalog, and can help one model DSL (domain specific languages).

Here is the code and interpreter output delimited by ```

code:
```
{code}
```

interpreter output:
```
{interpreter_output}
```

what the code is doing:
```
{explanation}
```

"""
        prompt_template = PromptTemplate(
            input_variables=["code", "interpreter_output"],
            template=code_description_template,
        )
        code_understander_chain = LLMChain(
            llm=self.llm, prompt=prompt_template, output_key="explanation"
        )

        prompt_template = PromptTemplate(
            input_variables=["code", "interpreter_output", "explanation"],
            template=code_painpoints_template,
        )
        painpoints_chain = LLMChain(
            llm=self.llm, prompt=prompt_template, output_key="pain_points"
        )

        overall_chain = SequentialChain(
            chains=[code_understander_chain, painpoints_chain],
            input_variables=["code", "interpreter_output"],
            # Here we return multiple variables
            output_variables=["explanation", "pain_points"],
            verbose=True,
        )

        output = overall_chain(parsed_code)

        #         return_output = f""" \
        # Here is what the code is doing: {output['explanation']}\n\nHere are the possible places where we can \
        # fix the code: \ {output['pain_points']}.

        # Your next step now is to generate a piece of code implementing one of the example fixes, and then testing if the code
        # actually works with running the FORMULA REPL. If the code works, then your job is done and you should return the code
        # as well as an explanation of what the fixes you made were. If the code does not work, then you should try to debug the code.

        # Remember the above task is for YOU, the chatbot and master formula programmar to do. You, the chatbot, have access to the
        # FORMULA repl commands with the LoadFormulaCode and QueryFormulaCode tools. You can also use the DecodeFormulaCodeLLM tool again if need be.
        # """

        return_output = f""" \
Here is what the code is doing: {output['explanation']}

Your next step now is to generate a piece of code implementing one of the example fixes, and then testing if the code
actually works with running the FORMULA REPL. If the code works, then your job is done and you should return the code
as well as an explanation of what the fixes you made were. If the code does not work, then you should try to debug the code.

Remember the above task is for YOU, the chatbot and master formula programmar to do. You, the chatbot, have access to the
FORMULA repl commands with the LoadFormulaCode and QueryFormulaCode tools. You can also use the DecodeFormulaCodeLLM tool again if need be.
"""
        return return_output
        # return f"Here is what the code is doing: {output['explanation']}\n\nHere are the possible places where we can fix the code: {output['pain_points']}"

    async def _arun(
        self,
    ):
        raise NotImplementedError("custom_search does not support async")


# class DecodeFormulaCodeLLM(BaseTool):
#     """A tool for querying FORMULA code"""

#     name = "DecodeFormulaCodeLLM"
#     description = DECODE_FORMULA_CODE_LLM_DESC
#     llm: BaseChatModel
#     # memory: ConversationBufferMemory

#     def _run(
#         self,
#         query: str,
#         run_manager: Optional[CallbackManagerForToolRun] = None,
#     ) -> Any:
#         # template = """You are a chatbot trying to fix the code from the human.

#         # {chat_history}
#         # Human: {human_input}
#         # Chatbot:"""

#         # prompt = PromptTemplate(
#         #     input_variables=["chat_history", "human_input"], template=template
#         # )

#         # memory = ConversationBufferMemory(memory_key="chat_history")
#         # llm_chain = LLMChain(
#         #     llm=self.llm,
#         #     # memory=self.memory,
#         #     prompt="You are a chatbot trying to fix the code from the human.",
#         #     verbose=True,
#         # )
#         # return llm_chain.predict(
#         #     human_input=DECODE_FORMULA_CODE_LLM_PROMPT.format(code=query)
#         # )
#         # return self.llm.predict(DECODE_FORMULA_CODE_LLM_PROMPT.format(code=query))

#     async def _arun(
#         self,
#     ):
#         raise NotImplementedError("custom_search does not support async")


class DebugFormulaCodeLLM(BaseTool):
    """A tool for querying FORMULA code"""

    name = "DebugFormulaCodeLLM"
    description = DEBUG_FORMULA_CODE_LLM_DESC
    llm: BaseChatModel
    # memory: ConversationBufferMemory

    def _run(self, **kwargs) -> Any:
        parsed_code = kwargs
        template = """
        You are a chatbot who is an expert at programming in Prolog and Formula,
designed to read broken FORMULA code and understand what the error is.

Formula a novel formal specification language based on open-world logic programs
and behavioral types. Its goals are (1) succinct specifications of domain-specific abstractions
and compilers, (2) efficient reasoning and compilation of input programs, (3) diverse syn-
thesis and fast verification. It takes a unique approach towards achieving these goals:
Specifications are written as strongly-typed open-world logic programs. They are highly
declarative and easily express rich synthesis / verification problems. Automated reason-
ing is enabled by efficient symbolic execution of logic programs into constraints. The language
is similar to datalog, and can help one model DSL (domain specific languages).

You will be given the code and the interpreter output. Your goal is to flesh out the debug message
and figure out what the error is.

Here is one example of an error message:

[]> (Failed) temp.4ml
temp.4ml (8, 30): Syntax error - Component got 1 arguments but needs 2
temp.4ml (9, 30): Syntax error - Component got 1 arguments but needs 2

This means that on line 8 and 9 character 30 there is an error where the component got 1 arguments but needs 2.

Here is the code that is broken:
```
{code}
```

and the interpreter output:

```
{interpreter_output}
```

"""

        output = self.llm.predict(template.format(**parsed_code))

        return_output = f""" \
Here is some debugging information: {output}.

Your next step now is to generate a piece of code implementing one of the example fixes, and then testing if the code
actually works with running the FORMULA REPL. If the code works, then your job is done and you should return the code
as well as an explanation of what the fixes you made were. If the code does not work, then you should try to debug the code.

Remember the above task is for YOU, the chatbot and master formula programmar to do. You, the chatbot, have access to the
FORMULA repl commands with the LoadFormulaCode and QueryFormulaCode tools. You can also use the DecodeFormulaCodeLLM tool again if need be.
"""

        return return_output

    async def _arun(
        self,
    ):
        raise NotImplementedError("custom_search does not support async")
