This is a tool that is leveraging gpt-4o-mini to answer questions about my
resume.

# How it works

There is 4 main steps that bring ChatterBox to life.

## Resume Summary
The tool takes in a summarised resume (see Updating the summary.json).
which has been split into smaller, context-aware chunks (e.g., work experiance, education, skills).
This is done for efficient querying and cost

## Embeddings
Each chunk of the summarized resume is converted into a high-dimensional vector (embedding) using the OpenAI text-embedding-ada-002 model.
These embeddings allow the system to compute the similarity between the user query and the resume chunks.

## Finding Relevant Chunks
When a user submits a query, the query is also converted into an embedding.
The system calculates cosine similarity between the query embedding and all the resume chunk embeddings.
The top 3 most relevant chunks are selected to create context.

## Generating Answers
The selected chunks and the user query are sent to the OpenAI GPT model (gpt-4o-mini) to generate a detailed, context-aware response.

# Updating the summary.json
in the tools folder there is a python script "chunkify-docx.py" which when run
takes an input resume file (in .docx format) and produces a output .json file.
This json file contains a summarised version of the resume split into relevant chunks.
As many words are removed as possible while still maintinaing
meaning. This is done to reduce cost when running the bot.

# TODO:
* support pdf format
* produces static embeddigs for summary rather then on each load

