

import streamlit as st
import pandas as pd
import re
import io
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import streamlit as st
from datetime import datetime

import re
from datetime import datetime
import pandas as pd

import re
from datetime import datetime
import pandas as pd

import re
from datetime import datetime

import re
import pandas as pd
from datetime import datetime

import re
from datetime import datetime

import re
from datetime import datetime
import pandas as pd
import nltk
nltk.download('punkt_tab')

def parse_whatsapp_chat(uploaded_file):
    try:
        chat_data = uploaded_file.getvalue().decode("utf-8")
        lines = chat_data.split('\n')

        parsed_data = []
        current_message = {'timestamp': None, 'sender': None, 'message': []}

        # Adjusted pattern for non-breaking spaces or invisible characters
        timestamp_patterns = [
            # dd/mm/yyyy, hh:mm (24-hour format)
            (r'(\d{2}/\d{2}/\d{4}),\s*(\d{1,2}:\d{2})\s*([AaPp][Mm]?)?\s*-', 
             lambda d, t, p: datetime.strptime(f"{d} {t} {p}" if p else f"{d} {t}", '%d/%m/%Y %I:%M %p' if p else '%d/%m/%Y %H:%M')),

            # dd/mm/yy, h:mm am/pm format
            (r'(\d{1,2}/\d{1,2}/\d{2}),\s*(\d{1,2}:\d{2})\s*([AaPp][Mm])\s*-',
             lambda d, t, p: datetime.strptime(f"{d}, {t} {p}", '%d/%m/%y, %I:%M %p')),

            # yyyy-mm-dd, hh:mm (24-hour format)
            (r'(\d{4}-\d{2}-\d{2}),\s*(\d{2}:\d{2})\s*-\s*',
             lambda d, t, _: datetime.strptime(f"{d} {t}", '%Y-%m-%d %H:%M')),

            # dd-mm-yyyy, hh:mm (24-hour format)
            (r'(\d{2}-\d{2}-\d{4}),\s*(\d{2}:\d{2})\s*-\s*',
             lambda d, t, _: datetime.strptime(f"{d} {t}", '%d-%m-%Y %H:%M')),

            # dd-mm-yy, h:mm am/pm format
            (r'(\d{2}-\d{2}-\d{2}),\s*(\d{1,2}:\d{2})\s*([AaPp][Mm])\s*-',
             lambda d, t, p: datetime.strptime(f"{d}, {t} {p}", '%d-%m-%y, %I:%M %p')),

            # mm/dd/yy, h:mm am/pm format
            (r'(\d{1,2}/\d{1,2}/\d{2}),\s*(\d{1,2}:\d{2})\s*([AaPp][Mm])\s*-',
             lambda d, t, p: datetime.strptime(f"{d}, {t} {p}", '%m/%d/%y, %I:%M %p')),

            # mm-dd-yyyy, hh:mm (24-hour format)
            (r'(\d{2}-\d{2}-\d{4}),\s*(\d{2}:\d{2})\s*-\s*',
             lambda d, t, _: datetime.strptime(f"{d} {t}", '%m-%d-%Y %H:%M')),

            # dd/mm/yyyy, hh:mm am/pm (handling non-breaking spaces or special chars)
            (r'(\d{2}/\d{2}/\d{4}),\s+(\d{1,2}:\d{2})\s*([AaPp][Mm])\s*-',
             lambda d, t, p: datetime.strptime(f"{d}, {t} {p}", '%d/%m/%Y %I:%M %p')),

            # New format: dd/mm/yyyy, h:mm am/pm format with non-breaking space (U+202F)
            (r'(\d{2}/\d{2}/\d{4}),\s*(\d{1,2}:\d{2})\s*([\u202F]?[AaPp][Mm])\s*-',
             lambda d, t, p: datetime.strptime(f"{d} {t} {p}", '%d/%m/%Y %I:%M %p')),
        ]
        
        def parse_timestamp(line):
            for pattern, parser in timestamp_patterns:
                match = re.match(pattern, line)
                if match:
                    try:
                        date_str, time_str = match.group(1), match.group(2)
                        period = match.group(3) if len(match.groups()) > 2 else None
                        timestamp = parser(date_str, time_str, period)
                        message_start = match.end()
                        return timestamp, line[message_start:]
                    except ValueError:
                        continue
            return None, None

        def parse_message_content(content):
            if ': ' in content:
                sender, message = content.split(': ', 1)
                return sender.strip(), message.strip()
            
            system_patterns = [
                r'Messages and calls are end-to-end encrypted',
                r'created group',
                r'added',
                r'joined using this group\'s invite link',
                r'left',
                r'removed',
                r'changed the subject',
                r'changed this group\'s icon',
                r'changed the group description',
                r'<Media omitted>',
                r'This message was deleted',
                r'You were added',
                r'joined using this group\'s invite link'
            ]
            
            for pattern in system_patterns:
                if re.search(pattern, content):
                    return 'System', content.strip()
            
            return 'System', content.strip()

        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            timestamp, message_content = parse_timestamp(line)
            
            if timestamp:
                if current_message['timestamp']:
                    parsed_data.append({
                        'timestamp': current_message['timestamp'],
                        'sender': current_message['sender'],
                        'message': ' '.join(current_message['message'])
                    })
                
                sender, message = parse_message_content(message_content)
                current_message = {
                    'timestamp': timestamp,
                    'sender': sender,
                    'message': [message]
                }
            else:
                current_message['message'].append(line)
        
        if current_message['timestamp']:
            parsed_data.append({
                'timestamp': current_message['timestamp'],
                'sender': current_message['sender'],
                'message': ' '.join(current_message['message'])
            })

        # Return the result as a dataframe
        return pd.DataFrame(parsed_data)
    
    except Exception as e:
        print(f"Error parsing chat: {e}")
        return pd.DataFrame()


