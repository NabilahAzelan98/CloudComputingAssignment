from flask import Flask, session
import boto3
import time

#setup a session for boto3 to connect to dynamo.  You need to change the region to the region your Dynamo is in.
dynamo_client = boto3.Session(region_name='ap-southeast-1').client('dynamodb')

def _get_dynamodb_client():
    return boto3.client('dynamodb')

def _get_dynamodb_resource():
    return boto3.resource('dynamodb')

def get_table_list():
    client = _get_dynamodb_client()
    return client.list_tables().get('TableNames')

def describe_table():
    client = _get_dynamodb_client()
    return client.describe_table().get('TableNames')


def get_session():
    dynamo_client = boto3.Session(region_name='ap-southeast-1').client('dynamodb')
    return dynamo_client

def get_table():
    s3_resource = _get_s3_resource()
    if 'table' in session:
        bucket = session['table']
    else:
        bucket = S3_BUCKET
#This first function get_all() will return all rows from the table in the table variable.
#I would certainly make this an argument in future revisions.
#Only the table variable would need to change to match the table you wish to read.
def get_all():
    response = _get_dynamodb_client()
    table='users'
    return response.scan(TableName=table)

#This code is here just to initalize your table.  This code will create a DynamoDB named per the variable in the function
#Again this should probably be made into an argument
#You only are required to setup the keys for your table

#put_item() is here to add a single generic row to your table.  I only have this here for demo purposes
#You could certainly alter this to pass one row of data into the table from your application
def put_item():
    dynamo_client.put_item(
    TableName='smartphone',
    Item={
        'ID': {'S': 'MWHM2X/A'},
        'Type': {'S': 'iPhone 11 Pro Max'}
    }
)

#This function allows you to retrieve a single item from your table (set in the variable)
#This would certainly be done with arguments for your tablename and filtered item
def get_item():
    table='bobTable'
    item='1942Casablanca'
    response = dynamo_client.get_item(
    Key={
        'event': {'S': item}
    },
    TableName=table  #could pass this value in as well to manage multiple tables
    )
    return response
