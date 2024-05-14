# 1. Create a new directory for the package
mkdir package
cd package/

# 2. Move the code to the directory
mv lambda_function.py package/lambda_function.py

# 3. Install dependencies into the local directory with `-t .`
pip3 install boto3 -t .
pip3 install --upgrade --force-reinstall "git+https://github.com/ytdl-org/youtube-dl.git" -t .

# 4. Create a zip folder of the code (create the deployment package itself)
cd package && zip -r ../lite-package-http.zip .

# 6. Upload deployment package to S3
aws s3 cp package.zip <s3 uri here>
