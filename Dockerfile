FROM python
RUN apt-get update
WORKDIR /webpage
COPY . .
RUN pip3 install -r requirements.txt
RUN chmod +x run.bash
EXPOSE 8000
EXPOSE 5000
CMD ./run.bash
