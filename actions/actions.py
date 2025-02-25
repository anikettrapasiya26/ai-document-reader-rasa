# Import Libraries :
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from datetime import date
import logging
# import openai
from actions.rasa_utils import TextExtraction, TextOcr, ner
from groq import Groq
import os

client = Groq(
    # This is the default and can be omitted
    api_key=os.environ.get("GROQ_API_KEY"),
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "you are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Explain the importance of fast language models",
        }
    ],
    model="llama-3.3-70b-versatile",
)

print(chat_completion.choices[0].message.content)

#Logger Function
def get_logger(date):
  
    # # #Create and configure logger
    # for handler in logging.root.handlers[:]:
    #     logging.root.removeHandler(handler)
    logging.basicConfig(filename="logs/"+str(date)+".log",
                        format='%(asctime)s %(message)s',
                        filemode='a',
                        level=logging.INFO)

    #Create an object
    logger=logging.getLogger()

    #Set the threshold of logger to DEBUG
    logger.setLevel(logging.DEBUG)
    return logger

# Text Summarization Code :
class ActionSummary(Action):  
  
  def name(self) -> Text:
    return "action_summary"

  def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    logger = get_logger(date.today())
    logger.info(str(tracker.latest_message['text']))
    try:
      keys = tracker.latest_message.get('text').split(' | ')[1:]
      keys = keys[0].split(',')
      document = TextExtraction(keys)
      
      # response = openai.ChatCompletion.create(
      # model="gpt-3.5-turbo",
      # messages= [{"role":"user", "content": f"summarize this document in 200 words single paragraph: {document}" }], 
      # )
      # output = response.choices[0].message.content
      
      response = client.chat.completions.create(
        messages=[
          {
            "role": "user",
            "content": f"summarize this document in 200 words single paragraph: {document}"
          }
        ],
        model="llama-3.3-70b-versatile",
      )
      output = response.choices[0].message.content
      
      
      logger.info(str(output))
      # dispatcher.utter_message(response.choices[0].message.content)
      dispatcher.utter_message(f'Summary : \n \n{output}')

    except Exception as e: 
      logger.error(str(e))
      dispatcher.utter_message(text=f"Error: {e}.")

# Text NER Code :
class ActionNer(Action):

  def name(self) -> Text:
    return "action_ner"

  def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    logger = get_logger(date.today())
    logger.info(str(tracker.latest_message['text']))    
    try:
      keys = tracker.latest_message.get('text').split(' | ')[1:]
      keys = keys[0].split(',')
      document = TextExtraction(keys)
      entities= ner(document)
      logger.info(entities)
      dispatcher.utter_message(str(entities))
    except Exception as e:
      logger.error(str(e))
      dispatcher.utter_message(text=f"Error: {e}.")
 
# Text Clause Extraction Code :  
class ActionClause(Action):

  def name(self) -> Text:
    return "action_clause"

  def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    logger = get_logger(date.today())
    logger.info(str(tracker.latest_message['text']))
    try:
      keys = tracker.latest_message.get('text').split(' | ')[1:]
      keys = keys[0].split(',')
      document = TextExtraction(keys)
      
      # response = openai.ChatCompletion.create(
      # model="gpt-3.5-turbo",
      # messages= [{"role":"user", "content": f"extract clauses and List out them with - and \n in one paragraph from this document : {document}" }], 
      # )
      response = client.chat.completions.create(
        messages=[
          {
            "role": "user",
            "content": f"extract clauses and List out them with - and \n in one paragraph from this document : {document}"
          }
        ],
        model="llama-3.3-70b-versatile",
      )
      output = response.choices[0].message.content
      
      # dispatcher.utter_message(response.choices[0].message.content)
      # output = response.choices[0].message.content
      logger.info(str(f'Clauses : \n \n{output}'))
      dispatcher.utter_message(f'Clauses : \n \n{output}')
    except Exception as e: 
      logger.error(str(e))
      dispatcher.utter_message(text=f"Error: {e}.")

# Text Keyword Extraction Code :
class ActionKeyword(Action):

  def name(self) -> Text:
    return "action_keyword"

  def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    logger = get_logger(date.today())
    logger.info(str(tracker.latest_message['text']))
    try:
      keys = tracker.latest_message.get('text').split(' | ')[1:]
      keys = keys[0].split(',')
      document = TextExtraction(keys)
      
      # response = openai.ChatCompletion.create(
      # model="gpt-3.5-turbo",
      # messages= [{"role":"user", "content": f"List out the appropriate Legal keywords with high probability according to standard legal document in new line with numbers from this document : {document}" }], 
      # )
      # # dispatcher.utter_message(response.choices[0].message.content)
      # output = response.choices[0].message.content
      
      response = client.chat.completions.create(
        messages=[
          {
            "role": "user",
            "content": f"List out the appropriate Legal keywords with high probability according to standard legal document in new line with numbers from this document : {document}"
          }
        ],
        model="llama-3.3-70b-versatile",
      )
      output = response.choices[0].message.content
      
      logger.info(str(f'Keywords : \n \n{output}'))
      dispatcher.utter_message(f'Keywords : \n \n{output}')

    except Exception as e: 
      logger.error(str(e))
      dispatcher.utter_message(text=f"Error: {e}.")
  
class ActionOCR(Action):

  def name(self) -> Text:
    return "action_ocr"

  def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    logger = get_logger(date.today())
    logger.info(str(tracker.latest_message['text']))    
    try:
      keys = tracker.latest_message.get('text').split(' | ')[1:]
      keys = keys[0].split(',')
      name = keys[0]
      url = TextOcr(keys,name)
      logger.info(str(url))
      dispatcher.utter_message(url)

    except Exception as e: 
      logger.error(str(e))
      dispatcher.utter_message(text=f"Error: {e}.")
      
class ActionCustomFallback(Action):

    def name(self) -> Text:
        return "action_custom_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger = get_logger(date.today()) 
        logger.info(tracker.latest_message)
        bot_reply = "Sorry, I couldn't understand !"
        logger.info(str(bot_reply))
        dispatcher.utter_message(text=bot_reply)
        return []