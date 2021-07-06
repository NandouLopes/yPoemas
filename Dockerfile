FROM python:3.8-slim-buster
LABEL version="0.1.0" maintainer="Nando Lopes<lopes.fernando@hotmail.com>"
WORKDIR /ypo
EXPOSE 8501
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT ["streamlit","run"]
CMD [ "streamlit", "run", "ypo.py" ]
