FROM python:3.14-slim

WORKDIR /app

# Copy the application code
COPY enheduanna/ ./enheduanna/
COPY pyproject.toml .
COPY VERSION .

# Install the application
RUN pip install --no-cache-dir .

# Create a directory for notes and config
RUN mkdir -p /notes /documents

# Create a default config file that uses container paths
RUN echo "---\nfile:\n  entries_directory: /notes\n  document_directory: /documents" > /root/.enheduanna.yml

# Set the default working directory to /notes
WORKDIR /notes

# Default command shows help
ENTRYPOINT ["enheduanna"]
CMD ["--help"]
