#!/bin/sh
set -e
ollama pull llama3
exec ollama serve