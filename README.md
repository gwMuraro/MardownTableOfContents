# MardownTableOfContents
Script that generates markdown table of contents with a markdown as parameter 

The script use some regexs. You can modify these regex to match better your titles. You can add if needed. 

## Formating 
The document has to be a little bit formated. 
* When you enter a level 1 Title (# ) precise a 'I' charactere ('I' for 1, 'II' for 2 etc.). This numerotation avoid some python comments or the document big title to be matched by the regex 
* The '#' (or '#...#') character has to be preceded by a '\n' and followed by a space.
* Do not put spaces at the end of the title. The link would be affected.
* For now, try to not put too much special chars in your titles 
  * For now, are managed '?' and ''' chars. 

## Runing example : 
* Install requirements : 
`pip install -r requirements.txt`
* The sample text is in the repository as 'example.md' file. You will have to precise the name of the markdown file in the python script. 
* Then run the script : `python mdBuildToc.py`
* Copy-paste the result into your document and it's all good 
* Don't forget to test links


