"""\
Graphical tests

@copyright: 2012-2016 Carsten Grohmann
@copyright: 2016 Dietmar Schwertberger

@license: MIT (see LICENSE.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

try:
    from .testsupport_new import WXGladeGUITest
except (SystemError, ValueError):
    from testsupport_new import WXGladeGUITest

import wx.xrc
import xrc2wxg
import common
import glob, shutil, os, sys, unittest


class TestGui(WXGladeGUITest):
    "Test GUI functionality"

    def test_NotebookWithoutTabs(self):
        "Test loading Notebook without tabs"
        self._messageBox = None
        infilename = self._get_casefile_path('Notebook_wo_tabs.wxg')
        self.frame._open_app(infilename, use_progress_dialog=False, add_to_history=False)
        err_msg = u'Error loading from a file-like object: Notebook ' \
                  u'widget "notebook_1" does not have any tabs! (line: 17, column: 20)'
        err_caption = u'Error'
        
        regex = u'Error loading .*Notebook widget "notebook_1" does not have any tabs! \(line: 17, column: 20\)'
        msg = ('Expected wxMessageBox(message="%s", caption="%s") got wxMessageBox(message="%s", caption="%s")'%(
                err_msg, err_caption, self._messageBox[0], self._messageBox[1] ) )
        self.assertRegexpMatches( self._messageBox[0], regex, msg=msg)

    def test_NotebookWithTabs(self):
        "Test loading Notebook with tabs"
        self._messageBox = None
        infilename = self._get_casefile_path('Notebook_w_tabs.wxg')
        self.frame._open_app(infilename, use_progress_dialog=False, add_to_history=False)
        self.assertFalse( self._messageBox, 'Loading test wxg file caused an error message: %s' % self._messageBox )

    def test_CodeGeneration_FontColour(self):
        'Test GUI code generation using "FontColour"'
        self.load_and_generate('FontColour')

    def test_StylelessDialog(self):
        "Test code generation for a style less dialog"
        self.load_and_generate('styleless-dialog')

    def test_CodeGeneration_AllWidgets_28(self):
        'Test GUI code generation using "AllWidgets_28"'
        self.load_and_generate('AllWidgets_28')
    
    def test_CodeGeneration_AllWidgets_30(self):
        'Test GUI code generation using "AllWidgets_30"'
        self.load_and_generate('AllWidgets_30', ['lisp'])

    def test_CodeGeneration_ComplexExample(self):
        'Test GUI code generation using "ComplexExample"'
        self.load_and_generate('ComplexExample')#, excluded=["wxg"])

    def test_CodeGeneration_ComplexExample30(self):
        'Test GUI code generation using "ComplexExample"'
        self.load_and_generate('ComplexExample_30', excluded=["lisp"])
        #self.load_and_generate('ComplexExample_30', included=["lisp"])
        # Lisp code has to raise an exception
        common.app_tree.app.properties["language"].set("lisp")
        self._process_wx_events()
        #import errors
        # neither of these works:
        #self.assertRaises( errors.WxgLispWx3NotSupported, common.app_tree.root.widget.generate_code)
        #exc = errors.WxgLispWx3NotSupported("%d.%d" % self.for_version))
        #self.assertRaises( exc, common.app_tree.root.widget.generate_code)

    def test_CodeGeneration_CustomWidget(self):
        'Test GUI code generation using "CustomWidget"'
        self.load_and_generate('CustomWidget')

    def test_Statusbar_wo_labels(self):
        "Test code generation for a wxStatusBar with fields but w/o labels"
        self.load_and_generate('Statusbar_wo_labels')

    def test_Lisp_wxBitmapButton(self):
        """Test Lisp code generation with small wxBitmapButton example

        @see: L{wxglade.widgets.bitmap_button.lisp_codegen}"""
        self.load_and_generate( 'Lisp_wxBitmapButton', included=['lisp'], test_GUI=False )

    def test_CalendarCtrl(self):
        "Test code generation for a CalendarCtrl"
        self.load_and_generate('CalendarCtrl', test_GUI=False)

    def test_FontColour(self):
        "Test code generation for fonts and colours"
        self.load_and_generate('FontColour', test_GUI=False)

    def test_Grid(self):
        "Test code generation with a grid widgets and handling events"
        self.load_and_generate('Grid', test_GUI=False)

    def test_Gauge(self):
        "Test code generation for a wxGauge"
        self.load_and_generate('Gauge', test_GUI=False)

    def test_HyperlinkCtrl(self):
        "Test code generation for a HyperlinkCtrl"
        # test for wxWidgets 2.8.X
        self.load_and_generate('HyperlinkCtrl_28', test_GUI=False)

    def test_Preferences(self):
        "Test code generation for some variants of the preferences dialog; also tests backwards compatibility"
        self.load_and_generate('Python_Preferences', included=["Python"], test_GUI=True)
        self.load_and_generate('Perl_Preferences', included=["Perl"], test_GUI=True)
        self.load_and_generate('CPP_Preferences', included=["C++"], test_GUI=True)
        self.load_and_generate('Lisp_Preferences', included=["Lisp"], test_GUI=True)

    def test_sizer_references(self):
        "Test storing references to sizers in class attributes"
        # don't store sizer references
        self.load_and_generate('Sizers_no_classattr', test_GUI=False)
        # store sizer references
        self.load_and_generate('Sizers_classattr', test_GUI=False)

    def _copy_and_modify(self, source, target, original=None, replacement=None):
        if original is None:
            shutil.copy2( source, target )
            return
        content = open(source,"rb").read().replace(original, replacement)
        open(target, "wb").write(content)
        shutil.copystat( source, target )

    def test_Python_Ogg1(self):
        "Test Python code generation with overwriting a single existing file, preserving manually added code"
        # set up filenames, copy the old file to the output path and modify it to trigger re-writing
        infilename = self._get_casefile_path('PyOgg1.wxg')
        generate_filename = self._get_outputfile_path('PyOgg1.py')
        expected_filename = self._get_casefile_path('PyOgg1.py')
        self._copy_and_modify(expected_filename, generate_filename, b"SetSize((500, 300))", b"SetSize((300, 300))")

        # load and set up project
        common.palette._open_app(infilename, use_progress_dialog=False, add_to_history=False)
        common.app_tree.app.properties["overwrite"].set(False)  # overwrite is 0 in the file
        common.app_tree.app.properties["output_path"].set(generate_filename)
        common.app_tree.app.properties["language"].set("python")
        # generate, compare and check for overwriting
        self._process_wx_events()
        common.app_tree.root.widget.generate_code()
        self._compare_files(expected_filename, generate_filename, check_mtime=True)

    def test_Python_Ogg2(self):
        "Test Python code generation with overwriting two existing files, preserving manually added code"
        infilename = self._get_casefile_path('PyOgg2.wxg')

        generate_app    = self._get_outputfile_path('PyOgg2_app.py')
        generate_dialog = self._get_outputfile_path('PyOgg2_MyDialog.py')
        generate_frame  = self._get_outputfile_path('PyOgg2_MyFrame.py')

        expected_app    = self._get_casefile_path('PyOgg2_app.py')
        expected_dialog = self._get_casefile_path('PyOgg2_MyDialog.py')
        expected_frame  = self._get_casefile_path('PyOgg2_MyFrame.py')

        self._copy_and_modify(expected_dialog, generate_dialog, b"SetSize((500, 300))", b"SetSize((300, 300))")
        self._copy_and_modify(expected_frame,  generate_frame,  b"SetSize((400, 300))", b"SetSize((300, 300))")

        # load and set up project
        common.palette._open_app(infilename, use_progress_dialog=False, add_to_history=False)
        common.app_tree.app.properties["overwrite"].set(False)  # overwrite is 0 in the file
        common.app_tree.app.properties["output_path"].set(self.outDirectory)
        common.app_tree.app.properties["language"].set("python")
        # generate, compare and check for overwriting
        self._process_wx_events()
        common.app_tree.root.widget.generate_code()
        self._compare_files(expected_app,    generate_app, check_mtime=True)
        self._compare_files(expected_dialog, generate_dialog, check_mtime=True)
        self._compare_files(expected_frame,  generate_frame, check_mtime=True)

    def test_all_Ogg1(self):
        "Test Python code generation with overwriting a single existing file, preserving manually added code"
        # XXX overwriting is only working if ALL files are there; if e.g. .h is missing, it fails!
        # set up filenames, copy the old file to the output path and modify it to trigger re-writing
        for language, P, E1, E2 in self.language_constants:
            infilename = self._get_casefile_path(P+'Ogg1.wxg')
            generate_filename = self._get_outputfile_path(P+'Ogg1'+E1)
            expected_filename = self._get_casefile_path(P+'Ogg1'+E1)
            self._copy_and_modify(expected_filename, generate_filename, b"(500, 300)", b"(300, 300)")
            if language=="C++":
                generate_filename_h = self._get_outputfile_path(P+'Ogg1.h')
                expected_filename_h = self._get_casefile_path(P+'Ogg1.h')
                self._copy_and_modify(expected_filename_h, generate_filename_h)
    
            # load and set up project
            common.palette._open_app(infilename, use_progress_dialog=False, add_to_history=False)
            common.app_tree.app.properties["overwrite"].set(False)  # overwrite is 0 in the file already
            common.app_tree.app.properties["output_path"].set(generate_filename)
            common.app_tree.app.properties["language"].set(language)
            # generate, compare and check for overwriting
            self._process_wx_events()
            common.app_tree.root.widget.generate_code()
            self._compare_files(expected_filename, generate_filename, check_mtime=True)

    def test_all_Ogg2(self):
        "Test Python code generation with overwriting a single existing file, preserving manually added code"
        # XXX overwriting is only working if ALL files are there; if e.g. .h is missing, it fails!
        # set up filenames, copy the old file to the output path and modify it to trigger re-writing
        for language, P, E1, E2 in self.language_constants:
            infilename = self._get_casefile_path(P+'Ogg2.wxg')
            generate_filename = self._get_outputfile_path(P+'Ogg2'+E1)
            expected_filename = self._get_casefile_path(P+'Ogg2'+E1)
            self._copy_and_modify(expected_filename, generate_filename, b"(500, 300)", b"(300, 300)")
            if language=="C++":
                generate_filename_h = self._get_outputfile_path(P+'Ogg2.h')
                expected_filename_h = self._get_casefile_path(P+'Ogg2.h')
                self._copy_and_modify(expected_filename_h, generate_filename_h)
    
            # load and set up project
            common.palette._open_app(infilename, use_progress_dialog=False, add_to_history=False)
            common.app_tree.app.properties["overwrite"].set(False)  # overwrite is 0 in the file
            common.app_tree.app.properties["output_path"].set(generate_filename)
            common.app_tree.app.properties["language"].set(language)
            # generate, compare and check for overwriting
            self._process_wx_events()
            common.app_tree.root.widget.generate_code()
            self._compare_files(expected_filename, generate_filename, check_mtime=True)

    def test_all_Ogg2(self):
        "Test code generation with overwriting multiples existing files, preserving manually added code"
        for language, P, E1, E2 in self.language_constants:
            if language=="C++":
                APP = "Ogg2_main"
            else:
                APP = 'Ogg2_app'
            infilename = self._get_casefile_path(P+'Ogg2.wxg')
            #APP = P+'Ogg2_app' if language!="C++" else 'main'  # XXX for C++, the main file does not follow the Application
            generate_app    = self._get_outputfile_path(P+APP+E1)
            generate_dialog = self._get_outputfile_path(P+'Ogg2_MyDialog'+E2)
            generate_frame  = self._get_outputfile_path(P+'Ogg2_MyFrame'+E2)
            #APP = 'Ogg2_app' if language!="C++" else 'Ogg2_main'
            expected_app    = self._get_casefile_path(P+APP+E1)
            expected_dialog = self._get_casefile_path(P+'Ogg2_MyDialog'+E2)
            expected_frame  = self._get_casefile_path(P+'Ogg2_MyFrame'+E2)
    
            self._copy_and_modify(expected_dialog, generate_dialog, b"(500, 300)", b"(300, 300)")
            self._copy_and_modify(expected_frame,  generate_frame,  b"(400, 300)", b"(300, 300)")
            if language=="C++":
                generate_filename_dialog_h = self._get_outputfile_path(P+'Ogg2_MyDialog.h')
                expected_filename_dialog_h = self._get_casefile_path(P+'Ogg2_MyDialog.h')
                generate_filename_frame_h = self._get_outputfile_path(P+'Ogg2_MyFrame.h')
                expected_filename_frame_h = self._get_casefile_path(P+'Ogg2_MyFrame.h')
                self._copy_and_modify(expected_filename_dialog_h, generate_filename_dialog_h)
                self._copy_and_modify(expected_filename_frame_h,  generate_filename_frame_h)

            # load and set up project
            common.palette._open_app(infilename, use_progress_dialog=False, add_to_history=False)
            if language=="C++":
                common.app_tree.app.properties["name"].set( "CPPOgg2_main" )
            common.app_tree.app.properties["overwrite"].set(False)  # overwrite is 0 in the file
            common.app_tree.app.properties["output_path"].set(self.outDirectory)
            common.app_tree.app.properties["language"].set(language)
            # generate, compare and check for overwriting
            self._process_wx_events()
            common.app_tree.root.widget.generate_code()
            check_mtime = language!="perl"
            self._compare_files(expected_app,    generate_app,    check_mtime=check_mtime)
            self._compare_files(expected_dialog, generate_dialog, check_mtime=check_mtime)
            self._compare_files(expected_frame,  generate_frame,  check_mtime=check_mtime)

    def _assert_error_message(self, substring ):
        self.assertTrue( self._messageBox, "No error message generated" )
        
        msg = ('Error message does not match: Expected message containing "%s"'
              ' \ngot wxMessageBox(message="%s", caption="%s")'%(substring, self._messageBox[0], self._messageBox[1] ))
        self.assertTrue( substring in self._messageBox[0], msg )
        self._messageBox = None
        
    def test_OutputFileAndDirectory(self):
        "Test check for output file and directory"
        infilename = self._get_casefile_path('Python_Preferences.wxg')
        common.palette._open_app(infilename, use_progress_dialog=False, add_to_history=False)

        # Single output file out_path shouldn't be a directory, non-existing file or non-writable directory
        common.app_tree.app.properties["output_path"].set(self.outDirectory)
        common.app_tree.root.widget.generate_code()
        self._assert_error_message( "can not be a directory when generating a single file" )

        common.app_tree.app.properties["output_path"].set( os.path.join(self.outDirectory,"non-existing/result.py") )
        common.app_tree.root.widget.generate_code()
        self._assert_error_message( "must be an existing directory" )

        #common.app_tree.app.properties["output_path"].set( os.path.join(self.outDirectory,"non-writable/result.py") )
        #common.app_tree.root.widget.generate_code()
        #self._assert_error_message( "" )

        # Multiple output file out_path should be a writable directory
        common.app_tree.app.properties["multiple_files"].set(1)
        common.app_tree.app.properties["output_path"].set( os.path.join(self.outDirectory,"non-existing") )
        common.app_tree.root.widget.generate_code()
        self._assert_error_message( " must be an existing directory" )

        #common.app_tree.app.properties["output_path"].set( os.path.join(self.outDirectory,"non-writable") )
        #common.app_tree.root.widget.generate_code()
        #self._assert_error_message( "can not be a directory when generating a single file" )

    def test_WxgXRCMultipleFilesNotSupported(self):
        "Test for multi file XRC projects."
        infilename = self._get_casefile_path('Python_Preferences.wxg')
        common.palette._open_app(infilename, use_progress_dialog=False, add_to_history=False)
        common.app_tree.app.properties["multiple_files"].set(1)
        common.app_tree.app.properties["language"].set("XRC")
        common.app_tree.root.widget.generate_code()
        self._assert_error_message( "XRC code cannot be split into multiple files" )

    def test_WxgTemplateCodegenNotPossible(self):
        "Test for code generation from a template"
        infilename = self._get_casefile_path('Python_Preferences.wxg')
        common.palette._open_app(infilename, use_progress_dialog=False, add_to_history=False)
        common.app_tree.app.properties["is_template"].set(True)
        common.app_tree.root.widget.generate_code()
        self._assert_error_message( "Code generation from a template is not possible" )

    def _assert_styles(self, got, expected, msg=None):
        if isinstance(got,      str): got      = got.split("|")
        if isinstance(expected, str): expected = expected.split("|")
        if isinstance(got,      (list,set)): got      = sorted(got)
        if isinstance(expected, (list,set)): expected = sorted(expected)
        msg = msg or "Style names"
        self.assertEqual(got, expected, '%s do not match: got "%s" expected %s'%(msg, got, expected))

    def test_StylesMixin(self):
        "StyleMixin: Test converting of styles"
        # XXX actually generate a file and simulate editing

        #common.palette._open_app(infilename, use_progress_dialog=False, add_to_history=False)
        common.app_tree.clear()
        import widgets.frame.frame
        widgets.frame.frame.builder(None,None,0, "wxFrame", "MyFrame", "frame")

        item = common.app_tree.root.children[0]
        common.adding_widget = True
        common.widget_to_add = "EditHyperlinkCtrl"
        item.widget.sizer.children[1].item.on_drop_widget(None)
        hyperlink = item.widget.sizer.children[1].item

        ## expand tree and show edit window
        #tree = common.app_tree.drop_target()
        #root = tree.GetRootItem()
        #first, cookie = tree.GetFirstChild(root)
        #if first.IsOk():
            #tree.expand()
            #self._process_wx_events()
            #tree.SelectItem(first)
            #self._process_wx_events()
            #node = tree.GetPyData(first)
            #tree.show_toplevel(node)
        self._process_wx_events()
        # check available style names
        sp = hyperlink.properties["style"]
        style_names = ['wxHL_ALIGN_CENTRE','wxHL_ALIGN_LEFT','wxHL_ALIGN_RIGHT','wxHL_CONTEXTMENU','wxHL_DEFAULT_STYLE']
        self._assert_styles(sp._names, style_names, "Style names for HyperlinkCtrl")

        # test setting all styles and check whether some are combined  (not too useful, as no exclusions are defined)
        sp.set( style_names )
        #self._assert_styles('wxHL_ALIGN_LEFT|wxHL_ALIGN_RIGHT|wxHL_DEFAULT_STYLE', sp.get_string_value(),
                            #"Full style flags for HyperlinkCtrl")
        self._assert_styles(style_names, sp.get_string_value(), "Full style flags for HyperlinkCtrl")

        return
        sp.set( "HL_ALIGN_LEFT" )
        self.assertEqual( ret, expected, 'EditStylesMixin.set_style(): got "%s" expect: "%s"' % (ret, expected) )
        esm.set_style([True, False, True, False, False])
        ret = esm.style_set
        expected = set(['wxHL_ALIGN_LEFT', 'wxHL_ALIGN_CENTRE'])
        self.assertEqual( ret, expected, 'EditStylesMixin.set_style(): got "%s" expect: "%s"' % (ret, expected) )
        
        esm.set_style('wxHL_DEFAULT_STYLE|wxHL_CONTEXTMENU')
        ret = esm.style_set
        expected = set(['wxHL_DEFAULT_STYLE',])
        self.assertEqual( ret, expected, 'EditStylesMixin.get_style(): got "%s" expect: "%s"' % (ret, expected) )

        # test generating a flag list
        ret = esm.get_style()
        expected = [False, False, False, False, True]
        self.assertEqual( ret, expected, 'EditStylesMixin.get_style(): got "%s" expect: "%s"' % (ret, expected) )

        # returning styles as a string concatenated with '|'
        ret = esm.get_string_style()
        expected = 'wxHL_DEFAULT_STYLE'
        self.assertEqual( ret, expected, 'EditStylesMixin.get_style_string(): got "%s" expect: "%s"' % (ret, expected) )

        # test setting styles via style dictionary
        from collections import OrderedDict
        styles = OrderedDict()
        styles[_('Border')] = ['wxALL', 'wxLEFT']
        styles[_('Alignment')] = ['wxEXPAND', 'wxALIGN_RIGHT']

        esm = edit_windows.EditStylesMixin('wxHyperlinkCtrl', styles)
        ret = esm.style_names[:]
        ret.sort()
        expected = ['wxALL', 'wxLEFT', 'wxEXPAND', 'wxALIGN_RIGHT']
        expected.sort()
        self.assertEqual( ret, expected, 'EditStylesMixin.__init__() failed: got "%s" expect: "%s"' % ( ret, expected) )

        # check handling of empty ('', None) styles
        for value, desc in (('', "''"), (None, 'None')):
            esm.set_style(value)
            ret = esm.style_set
            expected = set()
            self.assertEqual(ret, expected, 'EditStylesMixin.set_style(%s) failed: got "%s" expect: "%s"' % (desc, ret, expected))
            ret = esm.get_style()
            expected = [False, False, False, False]
            self.assertEqual( ret, expected, 'EditStylesMixin.get_style() failed: got "%s" expect: "%s"' % (ret, expected))
            ret = esm.get_int_style()
            expected = 0
            self.assertEqual( ret, expected, 'EditStylesMixin.get_int_style() failed: got "%s" expect: ' '"%s"' % (ret, expected) )

        # check handling of unsupported style
        esm = edit_windows.EditStylesMixin('wxStaticText')
        esm.codegen.for_version = (2, 8)

        # set un-supported style
        esm.set_style('wxST_ELLIPSIZE_MIDDLE')

        ret = esm.style_set
        expected = set(('wxST_ELLIPSIZE_MIDDLE',))
        self.assertEqual( ret, expected,
            'EditStylesMixin.set_style("wxST_ELLIPSIZE_MIDDLE") failed: got "%s" expect: "%s"' % (ret, expected))

        ret = esm.get_int_style()
        expected = 0
        self.assertEqual( ret, expected, 'EditStylesMixin.get_int_style() failed: got "%s" expect: "%s"' % (ret, expected))

    def test_missing_application_attributes(self):
        #"Test load wxg file w/ missing <application> attributes and generate code"
        "convert .xrc file with missing <application> attributes to .wxg and load it"
        # convert .xrc to .wxg
        infilename  = self._get_casefile_path('app_wo_attrs_gui.xrc')
        generated_filename = self._get_outputfile_path('app_wo_attrs_gui.wxg')
        xrc2wxg.convert(infilename, generated_filename)
        # compare
        expected_filename = self._get_casefile_path('app_wo_attrs_gui.wxg')
        self._compare_files(expected_filename, generated_filename)
        # open the .wxg file; there should be no problem
        self._messageBox = None
        self.frame._open_app(generated_filename, use_progress_dialog=False, add_to_history=False)
        self.assertFalse(self._messageBox,'Loading test wxg file caused an error message: %s'%self._messageBox)

    def test_unsupported_flags(self):
        "Test code generation with unsupported flags"
        self.load_and_generate('no_supported_flags', test_GUI=False)

    def test_load_xrc(self):
        "Test loading XRC files"
        res = wx.xrc.EmptyXmlResource()
        for filename in glob.glob(os.path.join(self.caseDirectory, '*.xrc')):
            self.assertTrue( res.Load(filename),
                             'Loading XRC file %s failed' % os.path.relpath(filename, self.caseDirectory) )

    def stop(self):
        print("XXX")  # nothing to do


if __name__ == '__main__':
    #unittest.main(failfast=True) # defaultTest="TestGui.test_missing_application_attributes"
    unittest.main()