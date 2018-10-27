"""Document helpers of contributions."""

from os.path import dirname, normpath, abspath, join

from django.core.files import File
from django.core.files.base import ContentFile


def get_pdf_document(file_name='document_1.pdf'):
    pdf_file = File(open(
        normpath(join(
            dirname(dirname(abspath(__file__))),
            'files/document_1.pdf'
        )),
        'rb'
    ))

    the_file = ContentFile(pdf_file.read(), file_name)
    the_file.content_type = 'application/pdf'

    return the_file


def get_doc_document(file_name='document_2.doc'):
    doc_file = File(open(
        normpath(join(
            dirname(dirname(abspath(__file__))),
            'files/document_2.doc'
        )),
        'rb'
    ))

    the_file = ContentFile(doc_file.read(), file_name)
    the_file.content_type = 'application/msword'

    return the_file
