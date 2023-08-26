# BloggingGPT

This is a beta of beta of beta. Can write good articles but that's it for now. It's in dev. 

Without SearchGPT, an article cost is around $1 and +/- 6k words.

With SearchGPT, an article cost is around $1.5 and +/- 6k words.

If you want to test it, create .env file, add all APIs (you can ignore WOLFRAM_ALPHA_APPID="" for now) and run main.py.

Blog example: https://iminsweden.com

## Update 26/08/2023

You need to add your login details for WP to .env and then add details about your blog to blogs/blogs.toml. You can add as many blogs as you want. The app will ask you which one you want to update.

If you want to use Midjorney you need to add 3rd party API key to enhancer/midjourney_ai.py

You can get it at [thenextleg.io](https://www.thenextleg.io/)

In blogs.toml, try to add as much info as possible. Long descriptions are better.

Default settings is 15 articles. If you want more in one go, go to orchestrar/blog.py and change the number in prompt. Don't forget to change the prompt for both keywords scenarios.
