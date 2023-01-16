FROM continuumio/anaconda3:latest
COPY ./code/ /usr/local/src/myscripts
WORKDIR /usr/local/src/myscripts
RUN conda env create -f code/requirements.txt && conda activate openai-qna-env
EXPOSE 80
CMD ["streamlit", "run", "OpenAI_Queries.py", "--server.port", "80"]