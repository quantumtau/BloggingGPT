from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from dotenv import load_dotenv
from config import Config

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Load the .env file
load_dotenv()

# Configure OpenAI API key
cfg = Config()

def post_to_wordpress(title, content, category, tags):
    wp_url = cfg.site_url
    wp_username = cfg.wp_admin_username
    wp_password = cfg.wp_admin_password
    wp_blogid = ""

    wp = Client(wp_url, wp_username, wp_password)

    post = WordPressPost()
    post.title = title
    post.content = content
    post.terms_names = {
        'category': [category],
        'post_tag': tags
    }
    post.post_status = 'draft'  # Set the status of the new post.

    wp.call(NewPost(post))