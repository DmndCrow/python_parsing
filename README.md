# python_parsing

Parsing novel chapters from https://www.wuxiaworld.co/ using BeautifulSoup and save them into pdf file.

1. python parsing.py get
  command will return books that user is reading
  
2. python parsing.py add novel_name
  command will add given novel, its shortened version into the list of reading novels.
  words must be separated with _. ex: Against_the_Gods
  [optional]: another argument that can be included is current reading chapter. ex:
    python parsing.py add against_the_gods 125
  after runnig command, shoertened version will be displayed. ex: Against_the_gods = atg
  
3. python parsing.py update novel_shortened_name new_chapter
  command is used to change current reading chapter to new_chapter. ex:
    python parsing.py update atg 145
    
4. python parsing.py generate novel_shortened_name
  command will create pdf file that will store all the chapters starting from current_chapter.
