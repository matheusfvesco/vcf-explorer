# Dasa Variant Calling Challenge

## Install

```bash
uv sync
```

## Docker

For building and running the service, inside a Docker container, you can use the `docker.sh` file. After the script succesfully runs, you should be able to access the API at [http://127.0.0.1:4000/](http://127.0.0.1:4000/) or follow the steps below.

### 1. Build the image

Use the following command to build the image:
```bash
docker build -t dasa-challenge .
```

### 2. Run the container

Run the container using the following command:
```bash
docker run dasa-challenge -p 4000:4000
```