# MardownTableOfContents
Script that generates markdown table of contents with a markdown as parameter 

The script use some regexs. You can modify these regex to match better your titles. 

## Formating 
The document has to be a little bit formated. 
* When you enter a level 1 Title (# ) precise a 'I' charactere ('I' for 1, 'II' for 2 etc.)
* Do not put spaces at the end of the title. The link would be affected.
* For now, try to not put too much special chars in your titles 
  * Are managed : '?' and ''' chars. 

## Runing example : 
The sample text is in the repository as 'example.md' file. You will have to precise the name of the markdown file in the python script. 

Then run python : `python mdBuildToc.py`

copy-paste the result :) 


