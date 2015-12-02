#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
web2py_ckeditor4: web2py plugin for CKEditor v4: http://ckeditor.com/
"""
from gluon.html import BUTTON

__author__ = 'Carlos Cesar Caballero'
__email__ = 'ccesar@daxslab.com'
__copyright__ = 'Copyright(c) 2015, Carlos Cesar Caballero, DaxsLab'
__license__ = 'LGPLv3'
__version__ = '0.1'
__status__ = 'Development'  # possible options: Prototype, Development, Production

import os
from gluon import *
from gluon.storage import Storage
from gluon.sqlhtml import FormWidget

class MediaGalley(object):
    """
    Adds a media galley to a web2py app
    """
    def __init__(self, db, download_url=('default','download'), autodelete=True):
        """
        Initializes the Media Galley module. Requires a DAL instance.
        """
        
        self.db = db
        
        self.settings = Storage()
        self.settings.table_upload = None
        self.settings.table_upload_name = 'plugin_daxs_media_galley_upload'
        self.settings.extra_fields = {}
        self.settings.url_upload = URL('plugin_daxs_media_galley', 'upload')
        self.settings.url_browse = URL('plugin_daxs_media_galley', 'browse')
        self.settings.browse_filter = {}
        self.settings.file_length_max = 10485760    # 10 MB
        self.settings.file_length_min = 0           # no minimum
        self.settings.autodelete = autodelete
        
        self.settings.download_url = download_url
        current.plugin_daxs_media_galley = self
    
    def define_tables(self, migrate=True, fake_migrate=False):
        """
        Called after settings are set to create the required tables for dealing
        with file uploads.
        """
        upload_name = self.settings.table_upload_name
        
        self.settings.table_upload = self.db.define_table(upload_name,
            Field('title', length=255),
            Field('filename', length=255),
            Field('flength', 'integer'),
            Field('mime_type', length=128),
            Field('upload', 'upload', autodelete=self.settings.autodelete),
            *self.settings.extra_fields.get(upload_name, []),
            migrate=migrate,
            fake_migrate=fake_migrate,
            format='%(title)s'
        )
        #lazy tables breaks this. Need to force the load of the table
        self.settings.table_upload.upload.requires = [
            IS_NOT_EMPTY(),
            IS_LENGTH(maxsize=self.settings.file_length_max, minsize=self.settings.file_length_min),
        ]

    def get_media_field(self):

        # return Field('media', 'list:reference '+self.settings.table_upload_name, widget=self.widget)
        return Field('media', widget=self.widget)
        # return Field('media', 'list:reference '+self.settings.table_upload_name)

    def widget(self, field, value, **attributes):
        """
        To be used with db.table.field.widget to set selected images from galley
        widget for the field.
        Simply set db.table.field.widget = daxs_media_galley.widget to use the widget.
        """
        # TODO: galley widget

        # default = dict(
        #     value=value,
        #     # _cols=80,
        #     # _rows=10
        # )
        #
        # attributes = FormWidget._attributes(field, default, **attributes)
        # attributes['_class'] = 'plugin_daxs_media_widget'

        current.response.files.append(URL(r=current.request, c='static', f='plugin_daxs_media_galley/js/widget.js'))

        # input = INPUT(_type='text', _name='name', value=value)
        input = INPUT(_name=field.name,
                      _id="%s_%s" % (field._tablename, field.name),
                      _class=field.type,
                      _value=value,
                      requires=field.requires,
                      _type='hidden')
        button = A('Select', _class='btn btn-primary', _onClick='show_galley()')
        javascript = self.load("%s_%s" % (field._tablename, field.name))

        galley_ids = value.split(',')
        images = ''
        galley_objects = self.db(self.db[self.settings.table_upload_name].id.belongs(galley_ids)).select()

        current.response.files.append(URL(r=current.request,c='static',f='plugin_daxs_media_galley/css/browse.css'))

        for galley_object in galley_objects:
            # images += '<img src="'+URL('default', 'download', args=[galley_object.upload])+'" width="150px">'

            category = self.filetype(galley_object.filename)
            if category != "image":
                url = category
            else:
                url = URL('default', 'download', args=[galley_object.upload])
            images += """<div class="item" data-id="%s" >
                <span class="delete">&nbsp;x&nbsp;</span>
                <img src="%s" />
                <div>%s</div>
            </div>""" % (galley_object.id, url, galley_object.title)

        xml = XML('<div id="daxs_galley_form_images_container">'+images+'</div>')

        result = CAT(javascript, input, button, xml)

        return result

    def load(self, id):
        galley_url = URL(c='plugin_daxs_media_galley', f='upload')
        download_url = URL('default', 'download')
        delete_url = URL('plugin_daxs_media_galley', 'delete')
        delete_question = current.T('Are you sure you want to delete this item?')
        return XML(
            (
                """
                <script  type="text/javascript">

                    var input_id = '%s';

                    function show_galley(){
                        var newwin = window.open("%s");
                        newwin.creator = self;
                    };

                    function add_object(id, image_url, title){
                        jQuery('#'+input_id)[0].value = jQuery('#'+input_id)[0].value+id+",";
                        //var new_image = $('<img src="'+image_url+'" width="150px">');

                        var new_image = $('<div class="item" data-id="'+id+'" ><span class="delete">&nbsp;x&nbsp;</span><img src="'+image_url+'" /><div>'+title+'</div></div>');

                        //console.log(jQuery('#daxs_galley_form_images_container')[0]);
                        jQuery('#daxs_galley_form_images_container').append(new_image);
                    };

                    jQuery(function() {
                        jQuery('.delete').click(function() {
                            if (confirm('%s')) {
                                var img_id = $(this).parent().data('id');
                                $(this).parent().remove();
                                var input_value = jQuery('#'+input_id)[0].value;
                                var input_chuncks = input_value.split(',');
                                var new_input_chunks = [];

                                for (var i=0; i<input_chuncks.length; i++) {
                                    if (input_chuncks[i] != img_id){
                                        new_input_chunks.push(input_chuncks[i]);
                                    }
                                }

                                var new_value = new_input_chunks.join(',');
                                if (new_value[new_value.length-1] != ','){
                                    new_value += ',';
                                }
                                if (new_value == ','){
                                    new_value='';
                                }
                                jQuery('#'+input_id)[0].value = new_value;
                            }
                            return false;
                        });
                    });
                </script>
                """
            ) % (id, galley_url, delete_question)
        )
        
    # def handle_upload(self):
    #     """
    #     Gets an upload from CKEditor and returns the new filename that can then be
    #     inserted into a database. Returns (new_filename, old_filename, length, mime_type)
    #     """
    #     upload = current.request.vars.upload
    #     path = os.path.join(current.request.folder, 'uploads')
    #
    #     if upload != None:
    #         if hasattr(upload, 'file'):
    #             form = SQLFORM.factory(
    #                 Field('upload', 'upload', requires=IS_NOT_EMPTY(), uploadfolder=path),
    #                 table_name = self.settings.table_upload_name
    #             )
    #
    #             old_filename = upload.filename
    #             new_filename = form.table.upload.store(upload.file, upload.filename)
    #             length = os.path.getsize(os.path.join(path, new_filename))
    #             mime_type = upload.headers['content-type']
    #
    #             return (new_filename, old_filename, length, mime_type)
    #         else:
    #             raise HTTP(401, 'Upload is not proper type.')
    #     else:
    #         raise HTTP(401, 'Missing required upload.')
            

    def filetype(self, filename):
        """
        Takes a filename and returns a category based on the file type.
        Categories: word, excel, powerpoint, flash, pdf, image, video, audio, archive, other.
        """
        parts = os.path.splitext(filename)
        if len(parts) < 2:
            return 'other'
        else:
            ext = parts[1][1:].lower()
            if ext == 'png' or ext == 'jpg' or ext == 'jpeg' or ext == 'gif':
                return 'image'
            elif ext == 'avi' or ext == 'mp4' or ext == 'm4v' or ext == 'ogv' or ext == 'wmv' or ext == 'mpg' or ext == 'mpeg':
                return 'video'
            elif ext == 'mp3' or ext == 'm4a' or ext == 'wav' or ext == 'ogg' or ext == 'aiff':
                return 'audio'
            elif ext == 'zip' or ext == '7z' or ext == 'tar' or ext == 'gz' or ext == 'tgz' or ext == 'bz2' or ext == 'rar':
                return 'archive'
            elif ext == 'doc' or ext == 'docx' or ext == 'dot' or ext == 'dotx' or ext == 'rtf':
                return 'word'
            elif ext == 'xls' or ext == 'xlsx' or ext == 'xlt' or ext == 'xltx' or ext == 'csv':
                return 'excel'
            elif ext == 'ppt' or ext == 'pptx':
                return 'powerpoint'
            elif ext == 'flv' or ext == 'swf':
                return 'flash'
            elif ext == 'pdf':
                return 'pdf'
            else:
                return 'other'