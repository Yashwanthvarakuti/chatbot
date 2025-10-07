from datasets import load_dataset

# Load the Bitext Customer Support Chat dataset
dataset = load_dataset("bitext/Bitext-customer-support-llm-chatbot-training-dataset")

# Print the first example from the training set
print(dataset['train'][0])
