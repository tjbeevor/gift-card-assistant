import streamlit as st
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Gift Card Savings Assistant",
    page_icon="💳",
    layout="wide"
)

# Custom CSS
def load_css():
    st.markdown("""
        <style>
        .main {
            background-color: #f0f8ff;
        }
        .stChat {
            border-radius: 15px;
            border: 2px solid #e1e4e8;
            padding: 20px;
        }
        .chat-message {
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            display: flex;
            align-items: flex-start;
        }
        .chat-message.user {
            background-color: #e3f2fd;
        }
        .chat-message.assistant {
            background-color: #f3e5f5;
        }
        .chat-icon {
            width: 50px;
            height: 50px;
            margin-right: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)

# Load the gift card data
def load_gift_card_data():
    with open('data/gift_card_data.json', 'r') as file:
        return json.load(file)

# Initialize Gemini
def initialize_gemini():
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    return genai.GenerativeModel('gemini-pro')

# Function to generate response
def get_gemini_response(model, query, gift_card_data):
    context = f"""
    You are a friendly and helpful gift card savings assistant. Your goal is to help users save money by 
    recommending the best gift cards for their shopping needs. Use the following gift card data to make 
    recommendations: {json.dumps(gift_card_data)}

    When making recommendations:
    1. Consider the user's shopping needs and match them with relevant retailers
    2. Calculate potential savings based on purchase amount (if provided)
    3. Suggest alternative retailers if applicable
    4. Be friendly and conversational
    5. Always explain why you're recommending specific cards
    6. If the user mentions a price, calculate the exact savings

    Current user query: {query}
    """

    response = model.generate_content(context)
    return response.text

def main():
    load_css()
    
    # Title and introduction
    st.title("💳 Gift Card Savings Assistant")
    st.markdown("""
    <div style='background-color: #e3f2fd; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h4>Welcome to your Gift Card Savings Assistant! 🎉</h4>
        <p>Tell me what you're planning to buy, and I'll help you save money by recommending the best gift cards!</p>
        <p>For example, try asking:</p>
        <ul>
            <li>"I want to buy a new laptop for $1000"</li>
            <li>"What's the best gift card for furniture shopping?"</li>
            <li>"I need to buy groceries"</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Load data and initialize model
    gift_card_data = load_gift_card_data()
    model = initialize_gemini()

    # Chat interface
    user_input = st.chat_input("What are you planning to buy?")

    if user_input:
        # Add user message to chat history
        st.session_state.chat_history.append(("user", user_input))
        
        # Get bot response
        response = get_gemini_response(model, user_input, gift_card_data)
        st.session_state.chat_history.append(("assistant", response))

    # Display chat history
    for role, message in st.session_state.chat_history:
        if role == "user":
            st.markdown(f"""
                <div class='chat-message user'>
                    <img class='chat-icon' src='https://api.dicebear.com/7.x/avataaars/svg?seed=user' />
                    <div>{message}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class='chat-message assistant'>
                    <img class='chat-icon' src='https://api.dicebear.com/7.x/bottts/svg?seed=assistant' />
                    <div>{message}</div>
                </div>
            """, unsafe_allow_html=True)

    # Sidebar with statistics
    with st.sidebar:
        st.markdown("### 📊 Gift Card Stats")
        
        # Calculate and display statistics
        max_discount = max(card['discount'] for card in gift_card_data['businesses'])
        avg_discount = sum(card['discount'] for card in gift_card_data['businesses']) / len(gift_card_data['businesses'])
        
        st.metric("Highest Available Discount", f"{max_discount}%")
        st.metric("Average Discount", f"{avg_discount:.1f}%")
        
        # Show top categories
        st.markdown("### 🏷️ Popular Categories")
        categories = ["Electronics", "Fashion", "Food & Dining", "Home & Garden", "Travel"]
        for category in categories:
            st.markdown(f"- {category}")

if __name__ == "__main__":
    main()
