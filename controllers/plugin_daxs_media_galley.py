__author__ = 'cccaballero'

from gluon import current
import os


def upload():

    path = os.path.join(request.folder, 'uploads')

    form = SQLFORM.factory(
        Field('upload', 'upload', requires=IS_NOT_EMPTY(), uploadfolder=path),
        table_name=current.plugin_daxs_media_galley.settings.table_upload_name
        )

    if form.accepts(request, session):
        upload = request.vars.upload
        old_filename = upload.filename
        print form.vars
        # new_filename = form.table.upload.store(upload.file, upload.filename)
        new_filename = form.vars.upload
        length = os.path.getsize(os.path.join(path, new_filename))
        mime_type = upload.headers['content-type']

        title = os.path.splitext(old_filename)[0]

        result = current.plugin_daxs_media_galley.settings.table_upload.validate_and_insert(
            title=title,
            filename=old_filename,
            upload=new_filename,
            flength=length,
            mime_type=mime_type
        )

    db = current.plugin_daxs_media_galley.db
    table_upload = current.plugin_daxs_media_galley.settings.table_upload
    browse_filter = current.plugin_daxs_media_galley.settings.browse_filter
    set = db(table_upload.id>0)
    for key, val in browse_filter.items():
        if value[0] == '<':
            set = set(table_upload[key]<value[1:])
        elif value[0] == '>':
            set = set(table_upload[key]>value[1:])
        elif value[0] == '!':
            set = set(table_upload[key]!=value[1:])
        else:
            set = set(table_upload[key]==value)

    rows = set.select(orderby=table_upload.title)

    return dict(form=form, rows=rows)


def browse():
    db = current.plugin_daxs_media_galley.db
    table_upload = current.plugin_daxs_media_galley.settings.table_upload
    browse_filter = current.plugin_daxs_media_galley.settings.browse_filter
    set = db(table_upload.id>0)
    for key, val in browse_filter.items():
        if value[0] == '<':
            set = set(table_upload[key]<value[1:])
        elif value[0] == '>':
            set = set(table_upload[key]>value[1:])
        elif value[0] == '!':
            set = set(table_upload[key]!=value[1:])
        else:
            set = set(table_upload[key]==value)

    rows = set.select(orderby=table_upload.title)

    return dict(rows=rows)


def delete():
    print "akaka"
    filename = request.args(0)
    if not filename:
        raise HTTP(401, T('Required argument filename missing.'))

    db = current.plugin_daxs_media_galley.db
    table_upload = current.plugin_daxs_media_galley.settings.table_upload
    db(table_upload.upload == filename).delete()

    # # delete the file from storage
    # path = os.path.join(request.folder, 'uploads', filename)
    # os.unlink(path)