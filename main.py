#Scraping Top Repositories for Topics on GitHub

#ToDo(Intro)
'''
Introduction about web scraping
Introduction about GitHub and the problem statement
Mention the tools you're using (Python, requests, Beautiful Soup, Pandas)
'''


'''
Here are the steps we'll follow:

- We're going to scrape https://github.com/topics
- We'll get a list of topics. For each topic, we'll get topic title, topic page URL and topic description
- For each topic, we'll get the top 25 repositories in the topic from the topic page
- For each repository, we'll grab the repo name, username, stars and repo URL
- For each topic we'll create a CSV file in the following format:

```
Repo Name,Username,Stars,Repo URL
three.js,mrdoob,69700,https://github.com/mrdoob/three.js
libgdx,libgdx,18300,https://github.com/libgdx/libgdx
```
'''


'''
Scrape the list of topics from Github
Explain how you'll do it.

- use requests to downlaod the page
- user BS4 to parse and extract information
- convert to a Pandas dataframe
'''

#write a function to download the page
from operator import index
import requests
from bs4 import BeautifulSoup

def get_topics_page():
    """Return BeautifulSoup doc which contain parsed html page"""
    topics_url = 'https://github.com/topics'
    response = requests.get(topics_url)
    if response.status_code != 200:
        raise Exception('Failed to load page {}'.format(topics_url))
    doc = BeautifulSoup(response.text, 'html.parser')
    with open("webpage.html", "w", encoding = 'utf-8') as file:
    
    # prettify the soup object and convert it into a string
        file.write(str(doc.prettify()))
    return doc

doc = get_topics_page()
# print(doc.text)

#Let's create some helper function to parse information from the page
#We will inspect inside the page to get the information

def get_topic_titles(doc):
    """Return the list of titles"""
    title_selector = "f3 lh-condensed mb-0 mt-1 Link--primary"
    topic_title_tag = doc.find_all('p', {'class': title_selector})

    topic_titles = []
    for tag in topic_title_tag:
        topic_titles.append(tag.text)
    return topic_titles
    

def get_topic_descs(doc):
    """Returns topics description"""
    desc_selector = "f5 color-fg-muted mb-0 mt-1"
    topic_description_tag = doc.find_all('p', {'class': desc_selector})

    topic_descriptions = []
    for tag in topic_description_tag:
        topic_descriptions.append(tag.text.strip())  
    return topic_descriptions


def get_topic_url(doc):
    """Returns topics URL"""
    topic_links_selector = "no-underline flex-1 d-flex flex-column"
    topic_link_tag = doc.find_all('a', {'class': topic_links_selector})

    topic_urls =[]
    base_url = "https://github.com"
    for tag in topic_link_tag:
        topic_urls.append(base_url + tag['href'])
    return topic_urls


#Lets put this all together into a single function

import pandas as pd

def scrape_topics():
    """Returns the topics dictionary"""
    topics_url = "https://github.com/topics"
    response = requests.get(topics_url)
    if response.status_code != 200:
        raise Exception('Failed to load page'.format(topics_url)) 

    topics_dict = {
        'title': get_topic_titles(doc),
        'description': get_topic_descs(doc),
        'url': get_topic_url(doc)
    }
    # topics_df = pd.DataFrame(topics_dict)
    # # Create CSV file(s) with the extracted information
    
    # topics_df.to_csv('topics.csv', index = None)        #index = None is to remove the index number showing in our o/p csv file
    return pd.DataFrame(topics_dict)


#Get the top repositories from a topic page

def get_topic_page(topic_url):
    """Get the each topics url"""
    #download the page
    response = requests.get(topic_url)
    #check sucessful response
    if response.status_code != 200:
        raise Exception('Failed to load page'.format(topic_url))
    #parse using beautifulsoup
    topic_doc = BeautifulSoup(response.text, 'html.parser')
    return topic_doc

def parse_star_count(star_str):
    """Returns the int value of the starts count"""
    star_str = star_str.strip()
    if star_str[-1] == 'k':
        return int(float(star_str[:-1])*1000)
    return int(star_str)

def get_repo_info(h3_tag, star_tag):
    """returns all the required info about repository"""
    base_url = "https://github.com/"
    a_tags = h3_tag.find_all('a')
    username = a_tags[0].text.strip()
    repo_name = a_tags[1].text.strip()
    repo_url = base_url + a_tags[1]['href']
    stars = parse_star_count(star_tag.text.strip())
    return username, repo_name, stars, repo_url

def get_topic_repos(topic_doc):
    """get h3 tag containing repo title, repo URL and username"""
    h3_selection_class = "f3 color-fg-muted text-normal lh-condensed"
    repo_tags = topic_doc.find_all('h3', {'class' : h3_selection_class})
    #get the star tags
    star_tag = topic_doc.find_all('span', class_= "Counter js-social-count")
    #get repo info
    
    topic_repos_dict ={
        'username': [],
        'repo_name': [],
        'stars': [],
        'repo_url': []
    }
    #get repo info
    for tag in range(len(repo_tags)):
        repo_info = get_repo_info(repo_tags[tag], star_tag[tag])
        topic_repos_dict['username'].append(repo_info[0])
        topic_repos_dict['repo_name'].append(repo_info[1])
        topic_repos_dict['repo_url'].append(repo_info[3])
        topic_repos_dict['stars'].append(repo_info[2])

    return pd.DataFrame(topic_repos_dict)


import os

def scrape_topic(topic_url, path):
    """Converts into csv file"""
    if os.path.exists(path):       #to check wether the file already exists or not
        print('The file {} already exists. Skipping...'.format(path))
        return
    topic_df = get_topic_repos(get_topic_page(topic_url))
    topic_df.to_csv(path, index = None)


#PUTTING it all together

#- we have function to get the list of the topics
#- we have a function to create a csv file for scraped repos from a topic page
#- Let's create a function to put them together


def scrape_topics_repos():
    print('Scraping list of topics')
    topics_df = scrape_topics()
    topics_df.to_csv('topics.csv', index = None)
    #create folder here
    os.makedirs('data', exist_ok= True)

    for index, row in topics_df.iterrows():         #looping through the rows in pandas dataframe(df)
        print('Scraping top repositories for "{}"'. format(row['title']))
        scrape_topic(row['url'], 'data/{}.csv'.format(row['title']))


#lets run it to scrape the top repos for all the topic on the first page of github.com/topics

scrape_topics_repos()

#To read CSV file using pandas
covid = pd.read_csv("./data/COVID-19.csv")
print(covid)