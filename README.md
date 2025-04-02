# ice-cat-wrangler
Timed interview test

A serverless REST API that identifies whether an uploaded image contains a cat

ICE cat-wrangler solution

Choice of several AWS image classification software. The most appropriate seem to be

1.  Rekognition
2. Amazon SageMaker AI Canvas

Rekognition seems more appropriate because cat classification is a ready made model.

Sagemaker allows more granular control and the option of reduced operation costs which comes with the disadvantage of increased engineer time.

As this is a MVP, it makes sense to use Rekognition as it can already classify the model and we do not know as of yet the volume of requests the cat-wrangler service will take.

We also will have the option to swap out the classification backend to something more performant later on once we have set up the infrastructure and interfaces that handle ingestion and image storage.



## considerations
1. internal tool – not public facing
2. speed is not of the utmost importance at this stage – (bypass s3 and use raw bytes to improve speed)
3. use for devs to upload files from their laptops
4. possible feature to bulk load files
5. need to figure out s3 storage structure
6. minimum of 3 endpoints
	a) submit image
	b) list all results for all ids – (with/without debug data)
	c) get specific result
	d) health -check
7. would need database to store images. Perhaps dynamodb is cheaper for small projects? Maybe need a cleaner to keep size small. https://www.qa.com/resources/blog/amazon-rds-vs-dynamodb-12-differences/


## Requirements

1) python 3.?
2) serverless
    - needs nvm
    - needs nodejs version ???

### Install nvm, node & serverless framework
```
curl https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash
source ~/.profile

nvm ls-remote # find latest 18.x version of nodejs
nvm install v18.20.8
nvm use v18.20.8
nvm alias default v18.20.8

npm i serverless -g
serverless
serverless update
```