def load_data():
    uploaded_file = st.file_uploader("Upload your WhatsApp chat file", type="txt")
    if uploaded_file is not None:
        return parse_whatsapp_chat(uploaded_file)
    else:
        return None

import matplotlib.pyplot as plt
import streamlit as st

def perform_eda(whatsapp_df):
    # Convert timestamp strings to datetime objects for analysis
    whatsapp_df['timestamp'] = pd.to_datetime(whatsapp_df['timestamp'], format='%m/%d/%y, %I:%M:%S %p')

    # Extract date, time, day of week, and hour for further analysis
    whatsapp_df['date'] = whatsapp_df['timestamp'].dt.date
    whatsapp_df['time'] = whatsapp_df['timestamp'].dt.time
    whatsapp_df['day_of_week'] = whatsapp_df['timestamp'].dt.day_name()
    whatsapp_df['hour'] = whatsapp_df['timestamp'].dt.hour

    # Message count analysis
    messages_per_day = whatsapp_df['date'].value_counts().sort_index()
    messages_per_sender = whatsapp_df['sender'].value_counts()
    messages_per_day_of_week = whatsapp_df['day_of_week'].value_counts()
    messages_per_hour = whatsapp_df['hour'].value_counts().sort_index()

    # Adjust the overall figure size (width, height)
    plt.figure(figsize=(10, 20))  # Width, Height

    # Messages per day
    plt.subplot(4, 1, 1)  # 4 rows, 1 column, position 1
    messages_per_day.plot(kind='line')
    plt.title('Messages per Day')
    plt.xlabel('Date')
    plt.ylabel('Number of Messages')

    # Messages per sender
    plt.subplot(4, 1, 2)  # 4 rows, 1 column, position 2
    messages_per_sender.plot(kind='bar')
    plt.title('Messages per Sender')
    plt.xlabel('Sender')
    plt.ylabel('Number of Messages')
    plt.xticks(rotation=45)

    # Messages per day of the week
    plt.subplot(4, 1, 3)  # 4 rows, 1 column, position 3
    messages_per_day_of_week.plot(kind='bar')
    plt.title('Messages per Day of the Week')
    plt.xlabel('Day of the Week')
    plt.ylabel('Number of Messages')

    # Messages per hour
    plt.subplot(4, 1, 4)  # 4 rows, 1 column, position 4
    messages_per_hour.plot(kind='bar')
    plt.title('Messages per Hour of the Day')
    plt.xlabel('Hour')
    plt.ylabel('Number of Messages')

    plt.tight_layout()  # Adjust the layout
    st.pyplot(plt)


def perform_date(whatsapp_df):
    # Convert timestamp strings to datetime objects for analysis
    whatsapp_df['timestamp'] = pd.to_datetime(whatsapp_df['timestamp'], format='%m/%d/%y, %I:%M:%S %p')

    # Extract date, time, day of week, and hour for further analysis
    whatsapp_df['date'] = whatsapp_df['timestamp'].dt.date
    whatsapp_df['time'] = whatsapp_df['timestamp'].dt.time
    whatsapp_df['day_of_week'] = whatsapp_df['timestamp'].dt.day_name()
    whatsapp_df['hour'] = whatsapp_df['timestamp'].dt.hour



from textblob import TextBlob

def perform_sentiment_analysis(whatsapp_df):
    # Sentiment Analysis Function
    def analyze_sentiment(message):
        return TextBlob(message).sentiment

    # Apply sentiment analysis to each message
    whatsapp_df['sentiment'] = whatsapp_df['message'].apply(lambda x: analyze_sentiment(x))

    # Extracting sentiment polarity and subjectivity
    whatsapp_df['polarity'] = whatsapp_df['sentiment'].apply(lambda x: x.polarity)
    whatsapp_df['subjectivity'] = whatsapp_df['sentiment'].apply(lambda x: x.subjectivity)

    return whatsapp_df

