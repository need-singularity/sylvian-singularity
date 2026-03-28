FROM python:3.11-slim
WORKDIR /app
COPY . /app/TECS-L
RUN pip install --no-cache-dir /app/TECS-L/n6-replication
RUN cd /app/TECS-L && n6-replicate fetch || true
WORKDIR /app/TECS-L
ENTRYPOINT ["n6-replicate"]
CMD ["run", "--tier", "1"]
