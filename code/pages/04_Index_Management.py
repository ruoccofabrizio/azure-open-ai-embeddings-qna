import streamlit as st
import os
import traceback
from utilities.helper import LLMHelper
import streamlit.components.v1 as components

def delete_embedding():
    llm_helper.vector_store.delete_keys([f"doc:{st.session_state['embedding_to_drop']}"])

def delete_file():
    embeddings_to_delete = data[data.filename == st.session_state['file_to_drop']].key.tolist()
    embeddings_to_delete = list(map(lambda x: f"doc:{x}", embeddings_to_delete))
    llm_helper.vector_store.delete_keys(embeddings_to_delete)


def ChangeButtonStyle(wgt_txt, wch_hex_colour = '#000000', wch_border_style = '', wch_textsize=''):
    htmlstr = """<script>
                    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
                    let backgroundColor = '#FFFFFF';
                    if (prefersDark) {{ backgroundColor = '#0E1117'; }}
                    var elements = window.parent.document.querySelectorAll('*'), i;
                    str_wgt_txt = '{wgt_txt}'
                    str_wgt_txt = str_wgt_txt.replace("/(^|[^\\])'/g", "$1\\'");
                    for (i = 0; i < elements.length; ++i)
                    {{ if (elements[i].innerText == str_wgt_txt) 
                        {{
                            parentNode = elements[i].parentNode;
                            element_type = elements[i].nodeName;
                            parent_type = parentNode.nodeName;
                            if (element_type == 'DIV' && parent_type == 'DIV') {{
                                // console.log(elements[i].parentNode.parentNode.nodeName);
                                elements[i].parentNode.parentNode.style.margin = "0"
                                elements[i].parentNode.parentNode.style.gap = "0"
                                }}
                            // console.log(str_wgt_txt + ' ( ' + element_type + ' ) : ' + parentNode + ' ( ' + parent_type + ' , ' + parentNode.innerText + ' )');
                            if (element_type == 'BUTTON') {{
                                elements[i].style.color  = '{wch_hex_colour}';
                                let border_style = '{wch_border_style}';
                                if (border_style.length > 0) {{
                                    elements[i].style.border ='{wch_border_style}';
                                    elements[i].style.outline ='{wch_border_style}';
                                    elements[i].addEventListener('focus', function() {{
                                        this.style.outline = '{wch_border_style}';
                                        this.style.boxShadow = '0px 0px 0px ' + backgroundColor;
                                        this.style.backgroundColor = '"' + backgroundColor + '"';
                                        // console.log(this.innerText + ' FOCUS');
                                        }});
                                    elements[i].addEventListener('hover', function() {{
                                        this.style.outline = '{wch_border_style}';
                                        this.style.boxShadow = '0px 0px 0px ' + backgroundColor;
                                        this.style.backgroundColor = '"' + backgroundColor + '"';
                                        // console.log(this.innerText + ' HOVER');
                                        }});
                                    }}
                                if ('{wch_textsize}' != '') {{
                                    elements[i].style.fontSize = '{wch_textsize}';
                                    }}
                            }}
                            else if (element_type == 'P' && '{wch_textsize}' != '') {{
                                elements[i].style.fontSize = '{wch_textsize}';
                                }}
                        }} }}
                        </script>  """
    htmlstr = htmlstr.format(wgt_txt=wgt_txt, wch_hex_colour=wch_hex_colour, wch_border_style=wch_border_style, wch_textsize=wch_textsize)
    components.html(f"{htmlstr}", height=0, width=0)

try:
    # Set page layout to wide screen and menu item
    menu_items = {
	'Get help': None,
	'Report a bug': None,
	'About': '''
	 ## Embeddings App
	 Embedding testing application.
	'''
    }
    st.set_page_config(layout="wide", menu_items=menu_items)

    llm_helper = LLMHelper()

    # Query RediSearch to get all the embeddings
    data = llm_helper.get_all_documents(k=1000)

    nb_embeddings = len(data)

    if nb_embeddings == 0:
        st.warning("No embeddings found. Go to the 'Add Document' tab to insert your docs.")
    else:
        st.dataframe(data, use_container_width=True)

        st.download_button("Download data", data.to_csv(index=False).encode('utf-8'), "embeddings.csv", "text/csv", key='download-embeddings')
        ChangeButtonStyle("Download data", "#ADCDE7", wch_textsize="10px")

        st.text("")
        st.text("")
        col1, col2, col3, col4 = st.columns([3,2,2,1])
        with col1:
            st.selectbox("Embedding id to delete", data.get('key',[]), key="embedding_to_drop")
            # ChangeButtonStyle("Embedding id to delete", "#ADCDE7", wch_textsize="10px")
        with col2:
            st.text("")
            st.text("")
            st.button("Delete embedding", on_click=delete_embedding)
            ChangeButtonStyle("Delete embedding", "#ADCDE7", wch_textsize="10px")
        with col3:
            st.selectbox("File name to delete", set(data.get('filename',[])), key="file_to_drop")
            # ChangeButtonStyle("File name to delete", "#ADCDE7", wch_textsize="10px")
        with col4:
            st.text("")
            st.text("")
            st.button("Delete file", on_click=delete_file)
            ChangeButtonStyle("Delete file", "#ADCDE7", wch_textsize="10px")

        st.text("")
        st.text("")
        st.button("Delete all embeddings", on_click=llm_helper.vector_store.delete_keys_pattern, args=("doc*",), type="secondary")
        ChangeButtonStyle("Delete all embeddings", "#ADCDE7", wch_textsize="10px")

except Exception as e:
    st.error(traceback.format_exc())
