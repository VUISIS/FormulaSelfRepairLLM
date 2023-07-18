from typing import Any, Dict, Optional

from os.path import abspath

from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
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
from prompts import LOAD_FORMULA_CODE, QUERY_FORUMULA_CODE
import os
from pythonnet import load


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


class LoadFormulaCode(BaseTool):
    """A tool for running python code in a REPL."""

    name = "LoadFormulaCode"
    description = LOAD_FORMULA_CODE

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Any:
        """Use the tool."""

        # Put the query string into a file ./temp.4ml
        with open("./temp.4ml", "w") as f:
            f.write(query)

        # Load the file into the FORMULA program
        if not ci.DoCommand("load ./temp.4ml"):
            raise Exception("Load command failed.")

        return "Successfully loaded FORMULA code, you can now query the code using the query formula code tool."


class QueryFormulaCode(BaseTool):
    """A tool for querying FORMULA code"""

    name = "QueryFormulaCode"
    description = QUERY_FORUMULA_CODE


    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Any:
        sw.GetStringBuilder().Clear()
        if not ci.DoCommand(query):
            raise Exception("Query command failed.")

        return sw.ToString()

class DecodeFormulaCodeLLM(BaseTool):
    """A tool for querying FORMULA code"""

    name = "DecodeFormulaCodeLLM"
    description = QUERY_FORUMULA_CODE
    llm = Field()
    memory = Field()

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Any:
        pass