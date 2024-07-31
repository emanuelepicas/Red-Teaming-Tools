from bs4 import BeautifulSoup
import requests

"""
TO BE DONE, possible feature to retrive a feed news panel on the bottom of the author page
"""

request= requests.get('https://news.ycombinator.com')

# Parse the HTML content with BeautifulSoup
soup = BeautifulSoup(request.text, 'html.parser')

# Find all <tr> tags within the table
table_rows = soup.select('table#hnmain td')

# Extract links with "https://" structure from <tr> elements
https_links = []
for row in table_rows:
    anchor_tag = row.find('a', href=True)
    if anchor_tag and anchor_tag['href'].startswith('https://') and 'https://news.ycombinator.com' not in anchor_tag['href']:
        https_links.append(anchor_tag['href'])

# Print the extracted links
for link in https_links:
    print(link)





with open('../base_templates/template1/author.html', 'r') as file:
    html_content = file.read()

    soup2 = BeautifulSoup(html_content, 'html.parser')

    news_section = soup2.new_tag('div', class_='news-section')
    ul = soup2.new_tag('ul', class_='article-list')

    for link in https_links:
        li = soup2.new_tag('li')
        anchor = soup2.new_tag('a', href=link, target='_blank')
        anchor.string = link
        li.append(anchor)
        ul.append(li)

    # Append the <ul> outside the loop
    news_section.append(ul)

    print(news_section)

    # Find the existing <div> with class 'news-section'
    existing_div = soup2.find('div', class_='news-section')

    print(existing_div)
    # Replace the existing <div> with the new_news_section
    existing_div.replace_with(news_section)

    # Print the updated soup2 (optional)
    print(soup2)

    # Save the updated HTML content back to the file

with open('../base_templates/template1/author.html', 'w') as file:
         file.write(str(soup2))





