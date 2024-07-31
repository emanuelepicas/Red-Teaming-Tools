import sys
import subprocess
import os
from generators.authorsListChatGPT import generate_Authors
from generators.authorsIntroductionChatGPT import create_authors_with_retries
from generators.articleGeneratorChatGPT import generate_article_with_retries
from generators.introductionBlog import generate_introduction_blog
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from site_models import Site, Author, Post
from utils.builder_from_command_line import generate_Folder
from generators.images.imgutils import getImageArticle, getBannerImage
from constant.constant import db_string


def createSite(authors, articles, company_name, company_sector, blog_domain, template_number, api_key_GPT, api_key_ninjas):
    '''
    Creation of the entire website
    '''
    engine = create_engine(db_string)
    Session = sessionmaker(bind=engine)
    session = Session()
    print('Session Created')
    print('DB initialized')
    print(db_string)
    base = declarative_base()
    base.metadata.create_all(bind=engine)

    # Creation of the website entities model
    cs = Site()
    cs.name = company_name
    cs.template = template_number
    cs.description = generate_introduction_blog(
        company_name, company_sector, api_key_GPT)
    cs.domain = blog_domain
    session.add(cs)
    session.commit()
    session.refresh(cs)
    site_id = cs.id
    # Retriving the banner images for the html pages
    getBannerImage(template_number, api_key_ninjas)

    numbers_of_authors = authors

    # Creation of the author entities

    names = generate_Authors(company_sector, numbers_of_authors, api_key_GPT)
    print(names)
    for name in names:
        author = create_authors_with_retries(company_sector, name, api_key_GPT)
        print(author[0])
        print(author[1])
        print(author[2])
        print(author[3])
        cs = Author()
        cs.name = author[0]
        cs.site = site_id
        cs.age = author[2]
        cs.profession = author[1]
        cs.image = author[4]
        cs.bio = author[3]
        session.add(cs)
        session.commit()
        session.refresh(cs)
        author_id = cs.id
        for _ in range(articles):
            cs = Post()
            topic = company_sector
            article = generate_article_with_retries(topic, name, api_key_GPT)
            cs.name = name
            cs.site = site_id
            cs.posted = article[0]
            cs.title = article[2]
            cs.uri = article[3]
            cs.seo = article[4]
            cs.text = article[5]
            cs.author = author_id
            cs.image = getImageArticle(api_key_ninjas)
            session.add(cs)
            session.commit()

    generate_Folder(site_id)

    print('The folder has been generated in /tmp')


script_path = os.path.abspath(__file__)
script_filename = os.path.basename(script_path)


def display_help():
    print("Usage:")
    print(f'python {script_filename} "number_of_authors" "number_of_articles_for_each_author" "company_name" "company_sector_name" "blog_domain" "template_number(1/2)" "api_key_GPT" "api_key_Ninjas"')
    print(
        f'Example: python {script_filename} 2 2 Secura security secura1.com 1 sk-8adhoihSAMPLE bUtQa4GTU1SAMPLE')


if __name__ == "__main__":
    if len(sys.argv) != 9 or sys.argv[1] == "--help" or sys.argv[1] == "-h":
        display_help()
    else:
        try:

            command = ['python', 'site_models.py']
            output = subprocess.run(command, check=True)
            print("Database inizialized")

            if len(sys.argv) == 9:
                number_of_authors = int(sys.argv[1])
                number_of_articles = int(sys.argv[2])
                company_name = str(sys.argv[3])
                company_sector = str(sys.argv[4])
                blog_domain = str(sys.argv[5])
                template_number = str(sys.argv[6])
                api_key_GPT = str(sys.argv[7])
                api_key_ninjas = str(sys.argv[8])
            else:
                display_help()

            print(f'Number of authors: {number_of_authors}')
            print(f'Number of articles for each authors: {number_of_articles}')
            print(f'Company name: {company_name}')
            print(f'Company sector: {company_sector}')
            print(f'Blog domain: {blog_domain}')
            print(f'Template domain: {template_number}')

            if number_of_authors is None or number_of_articles is None or number_of_authors is None:
                display_help()

            createSite(number_of_authors, number_of_articles, company_name,
                       company_sector, blog_domain, template_number, api_key_GPT, api_key_ninjas)

        except ValueError:
            print(
                "Invalid input. Please provide valid integers for number_of_authors and number_of_articles.")
            display_help()
