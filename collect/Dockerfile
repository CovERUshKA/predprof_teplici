FROM python

WORKDIR /predprof_teplici
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt requirements.txt
RUN pip install --user -r requirements.txt

ENV PATH=/root/.local/bin:$PATH

COPY . .

RUN 

CMD python main.py