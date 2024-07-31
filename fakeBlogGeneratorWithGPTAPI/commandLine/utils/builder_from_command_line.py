from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from constant.constant import db_string
from site_models import Site
from utils.builder import BuilderProject
import sys
sys.path.append('../../')


def generate_Folder(site_id):

    engine = create_engine(db_string)
    Session = sessionmaker(bind=engine)
    session = Session()
    print(site_id)
    get_site_data = session.query(Site).filter(Site.id == site_id).first()
    data = get_site_data
    print(get_site_data)
    BuilderProject(data).copy_static_template_data()
    BuilderProject(data).render_post_list_GPT()
    BuilderProject(data).render_posts_GPT()
    BuilderProject(data).render_authors_GPT()
    BuilderProject(data).build_htaccess()

