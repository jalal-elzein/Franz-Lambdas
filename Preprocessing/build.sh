#!/bin/bash

default_output_zip_filename="preprocessing.zip"

if [ $# -eq 0 ]; then
    output_zip_filename="$default_output_zip_filename"
else
    output_zip_filename="$1"
fi

mkdir preproc_package

cp lambda_function.py preproc_package/lambda_function.py

pip install pedalboard -t ./preproc_package

cd preproc_package && zip -r "../$output_zip_filename" .

cd ..
rm -rf preproc_package
