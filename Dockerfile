# Use the official Python image as the base image
FROM python:3.11

# Update the package list and install required system packages
RUN apt-get -y update

# Set the working directory
WORKDIR /app

# Upgrade pip and install poetry
RUN pip install --upgrade pip
RUN pip install --no-cache-dir poetry

# Copy the pyproject.toml and poetry.lock files to the working directory
COPY pyproject.toml poetry.lock ./

# Install project dependencies without installing the root package
RUN poetry install --no-root

# Copy the rest of the application code
COPY . .

# Expose the application port
EXPOSE 8000

# Set the entrypoint to use poetry
ENTRYPOINT ["poetry", "run"]

# Start the application using uvicorn
CMD ["uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
