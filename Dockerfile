FROM continuumio/anaconda3:latest
COPY ./code/ /usr/local/src/myscripts
WORKDIR /usr/local/src/myscripts
RUN conda env create -f environment.yml
EXPOSE 80
CMD ["conda", "activate", "openai-qna-env;", "streamlit", "run", "OpenAI_Queries.py", "--server.port", "80"]