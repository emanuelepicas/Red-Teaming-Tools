# fakeBlogGeneratorWithGPTAPI

This program generates a website automatically, more precisely, a blog utilizing the ChatGPT API (Model 3.5-turbo).
Services used: ChatGPT, Ninjas API, and https://this-person-does-not-exist.com/ (for retrieving profile images).
Therefore, you will need two API keys to excecute this program, one for chatGPT API and one for Ninjas API, documentation link below:

- ChatGPT API: https://platform.openai.com/account/api-keys
- Ninjas API: https://api-ninjas.com/api/randomimage

### Installing
- Clone or download the toolkit repo and navigate to this folder.
- Run `python3 -m pip install -r requirements.txt`.

### Usage


`python main.py "number_of_authors" "number_of_articles_for_each_author" "company_name" "company_sector_name" "blog_domain" "template_number(1/2)" "api_key_GPT" "api_key_Ninjas"`

**Example:** 
`python main.py 2 2 Microsoft security microsoft.com 1 sk-8adhoihsample bUtQa4GTU1sample`

All errors from ChatGPT responses and connection timeout issues should be handled. 
If not, just rerun the script; it will take less than 3/4 minutes in the worst-case scenario.

**Successful outcome:**

```
Copy from ~/fakeBlogGeneratorWithGPTAPI/commandLine/base_templates/template1/static to /tmp/site_builder_1/
The folder has been generated in /tmp
```

### How to deploy
- In the folder **nginx_configuration_utils**, there are sample configurations (**reveproxy.conf**) for nginx and two scripts available for moving the folder generated.
- Create a path (e.g., `/var/www/html/website`).
- Modify the `/etc/nginx/sites-enabled/revproxy.conf` file and edit the **location** parameter as follows:

```nginx
server {
	listen 90 default_server;
	listen [::]:90 default_server;

	root /var/www/html;

	server_name _;

	location / {
		root /var/www/html/website/site_builder_1; # for the template
		index index.html;
	}
}
```

- Execute either script 1 or 2 depending on the chosen template (**sudo script_template_1.sh**).

## Enjoy!