import streamlit as st
import google.generativeai as genai
import os
from pathlib import Path
import json

genai.configure(api_key=st.secrets["gemini_api_key"])

def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    return file

generation_config = {
    "temperature": 0.3,
    "response_mime_type": "application/json"
}

Prompt_for_audio_transcript = '''
You are an AI assistant tasked with evaluating the quality of customer service provided by a Customer Service Representative (CS) based on a conversation transcript between the CS and a customer.
The Conversations will  revolves around vehicle insurance claims and policy management. Customers often reach out the  support team to file accident claims and address billing concerns and also querying about insurance policy avaliability. The representative,assists with claims processing, reviews policies for potential savings, and ensures customers are not overcharged. The focus is on providing empathetic support, streamlining the claims process, and offering proactive solutions to enhance customer satisfaction and retention. Overall, the aim is to resolve issues efficiently and optimize insurance coverage and costs for the customers.The customer representatives belongs to a insurance company  which operates in the vehicle insurance industry, providing services such as policy management, billing support, and claims processing.The insurance company  works with multiple providers (e.g., Provider Allison and Provider B: Benhur), offering features like accident forgiveness and flexible deductibles to cater to diverse customer needs.

Your role is to analyze the provided transcript and evaluate the CS's performance according to predefined criteria. For each criterion, you will provide a rating on a scale from 1 to 10, where:

1 - Very Poor/Not Done

10 - Excellent/Outstanding

Each rating must be based on specific behaviors or actions observed in the transcript. If a required behavior is not present, assign an appropriate lower rating. Provide a brief explanation for each rating based on your analysis of the transcript. If the transcript lacks information for a specific question, indicate it and provide a rating of 1.
Use the context provided in each question to rate the customer care representative.

**Evaluation Criteria**:
1. Did the CS use a friendly and professional greeting, clearly identifying themselves?
Context: The customer service representative should start the call with a polite greeting and clearly state their name. For example, "Hello, thank you for calling NewCo! My name is Paul. How can I assist you today?" If this is done,then give good rating else give bad rating(1-3).

2. Did the CS introduce themselves in a friendly and professional manner?
(Context: The introduction should be warm and professional, making the customer feel welcomed. For example, "My name is Paul. How can I assist you today?" If the introduction is friendly and professional,then give high rating else give low rating.)

3. Did the CS disclose that the call was being recorded?
(Context: The CS should inform the customer that the call is being recorded for quality or training purposes.Give low rating if the customer care executive does not say anything about call recording.)


4. Did the CS use empathetic language to acknowledge the customer's concerns?
(Context: The CS should use phrases like "I'm sorry to hear about that" or "I understand how that can be frustrating." If the CS uses empathetic language consistently,then give high rating. For example, "I'm sorry to hear about the accident. I'm here to help you through the process and make it as easy as possible.")

5. Did the CS demonstrate active listening, provide acknowledgments, and avoid interrupting the customer?
(Context: The CS should allow the customer to speak without interruption and acknowledge their concerns. For example, "Thanks, I appreciate that." If the CS demonstrates active listening and provides acknowledgments,then only give high rating.)

6. Did the CS maintain a professional and courteous tone without expressing personal opinions?
(Context: The CS should maintain a neutral and professional tone throughout the call. If the CS avoids personal opinions and maintains a courteous tone,then only give good rating. For example, "I completely understand. I'll make sure your policy reflects only what's necessary.")

7. Was the CS able to effectively gather information and ask clarifying questions to understand the customer's needs?
(Context: The CS should ask relevant questions to understand the customer's situation. For example, "Could you please tell me a bit more about what happened during the accident?" If the CS effectively gathers information,then give high rating.)

8. Did the CS prioritize the customer's needs throughout the call?
(Context: The CS should focus on addressing the customer's primary concerns first. For example, filing the claim before discussing policy reviews. If the CS prioritizes the customer's needs,then give high rating.)

9. Did the CS check if the customer has a website application or applied at The General in the last 6 months?
(Context: The CS should ask if the customer has applied for insurance through the website or with The General in the last six months. For example, "Have you applied for insurance through our website or with The General in the last six months?" If this question is asked,then give good rating. If not, then give bad rating.)

10. Did the CS focus on providing solutions and offer multiple resolution options?
(Context: The CS should offer various solutions to the customer's problem. For example, suggesting a policy review or custom quote.2nd example will be "I’ll compare your current policy with what Benhur can offer and share the best options with you." If the CS provides multiple resolution options,then only give good rating.)

11. Did the CS utilize features and benefits to gain the customer's buy-in?
(Context: The CS should highlight the benefits of suggested solutions. For example, mentioning accident forgiveness or flexible deductibles.2nd example will be "Benhur offers accident forgiveness and flexible deductible options that could lower your monthly payment." If the CS utilizes features and benefits effectively,then give good rating.)

12. Did the CS ask for permission to conduct a custom quote for car insurance?
(Context: The CS should ask for the customer's consent before conducting a custom quote. For example, "Would you be open to a quick custom quote to explore cost-saving opportunities?" If the CS asks for permission,then only give good rating.)

13. Did the CS proactively overcome customer objections?
(Context: The CS should address and overcome customer objections. For example, reassuring the customer that a policy review won't impact current rates.Anathor example will be if a customer asks that will i have to take new policy while moving to other location,The CS should deny if existing policy works in that location by providing the comparative details. If the CS proactively overcomes objections,then give good rating.)

14. Did the CS use multiple closing statements during the presentation?
(Context: The CS should use multiple closing statements to reinforce the solution. For example, summarizing the benefits and next steps. If the CS uses multiple closing statements,then give good rating.)

15. Did the CS verify the customer's information accurately?
(Context: The CS should confirm the customer's details such as name, address, phone number, and details about the insurance claims policy. For example, "Could you please confirm your full name, address, and the best phone number to reach you at?" If the CS verifies the information accurately,then give good rating.)

16. Did the CS complete all necessary legal disclosures during the call?
(Context: The CS should inform the customer about terms, conditions, and exclusions . For example, "Please review the terms, conditions, and exclusions in the policy documents."Specifically look for the agent stating something like: "Before we finish, I need to let you know that all changes to your policy, including any adjustments or new coverage, are subject to the terms, conditions, and exclusions outlined in your policy documents." This is a crucial legal disclosure. Rate highly if this (or a similar) disclosure is made.)

17. Did the CS end the call with a courteous and professional closing, thanking the customer for their time?
(Context: The CS should end the call politely and thank the customer. For example, "Thank you for choosing NewCo, and have a great day!"Evaluate the agent's closing remarks. Look for phrases like "Thank you for calling NewCo", "I appreciate your patience", "Have a wonderful day!", "Drive safely!". A higher rating for a polite and appreciative closing.)

ANALYZE THE CONVERSATION BEFORE GIVING ANY RATING.DONOT BLINDLY GIVE ANY RATING.THESE SHOULD BE VALID REASON TO GIVE SOME RATING TO CUSTOMER REPRESENTATIVE.

Provide the ratings along with a brief explanation for each based on your analysis of the transcript. If any aspect is missing or incomplete, rate it accordingly and provide a reason.

Please analyze the customer care call transcript and evaluate the Customer Service Representative's (CS) performance based on the questions listed above. Provide a rating for each question on a scale of 1 to 5, where 1 is the lowest and 5 is the highest. Include a brief explanation for each rating based on your analysis of the transcript.Final output should be in Proper json format.

I NEED THE COMPLETE DETAILED  SUMMARY OF WHATEVER HAPPENED IN THE CONVERSATION IN 100 WORDS in paragraph format.(it must be of 100 words AND includes all the important points of conversation.)

Solutions given by agent: Added a new key in the JSON structure to capture the solutions offered by the agent during the conversation. This will be populated based on the transcript.

ALSO PREDICT SOME IMPORTANT WORDS (AROUND 20-30) FOR WORDCLOUD FORMATION [THE WORDS SHOULD BE MOST IMPORTANT FROM THE CONTEXT]

AFTER THAT I NEED A OVERALL SENTIMENT OF CUSTOMER ALSO .

INCLUDE EVERYTHING IN JSON SCHEMA AS DESCRIBED BELOW.

RESPONSE FORMAT:
I NEED A JSON FILE WITH THE FOLLOWING STRUCTURE
{Question Number : Rating,Explanation of the rating provided.
 Question number : Rating,Explanation of the rating provided.
 .....

 Summary of Conversation:
 "Solutions given by agent": [],
 "Important Words": [],
 "Overall Sentiment of Customer": [],

 }
 The structure should follow for all 17 questions.

'''

