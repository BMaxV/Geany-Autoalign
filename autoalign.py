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

###############
# this should be working correctly, at least for me
# if you encounter any problems, please leave me a message 
# on the projects github page https://github.com/BMaxV/Geany-Autoalign
##############


import geany
import re

class AlignPlugin(geany.Plugin):
    """ this plugin aligns all lines with a "=" in it with each other
    it stops when it's a different block or when it encounters a ":" 
    
    this is for right now, if there are some other alignment symbols you want,
    this could obviously be extended to do so.
    """
    __plugin_name__ = "Align Plugin"
    __plugin_version__ = "0.9"
    __plugin_description__ = "automatically aligns subsequent lines with shared elements or operators like = or , or ("
    __plugin_author__ = "Max Voss https://github.com/BMaxV"

    def __init__(self):
        
        geany.signals.connect('geany-startup-complete',self.startstuff)
        
        #switches between analysis and writing to the document.
        #useful because you can test if it's working correctly in the document
        #by analysing the document but simply not changing it.
        self.execute = True
        
        #turns of print statements for debugging.
        self.test=False
        
        if self.test:
            print("init")
        #TODO: resetting scroll state seamlessly
        #TODO: specify editor notify event to listen to (text change)
        
        #just to keep track of how many times this was triggered
        self.c=0
        
        
    def startstuff(self,*args):
        """initializes the binding, if it were run on start up, it would
        be triggered too many times needlessly"""
        geany.signals.connect('editor-notify', self.main)
        
    def main(self,*args):
        """nice separation of functionality, maybe I'll cut down my god
        function later, right now it's small enough to be read at once"""
        #print("main")
        codes=[2001,2007] #2008
        #2001 is charadded,2005 is all keypresses
        #1 is supposedly content change
        
        if args[2].nmhdr.code in codes:
            if self.test:
                print("triggercode:")
                print(args[2].nmhdr.code)
            
            #putting it behind the 'if' somehow stops the changes
            #from being applied or something.
            
            #correct code? hm...
            self.detect_symbols()
        
    def line_split(self,foundlines,s):
        """splits the lines into the parts left and right of the symbol to be aligned"""
        #now everything is in order
        stringlines=[]
        
        #put em in a list
        for ind in foundlines:
            l=self.scin.get_line(ind)
            stringlines.append(l)
        
        #first lets get the maximum difference
        
        #split it up
        varnames    = []
        assignments = []
        
        c=0
        m=len(stringlines)
        
        self.new_cursor_position="undefined"
            
        while c < m:
            line        = stringlines[c]
            new_s_index = line.find(s)
            var         = line[:new_s_index]
            assignment  = line[new_s_index+1:]
            
            varnames.append(var)
            assignments.append(assignment)
            
            #find the relative cursor position in my parts:
            
            
            if self.test:
                print("line and cursorline pre assign")
                print(c)
                print(self.cursor_line_foundline_index)
            
            if c==self.cursor_line_foundline_index:
                if self.test:
                    print("in cursorline")
                if self.relative_cursor_in_line_position -1 == new_s_index:
                    if self.test:
                        print("at symbol set")
                    self.new_cursor_position = "at symbol"
                    self.in_section_index    = 0
                
                if self.relative_cursor_in_line_position < self.firstindent:
                    if self.test:
                        print("in indent set")
                    
                    self.new_cursor_position = "in indent"
                    
                    self.new_cursor_offset   = self.relative_cursor_in_line_position
                    #the cursor is inside the indentation block, I have to move it I think.
                
                #here the offset needs to be different.
                
                if self.firstindent-1 < self.relative_cursor_in_line_position < new_s_index+1:
                    if self.test:
                        print("in var set")
                    #the cursor is inside the variable, I think
                    self.new_cursor_position = "in var"
                    
                    self.in_section_index = self.relative_cursor_in_line_position
                 
                if self.relative_cursor_in_line_position-1 > new_s_index:
                    if self.test:
                        print("after symbol set")
                        print(self.relative_cursor_in_line_position )
                        print(new_s_index)
                    self.new_cursor_position = "after symbol"
                    self.in_section_index    = self.relative_cursor_in_line_position - new_s_index
                
                if self.new_cursor_position=="undefined":
                    if self.test:
                        print("UNDEFINED")
                        print(self.relative_cursor_in_line_position)
                        print(self.firstindent)
            c+=1
        return varnames,assignments
        
    def find_lines(self,line_number,line,symbol,notkeys):
        """finds all adjecent lines that also need to be aligned"""
        s=symbol
        foundlines=[]
        
        #if it's a stop symbol continue
        
        #if yes go on searching for the other lines if they have one too
        foundlines.append(line_number)
        
        #indentation assuming there is no trailing whitespace, which there shouldn't be anyway
        
        matchstring="[\S]"
        matchob=re.search(matchstring,line)
        indents = matchob.start()
        
        if self.test:
            print ("indents")
            print(indents)
            
        #save it for later
        self.firstindent=indents
        
        sindex = line.find(s)
        
        #go up...
        up       = 1
        combined = line_number-up
        
        while combined!=-1:
            
            #get the line
            combined = line_number-up
            line     = self.scin.get_line(combined)
            
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
                if indents==self.firstindent:
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
            line=self.scin.get_line(combined)
            
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
                
                if indents==self.firstindent:
                    foundlines.append(combined)
                else:
                    if self.test:
                        print "'"+line+"'", "was not indented the same way", indents,self.firstindent
                    break
            else:
                break
            down+=1
        return foundlines
    
    def buffervars(self,varnames):
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
                    
                newvar=self.firstindent*" " +var+" "*d
                
            else:
                newvar=self.firstindent*" " +var
            newvarnames.append(newvar)
            c+=1
            
        return newvarnames
        
    def cursor_position(self,foundlines):
    
        self.cursor_position_before=self.scin.get_current_position()
        #get the first line start
        self.blockstart = self.scin.get_position_from_line(foundlines[0])
        
        blockend    = self.blockstart            
        
        c=0
        m=len(foundlines)
        while c < m:
            l=foundlines[c]
            ll=self.scin.get_line_length(l)
            blockend+=ll
            if self.blockstart <=self.cursor_position_before <= blockend:
                self.cursorline = l
                cursorlinestart = self.scin.get_position_from_line(l)
                
                self.relative_cursor_in_line_position = self.cursor_position_before - cursorlinestart
                self.cursor_line_foundline_index      = c
                break
                
            c+=1
            
    def set_lines(self,foundlines,newlines):
        if self.test:
            print("")
            print("")
            print(self.c)
            print("")
            print("")
        
        c=0
        m=len(foundlines)
        while c < m:
            
            linenumber  = foundlines[c]
            line        = self.scin.get_line(linenumber)

            startpos=self.scin.get_position_from_line(linenumber) 
            #selection start
            self.scin.set_selection_start(startpos)
            lenpnl=self.scin.get_line_length(linenumber)                
            endpos=startpos+lenpnl
            #selection end
            self.scin.set_selection_end(endpos)
                            
            t=newlines[c]
            #set new text
            self.scin.replace_sel(t)
            
            newlinepos = self.scin.get_position_from_line(linenumber)
            nll        = self.scin.get_line_length(linenumber)                
            
            new_cursor_pos = newlinepos
           
            c+= 1
            
        return new_cursor_pos
    
    def assemble_new_lines(self,newvarnames,assignments,symbol):
        
        newblocklength=0
        
        newlines = []
        c        = 0
        l       = len(newvarnames)
        if self.test:
            print("assignments")
            
        while c < l:
            a=assignments[c]
            a=a.strip()
            a=a.rstrip('\r\n')
            if self.test:
                print("'"+a+"'")
            newline = newvarnames[c]+" "+symbol+" "+a+"\n"
            newlines.append(newline)
            
            if c == self.cursor_line_foundline_index:
                #this is the new line my cursor needs to be in.
                
                new_symbol_index = len(newvarnames[c])
                
                self.new_inline_index=0
                if self.test:
                    print("new cursor position")
                    print(self.new_cursor_position)
                
                if self.new_cursor_position == "at symbol":
                    if self.test:
                        print("at symbol")
                        print("new symbol index")
                        print(new_symbol_index)
                    self.new_inline_index = new_symbol_index +3
                    
                if self.new_cursor_position == "in indent":
                    if self.test:
                        print("in indent")
                    self.new_inline_index = self.in_section_index #?
                
                if self.new_cursor_position == "in var":
                    if self.test:
                        print("in var")
                    self.new_inline_index = self.in_section_index
                    
                if self.new_cursor_position == "after symbol":
                    if self.test:
                        print("after symbol")
                    self.new_inline_index = new_symbol_index  + self.in_section_index
                if self.test:
                    print("hurr")
                #oldblockstart + newblock length up to this line, + newline index
                self.new_cursor_position = self.blockstart + newblocklength + self.new_inline_index
            #anticipate new cursor position
            #
            
            newblocklength+=len(newline)
            
            c+=1
            
        return newlines
    
    def detect_symbols(self):
        """the god function running this plugin"""
        
        self.c+=1
        
        symbols=["=",]
        notkeys=[":","+=","!="] #lines with these symbols break all aligment
        
        doc=geany.document.get_current()
        if doc==None:
            if self.test:
                print("no document, aborting")
            return
        self.scin=doc.editor.scintilla
        
        #obvious
        line_number = self.scin.get_current_line()
        line        = self.scin.get_line(line_number)
        
        for s in symbols:
            
            foundlines=[]
            
            if s in line:
                stop=False
                for nk in notkeys:
                    if nk in line:
                        stop=True
                        
                if stop==True:
                    if self.test:
                        print("continuing")
                    continue
                
                foundlines=self.find_lines(line_number,line,s,notkeys)
            else:
                if self.test:
                    print("symbol not in line")
                continue
            
            # ok so by now we have all relevant line numbers
            #which also means, if there is only one, we can stop
            
            if len(foundlines)==1:
                if self.test:
                    print("online one line")
                continue
            
            #let's sort them too please
            foundlines.sort()
            
            if self.test:
                print("finding lines")
                for line in foundlines:
                    tline=self.scin.get_line(line)
                    print("'"+tline+"'")
            
            self.cursor_position(foundlines)
            
            varnames,assigments=self.line_split(foundlines,s)
            newvarnames=self.buffervars(varnames)
           
            #now I just need to write the new lines...
            #anyway the new lines should be like this:
            #everything should be in order since we sorted once and then only iterated normaly
            newlines=self.assemble_new_lines(newvarnames,assigments,s)
        
            if self.test:
                print("the newlines should be")
                for line in newlines:
                    print("'"+line+"'")
            
            if self.execute==False:
                return
            
            #ok so. ideally the new position would be 
            #where the old position was, in terms of syntax, or relative inside of words.
            alltext = self.scin.get_contents()
            oldpos  = self.scin.get_current_position()
            if self.test:
                print("old cursor position")
                print(len(alltext))
                print(oldpos)
                print(alltext[oldpos-1])
            
            new_cursor_pos=self.set_lines(foundlines,newlines)
            
            #this should be where the new cursor position sits
            alltext=self.scin.get_contents()
            if self.test:
                print("new cursor position")
                print(alltext[self.new_cursor_position]+"#")
            self.scin.set_current_position(self.new_cursor_position)
