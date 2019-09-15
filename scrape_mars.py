# Dependencies
from bs4 import BeautifulSoup
import requests
import pandas as pd
from splinter import Browser




# Initiaize browser
def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "chromedriver"}
    return Browser("chrome", **executable_path, headless=False)



# create mars dict that we can insert into mongo
mars= {}

def scrape():
    browser = init_browser()


    #=======mars news=========#
    # news title
    news_url="https://mars.nasa.gov/news/"
    response = requests.get(news_url)
    news_soup = BeautifulSoup(response.text, 'html.parser')
    news_title=news_soup.find('div', class_='content_title').find('a').text.strip()
    mars["title"]= news_title

    #news content
    news_p=news_soup.find('div', class_='rollover_description_inner').text.strip()
    mars["content"]=news_p


    #=======Featured Image=========#
    img_url="https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(img_url)
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')
    feature_image_url=img_soup.find("div",class_="carousel_items").find("article")["style"].replace("background-image: url('/","https://www.jpl.nasa.gov/").replace("')","").replace(";","")
    mars["featured_img_url"]=feature_image_url



    #=======Mars Weather=========#
    weather_url="https://twitter.com/marswxreport?lang=en"
    response = requests.get(weather_url)
    weather_soup = BeautifulSoup(response.text, 'html.parser')
    weathers=weather_soup.findAll("div",class_="js-tweet-text-container")
    
    for weather in weathers:
        result=weather.find('p').text
        if "InSight sol" in result:
            mars_weather=result
            break
        else:
            pass
    mars["weather"]=mars_weather


    #=======Mars Facts=========#
    facts_url="https://space-facts.com/mars/"
    tables = pd.read_html(facts_url)
    df=tables[1]
    df.columns=["Description","value"]
    df=df.set_index('Description')
    html_table = df.to_html()
    mars["facts"]=html_table

    #=======Mars Hemispheres=========#
    hem_url="https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    response = requests.get(hem_url)
    hem_soup = BeautifulSoup(response.text, 'html.parser')
    
    hems=hem_soup.findAll('div',class_="item")
    
    hems_main_url="https://astrogeology.usgs.gov"

    hemisphere_image_urls=[]
    dicts={}
    for hem in hems:
        dicts['title']=hem.find('h3').text
        partial_url=hem.find("a", class_="itemLink product-item")['href']
        
        # visit the link contains the high resolution images
        browser.visit(hems_main_url+partial_url)
        
        partial_img_html = browser.html
        partial_img_soup = BeautifulSoup(partial_img_html, "html.parser")
        
        partial_img_url=partial_img_soup.find('div',class_="wide-image-wrapper").find("a")['href']
        dicts['partial_img_url']=partial_img_url
        hemisphere_image_urls.append(dicts.copy())

    mars["hem_imgs"]=hemisphere_image_urls
    

    browser.quit()

    return mars