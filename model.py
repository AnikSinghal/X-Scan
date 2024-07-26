from transformers import pipeline
classifier=pipeline("sentiment-analysis")
res=classifier("i have been waiting for a huggingface course my whole life.")
print(res)