import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def visualize_sentiment_analysis(whatsapp_df):
    # Sentiment Polarity Distribution
    plt.figure(figsize=(12, 6))

    # Distribution of Polarity Scores
    plt.subplot(1, 2, 1)
    sns.histplot(whatsapp_df['polarity'], kde=True, bins=30)
    plt.title('Distribution of Sentiment Polarity')
    plt.xlabel('Polarity Score')
    plt.ylabel('Frequency')

    # Average Sentiment Polarity per Day
    avg_polarity_per_day = whatsapp_df.groupby('date')['polarity'].mean()
    plt.subplot(1, 2, 2)
    avg_polarity_per_day.plot(kind='line', color='blue')
    plt.title('Average Sentiment Polarity per Day')
    plt.xlabel('Date')
    plt.ylabel('Average Polarity Score')

    plt.tight_layout()
    st.pyplot(plt)


import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from gensim import corpora
from gensim.models.ldamodel import LdaModel
import streamlit as st

# Ensure NLTK data is downloaded (you might need to handle this outside the function if it causes issues in Streamlit)
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

def perform_topic_modeling(whatsapp_df, num_topics=5):
    def preprocess_text(text):
        tokens = word_tokenize(text.lower())
        tokens = [word for word in tokens if word.isalpha()]  # Remove non-alphabetic tokens
        tokens = [word for word in tokens if word not in stopwords.words('english')]  # Remove stopwords
        return tokens

    whatsapp_df['processed_message'] = whatsapp_df['message'].apply(preprocess_text)

    # Creating a dictionary and corpus needed for topic modeling
    dictionary = corpora.Dictionary(whatsapp_df['processed_message'])
    corpus = [dictionary.doc2bow(text) for text in whatsapp_df['processed_message']]

    # Running LDA model
    lda_model = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=10)
    return lda_model


import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

def visualize_topics(lda_model, num_words=10):
    topics = {i: [word for word, _ in lda_model.show_topic(i, topn=num_words)] for i in range(lda_model.num_topics)}
    topics_df = pd.DataFrame(topics)

    plt.figure(figsize=(15, 5))
    for i in topics_df.columns:
        plt.subplot(1, len(topics_df.columns), i+1)
        plt.barh(topics_df[i], range(len(topics_df[i])), color='blue')
        plt.title(f'Topic {i}')
        plt.yticks(range(len(topics_df[i])), topics_df[i])
    plt.tight_layout()
    st.pyplot(plt)


import matplotlib.pyplot as plt
import streamlit as st

def user_messages(whatsapp_df):
    # Counting messages per sender
    messages_per_sender = whatsapp_df['sender'].value_counts()

    # Plotting the number of messages sent by each user
    plt.figure(figsize=(10, 6))
    messages_per_sender.plot(kind='bar')
    plt.title('Number of Messages per User')
    plt.xlabel('User')
    plt.ylabel('Number of Messages')
    plt.xticks(rotation=45)

    st.pyplot(plt)



import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
import streamlit as st

def preprocess_and_extract_words(whatsapp_df):
    nltk.download('stopwords', quiet=True)

    def preprocess_text(text):
        tokens = re.findall(r'\b\w+\b', text.lower())
        tokens = [word for word in tokens if word.isalpha()]  # Remove non-alphabetic tokens
        tokens = [word for word in tokens if word not in stopwords.words('english')]  # Remove stopwords
        return tokens

    whatsapp_df['processed_words'] = whatsapp_df['message'].apply(preprocess_text)
    all_processed_words = sum(whatsapp_df['processed_words'], [])
    processed_word_freq = Counter(all_processed_words)

    return processed_word_freq

import emoji
from collections import Counter

def extract_and_count_emojis(whatsapp_df):
    def extract_emojis(text):
        return [char for char in text if char in emoji.EMOJI_DATA]

    all_emojis = sum(whatsapp_df['message'].apply(extract_emojis), [])
    emoji_freq = Counter(all_emojis)

    return emoji_freq

import matplotlib.pyplot as plt

import streamlit as st

def visualize_words_and_emojis(processed_word_freq, emoji_freq):
    top_words = processed_word_freq.most_common(10)
    top_emojis = emoji_freq.most_common(10)

    words, word_counts = zip(*top_words)
    emojis, emoji_counts = zip(*top_emojis)

    # Increase the figure size and change layout to 2 rows, 1 column
    plt.figure(figsize=(10, 12))  # Adjust the size as needed

    # Plot for top words
    plt.subplot(2, 1, 1)  # 2 rows, 1 column, position 1
    plt.bar(words, word_counts, color='skyblue')
    plt.title('Top 10 Unique Words')
    plt.xlabel('Words')
    plt.ylabel('Frequency')

    # Plot for top emojis
    plt.subplot(2, 1, 2)  # 2 rows, 1 column, position 2
    plt.bar(emojis, emoji_counts, color='lightgreen')
    plt.title('Top 10 Emojis')
    plt.xlabel('Emojis')
    plt.ylabel('Frequency')

    plt.tight_layout()  # Adjust layout
    st.pyplot(plt)



