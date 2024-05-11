mkdir preproc_package

cp lambda_function.py preproc_package/lambda_function.py

pip install pedalboard -t ./preproc_package

cd preproc_package && zip -r ../preprocessing.zip .