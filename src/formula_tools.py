from typing import Any, Dict, Optional

from os.path import abspath

from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
from langchain.chat_models.base import BaseChatModel

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
from memory import SingletonMemory

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
    if not ci.DoCommand("load ./temp.4ml"):
        raise Exception("Load command failed.")

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

    return sw.ToString()


QueryFormulaCode = Tool.from_function(
    func=_QueryFormulaCode, name="QueryFormulaCode", description=QUERY_FORUMULA_CODE
)


class DecodeFormulaCodeLLM(BaseTool):
    """A tool for querying FORMULA code"""

    name = "DecodeFormulaCodeLLM"
    description = DECODE_FORMULA_CODE_LLM_DESC
    llm: BaseChatModel
    # memory: ConversationBufferMemory

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Any:
        # template = """You are a chatbot trying to fix the code from the human.

        # {chat_history}
        # Human: {human_input}
        # Chatbot:"""

        # prompt = PromptTemplate(
        #     input_variables=["chat_history", "human_input"], template=template
        # )

        # memory = ConversationBufferMemory(memory_key="chat_history")
        # llm_chain = LLMChain(
        #     llm=self.llm,
        #     # memory=self.memory,
        #     prompt="You are a chatbot trying to fix the code from the human.",
        #     verbose=True,
        # )
        # return llm_chain.predict(
        #     human_input=DECODE_FORMULA_CODE_LLM_PROMPT.format(code=query)
        # )
        print(SingletonMemory().get_memory())
        return self.llm.predict(DECODE_FORMULA_CODE_LLM_PROMPT.format(code=query))

    async def _arun(
        self,
    ):
        raise NotImplementedError("custom_search does not support async")