import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import streamlit as st

def forecast_message_trends(whatsapp_df):
    if 'date' not in whatsapp_df.columns:
        st.error("Date column not found in the data.")
        return

    message_counts = whatsapp_df.groupby('date').size().reset_index(name='count')

    # Ensure the 'date' column is a datetime object
    message_counts['date'] = pd.to_datetime(message_counts['date'])
    start_date = message_counts['date'].min()

    # Calculate the number of days since the start for each date
    message_counts['date_numeric'] = (message_counts['date'] - start_date).dt.days

    X = message_counts[['date_numeric']]
    y = message_counts['count']

    model = LinearRegression()
    model.fit(X, y)

    future_days = st.slider("Select number of days to forecast", 10, 60, 30)
    future_dates = pd.date_range(start=message_counts['date'].max(), periods=future_days)

    # Calculate days since start for future dates
    future_dates_numeric = (future_dates - start_date).days

    future_predictions = model.predict(np.array(future_dates_numeric).reshape(-1, 1))

    plt.figure(figsize=(14, 8))
    plt.plot(message_counts['date'], y, label='Historical Message Counts')
    plt.plot(future_dates, future_predictions, label='Predicted Message Counts', color='red')
    plt.xlabel('Date')
    plt.ylabel('Number of Messages')
    plt.title('Predicted Future Message Trends')
    plt.legend()

    st.pyplot(plt)



import streamlit as st


def display_alerts(whatsapp_df):
    # Define your alert conditions
    keywords = ['help', 'important', 'ASAP']
    sentiment_threshold = 0.7  # example threshold for positive sentiment

    # Check for keyword alerts and high sentiment messages
    alerts = []
    for index, row in whatsapp_df.iterrows():
        # Check for keyword alerts
        if any(keyword in row['message'].lower() for keyword in keywords):
            alerts.append((row['timestamp'], 'keyword', row['message']))

        # Check for sentiment alerts
        if row.get('polarity') and row['polarity'] > sentiment_threshold:
            alerts.append((row['timestamp'], 'sentiment', row['message']))

    # Display alerts
    if alerts:
        for alert in alerts:
            if alert[1] == 'keyword':
                # Display keyword alerts in one color (e.g., blue)
                st.markdown(f"<span style='color: blue;'>Alert at {alert[0]} due to {alert[1]}: {alert[2]}</span>", unsafe_allow_html=True)
            elif alert[1] == 'sentiment':
                # Display sentiment alerts in another color (e.g., green)
                st.markdown(f"<span style='color: green;'>Alert at {alert[0]} due to {alert[1]}: {alert[2]}</span>", unsafe_allow_html=True)
    else:
        st.write("No alerts based on the given conditions.")


from transformers import pipeline
import streamlit as st

def transformers_sentiment_analysis(whatsapp_df):
    # Load sentiment analysis pipeline
    sentiment_pipeline = pipeline("sentiment-analysis")

    # Display a selectbox to choose a message
    message_index = st.selectbox("Select a message index", whatsapp_df.index)
    example_message = whatsapp_df.loc[message_index, 'message']

    # Analyze sentiment
    if st.button("Analyze Sentiment"):
        result = sentiment_pipeline(example_message)
        st.write(f"Message: {example_message}\nSentiment: {result[0]}")


from transformers import pipeline
import streamlit as st

def transformers_ner_analysis(whatsapp_df):
    # Load NER pipeline
    ner_pipeline = pipeline("ner", grouped_entities=True)

    # Display a selectbox to choose a message
    message_index = st.selectbox("Select a message index for NER", whatsapp_df.index)
    example_message = whatsapp_df.loc[message_index, 'message']

    # Perform NER
    if st.button("Perform NER"):
        result = ner_pipeline(example_message)
        st.write(f"Message: {example_message}")
        st.write("Named Entities:")
        for entity in result:
            st.write(f"{entity['entity_group']} ({entity['score']:.2f}): {entity['word']}")


from transformers import pipeline
import streamlit as st

def transformers_text_summarization(whatsapp_df):
    # Load summarization pipeline
    summarizer = pipeline("summarization")

    # User input for selecting the range of messages
    start_index = st.number_input("Start index of messages", min_value=0, max_value=len(whatsapp_df)-1, value=30)
    end_index = st.number_input("End index of messages", min_value=0, max_value=len(whatsapp_df)-1, value=35)

    # Ensure start index is less than end index
    if start_index >= end_index:
        st.error("Start index should be less than end index.")
        return

    # Concatenate messages for summarization
    long_text = ' '.join(whatsapp_df['message'][start_index:end_index])

    # Summarize
    if st.button("Summarize"):
        with st.spinner("Summarizing..."):
            summary = summarizer(long_text, max_length=130, min_length=30, do_sample=False)
            st.write("Original Text:")
            st.write(long_text)
            st.write("Summary:")
            st.write(summary[0]['summary_text'])


