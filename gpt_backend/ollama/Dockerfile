# ollama/Dockerfile
FROM ollama/ollama:latest

# Install curl on Debian/Ubuntu base
RUN apt-get update \
 && apt-get install -y curl \
 && rm -rf /var/lib/apt/lists/*

# Copy in your entrypoint script (must be in build context)
COPY ollama-entrypoint.sh /ollama-entrypoint.sh
RUN chmod +x /ollama-entrypoint.sh

# Use your warm-up+pull entrypoint
ENTRYPOINT ["/ollama-entrypoint.sh"]
