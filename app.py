import requests
from bs4 import BeautifulSoup
import pymongo
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)

@app.route("/", methods=['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        try:
            save_dir = "images/"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            chrome_options = Options()
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
            for key, value in headers.items():
                chrome_options.add_argument(f"--{key}={value}")
            driver = webdriver.Chrome(options=chrome_options)
            query = request.form['content'].replace(" ", "")
            driver.get(
                f"https://www.google.com/search?q={query}&tbm=isch&ved=2ahUKEwi41rm2qoCDAxW6bGwGHcdFAUAQ2-cCegQIABAA&oq=sachin+tendulkar&gs_lcp=CgNpbWcQAzIECCMQJzIICAAQgAQQsQMyCAgAEIAEELEDMggIABCABBCxAzIKCAAQgAQQigUQQzIICAAQgAQQsQMyCAgAEIAEELEDMgUIABCABDIFCAAQgAQyBQgAEIAEUOsBWJQJYNMLaABwAHgBgAHDAYgBwwmSAQMwLjiYAQCgAQGqAQtnd3Mtd2l6LWltZ8ABAQ&sclient=img&ei=3E1zZbj4ELrZseMPx4uFgAQ&bih=955&biw=1920&rlz=1C1ONGR_en-GBIN1021IN1021")
            response = driver.page_source
            soup = BeautifulSoup(response, 'html.parser')
            images_tags = soup.find_all("img")
            del images_tags[0]
            img_data_mongo = []
            image_urls = []
            for i, image_tag in enumerate(images_tags):
                image_url = image_tag['src']
                image_urls.append(image_url)
                response = requests.get(image_url)
                image_data = response.content
                img_data_mongo.append({"index": image_url, "image": image_data})
                with open(os.path.join(save_dir, f"{query}_{i}.jpg"), "wb") as f:
                    f.write(image_data)
            client = pymongo.MongoClient(
                "mongodb+srv://imagescraping:imagescraping@cluster0.n5oi56f.mongodb.net/?retryWrites=true&w=majority")
            db = client['image_scrap']
            review_col = db['image_scrap_data']
            review_col.insert_many(img_data_mongo)
            driver.quit()
            return render_template("result.html", image_urls=image_urls)
        except Exception as e:
            return f"Something is Wrong: {str(e)}"
    else:
        return render_template("index.html")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
