# flake8: noqa
from langchain.prompts import PromptTemplate

template = """{summaries}
Please reply to the question using only the information present in the text above. 
Each source has a name followed by colon and the actual information, always include the source name for each fact you use in the response. Always use double square brackets to reference the filename source, e.g. [[info1.pdf.txt]]. Don't combine sources, list each source separately, e.g. [[info1.pdf]][[info2.txt]].
If you can't find it, reply politely that the information is not in the knowledge base.
Question: {question}
Answer:"""

PROMPT = PromptTemplate(template=template, input_variables=["summaries", "question"])

EXAMPLE_PROMPT = PromptTemplate(
    template="Content: {page_content}\nSource: {source}",
    input_variables=["page_content", "source"],
)


