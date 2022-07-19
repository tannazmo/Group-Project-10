# Analysis of adverse reaction of FDA Approved medicine ATORVASTATIN

## Presentation

This project will be a supervised machine learning of Classification type. 

### Content

#### Selected topic 
Taking the most prescribed drug, Atorvastatin, leading to hospitatlization and death.


#### Reason why they selected their topic 
To be able to predict the incidences of hospitalisation or death based on an adverse effect dataset from FDA.

We wanted to work with a real-world dataset, and from this data set, we could ask and answer a question about an important question that could be anyone's question and concern, no matter where in the world they live or what in the world they do. 

#### Description of their source of data 
This is a dataset provided by the FDA based upon submissions by medical professionals about medications and their effect (adverse effect) on those who take them.
It is important to mention that our datasource is limited to the reported cases.

#### Questions they hope to answer with the data
The question to answer is the likelihood of getting hospitalised or dying if experiencing any side effects by taking this medication. Using a supervised machine learning classificaion method, we want to be able to predict, -by looking at the age, gender, adverse reactions, drug indication- whether the patient will have serious reactions to Atorvastatin leading to  hospitalisation or not and whether they will have very serious reactions that may cause death or not. 

![Machine_Learning_model](Resources/Model.png "Machine Learning Model diagram")


#### Technologies, languages, tools, and algorithms used throughout the project
* Data in the format of JSON retrieved from FDA Website using API, then converted to CSV, then stored to Amazon S3
* Python files to run on Google Colab will be using Pandas and PySpark libraries.
* The cleaned data will be loaded in a PostgreSQL on AWS.
* Data will be processed with a superised machine learning model potentially Neural Networks.
* Presentation Slides on Google Slides 
* For visualisation, we will have an interactive Tableau dashboard.

