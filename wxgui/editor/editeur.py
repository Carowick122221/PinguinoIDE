#!/usr/bin/env python
# generated by wxGlade 0.4.1 on Fri Jul 18 12:43:34 2008

"""-------------------------------------------------------------------------
 editeur, an editor class for Pinguino IDE

                         (c) 2008 Jean-Pierre MANDON <jp.mandon@gmail.com> 

        This library is free software; you can redistribute it and/or
        modify it under the terms of the GNU Lesser General Public
        License as published by the Free Software Foundation; either
        version 2.1 of the License, or (at your option) any later version.

        This library is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
        Lesser General Public License for more details.

        You should have received a copy of the GNU Lesser General Public
        License along with this library; if not, write to the Free Software
        Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
-------------------------------------------------------------------------"""

# $Id: editeur.py,v beta 1 2008/09/06 15:03:00 jean-pierre mandon
# bug #01 replaced splitext by split in savefile
# $Id: editeur.py,v beta 6 2009/06/17 17:00:00 jean-pierre mandon
# full support of UTF8
# case sensitive help
# $Id: editeur.py,v beta 2 2010/02/15 15:03:00 jean-pierre mandon
# added function highlightline
# lexer modified

import wx
import os
import sys
import codecs
import wx.stc as stc
import keyword
from wxgui._trad import _
from dic import Autocompleter

class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, Open):
        wx.FileDropTarget.__init__(self)
        self.Open = Open

    def OnDropFiles(self, x, y, filenames):
        for file in filenames: self.Open(file)



########################################################################
class Editor:

    #----------------------------------------------------------------------
    def __initEditor__(self):
        """Constructor"""
        self.onglet=[]
        self.stcpage=[]
        self.filename=[]
        self.sheetFunctions = []
        self.choiceFunctions = []
        self.line=-1
        self.inhibitChangeEvents = False
        if self.getElse("Main", "tools", "True") and self.getElse("Tools", "files", "True"):
            self.notebookEditor.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.Files.update_dockFiles)

    #----------------------------------------------------------------------
    def getFontPreferences(self):	
        self.loadConfigFile()
        def setDefault():
            font = wx.Font(10, wx.TELETYPE, wx.NORMAL, wx.NORMAL, True)
            self.setConfig("Source", "font", font.FaceName)
            self.setConfig("Source", "size", font.PointSize)
            return font      

        try:
            if self.getConfig("Source", "fontdefault") == "False":
                try:
                    FaceNAme = self.getConfig("Source", "font")
                    PointSize = self.getConfig("Source", "size")
                    font = wx.Font(10, wx.TELETYPE, wx.NORMAL, wx.NORMAL, True)
                    font.SetFaceName(FaceNAme)
                    font.SetPointSize(PointSize)
                except: font = setDefault()
                return font

            else:
                font = wx.Font(10, wx.TELETYPE, wx.NORMAL, wx.NORMAL, True)
                return font
        except:
            self.setConfig("Source", "fontdefault", True)
            font = setDefault()
            return font
    
    #----------------------------------------------------------------------
    def getCurrentPage(self):
        """"""
        return self.stcpage[self.notebookEditor.GetSelection()]
        

    #----------------------------------------------------------------------
    def focus(self, event=None):
        self.getCurrentPage().SetFocus()
        return

    #----------------------------------------------------------------------
    def buildSheet(self, name):
        p = wx.Panel(self.notebookEditor,-1, style = wx.NO_FULL_REPAINT_ON_RESIZE)
        self.onglet.append(p)

        stc = wx.stc.StyledTextCtrl(id=wx.NewId(),
                                    name='styledTextCtrl1', parent=p,  # pos=wx.Point(0, 35),
                                    size=wx.Size(-1, -1), 
                                    style=wx.SUNKEN_BORDER)

        stc.SetUseTabs(False)

        self.loadConfigFile()
        try:
            tabSize = self.getConfig("Source", "tabSize")
            stc.SetTabWidth(tabSize)
        except:
            tabSize = 4
            self.setConfig("Source", "tabSize", tabSize)
            stc.SetTabWidth(tabSize)
            
        #self.saveConfig()
        stc.SetLexer(wx.stc.STC_LEX_CPP)

        stc.SetMargins(2,2)
        stc.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER) 
        stc.SetMarginWidth(1, 40)
        stc.SetMarginWidth(2, 10)
        stc.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER,"fore:#000000,back:#afc8e1ff,size:500")  
        stc.SetMarginSensitive(1, True)
        stc.SetMarginSensitive(2, True)

        stc.SetMarginType(3, wx.stc.STC_MARGIN_SYMBOL)
        stc.SetMarginMask(3, wx.stc.STC_MASK_FOLDERS)
        stc.SetMarginSensitive(3, True)
        stc.SetMarginWidth(3, 12)                

        stc.SetProperty("fold", "1")
        stc.SetProperty("tab.timmy.whinge.level", "1")

        stc.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEROPEN,    wx.stc.STC_MARK_BOXMINUS,          "white", "#808080")
        stc.MarkerDefine(wx.stc.STC_MARKNUM_FOLDER,        wx.stc.STC_MARK_BOXPLUS,           "white", "#808080")
        stc.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERSUB,     wx.stc.STC_MARK_VLINE,             "white", "#808080")
        stc.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERTAIL,    wx.stc.STC_MARK_LCORNER,           "white", "#808080")
        stc.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEREND,     wx.stc.STC_MARK_BOXPLUSCONNECTED,  "white", "#808080")
        stc.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEROPENMID, wx.stc.STC_MARK_BOXMINUSCONNECTED, "white", "#808080")
        stc.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERMIDTAIL, wx.stc.STC_MARK_TCORNER,           "white", "#808080")

        self.stcpage.append(stc)
        stc.SetMinSize(wx.Size(-1, -1))

        p.SetAutoLayout( True )
        p.Layout()

        boxSizer = wx.BoxSizer(orient=wx.VERTICAL)        
        boxSizer.Fit(p)
        boxSizer.SetSizeHints(p)
        p.SetSizer(boxSizer)        
        boxSizer.AddWindow(stc, 1, border=0, flag=wx.EXPAND|wx.ADJUST_MINSIZE)


        self.notebookEditor.AddPage(p,os.path.split(name)[1])
        self.SendSizeEvent()
