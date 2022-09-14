#Top repositories for GitHub Topics

#Step 1: Picking up the website and describing the objectives
'''
****Project Outline****
- We are going to scrape "https://github.com/topics"
- We will get a list of topics. For each topic, we'll get topic title, topic 
  page URL and topic description
- For each topic we will get the top 25 repositories in the topic from the topic page
- For each repository, we'll get the repo name, username, star and repo URL.
- For each topic we'll create a CSV file in the following format:
    Repo name,Username,Stars,Repo URL
    Blog,Igianshu,7300,https://github.com/ljianshu/Blog.git
    metafizzy,infinite-scroll,7100,https://github.com/metafizzy/infinite-scroll.git

'''
#Step 2: Use the requests library to download web pages
import requests
from selenium import webdriver
from bs4 import BeautifulSoup


topics_url = "https://github.com/topics"
response = requests.get(topics_url)
# response.status_code      #This will give 200-299 as o/p which means get request is executed properly
page_content = response.text

# print(page_content[:1000])
 
# with open('webpage.html', 'w') as f:        #We can save a webpage with Selenium webdriver in Python.
#     f.write(page_content)





#Step 3: Use Beautiful Soup to parse and extract information

doc = BeautifulSoup(page_content, 'html.parser')    #So doc is a beautifulsoup object, inside it contains all the all the html content in the parsed format
# print(type(doc))
# print(doc)


title_selector = "f3 lh-condensed mb-0 mt-1 Link--primary"
topic_title_tag = doc.find_all('p', {'class': title_selector})
# print(len(p_tag))
# print(topic_title_tag)
# print(p_tag[:5])        #grabbing first 5 'p' tags 
topic_titles = []
for tag in topic_title_tag:
    topic_titles.append(tag.text)
# print(topic_titles)


desc_selector = "f5 color-fg-muted mb-0 mt-1"
topic_description_tag = doc.find_all('p', {'class': desc_selector})
# print(topic_description_tag)
topic_descriptions = []
for tag in topic_description_tag:
    topic_descriptions.append(tag.text.strip())     #strip() method is used to remove extra space from the beginning and end
# print(topic_descriptions)


topic_links_selector = "no-underline flex-1 d-flex flex-column"
topic_link_tag = doc.find_all('a', {'class': topic_links_selector})

# topic_title_tag0 = topic_title_tag[1]
# print(topic_title_tag0.parent)
# print(topic_link_tag)
topic_urls =[]
base_url = "https://github.com"
for tag in topic_link_tag:
    topic_urls.append(base_url + tag['href'])
# print(topic_urls) 



#Now, lets create a dataframe from list using pandas--supporting document "https://www.geeksforgeeks.org/create-a-pandas-dataframe-from-lists/"

#importing pandas as pd
import pandas as pd

#we have list of 'topic_titles', 'topic_descriptions' and 'topic_urls'

#creating dictionary of lists
topis_dict = {
    'title': topic_titles,
    'description': topic_descriptions,
    'url': topic_urls
}

topics_df = pd.DataFrame(topis_dict)

# print(topics_df)


#Step 4: Create CSV file(s) with the extracted information
topics_df.to_csv('topics.csv', index = None)        #index = None is to remove the index number showing in our o/p csv file



#Getting information out of the topic page
# topic_page_url = topic_urls[0]
# # print(topic_page_url)

def parse_star_count(star_str):
    star_str = star_str.strip()
    if star_str[-1] == 'k':
        return int(float(star_str[:-1])*1000)
    return int(star_str)



def get_topic_page(topic_url):
    #download the page
    response = requests.get(topic_url)
    #check sucessful response
    if response.status_code != 200:
        raise Exception('Failed to load page'.format(topic_url))
    #parse using beautifulsoup
    topic_doc = BeautifulSoup(response.text, 'html.parser')
    return topic_doc


def get_repo_info(h3_tag, star_tag):
    """returns all the required info about repository"""
    global base_url
    a_tags = h3_tag.find_all('a')
    username = a_tags[0].text.strip()
    repo_name = a_tags[1].text.strip()
    repo_url = base_url + a_tags[1]['href']
    stars = parse_star_count(star_tag.text.strip())

    return username, repo_name, stars, repo_url


def get_topic_repos(topic_doc):
    #get h3 tag containing repo title, repo URL and username
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
    for tag in range(len(repo_tags)):
        repo_info = get_repo_info(repo_tags[tag], star_tag[tag])
        topic_repos_dict['username'].append(repo_info[0])
        topic_repos_dict['repo_name'].append(repo_info[1])
        topic_repos_dict['repo_url'].append(repo_info[3])
        topic_repos_dict['stars'].append(repo_info[2])

    return pd.DataFrame(topic_repos_dict)

#Try creating any of one topic file(here, ansible)
print(topic_urls[6])
ansible_top_repos = get_topic_repos(get_topic_page(topic_urls[6]))
ansible_top_repos.to_csv('ansible.csv', index = None) 






covid = pd.read_csv("./data/COVID-19.csv") #to read csv file using pandas