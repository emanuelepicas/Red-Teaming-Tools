import openai
import re



def generate_introduction_blog(company,sector, api_key_GPT):
    '''
    Generate Introduction Blog for the main page
    '''
    #Token Inizialization
    openai.api_key = api_key_GPT

    #Query for chatGPT
    query = f'can you give me an introduction for a blog of four lines of  a {sector} company named  {company} ? Can you print just the text?'
    full_message = []
    full_message.append({'role': 'user', 'content': query})

    return introduction_blog(full_message)


def introduction_blog(prompt, model="gpt-3.5-turbo"):
            response = openai.ChatCompletion.create(
                model=model,
                messages=prompt,
                max_tokens=300,
                n=1,
                stop=None,
                temperature=1.3, #Temperature is a parameter that controls the “creativity” or randomness of the text generated by GPT-3. 
            )
     
            text = response.choices[0].message.content.strip()
            print(text)
            
            # Sanitizing the responses from chatGPT, the function below handle the main text addition text by ChatGPT 
            textSanitized = textSanitization(text)

            return textSanitized

def textSanitization(text):
    '''
    Sanitization of the text prompted by chatGPT
    '''
    # Remove content within parentheses with "Word count" or "Date" patterns
    text = re.sub(r'\(Word count:.*\n?|\(Date:.*\n?|\(\d+ words\)|Word count:\s*\d+', '', text, flags=re.IGNORECASE)

    # Remove content within square brackets with "Word count" pattern (case insensitive)
    text = re.sub(r'\[Word count:\s*\d+\]', '', text, flags=re.IGNORECASE)

    # Remove content after "Read more at::" (dotall flag used to match across lines)
    text = re.sub(r'Read more at::.*$', '', text, flags=re.DOTALL)

    # Remove "Note," "(Note:," or "Note to:" followed by any content (dotall flag used)
    text = re.sub(r'(?:Note|\(Note:|Note to):.*$', '', text, flags=re.DOTALL)

    # Remove "(Please note:" and its content
    text = re.sub(r'\(Please note:[^)]*\)', '', text)

    text = re.sub(r'Sure.*\n.*', ' ', text)

    if '"' in text:
           text.replace('"','')

    # Remove hyphens
    text = text.replace('-', '')

    return text
