from ibm_watsonx_ai.foundation_models import Model
import streamlit as st

creds = {
		"url" : "IBM_CLOUD",
		"apikey" : "USE_IBM_API_KEY"
}
project_id = "USE_IBM_PROJECT_ID"

## helper function
def generate_text(model, prompt_input):
	generated_text = model.generate_text(prompt=prompt_input)
	return generated_text

def generate_text_stream(model, prompt_input):
	generated_text = model.generate_text_stream(prompt=prompt_input)
	return generated_text

## helper function for model object
@st.cache_resource
def get_model(model_id, decoding_method="greedy", min_tokens=1, max_tokens=1000, stop_sequences=[]):
	parameters = {
        "decoding_method": decoding_method,
        "min_new_tokens": min_tokens,
        "max_new_tokens": max_tokens,
		"include_stop_sequence": False,
		"stop_sequences": stop_sequences
    }
	model =  Model(
        model_id = model_id,
        params = parameters,
        credentials = creds,
		project_id = project_id
    )
	return model
