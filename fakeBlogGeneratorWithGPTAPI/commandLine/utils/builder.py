"""
Main class for building websites
"""
from site_models import Site
import re
from jinja2 import Environment, FileSystemLoader
import hashlib
import shutil
import tempfile
import os
import sys
sys.path.append('../')


class BuilderProject:
    site_data: Site = None
    template_path: str = None
    create_new: str = None

    def __init__(self, site: Site):
        self.site_data = site
        get_template_path = os.path.join(
            os.path.dirname(
                __file__), "../", "base_templates", "template%s" % self.site_data.template
        )
        self.template_path = os.path.abspath(get_template_path)
        path = tempfile.gettempdir()
        self.create_new = os.path.join(
            path, "site_builder_%s%s" % (self.site_data.template, os.path.sep)
        )

    def init_directory(self):
        if not os.path.exists(self.create_new):
            os.mkdir(self.create_new)
        return self.create_new

    def copy_and_overwrite(self, from_path, to_path):
        if os.path.exists(to_path):
            shutil.rmtree(to_path)
        shutil.copytree(from_path, to_path)

    def copy_static_template_data(self):
        get_static = os.path.join(self.template_path, "static")
        get_dst = self.init_directory()
        print("Copy from %s; to %s" % (get_static, get_dst))
        self.copy_and_overwrite(get_static, get_dst)

    def get_combined_data(self):
        output = {
            "posts": {},
            "authors": {},
            "details": {},
            "site": self.site_data.readable()
        }
        for author in self.site_data.authors:
            author_data = author.readable()
            output["authors"][author_data["id"]] = author_data
        for post in self.site_data.posts:
            post_data = post.readable()
            output["posts"][post_data["id"]] = post_data
        for site_var in self.site_data.variables:
            output["details"][site_var.key] = site_var.value
        hl = hashlib.sha1()
        for rand_x in range(25):
            hl.update(os.urandom(24))
            output["details"].update({
                "random_%d" % rand_x: hl.hexdigest()
            })
        return output

    def replace_background_images(self, file_path):
        # Define the pattern to search for
        pattern = r'style="background-image: url\((.*?)\);"'

        # Define the replacement text
        replacement = 'style="background-color: url(/images/bannerImage.png);"'

        # Read the content of the file
        with open(file_path, 'r') as f:
            file_content = f.read()

        # Use regex to find and replace the pattern in the file content
        modified_content = re.sub(pattern, replacement, file_content)

        # Write the modified content back to the file
        with open(file_path, 'w') as f:
            f.write(modified_content)

    def render_post_list_GPT(self):
        gcd = self.get_combined_data()
        get_index_template = os.path.join(self.template_path, "index.html")
        get_posts_dir = os.path.join(self.create_new, "posts")
        if not os.path.exists(get_posts_dir):
            os.mkdir(get_posts_dir)

        # Initialize Jinja2 environment
        env = Environment(loader=FileSystemLoader(self.template_path))
        template = env.get_template("index.html")
        rendered_template = template.render(site=gcd)

        target_file = os.path.join(self.create_new, "index.html")

        # self.replace_background_images(target_file)

        with open(target_file, "w") as wf:
            wf.write(rendered_template)

            return rendered_template

    def render_posts_GPT(self):
        gcd = self.get_combined_data()
        get_post_template = os.path.join(self.template_path, "post.html")

        # Initialize Jinja2 environment
        env = Environment(loader=FileSystemLoader(self.template_path))
        template = env.get_template("post.html")

        for post_id, post_data in gcd['posts'].items():
            rendered_template = template.render(site=gcd, post=post_data)
            target_file = os.path.join(
                self.create_new, "posts", "%s.html" % post_data['uri'])
            # self.replace_background_images(target_file)
            with open(target_file, "w") as wf:
                wf.write(rendered_template)

        return True

    def render_authors_GPT(self):
        gcd = self.get_combined_data()
        get_author_template = os.path.join(self.template_path, "author.html")
        get_authors_dir = os.path.join(self.create_new, "authors")
        if not os.path.exists(get_authors_dir):
            os.mkdir(get_authors_dir)

        # Initialize Jinja2 environment
        env = Environment(loader=FileSystemLoader(self.template_path))
        template = env.get_template("author.html")

        for author_id, author_data in gcd['authors'].items():
            rendered_template = template.render(site=gcd, author=author_data)
            target_file = os.path.join(
                self.create_new, "authors", "%s.html" % author_data['id'])
            # self.replace_background_images(target_file)
            with open(target_file, "w") as wf:
                wf.write(rendered_template)

        return True

    def build_htaccess(self):
        gcd = self.get_combined_data()
        if gcd['details'].get("use_rewrite", None):

            htaccess_body = """
RewriteEngine on


RewriteCond %{THE_REQUEST} /([^.]+)\\.html [NC]
RewriteRule ^ /%1 [NC,L,R]

RewriteCond %{REQUEST_FILENAME}.html -f
RewriteRule ^ %{REQUEST_URI}.html [NC,L]"""
            get_htaccess = os.path.join(self.create_new, ".htaccess")
            with open(get_htaccess, "w") as f:
                f.write(htaccess_body)

        if not gcd['details'].get("allow_indexing", None):
            htaccess_body = """User-agent: *
            Disallow: /
            """
            get_htaccess = os.path.join(self.create_new, "robots.txt")
            with open(get_htaccess, "w") as f:
                f.write(htaccess_body)