from transformers import pipeline
import streamlit as st

def transformers_text_generation():
    # Load text generation pipeline
    generator = pipeline("text-generation", model="gpt2")

    # User input for starting text
    starting_text = st.text_input("Enter starting text for generation", "Let's plan a meetup")

    # Generate text
    if st.button("Generate Text"):
        with st.spinner("Generating..."):
            generated = generator(starting_text, max_length=50, num_return_sequences=1)
            st.write("Generated Text:")
            st.write(generated[0]['generated_text'])


import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def message_frequency(whatsapp_df):
    # Ensure the 'timestamp' column is in datetime format
    whatsapp_df['timestamp'] = pd.to_datetime(whatsapp_df['timestamp'])

    # Active Time Analysis: Count messages per hour of the day
    messages_per_hour = whatsapp_df['timestamp'].dt.hour.value_counts().sort_index()

    # Plotting the number of messages per hour
    plt.figure(figsize=(14, 8))
    messages_per_hour.plot(kind='bar')
    plt.title('Message Frequency by Hour of Day')
    plt.xlabel('Hour of Day')
    plt.ylabel('Number of Messages')
    plt.xticks(range(0, 24))
    st.pyplot(plt)

    # Response Time Analysis: Calculate time differences between messages
    whatsapp_df['response_time'] = whatsapp_df['timestamp'].diff()

    # Convert time differences to minutes
    whatsapp_df['response_time_minutes'] = whatsapp_df['response_time'].dt.total_seconds() / 60

    # Calculate average response time
    average_response_time = whatsapp_df['response_time_minutes'].mean()
    st.write(f"Average response time: {average_response_time:.2f} minutes")

from wordcloud import WordCloud
import matplotlib.pyplot as plt
import streamlit as st
import nltk
from nltk.corpus import stopwords
import re

def generate_wordcloud(whatsapp_df):
    nltk.download('stopwords', quiet=True)

    def preprocess(text):
        stop_words = set(stopwords.words('english'))
        words = re.findall(r'\b\w+\b', text.lower())
        return [word for word in words if word not in stop_words and word.isalpha()]

    # Combining all messages into a single text
    all_text = ' '.join(preprocess(' '.join(whatsapp_df['message'])))

    # Creating a word cloud
    wordcloud = WordCloud(width=800, height=800, background_color='white', min_font_size=10).generate(all_text)

    # Display the word cloud
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    st.pyplot(plt)


import streamlit as st

def show_top_users_by_messages(whatsapp_df):
    top_senders = whatsapp_df['sender'].value_counts().head(5)

    st.subheader("Top 5 Users by Number of Messages")
    st.bar_chart(top_senders)


def show_word_count_top_users(whatsapp_df):
    whatsapp_df['word_count'] = whatsapp_df['message'].apply(lambda x: len(x.split()))
    word_counts = whatsapp_df.groupby('sender')['word_count'].sum().sort_values(ascending=False).head(5)

    st.subheader("Word Count of Top 5 Users")
    st.bar_chart(word_counts)


def show_one_word_messages_top_users(whatsapp_df):
    whatsapp_df['is_one_word'] = whatsapp_df['word_count'] == 1
    one_word_counts = whatsapp_df[whatsapp_df['is_one_word']].groupby('sender').size().sort_values(ascending=False).head(5)

    st.subheader("One-Word Messages by Top 5 Users")
    st.bar_chart(one_word_counts)


import emoji

def show_emoji_usage_top_users(whatsapp_df):
    whatsapp_df['emoji_count'] = whatsapp_df['message'].apply(lambda x: len([char for char in x if char in emoji.EMOJI_DATA]))
    max_emojis = whatsapp_df.groupby('sender')['emoji_count'].sum().sort_values(ascending=False).head(5)

    st.subheader("Emoji Usage by Top 5 Users")
    st.bar_chart(max_emojis)


import matplotlib.pyplot as plt

def most_active_time(whatsapp_df):
    # Convert 'timestamp' column to datetime if it's not already
    if not pd.api.types.is_datetime64_any_dtype(whatsapp_df['timestamp']):
        whatsapp_df['timestamp'] = pd.to_datetime(whatsapp_df['timestamp'])

    whatsapp_df['hour'] = whatsapp_df['timestamp'].dt.hour
    active_hours = whatsapp_df['hour'].value_counts().sort_index()

    st.subheader("Most Active Hours of the Day")
    plt.figure(figsize=(12, 6))
    plt.bar(active_hours.index, active_hours.values)
    plt.xlabel('Hour of the Day')
    plt.ylabel('Number of Messages')
    plt.title('Activity by Hour')
    st.pyplot(plt)


