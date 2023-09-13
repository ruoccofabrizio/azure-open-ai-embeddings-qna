from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import os
from dotenv import load_dotenv
import uuid
# from utilities.helper import LLMHelper

class AzureFormRecognizerClient:
    def __init__(self, form_recognizer_endpoint: str = None, form_recognizer_key: str = None):

        load_dotenv()

        self.pages_per_embeddings = int(os.getenv('PAGES_PER_EMBEDDINGS', 1))
        self.section_to_exclude = ['footnote', 'pageHeader', 'pageFooter', 'pageNumber']

        self.form_recognizer_endpoint : str = form_recognizer_endpoint if form_recognizer_endpoint else os.getenv('FORM_RECOGNIZER_ENDPOINT')
        self.form_recognizer_key : str = form_recognizer_key if form_recognizer_key else os.getenv('FORM_RECOGNIZER_KEY')

    def analyze_read(self, formUrl):

        document_analysis_client = DocumentAnalysisClient(
            endpoint=self.form_recognizer_endpoint, credential=AzureKeyCredential(self.form_recognizer_key)
        )
        
        poller = document_analysis_client.begin_analyze_document_from_url(
                "prebuilt-layout", formUrl)
        layout = poller.result()

        results = []
        page_result = ''
        for p in layout.paragraphs:
            page_number = p.bounding_regions[0].page_number
            # print(" -------------- page_number -----------------")
            # print(page_number)
            output_file_id = int((page_number - 1 ) / self.pages_per_embeddings)

            if len(results) < output_file_id + 1:
                results.append('')

            if p.role not in self.section_to_exclude:
                results[output_file_id] += f"{p.content}\n"

        for t in layout.tables:
            page_number = t.bounding_regions[0].page_number
            # print(" -------------- page_number_table -----------------")
            # print(page_number)
            output_file_id = int((page_number - 1 ) / self.pages_per_embeddings)
            
            if len(results) < output_file_id + 1:
                results.append('')
            previous_cell_row=0
            rowcontent='| '
            tablecontent = ''
            for c in t.cells:
                if c.row_index == previous_cell_row:
                    rowcontent +=  c.content + " | "
                else:
                    tablecontent += rowcontent + "\n"
                    rowcontent='|'
                    rowcontent += c.content + " | "
                    previous_cell_row += 1
            results[output_file_id] += f"{tablecontent}|"
        # print(" -------------- results -----------------")
        # print(results[1])
        # print(" -------- len(results) -----------------")
        # print(len(results))
        return results

    # def analyze_read_pdf_normal(self, file_path, helper):
    #     """
    #     Process a PDF file using Azure Form Recognizer, extract text from each page, and add embeddings for each page.
        
    #     Args:
    #     - file_path (str): Path to the PDF file.
    #     - helper (Any): An instance of the LLMHelper class for adding embeddings.
        
    #     Returns:
    #     - List[str]: List of URLs for the indexed pages.
    #     """
    #     indexed_pages = []
        
    #     # Initialize AzureFormRecognizerClient
    #     form_recognizer_client = AzureFormRecognizerClient()
        
    #     with open(file_path, 'rb') as file:
    #         # Save the PDF temporarily to a storage and get its URL for form recognizer
    #         # This is a placeholder logic and may need to be updated based on actual implementation
    #         temp_file_name = f"temp_pdf_{uuid.uuid4()}.pdf"
    #         pdf_url = helper.blob_client.upload_file(file.read(), file_name=temp_file_name, content_type='application/pdf')
            
    #         # Analyze the PDF using Azure Form Recognizer
    #         analyzed_results = form_recognizer_client.analyze_read(pdf_url)
            
    #         # Iterate over the results to create embeddings for each page
    #         for page_text in analyzed_results:
    #             # Upload the text for each page and add embeddings
    #             temp_txt_file_name = f"temp_page_{len(indexed_pages)}.txt"
    #             source_url = helper.blob_client.upload_file(page_text, file_name=temp_txt_file_name, content_type='text/plain; charset=utf-8')
    #             helper.add_embeddings_lc(source_url)
    #             indexed_pages.append(source_url)
                
    #             # Clean up the temporary text file
    #             os.remove(temp_txt_file_name)
        
    #     # Clean up the temporary PDF file
    #     os.remove(temp_file_name)
        
    #     return indexed_pages
        
    # def analyze_read(self, formUrl):
    #     document_analysis_client = DocumentAnalysisClient(
    #         endpoint=self.form_recognizer_endpoint, credential=AzureKeyCredential(self.form_recognizer_key)
    #     )
        
    #     poller = document_analysis_client.begin_analyze_document_from_url(
    #             "prebuilt-layout", formUrl)
    #     layout = poller.result()

    #     results = []
    #     page_data = []
    #     for p in layout.paragraphs:
    #         page_number = p.bounding_regions[0].page_number
    #         output_file_id = int((page_number - 1 ) / self.pages_per_embeddings)

    #         if len(results) < output_file_id + 1:
    #             results.append('')
    #             page_data.append([])

    #         if p.role not in self.section_to_exclude:
    #             results[output_file_id] += f"{p.content}\n"
    #             page_data[output_file_id].append(page_number)

    #     for t in layout.tables:
    #         page_number = t.bounding_regions[0].page_number
    #         output_file_id = int((page_number - 1 ) / self.pages_per_embeddings)
            
    #         if len(results) < output_file_id + 1:
    #             results.append('')
    #             page_data.append([])
                
    #         previous_cell_row = 0
    #         rowcontent = '| '
    #         tablecontent = ''
    #         for c in t.cells:
    #             if c.row_index == previous_cell_row:
    #                 rowcontent +=  c.content + " | "
    #             else:
    #                 tablecontent += rowcontent + "\n"
    #                 rowcontent = '|'
    #                 rowcontent += c.content + " | "
    #                 previous_cell_row += 1
    #         results[output_file_id] += f"{tablecontent}|"
    #         page_data[output_file_id].append(page_number)

    #     return results, page_data
