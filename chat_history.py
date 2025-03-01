from common import *

qa_memory = []
memory_size = 3

# add question/answer and maintain size
def update_memory(question, answer, document):
    qa_memory.append({'question': question, 'answer': answer, 'document': document})
    if len(qa_memory) > memory_size:
        qa_memory.pop(0)
        

# get history in prompt format
def get_chat_history_prompt():
    history = ""
    if qa_memory:
        for qa_pair in qa_memory:
            history += f"\n\n<|start_of_role|>user<|end_of_role|>\n{qa_pair['document']}"
            history += f"\n\n<|start_of_role|>user<|end_of_role|>\n{qa_pair['question']}"
            history += f"\n\n<|start_of_role|>assistant<|end_of_role|>\n{qa_pair['answer']}"
    return history


# reset memory
def reset_memory():
    qa_memory.clear()



