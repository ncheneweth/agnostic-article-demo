# agnostic-article-demo

To see an example of using local llms, here is a simple experiment you can perform. 

The categorize.py script watches a folder on your desktop. If you drop a PDF file into the folder, the script will extract the text contents from the file, form a prompt asking an openai model to classify the type of document based on a list of categories defined in a yaml file (also in the desktop folder).

## Requirements

* A Mac with Apple Intelligence.
* [Homebrew](https://brew.sh) package manager.
* Python3

## Running the document categorizer on MacOS (requires Apple Intelligence)

1. clone this repository

```bash
git clone https://github.com/ncheneweth/agnostic-article-demo
cd agnostic-article-demo
```

2. Install [osaurus](https://github.com/dinoki-ai/osaurus) and launch api server

```bash
brew install --cask osaurus
osaurus serve
```
See Osaurus repository for instructions to install from release.  

3. Python setup and script dependencies  

The categorize.py script requires Python3 and the following packages:  
* watchdog    # to watch a folder for changes
* openai      # interacting with openai compatible API endpoints
* pyyaml      # load and parse yaml files
* pypdf       # load and parse PDF documents

If you don't have Python3 on your Mac, use Homebrew to [install](https://formulae.brew.sh/formula/python@3.14#default). Or, many developers use [Pyenv](https://github.com/pyenv/pyenv) to manage installed python versions. The example command line instructions below assume that you have installed pyenv along with version 3.13.8 of python.
 
```bash
echo '3.13.8' > .python-version   # or your version of choice
python -m venv .venv              # it is a good practice to define a virtual python environment for managing packages
source .venv/bin/activate         # activiate the virtual environment just defined
pip install -r requirements.txt   # now install the pacakges used by the script
```

4. Setup the watch folder and category descriptions

* create a folder on your desktop named **Inbox**  
* copy the categories.yaml file into the Inbox folder

You can customize the location of the folder and the category filename defined in the python script.  

The example categories.yaml contains some default categories.  

5. Run the script

```bash
python categorize.py

Watching inbox: /Users/username/Desktop/Inbox
Categories: receipts, real estate, tax returns
Press Ctrl+C to stop.
```

6. Try dropping different kinds of PDF files into the Inbox folder.

We all have bills, letters, forms, and countless other PDF files. Find a few and drag them into the Inbox. Now look at the output in your terminal window. How does the foundation model categorize the file?  

Try customizing the categories and descriptions to match the kinds of documents you drop in the folder. Add a category and then experiment with descriptions to see how the model performs.  

You can also try using some different models. Use Osaurus to download different models and change the value of LLM_MODEL in the script to use the desired model.   

Suggestions:  
- meta-llama-3.1-8b-instruct-4bit  
- qwen3-8b-4bit  

**Downloading Models**  
1. Click the Osaurus menu bar icon
2. Select Model Manager
3. Browse or search for models
4. Click Download on your chosen model
5. Monitor progress in the download queue

There are also several different ways of serving these small models besides osaurus. You might want to experiment with tools like ollama or LM Studio.  

