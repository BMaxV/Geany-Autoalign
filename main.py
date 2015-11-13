"""
The MIT License (MIT)

Copyright 2015 Max Voss

Permission is hereby granted, free of charge, to any person obtaining a 
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without 
limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons
to whom the Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

####################
#THIS IS CURRENTLY NOT WORKING CORRECTLY
####################

import geany
import re

class AlignPlugin(geany.Plugin):
    """ this plugin aligns all lines with a "=" in it with each other
    it stops when it's a different block or when it encounters a ":" 
    
    this is for right now, if there are some other alignment symbols you want,
    this could obviously be extended to do so.
    """
    __plugin_name__ = "Align Plugin"
    __plugin_version__ = "0.01"
    __plugin_description__ = "automatically aligns subsequent lines with shared elements or operators like = or , or ("
    __plugin_author__ = "Max Voss github"

    def __init__(self):
        geany.signals.connect('geany-startup-complete',self.startstuff)
        
        #switches between analysis and writing to the document.
        #useful because you can test if it's working correctly in the document
        #by analysing the document but simply not changing it.
        self.execute = True
        
        #turns of print statements for debugging.
        self.test=False
        
        #TODO: resetting scroll state seamlessly
        #TODO: specify editor notify event to listen to (text change)
        
        
    def startstuff(self,*args):
        """initializes the binding, if it were run on start up, it would
        be triggered too many times needlessly"""
        geany.signals.connect('editor-notify', self.main)
        
    def main(self,*args):
        """nice separation of functionality, maybe I'll cut down my god
        function later, right now it's small enough to be read at once"""
        self.detect_symbols()
                
    def detect_symbols(self):
        """the god function running this plugin"""
        symbols=["=",]
        notkeys=[":","+="] #lines with these symbols break all aligment
        
        doc=geany.document.get_current()
        if doc==None:
            return
        scin=doc.editor.scintilla
        
        
        #obvious
        line_number = scin.get_current_line()
        line        = scin.get_line(line_number)
        
        
        for s in symbols:
            foundlines=[]
            
            if s in line:
                
                #if it's a stop symbol continue
                stop=False
                for nk in notkeys:
                    if nk in line:
                        stop=True
                if stop==True:
                    continue
                
                #if yes go on searching for the other lines if they have one too
                foundlines.append(line_number)
                
                #indentation assuming there is no trailing whitespace, which there shouldn't be anyway
                
                matchstring="[\S]"
                matchob=re.search(matchstring,line)
                indents = matchob.start()
                if self.test:
                    print "indents",indents
                #save it for later
                firstindent=indents
                
                sindex = line.find(s)
                
                
                #go up...
                up       = 1
                combined = line_number-up
                
                
                
                while combined!=-1:
                    
                    #get the line
                    combined = line_number-up
                    line     = scin.get_line(combined)
                    
                    #they're already aligned if...
                    if line.find(s)==sindex:
                        break
                        
                    #similar conditions...
                    if s in line:
                        
                        stop=False
                        for nk in notkeys:
                            if nk in line:
                                stop=True
                        if stop==True:
                            break
                        
                        #only add when the number of indents is the same
                        matchstring="[\S]"
                        matchob=re.search(matchstring,line)
                        indents = matchob.start()
                        if indents==firstindent:
                            foundlines.append(combined)
                        else:
                            break
                    else:
                        break
                    up+=1
                    
                #same as up, except down
                down     = 1
                combined = line_number-down
                while True :
                    combined=line_number+down
                    line=scin.get_line(combined)
                    
                    if line.find(s)==sindex:
                        break
                        
                    if s in line:
                        stop=False
                        for nk in notkeys:
                            if nk in line:
                                stop=True
                        if stop==True:
                            break
                        
                        #find the first letter in the line, set all spaces before as indents
                        matchstring="[\S]"
                        matchob=re.search(matchstring,line)
                        indents = matchob.start()
                        
                        if indents==firstindent:
                            foundlines.append(combined)
                        else:
                            if self.test:
                                print "'"+line+"'", "was not indented the same way", indents,firstindent
                            break
                    else:
                        break
                    down+=1
            else:
                continue
            
            
            # ok so by now we have all relevant line numbers
            #which also means, if there is only one, we can stop
            
            if len(foundlines)==1:
                continue
            
            
            
            #let's sort them too please
            foundlines.sort()
            if self.test:
                print("finding lines")
                for line in foundlines:
                    tline=scin.get_line(line)
                    print("'"+tline+"'")
                
            #now everything is in order
            
            stringlines=[]
            
            #put em in a list
            for ind in foundlines:
                l=scin.get_line(ind)
                stringlines.append(l)
            
            
            #first lets get the maximum difference
            
            #split it up
            varnames    = []
            assignments = []
            
            for line in stringlines:
                tup=line.split(s)
                varnames.append(tup[0])
                assignments.append(tup[1])
            
            #iterate and set max
            c          = 0
            maxlen     = 0
            varnamelen = len(varnames)
            biggest    = None
            while c < varnamelen:
                var    = varnames[c]
                var    = var.strip()
                varlen = len(var)
                if varlen > maxlen:
                    maxlen  = varlen
                    biggest = var
                    
                c+=1
            if self.test:
                print("maxlen is from" ,biggest,"and is the length",maxlen)
                print("stripped vars")
                
            #now fill in the blanks
            c           = 0
            newvarnames = []
            while c < varnamelen:
                var = varnames[c]
                var = var.strip()
                if self.test:
                    print("'"+var+"'")
                varlen=len(var)
                if varlen < maxlen:
                    d    =  maxlen-varlen
                    
                    if self.test:
                        print("'"+var+"'")
                        print"difference between this and max is" ,d
                        
                        
                    newvar=firstindent*" " +var+" "*d
                    
                else:
                    newvar=firstindent*" " +var
                newvarnames.append(newvar)
                c+=1
            
            #now I just need to write the new lines...

            #anyway the new lines should be like this:
            
            #everything should be in order since we sorted once and then only iterated normaly
            
            newlines = []
            c        = 0
            ml       = len(foundlines)
            if self.test:
                print("assignments")
            while c < ml:
                a=assignments[c]
                a=a.strip()
                a=a.rstrip('\r\n')
                if self.test:
                    print("'"+a+"'")
                newline = newvarnames[c]+" = "+a+"\n"
                newlines.append(newline)
                c+=1
            if self.test:
                print("the newlines should be")
            newblock=""
            for line in newlines:
                if self.test:
                    print("'"+line+"'")
                newblock+=line
            the_entire_file = scin.get_contents()
            
            linenumber = 0
            newend     = 0
            c          = 0
            m          = len(foundlines)
            oldblock   = ""
            
            while c < m:
                linenumber  = foundlines[c]
                line        = scin.get_line(linenumber)
                
                oldblock+= line
                
                c+= 1
            
            cupos    = scin.get_current_position()
            startpos = the_entire_file.find(oldblock)
            posd     = cupos-startpos
            if self.test:
                print(posd)
                print(startpos)
                
            end = startpos+len(oldblock)
            if self.test:
                print(end)
            
            the_entire_file = the_entire_file[:startpos]+ newblock+ the_entire_file[end:]
            
            newcurpos=startpos+len(newblock)-1
            
            #I still have to set the position of the cursor correctly
            if self.execute==True:
                scin.set_text(the_entire_file)
                scin.set_current_position(newcurpos)
                scin.scroll_caret()