system_prompt='''You are a highly skilled AI assistant with a deep understanding of pdf file analysis, natural language processing, and emotional intelligence. You are meticulous, detail-oriented, and committed to delivering accurate and structured results. Your goal is to provide a comprehensive analysis of the call center transcript pdf, ensuring the transcript is clear, emotions are accurately detected, and the output is well-organized for further use.'''

st.title("Welcome to Transcript PDF Analysis")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"], accept_multiple_files=False)

# Model selection dropdown
model_option = st.selectbox("Select Model", [
    "Gemini 1.5 pro",
    "Gemini 1.5 Flash",
    "Gemini 1.5 flash 8b",
    "Gemini 2.0 Flash Exp"
])

model_name_map = {
    "Gemini 1.5 pro": "gemini-1.5-pro-002",
    "Gemini 1.5 Flash": "gemini-1.5-flash-002",
    "Gemini 1.5 flash 8b": "gemini-1.5-flash-8b-001",
    "Gemini 2.0 Flash Exp": "gemini-2.0-flash-exp"
}

if uploaded_file is not None:
    file_extension = Path(uploaded_file.name).suffix.lower()
    valid_extensions = [".pdf"]
    
    if file_extension not in valid_extensions:
        st.error("PDF FILE IS NOT IN VALID FORMAT")
    else:
        # Save the uploaded file temporarily
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Upload to Gemini
        mime_type = "application/pdf"
        mypdf = upload_to_gemini(uploaded_file.name, mime_type=mime_type)
        
        st.write("PDF uploaded successfully.")
        
        if st.button("View Analysis"):
            model_name = model_name_map[model_option]
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_prompt
            )
            
            response = model.generate_content([mypdf, Prompt_for_audio_transcript], generation_config=generation_config)
            try:
                json_response = json.loads(response.text)
                st.json(json_response, expanded=True)
                
                # Add the download button for JSON
                st.download_button(
                    label="Download JSON",
                    data=json.dumps(json_response, indent=4),
                    file_name="analysis.json",
                    mime="application/json"
                )
                
            except json.JSONDecodeError:
                st.write("Here is the raw output from the model:")
                st.text(response.text)

# Clean up temporary files after session
@st.cache_data()
def get_session_files():
    return []

def remove_temp_files():
    for file_path in get_session_files():
        if os.path.exists(file_path):
            os.remove(file_path)

remove_temp_files()
