# AwesomeCure
>  Analyze and cure awesome lists by collecting, processing and presenting data from listed Git projects.

 [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/protontypes/AwesomeCure.git/HEAD)

AwesomeCure provides basic scripts to analyze Git projects within an Awesome list getting an overview of the represented open source domains. Use the GitHub API to retrieve meta data and generate various metrics about the state of open source ecosystems. As a result, spreadsheets and plots are created to sort and analyze all entries according to you needs. 

## Background

Awesome lists are a central part of the open source ecosystem. They allow developers to get an overview of open source projects in different domains. A state of the art cross-platform search engine for open source projects does not yet exist. Therefore, those lists represent central indexes for the diverse open source communities. Interfaces can be created between projects, development resources are concentrated and the wheel is not reinvented again and again.

Maintaining an Awesome list requires removing inactive projects on a regular basis, investigating new projects and engaging the community to update the list. Without these measures, new and still active projects get lost in the multitude of inactive projects. The processing of such list gives the possibility to analyze these ecosystems with the help of data science methods in order to identify potentials and risks within the domain. 

## Application
The [OpenSustain.tech](https://opensustain.tech/) website is based on such an Awesome list, giving an overview of the active open source projects in climate and sustainable technology. In the current prototype project state, AwesomeCure can only be applied to this list, but generalization to all Awesome lists is possible.

Most of the entries are linked to GitHub or GitLab repository of the underlying project. Therefore, AwesomeCure is able to analyze every project via the platform API to extract meta data from the listed projects. In this way, various health indicators are extracted like:

* Last activity
* Community Distribution Score ( How much does the project depend on a single person)
* Number of reviews per pull request
* Days until the last commit and last closed issue
* Total number of stars, contributors
* Use licenses 
* Any many more...

## Install

Clone the GitHub repository:

```
git clone git@github.com:protontypes/AwesomeCure.git
```

Install Jupiter notebook:

```
pip install jupyterlab
pip install notebook
```

Install the dependencies:

```
cd AwesomeCure
pip install -r requirements.txt   
```

Add a `.env` with your personal GitHub token to the root project folder (see more information on that [here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)).  Give the API key the minimum number of permissions. The `.env` file is excluded from version control by the .gitignore file and in this way not uploaded to GitHub. Open the .env file with your favored editor and add 
```
GITHUB=Your_API_Key
```

Run the Jupyter Notebook
```
jupyter notebook
```
A browser window should open, if not, click (or copy paste) the link from your terminal output.

## Architecture

The project was split into two Jupyter notebooks.  One for data acquisition and one for data processing and plotting. 

### Data Acquisition

The [AwesomeCure.ipynb](./awesomecure.ipynb) notebook lets you read the Awesome list from any repository. Depending on the size of the list the processing can take multiple hours.

![AwesomeCure](./docs/AwesomeCure.png)

### Data Processing

Data processing is done in the [ost_analysis.ipynb](ost_analysis.ipynb) with the output csv files form the data acquisition. Since not API key is needed for this step the processing can also been done online within Binder:

 [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/protontypes/AwesomeCure.git/HEAD)

![OST_Analysis](./docs/OST_Analysis.png)

## Results
Plotting the dataset gives insides into the Open Source Ecosystems from different perspectives. 

### Programming Languages 

![programming_languages](./docs/programming_languages.png)

### Project Scores 

![Score_example_plot](./docs/Score_example_plot.png)


### Communities and Organizations 

![organizations](./docs/organizations.png)

![organizations_forms](./docs/organizations_forms.png)

## An extended Poetry's command-line interface by developing plugins as an alternative to Jupyter Notebooks

##### Usage:

From an integrated terminal, the plugin needs to depend on Poetry to interface with it, so we can run the following commands:

```
poetry install
```

If it's needed, we can use poetry or pip to install the command-line interface:

```
poetry add open-sustain-tech
```

or,

```
pip install open-sustain-tech
```

To run the plugin, we can use the following command:

```
oss-opt
```
or, commonly to poetry and python:

```
poetry run python -m open_sustain_tech
```

or,

```
poetry run oss-opt
```

As described in the `protontypes/AwesomeCure` under the `README.md` file, and under the `Architecture` section in reference to the `Data Acquisition`, the `oss-opt` command-line interface lets read the Awesome list from any repository as well.

**Note:** Depending on the size of the list, the processing can take multiple hours.

This is an update to the open_sustain_tech command-line interface, and here are the main changes to consider regarding this update:

- The OpenSustainTech class is a subclass of the Command class from the cleo library. It has a handle method that is used to handle the command when the user executes it. The factory function is a simple function that creates and returns an instance of the OpenSustainTech class. This function is used as a "factory" for creating OpenSustainTech instances.

- The Options class is a data class (thanks to the @dataclass decorator) that contains options for the command-line parser. It uses the simple_parsing library to define the options and their default values.

- An ArgumentParser object is created and configured to use the options defined in the Options class. The command-line arguments are then parsed and stored in the args variable.

- The OSSOptionPlugin class is a subclass of ApplicationPlugin from the poetry library. It has an activate method that is used to register the open_sustain_tech command with the application. It also has a commands property that returns a list of available commands, in this case, an instance of OpenSustainTech.

## Many thanks to:
Tobias Augspurger 