def laugh_counter(whatsapp_df):
    laugh_words = ['lol', 'haha', '😂']
    whatsapp_df['laugh_count'] = whatsapp_df['message'].apply(lambda x: sum(word in x.lower() for word in laugh_words))

    total_laughs = whatsapp_df['laugh_count'].sum()

    st.subheader("Total 'LOLs' and 'Hahas'")
    st.write(f"Total LOLs and Hahas in the chat: {total_laughs}")


from collections import Counter
import emoji
from itertools import chain



def most_used_emojis(whatsapp_df):
    def extract_emojis(s):
        return [c for c in s if c in emoji.EMOJI_DATA]

    all_emojis = list(chain(*whatsapp_df['message'].apply(extract_emojis)))
    emoji_freq = Counter(all_emojis).most_common(5)

    st.subheader("Top 5 Emojis Used")
    for item in emoji_freq:
        st.write(f"{item[0]}: {item[1]} times")


import random

import streamlit as st

import pandas as pd

import streamlit as st
import pandas as pd

import streamlit as st
import pandas as pd

def mystery_user_challenge(data, sample_size=5):
    # Check if the sample is already stored in session state
    if 'sample_messages' not in st.session_state:
        st.session_state.sample_messages = data.sample(sample_size)

    sample_messages = st.session_state.sample_messages

    # Display the challenge
    st.markdown("""<h2 style='color: #4CAF50;'>Mystery User Challenge</h2>""", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 18px;'>Guess who sent these messages:</p>", unsafe_allow_html=True)

    # Initialize session state for storing user guesses
    if 'guesses' not in st.session_state:
        st.session_state.guesses = [''] * sample_size

    # Display messages and input fields
    for index, (i, row) in enumerate(sample_messages.iterrows()):
        st.markdown(f"<p style='background-color: #f1f1f1; padding: 10px; border-radius: 5px;'>Message: '<strong>{row['message']}</strong>'</p>", unsafe_allow_html=True)
        st.session_state.guesses[index] = st.text_input(
            f"Guess for message {index+1}", value=st.session_state.guesses[index], key=f"guess_{i}"
        )

    # Add a submit button for processing guesses
    if st.button("Submit Guesses"):
        st.markdown("""<h3 style='color: #2196F3;'>Your Guesses vs Actual Users</h3>""", unsafe_allow_html=True)
        for i, (guess, (j, row)) in enumerate(zip(st.session_state.guesses, sample_messages.iterrows()), 1):
            actual_user = row['sender']  # Assuming 'user' column exists in the data
            if guess.strip().lower() == actual_user.strip().lower():
                color = "#4CAF50"  # Green for correct guesses
            else:
                color = "#F44336"  # Red for incorrect guesses
            st.markdown(f"<p style='font-size: 16px;'><strong>Message {i}:</strong> Your guess: <span style='color: {color};'>{guess}</span> | Actual user: <strong>{actual_user}</strong></p>", unsafe_allow_html=True)

# Example usage (ensure `data` has 'message' and 'user' columns)
# data = pd.DataFrame({
#     'message': ['Hello!', 'How are you?', 'Good morning!', 'See you later.', 'Take care!'],
#     'user': ['Alice', 'Bob', 'Charlie', 'David', 'Eve']
# })
# mystery_user_challenge(data
# Usage
#mystery_user_challenge(data)



from collections import Counter
import random

def chat_wordle(whatsapp_df):
    common_words = [word for word, count in Counter(" ".join(whatsapp_df['message']).split()).items() if count > 5]
    secret_word = random.choice(common_words)

    st.subheader("Chat Wordle")
    st.write("Guess the common word used in the chat:")
    user_guess = st.text_input("Enter your guess:")

    if user_guess:
        if user_guess.lower() == secret_word.lower():
            st.success("Correct! You guessed the word!")
        else:
            st.error("Wrong guess. Try again!")

from textblob import TextBlob

def mood_meter(whatsapp_df):
    whatsapp_df['sentiment'] = whatsapp_df['message'].apply(lambda x: TextBlob(x).sentiment.polarity)
    daily_sentiment = whatsapp_df.resample('D', on='timestamp').sentiment.mean()

    st.subheader("Mood Meter Over Time")
    plt.figure(figsize=(10, 5))
    plt.plot(daily_sentiment.index, daily_sentiment.values, marker='o')
    plt.axhline(y=0, color='gray', linestyle='--')
    plt.title("Daily Chat Sentiment")
    plt.xlabel("Date")
    plt.ylabel("Sentiment Score")
    st.pyplot(plt)


import streamlit as st

def display_big_bold_centered_text(text):
    st.markdown(f"""
        <style>
        .big-font {{
            font-size:30px !important;
            font-weight: bold;
            text-align: center;
        }}
        </style>
        <div class='big-font'>
            {text}
        </div>
        """, unsafe_allow_html=True)



senti_text = """The visualizations for the sentiment analysis of your WhatsApp chat data provide insights into the emotional tone of the group conversations:

Distribution of Sentiment Polarity:

This histogram shows the frequency distribution of polarity scores across all messages. Polarity scores range from -1 (very negative) to +1 (very positive), with scores
around 0 indicating neutral sentiment. The shape of the distribution can give an idea of the overall positivity or negativity of the group's conversations.

Average Sentiment Polarity per Day:

This line plot shows the average sentiment polarity for each day. Fluctuations in this plot indicate changes in the group's overall mood on a day-to-day basis.
Peaks (high values) suggest days with more positive conversations, while troughs (low values) indicate days with more negative sentiments. These visualizations are
essential for understanding the emotional dynamics of the group over time and can be particularly insightful when correlated with specific events or topics
discussed in the group."""


topic_text = """This code performs the following steps:

Preprocesses the text data by tokenizing, converting to lowercase, removing non-alphabetic tokens, and filtering out stopwords. Creates a dictionary and
corpus needed for LDA topic modeling. Runs the LDA model to discover topics in the chat data. Displays the top words associated with each topic.
The output will be a set of topics, each represented by a set of words that are most significant to that topic. This can help you understand the main
themes of discussion in your WhatsApp group chat."""


emoji_text ="""Most Common Emojis: The list and bar chart of the most common emojis give a quick insight into the prevalent moods and reactions in the
group chat. For example, a preponderance of laughter or smiley emojis might suggest a generally light-hearted and positive group atmosphere.

Emoji Usage Patterns: By examining which emojis are most frequently used, you can infer the group's general mood and preferences. For instance:

Frequent use of hearts and smiley faces might indicate a friendly and positive interaction style. Use of surprise or shock emojis could imply
frequent sharing of surprising or unexpected news. Contextual Analysis: For a deeper understanding, consider the context in which these emojis are
used. This could involve analyzing the text surrounding the emoji usage to interpret the sentiments more accurately."""




forecasting_text = """Historical Message Counts (Blue Line): This represents the actual number of messages sent in the group for each time point in your
historical data. The spikes indicate days with a high number of messages, which could be due to specific events or conversations that engaged many members of the group.

Predicted Message Counts (Red Line): This shows the predicted number of messages based on the linear regression model. It appears as a flat line because
a simple linear regression model doesn't capture the variability or seasonality in the data; it only predicts the average trend.

Here's how to interpret the graph:

The blue line's spikes and troughs represent the natural variability in how many messages are sent each day. Some days are busier than others. The red line's
flatness indicates that the linear regression model predicts that, on average, the future will continue with the same average message count as the historical mean.
It does not predict the ups and downs because it's not a time-series model that captures patterns over time. For more accurate forecasting, especially for
time series data like this, you might consider using models that can account for seasonality, trends, and irregular cycles, such as ARIMA, SARIMA, or even LSTM networks
for deep learning approaches.

It's also worth noting that the linear model will not capture any potential future events that could cause spikes in messaging - it assumes the future will be like
the past, on average."""


word_cloud_text = """How to Interpret the Output: Word Clouds:

The size of each word in the word cloud indicates its frequency in the chat. Larger words were mentioned more frequently, highlighting the key themes or
subjects that dominate the group's conversations. It gives a quick visual representation of the most discussed topics. Trending Topics (Not included in the
code but typically involves Topic Modeling):

Trending topics analysis would identify the main themes or topics in the chat over time. Each topic would be represented by a set of words that frequently
occur together. By analyzing how the prominence of these topics changes over time, you can understand shifts in the group's focus or interest."""



def main():
    #st.image('/Users/senthilesakkiappan/Desktop/Stream_Lit_Myfolder/streamlit_01.jpg', width=700)
    st.image('assets/streamlit_01.jpg', width=600 ,)
    st.title("WAllytics - WhatsApp Chat Analysis")

    data = load_data()

    if data is not None:
        # Further analysis options go here
        pass  # Replace with analysis function calls

    with st.sidebar:
      #st.image('/Users/senthilesakkiappan/Desktop/Stream_Lit_Myfolder/streamlit.jpg', width=300)  # Display a logo
      st.image('assets/streamlit.jpg', width=300)  # Display a logo
      st.write("## Navigation")
      analysis_option = st.selectbox("Choose the Analysis you want to perform",
                      ["About the App","Show Data","EDA", "Sentiment Analysis","User Analysis","Topic Analysis","Emojis and Words Analysis", "Forecasting","Alert",
                       "Funny Analysis","Message Frequency",
                       "Challenge","Wordcloud"])



#    analysis_option = st.selectbox("Choose the Analysis you want to perform",
#                      ["About the App","Show Data","EDA", "Sentiment Analysis", "Topic Analysis","Emojis and Words Analysis", "Forecasting","Alert",
#                       "Transformers-Sentiment Analysis","NER","Summarization","Text Generation","Message Frequency","Wordcloud"])
    # Create a placeholder for future outputs
    output_placeholder = st.empty()


    if data is not None:
            if analysis_option == "EDA":

                output_placeholder.empty()  # Clear previous output
                display_big_bold_centered_text("EDA")
                perform_eda(data)
                # Call EDA function
                # eda_function(data)
                pass

            elif analysis_option == "User Analysis":

                display_big_bold_centered_text("""Detailed User Analysis""")
                show_top_users_by_messages(data)
                show_word_count_top_users(data)
                show_one_word_messages_top_users(data)
                show_emoji_usage_top_users(data)
            elif analysis_option == "Funny Analysis":
                display_big_bold_centered_text("Funny Analysis")
                most_active_time(data)
                laugh_counter(data)
                most_used_emojis(data)
                mood_meter(data)
            elif analysis_option == "Challenge":
                display_big_bold_centered_text("Challenge")
                mystery_user_challenge(data)
                chat_wordle(data)

            elif analysis_option == "Sentiment Analysis":
                output_placeholder.empty()  # Clear previous output
                display_big_bold_centered_text("Sentiment Analysis")
                perform_date(data)
                analyzed_data = perform_sentiment_analysis(data)
                visualize_sentiment_analysis(analyzed_data)
                st.markdown(senti_text)
                # Call Sentiment Analysis function
                # sentiment_analysis_function(data)
                pass
            elif analysis_option == "Topic Analysis":
                output_placeholder.empty()  # Clear previous output
                display_big_bold_centered_text("Topic Analysis")
                num_topics = st.slider("Select number of topics", 3, 10, 5)
                lda_model = perform_topic_modeling(data, num_topics=num_topics)
                visualize_topics(lda_model)
                st.markdown(topic_text)
                # Call Topic Analysis function
                # ...
                pass
            elif analysis_option == "Show Messages per User":
                output_placeholder.empty()  # Clear previous output
                display_big_bold_centered_text("Show Messages per User")
                user_messages(data)

            elif analysis_option == "Emojis and Words Analysis":
                output_placeholder.empty()  # Clear previous output
                display_big_bold_centered_text("Emojis and Words Analysis")
                processed_word_freq = preprocess_and_extract_words(data)
                emoji_freq = extract_and_count_emojis(data)
                visualize_words_and_emojis(processed_word_freq, emoji_freq)
                st.markdown(emoji_text)
            elif analysis_option == "Forecasting":
                output_placeholder.empty()  # Clear previous output
                display_big_bold_centered_text("Forecasting")
                perform_date(data)
                forecast_message_trends(data)
                st.markdown(forecasting_text)
            elif analysis_option == "Alert":
                output_placeholder.empty()  # Clear previous output
                display_big_bold_centered_text("Alerts")
                display_alerts(data)
            elif analysis_option == "Message Frequency":
                output_placeholder.empty()  # Clear previous output
                display_big_bold_centered_text("Message Frequency")
                message_frequency(data)
            elif analysis_option == "Wordcloud":
                output_placeholder.empty()  # Clear previous output
                display_big_bold_centered_text("Wordcloud")
                generate_wordcloud(data)
                st.markdown(word_cloud_text)
            elif analysis_option == "Show Data":
                display_big_bold_centered_text("Display the datafrrame")
                st.dataframe(data.head(500))
            elif analysis_option == "About the App":
                display_big_bold_centered_text("About the App")
                st.write("""
                          # WAllytics - WhatsApp Chat Analysis App
                          Welcome to the WhatsApp Chat Analysis App! This application offers a range of analytical tools to help you
                          gain insights from your WhatsApp chat data. Here’s what you can do with this app:

                          - **EDA (Exploratory Data Analysis):** Get a general overview of your chat data through various statistics and visualizations.
                          - **Sentiment Analysis:** Understand the emotional tone of the messages in your chat.
                          - **Topic Analysis:** Discover the common topics discussed in your chat.
                          - **Emojis and Words Analysis:** Explore the usage patterns of emojis and frequently used words.
                          - **Forecasting:** Predict future trends in your chat message frequency.
                          - **Alert:** Set up alerts based on specific keywords or sentiments.
                          - **Message Frequency:** Analyze the frequency of messages at different times.
                          - **Wordcloud:** Visualize the most common words in your chat in a word cloud format.

                          Dive into your WhatsApp chat data and uncover interesting insights with this app!
                          """)



            # ... other analysis options



if __name__ == "__main__":
    main()

