# AwesomeCure
Analyze and cure awesome lists by mining data from listed Git projects.

Awesome lists play a central role within an open source ecosystem by providing an index to the various open source domains. Without this infrastructure, it would be impossible for newcomers to find out what tools, frameworks, data and communities exist. Maintaining an Awesome List requires removing inactive projects on a regular basis. Without these measures, new and still active projects get lost in the multitude of inactive projects. At the same time, they help to concentrate open source resources on active projects instead of reinventing the wheel over and over again.

AwesomeCure provides simple tools to analyze Git projects within an Awesome list and get an overview of the represented open source ecosystem. It uses the GitHub API to retrieve project metadata and generate various metrics about the state of the project. As a result, a CSV is created to sort and analyze the listed projects according to the different criteria. 

## Install

First, you need to clone the GitHub-Repo. Do something like:

```git clone git@github.com:protontypes/AwesomeCure.git

Then, you need to install jupiter notebook:
(for example via pip)

```pip install jupyterlab
```pip install notebook

Then, add a `.env with your persoal git hub token
https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token

then run ```jupyter notebook

and there you go :)
