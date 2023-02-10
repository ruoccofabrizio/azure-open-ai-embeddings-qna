from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import os

PAGES_PER_EMBEDDINGS = os.environ('PAGES_PER_EMBEDDINGS', 2)
SECTION_TO_EXCLUDE = ['title', 'sectionHeading', 'footnote', 'pageHeader', 'pageFooter', 'pageNumber']

def analyze_read(formUrl):

    document_analysis_client = DocumentAnalysisClient(
        endpoint=os.environ['FORM_RECOGNIZER_ENDPOINT'], credential=AzureKeyCredential(os.environ['FORM_RECOGNIZER_KEY'])
    )
    
    poller = document_analysis_client.begin_analyze_document_from_url(
            "prebuilt-layout", formUrl)
    layout = poller.result()

    results = []
    page_result = ''
    for p in layout.paragraphs:
        page_number = p.bounding_regions[0].page_number
        output_file_id = int((page_number - 1 ) / PAGES_PER_EMBEDDINGS)

        if len(results) < output_file_id + 1:
            results.append('')

        if p.role not in SECTION_TO_EXCLUDE:
            results[output_file_id] += f"{p.content}\n"

    for t in layout.tables:
        page_number = t.bounding_regions[0].page_number
        output_file_id = int((page_number - 1 ) / PAGES_PER_EMBEDDINGS)

        if len(results) < output_file_id + 1:
            results.append('')
        previous_cell_row=0
        rowcontent='| '
        tablecontent = ''
        for c in t.cells:
            if c.row_index == previous_cell_row:
                rowcontent +=  c.content
                previous_cell_row=c.row_index
            else:
                tablecontent += " | " + "\n" + rowcontent
                rowcontent='| '
                rowcontent += c.content + " | "
                previous_cell_row += 1
        results[output_file_id] += f"{tablecontent}|"
    print (results)
    return results
