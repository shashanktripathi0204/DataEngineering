FROM python:3.9

RUN pip install pandas

# location in the image where we will copy the file
WORKDIR /app

# COPY <-files from the current working directory-> <-to docker image->
#      <-name in the source on the host machine-> <-name in the destination docker image->
COPY pipeline.py pipeline.py

ENTRYPOINT [ "python", "pipeline.py" ]