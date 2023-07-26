# Self-fixing Formula LLM Model

This repository aims to utilize Langchain and FORMULA to create a Language Model (LLM) that can fix broken FORMULA code. By feeding your broken code to the LLM, it will attempt to provide a corrected version.

## How to Use

1. Install all the dependencies:
   ```bash
   pip3 install openai langchain
   ```

2. Copy and paste the compiled CommandLine FORMULA program into the `CommandLine` folder. The folder should contain the following files:
   - Antlr4.Runtime.Standard.dll
   - CommandLine.exe.config
   - Core.dll
   - CommandLine.dll
   - and more

Some commands that might be useful to doing this are:
```bash
cd Users/<USERNAME>/formula/Src/CommandLine/bin/Release/<PLATFORM>/x64/net6.0
cp -R * /Users/<USERNAME>/FormulaSelfRepairLLM/CommandLine
cp runtimes/osx-x64/native/libz3.dylib /Users/<USERNAME>/git/FormulaSelfRepairLLM/CommandLine
```

3. Create a new file called `config.py` (see `sample_config.py`) and fill in the details.

Now, you can try running the program using the following command:
```bash
python3 main.py --code_file sample_brokencode.4ml --output_file formula_output.txt
```

## How the Program Works

Langchain works based on agents (see [documentation](https://python.langchain.com/docs/modules/agents/)). An agent has multiple tools at its disposal and can prompt or process LLM to decide when to use a certain tool.

In this repository, there are 4 main tools in use:

1. DecodeFormulaLLM
   - This tool is used to describe what the formula code is doing and identify potential locations where the code might be broken in natural language. This makes it easier for the LLM to understand compared to raw code. This tool can also be used independently if needed.

2. LoadFormula
   - The agent calls this tool after it has created a potential fix for the provided formula code. It loads the given FORMULA code into an instance of the FORMULA program.

3. QueryFormula
   - This tool allows the agent to query the loaded FORMULA program to check if the formula code is valid or not.

4. DebugFormulaLLM
   - When the LLM creates code that is broken and not working, it can call on this tool to attempt to create a fix for the broken code.

## Future Work

Moving forward, there are several avenues for enhancing the capabilities of the self-repairing FORMULA LLM model. One crucial aspect is fine-tuning the model, especially for specific tasks related to describing how the code works. The challenge lies in obtaining a high-quality training dataset. To address this, one potential approach is to leverage the power of GPT by using it to generate diverse formula codes and then deliberately breaking the generated code. Trying to deliberately break the generated code could be done with seeking additional code-breaking assistance from GPT. What we have tried to some success is introducing random mutations into the Antlr AST parsing tree and observing the code's behavior.

Another promising direction is injecting the model with more context about FORMULA and its workings. Fine-tuning the LLM with various examples of functioning FORMULA code could lead to more accurate and informed code repairs. Additionally, refining the prompts and engineering them to align better with GPT's understanding can improve the model's performance significantly.

Exploring alternative large language models, such as GPT-4, is also worth considering. As language models evolve, their capabilities and performance can differ substantially, and a more advanced model may yield better results.

To address potential issues with infinite loops and repetitive behavior in code-fixing attempts, implementing a more robust memory system and introducing early stoppage mechanisms could be valuable. These measures would prevent excessive calls to the OpenAI API and improve overall efficiency.

Utilizing Large Language Model Technology to create self repairing modules for different code bases can end up becoming a very innovation new tool to help software developers speed up the time they spend debugging.