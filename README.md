# Franz Lambdas 
This repository holds the code for all the AWS Lambda Functions that [Franz](https://github.com/mahmoudjlb/franz) utilizes

# Download 

# Conversion 

# Preprocessing 
The preprocessing script is quite simple, and therefore, we use a zipped deployment package approach for it. 
## Dependencies 
`boto3` & `pedalboard`
## Updating 
1. Create the zip package with a unique name
```sh
bash build.sh preprocessing-x.zip
```
2. Upload the deployment package to S3
```sh
aws s3 cp preprocessing-x.zip s3://franz-lambda-deployments/preprocessing-x.zip
```
3. Switch the code source of the function in the AWS Management Console
# Transcription 