#        self._mgr.Update()
        self.panelEditor.Layout()
        self.sheetFunctions.append({})      

    #----------------------------------------------------------------------
    def New(self, name):
        self.background.Hide()
        self.notebookEditor.Show()
        self.buildSheet(name)
        self.notebookEditor.ChangeSelection(len(self.onglet)-1) ### Set ~ ChangeSelection -- bjoernp
        newIdx = self.notebookEditor.GetSelection()
        #self.stcpage[newIdx].Bind(stc.EVT_STC_MODIFIED,self.focus)
        self.stcpage[newIdx].Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.stcpage[newIdx].Bind(wx.EVT_LEFT_UP, self.Onclick)
        self.stcpage[newIdx].Bind(wx.EVT_RIGHT_UP, self.Onclick)   
        self.filename.append(name+".pde")
        self.seteditorproperties(self.reservedword, self.rw)
        self.editeur=self.stcpage[newIdx]
        self.editeur.Bind(wx.EVT_CONTEXT_MENU, self.OnContexMenuTools)
        
        if self.getElse("main", "auto-complete", "True") and self.getElse("Completer", "enable", "True"):
            self.editeur.Bind(wx.EVT_KEY_UP, self.OnKeyEvent)
        
        self.editeur.Bind(wx.EVT_CHAR, self.OnInsertChar)
        self.editeur.Bind(stc.EVT_STC_UPDATEUI, self.OnUpdateUI)
        self.editeur.Bind(stc.EVT_STC_UPDATEUI, self.updateStatusBar)
        self.editeur.Bind(wx.EVT_LEFT_UP, self.OnLeftCklick)
        self.editeur.Bind(wx.stc.EVT_STC_MARGINCLICK, self.OnMarginClick)    
        self.editeur.Bind(wx.stc.EVT_STC_SAVEPOINTLEFT, self.OnSavepointLeft)  
        self.editeur.Bind(wx.stc.EVT_STC_SAVEPOINTREACHED, self.OnSavepointReached)
        
        color = self.getColorConfig("Highligh", "selection", [241, 132, 88])         
        self.editeur.SetSelBackground(True, color)

        
        if self.getElse("Main", "open-save", "True") and self.getElse("Open/Save", "template", "True"):
            self.insertSnippet("Insert Info {snippet}")
            self.editeur.GotoLine(self.editeur.LineCount)
            self.editeur.AppendText("\n\n")
            self.editeur.GotoLine(self.editeur.LineCount)
            self.insertSnippet("Bare Minimum {snippet}")
            self.editeur.SetFocus()
        
        if self.getElse("Main", "tools", "True") and self.getElse("Tools", "files", "True"):
            self.Files.update_dockFiles()

        dt = MyFileDropTarget(self.Open)
        self.editeur.SetDropTarget(dt)        


    #----------------------------------------------------------------------
    def updatenotebook(self):
        if self.notebookEditor.PageCount == 0:
            self.splitterCO.Hide()
            self.notebookEditor.Hide()
            self.background.Show()
        else:
            self.splitterCO.Show()
            self.background.Hide()
            self.notebookEditor.Show()
            self.panelPrincipal.Layout()
            self.panelCentral.Layout()


    #----------------------------------------------------------------------
    def OpenDialog(self,wildcard):
        """ Open Dialog and load file in a new editor """

        try: defaultDir=os.path.split(self.filename[self.notebookEditor.GetSelection()])[0]
        except: defaultDir = os.getcwd()

        opendlg = wx.FileDialog(self,
                                message=_("Choose a file"),
                                #defaultDir=os.getcwd(),
                                defaultDir=defaultDir, 
                                defaultFile="",
                                wildcard=wildcard,
                                style=wx.OPEN  | wx.CHANGE_DIR)

        if opendlg.ShowModal() == wx.ID_OK:
            paths = opendlg.GetPaths()
            for path in paths:
                self.Open(path)

    #----------------------------------------------------------------------
    def Open(self, path):
        file = os.path.basename(path)
        directory,extension = os.path.splitext(path)

        if path in self.filename:

            dlg = wx.MessageDialog(self,
                                   _("File is already opened, reload it ?"), _("Warning")+"!",
                                   wx.YES_NO | wx.ICON_WARNING)
            result=dlg.ShowModal()
            dlg.Destroy()                        
            if (result==wx.ID_NO):
                return
            else:
                index = self.filename.index(path)
                self.stcpage[index].ClearAll()
                fichier=open(path,'r')
                self.stcpage[index].SetText(fichier.read())
                fichier.close()
                return
            
        self.inhibitChangeEvents = True
        self.New(file.replace(extension,""))

        pageIdx = self.notebookEditor.GetSelection()
        self.stcpage[pageIdx].ClearAll()
        self.filename[pageIdx]=path
        fichier=codecs.open(path,'r','utf8')
        #for line in fichier:
        #    self.stcpage[pageIdx].AddText(line)
        self.stcpage[pageIdx].SetText(fichier.read())
        fichier.close()
        self.notebookEditor.SetPageText(pageIdx,file.replace(extension,""))
        self.editeur.GotoLine(self.editeur.LineFromPosition(0))
        
        if self.getElse("Main", "tools", "True") and self.getElse("Tools", "files", "True"):
            self.Files.update_dockFiles()
        
        #self.notebookEditor.Update()
        self.stcpage[pageIdx].EmptyUndoBuffer()
        #self.stcpage[pageIdx].SetSavePoint()
        self.inhibitChangeEvents = False
        self.SendSizeEvent()

        self.addFile2Recent(path)




    #----------------------------------------------------------------------
    def highlightline(self,line,color):
        """highlight a line """
        self.getCurrentPage().GotoLine(line)
        self.getCurrentPage().SetCaretLineBack(color)
        self.getCurrentPage().SetCaretLineVisible(True)
        self.focus()
        self.Refresh()
        return
    
    #----------------------------------------------------------------------
    def CloseTab(self):
        """ close the current tab """
        if len(self.onglet) <= 0: return False

        pageIdx = self.notebookEditor.GetSelection()
        if self.notebookEditor.GetPageText(pageIdx)[0]=="*":
            dlg = wx.MessageDialog(self,
                                   _("Save file ?\n"+self.filename[pageIdx]), _("Warning")+"!",
                                   wx.YES_NO | wx.ICON_WARNING | wx.CANCEL
                                   )
            result=dlg.ShowModal()
            dlg.Destroy()
            if (result==wx.ID_CANCEL): return True
            if (result==wx.ID_YES): self.OnSaveAs()  
        self.filename.remove(self.filename[pageIdx])
        self.onglet.remove(self.onglet[pageIdx])
        self.stcpage.remove(self.stcpage[pageIdx])
        self.notebookEditor.DeletePage(pageIdx)
        self.sheetFunctions.remove(self.sheetFunctions[pageIdx])
        #self.choiceFunctions.remove(self.choiceFunctions[page])
        if pageIdx > 0:
            self.notebookEditor.SetSelection(pageIdx-1)
            self.notebookEditor.Update()
        return True
    
    
    #----------------------------------------------------------------------
    def Save(self, event=None):
        """ Save file without dialog box """
        if len(self.onglet)>0:
            path=self.filename[self.notebookEditor.GetSelection()]
            fichier=codecs.open(path,'w','utf8')
            for i in range(0,self.getCurrentPage().GetLineCount()):
                fichier.writelines(self.getCurrentPage().GetLine(i))
            fichier.close()
            
            if self.notebookEditor.GetPageText(self.notebookEditor.GetSelection())[0]=="*":
                chaine=self.notebookEditor.GetPageText(self.notebookEditor.GetSelection())
                chaine=chaine[1:len(chaine)]
                self.notebookEditor.SetPageText(self.notebookEditor.GetSelection(),chaine)
            self.getCurrentPage().SetSavePoint()
           
            self.addFile2Recent(path)
    
    #----------------------------------------------------------------------
    def SaveAs(self):
        wildcard = "Pde files (*.pde)|*.pde|"
        if len(self.onglet)>0: 
            pageIdx = self.notebookEditor.GetSelection()
            path=self.filename[pageIdx]
            # directory,extension=os.path.splitext(path) bug #01 2008-09-06
            directory,extension=os.path.split(path)
            file=os.path.basename(path)  
            filedlg = wx.FileDialog(
                self, 
                message=_("Save file as")+" ...", 
                defaultDir=directory, 
                defaultFile=file,
                wildcard=wildcard, 
                #wildcard=type+" (*"+extensionSave+")|*"+extensionSave,
                style=wx.SAVE)
            filedlg.SetFilterIndex(2)
            if filedlg.ShowModal() == wx.ID_OK:
                path = filedlg.GetPath() 
            else:
                return
            if (path!=""):
                if os.path.exists(path):
                    dlg = wx.MessageDialog(self,
                                           _("File already exist, Overwrite it ?"), _("Warning")+"!",
                                           wx.YES_NO | wx.ICON_WARNING
                                           )
                    result=dlg.ShowModal()
                    dlg.Destroy()                        
                    if (result!=wx.ID_YES):
                        return 0         
            self.filename[pageIdx]=path
            directory,extension=os.path.splitext(path)
            file=os.path.basename(path)                
            self.notebookEditor.SetPageText(pageIdx,file.replace(extension,""))
            fichier=codecs.open(path,'w','utf8')                        
            for i in range(0,self.stcpage[pageIdx].GetLineCount()):
                fichier.writelines(unicode(self.stcpage[pageIdx].GetLine(i)))
            fichier.close()
            self.stcpage[pageIdx].SetSavePoint()    
    

    #----------------------------------------------------------------------
    def GetPath(self):
        """ return the complete path of file """
        if self.notebookEditor.GetSelection()!=-1:
            return self.filename[self.notebookEditor.GetSelection()]
        else:
            return -1

    #----------------------------------------------------------------------
    def SetModified(self,status):
        pageIdx =  self.notebookEditor.GetSelection()
        modSet = self.notebookEditor.GetPageText(pageIdx)[0] == "*"
        if status == False:
            if modSet:
                self.notebookEditor.SetPageText(pageIdx,self.notebookEditor.GetPageText(pageIdx)[1:])
        else:
            if not modSet: 
                self.notebookEditor.SetPageText(pageIdx,"*"+self.notebookEditor.GetPageText(pageIdx))

    #----------------------------------------------------------------------
    def Onclick(self,event):
        self.getCurrentPage().SetCaretLineVisible(False)
        event.Skip()

    #----------------------------------------------------------------------
    def getIndent(self):
        indent = " " * self.getElse("Source", "tabSize", 4)
        return indent
    
    #----------------------------------------------------------------------
    def getNormIdent(self):
        textEdit = self.getCurrentPage()
        columna = textEdit.GetColumn(textEdit.CurrentPos)
        idn = len(self.getIndent())
        rango = range(0, columna+idn+1, idn)
        for i in rango:
            if columna < i: break
        norm_indent = i - columna
        return " " * norm_indent
        
    #----------------------------------------------------------------------
    def seteditorproperties(self,reservedword,rw):
        """ set the layout,keywords and layout for syntax"""
        kw = keyword.kwlist
        kw.extend(reservedword)
        kw.extend(Autocompleter["reserved"])

        font = self.getFontPreferences()     
        self.getCurrentPage().SetKeyWords(0, " ".join(kw))
        
        self.getCurrentPage().StyleSetSpec(stc.STC_STYLE_BRACELIGHT,  "face:%s,size:%d,fore:#008000,back:#87deaa,bold" %(font.GetFaceName(), font.GetPointSize()))
        self.getCurrentPage().StyleSetSpec(stc.STC_STYLE_BRACEBAD,    "face:%s,size:%d,fore:#ff0000,back:#ffaaaa,bold" %(font.GetFaceName(), font.GetPointSize()))         

        self.getCurrentPage().StyleSetSpec(stc.STC_C_PREPROCESSOR, "face:%s,size:%d,fore:#d36820" %(font.GetFaceName(), font.GetPointSize()))                
        self.getCurrentPage().StyleSetSpec(stc.STC_C_DEFAULT, "face:%s,size:%d,fore:#000000" %(font.GetFaceName(), font.GetPointSize()))
        self.getCurrentPage().StyleSetSpec(stc.STC_C_COMMENT, "face:%s,size:%d,fore:#c81818" %(font.GetFaceName(), font.GetPointSize()))
        self.getCurrentPage().StyleSetSpec(stc.STC_C_COMMENTLINE, "face:%s,size:%d,fore:#007F00" %(font.GetFaceName(), font.GetPointSize()))
        self.getCurrentPage().StyleSetSpec(stc.STC_C_NUMBER, "face:%s,size:%d,fore:#ff0000" %(font.GetFaceName(), font.GetPointSize()))
        self.getCurrentPage().StyleSetSpec(stc.STC_C_STRING, "italic,face:%s,size:%d,fore:#7f0000" %(font.GetFaceName(), font.GetPointSize()))
        self.getCurrentPage().StyleSetSpec(stc.STC_C_CHARACTER, "face:%s,size:%d,fore:#cc0000" %(font.GetFaceName(), font.GetPointSize()))
        self.getCurrentPage().StyleSetSpec(stc.STC_C_WORD, "face:%s,size:%d,fore:#0C36F0" %(font.GetFaceName(), font.GetPointSize()))
        self.getCurrentPage().StyleSetSpec(stc.STC_C_OPERATOR, "face:%s,size:%d,bold" %(font.GetFaceName(), font.GetPointSize()-1))
        self.getCurrentPage().StyleSetSpec(stc.STC_C_IDENTIFIER, "face:%s,size:%d" %(font.GetFaceName(), font.GetPointSize()))
        self.getCurrentPage().StyleSetSpec(stc.STC_C_STRINGEOL, "fore:#000000,back:#E0C0E0,eol,size:%d" % font.GetPointSize())
        self.getCurrentPage().StyleSetSpec(stc.STC_C_COMMENTDOC, "fore:#5e5ef1,size:%d" % font.GetPointSize())
        self.getCurrentPage().StyleSetSpec(stc.STC_C_COMMENTLINEDOC,  "fore:#007F00,size:%d" % font.GetPointSize())
        self.getCurrentPage().StyleSetSpec(stc.STC_C_GLOBALCLASS, "fore:#7F7F7F,size:%d" % font.GetPointSize())
        self.getCurrentPage().SetCaretForeground("BLACK")
        
        self.getCurrentPage().SetCaretWidth(1)
        self.getCurrentPage().UsePopUp(1)

