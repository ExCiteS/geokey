"""Document helpers of contributions."""

from os.path import dirname, normpath, abspath, join

from django.core.files import File


def get_pdf_document():
    return File(open(
        normpath(join(
            dirname(dirname(abspath(__file__))),
            'media/files/document_1.pdf'
        )),
        'rb'
    ))


def get_doc_document():
    return File(open(
        normpath(join(
            dirname(dirname(abspath(__file__))),
            'media/files/document_2.doc'
        )),
        'rb'
    ))
