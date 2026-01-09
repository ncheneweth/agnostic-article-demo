# agnostic-article-demo
Demonstrate simple use of local Apple intelligence language model

To see an example of using local llms, here is a simple experiment you can perform. 

The categorize.py script watches a folder on your desktop. If yo drop a PDF file into the folder, the script will extract the text contents from the file, form a prompt asking an openai model to classify the type of document based on a list of categories defined in a yaml file (also in the desktop folder).

Try customizing the categories and descriptions. You can add a category and then experiment with descriptions to see how the model performs.

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

3. Install script dependencies (with python virtual env)

Assumes _pyenv_  
```bash
echo '3.13.8' > .python-version   # or your version of choice
pip install -r requirements.txt
```

4. Setup the folder and categories

* create a folder on your desktop named **Inbox**  
* copy the categories.yaml file into the Inbox folder

The location of the folder and the yaml filename can be customized in the python script.  

There are a default set of categories in the yaml. You can define your own and  use your own descriptions.  

5. Run the script

```bash
python categorize.py

Watching inbox: /Users/username/Desktop/Inbox
Categories: receipts, real estate, tax returns
Press Ctrl+C to stop.
```

6. Try dropping different kinds of PDF into the Inbox folder.

We all have bills, letters, forms, and countless other PDF files. Find a few and drag them into the Inbox. Now look at the output in your terminal window. How does the foundation model categorize the file?  

There probably isn't a useful category for the file you chose. Add a category and a description. Tweak the description until the model gets better at identifying the file type.

Try using some different models.  

Suggestions:  
- meta-llama-3.1-8b-instruct-4bit  
- qwen3-8b-4bit  

There are also several different ways of serving these small models besides osaurus. You might want to experiment with tools like ollama or LM Studio.

