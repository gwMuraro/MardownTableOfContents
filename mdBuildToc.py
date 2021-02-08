
import re

patterns = [
            re.compile('\n#{1} ([I|^#].+)( *\n)'), 
            re.compile('\n#{2} ([^#].+)( *\n)'), 
            re.compile('\n#{3} ([^#].+)( *\n)'),  
]

def recFindTitles(pattern, doc, pos, to, level) :
  str = ""
  # get field of next recurse 
  title = pattern.search(doc, pos = pos, endpos = to)
  
  # Last none element case
  if title == None : 
    return "" 
  
  next_title = pattern.search(doc, pos = title.end(), endpos = to)
  
  # Current title formating 
  nb_of_spaces = '\t' * level
  text_title = title.group(1)
  text_link = title.group(1).replace(' ', '-').replace("?", '').replace('\'', '').lower()
  str += nb_of_spaces + '* [' + text_title + '](#' + text_link + ')\n' 

  # get recursion 1 level down 
  if len(patterns) >= level + 1 and next_title != None :
    str += recFindTitles(patterns[level + 1], doc, title.end(), next_title.start(), level+1)

  # get recursion at same level
  str += recFindTitles(patterns[level], doc, title.end(), to, level)

  return str 

with open('example.md') as file : 
  doc = file.read()
  str = recFindTitles(patterns[0], doc, 0, len(doc), 0)
print(str)
