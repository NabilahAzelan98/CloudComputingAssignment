from flask import Flask, render_template, request, redirect, url_for, flash, \
    Response, session, jsonify
from flask_bootstrap import Bootstrap
from filters import datetimeformat, file_type
from resources import get_bucket, get_buckets_list, _get_s3_resource, get_s3_client
from aws_controller import _get_dynamodb_client, _get_dynamodb_resource, get_table_list, get_table, get_session
from boto3.dynamodb.conditions import Key, Attr
import botocore.session
import logging


app = Flask(__name__,template_folder = 'template')
Bootstrap(app)
app.secret_key = 'secret'
app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['file_type'] = file_type

#------------ S3 settings ---------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")

@app.route('/s3home', methods=['GET', 'POST'])
def s3home():
    if request.method == 'POST':
        return redirect(url_for('bucket'))
    else:
        return render_template("index.html")


@app.route('/bucket', methods=['GET', 'POST'])
def bucket():
    if request.method == 'POST':
        bucket = request.form['bucket']
        session['bucket'] = bucket
        return redirect(url_for('files'))
    else:
        buckets = get_buckets_list()
        return render_template("bucket.html", buckets=buckets)


@app.route('/files')
def files():
    my_bucket = get_bucket()
    summaries = my_bucket.objects.all()

    return render_template('files.html', my_bucket=my_bucket, files=summaries)


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']

    my_bucket = get_bucket()
    my_bucket.Object(file.filename).put(Body=file)

    flash('File uploaded successfully')
    return redirect(url_for('files'))


@app.route('/delete', methods=['POST'])
def delete():
    key = request.form['key']

    my_bucket = get_bucket()
    my_bucket.Object(key).delete()

    flash('File deleted successfully')
    return redirect(url_for('files'))


@app.route('/create', methods=['POST'])
def create():
    name = request.form['buck_name']

    my_bucket = get_s3_client()
    my_bucket.create_bucket(
       ACL='public-read-write',
       Bucket=name,
       CreateBucketConfiguration={ 'LocationConstraint': 'ap-southeast-1'}
    )

    flash('Bucket created successfully')
    return redirect(url_for('bucket'))


@app.route('/deletebucket', methods=['POST'])
def deletebucket():
    name = request.form['bucket']

    my_bucket = _get_s3_resource()
    my_bucket.Bucket(name).delete()

    flash('Bucket deleted succesfully')
    return redirect(url_for('bucket'))


@app.route('/download', methods=['POST'])
def download():
    key = request.form['key']

    my_bucket = get_bucket()
    file_obj = my_bucket.Object(key).get()

    return Response(
        file_obj['Body'].read(),
        mimetype='text/plain',
        headers={"Content-Disposition": "attachment;filename={}".format(key)}
    )

#------------ DynamoDB settings ---------------------
@app.route('/dynamodb', methods=['GET', 'POST'])
def dynamodb():
        tables = get_table_list()
        return render_template("dynamodb.html", tables=tables)

@app.route('/create_table', methods=['POST'])
def create_table():
    Table_Name = request.form['Tablename']
    my_table = _get_dynamodb_client()
    my_table.create_table(
    TableName=Table_Name,
    KeySchema=[
    {
    'AttributeName': 'ID',
    'KeyType': 'HASH'
    },
    {
    'AttributeName': 'Type',
    'KeyType': 'RANGE'
    },
    ],
    AttributeDefinitions=[
    {
    'AttributeName': 'ID',
    'AttributeType': 'S'
    },
    {
    'AttributeName': 'Type',
    'AttributeType': 'S'
    },
    ],
    ProvisionedThroughput={
    'ReadCapacityUnits': 5,
    'WriteCapacityUnits': 5
    }
    )

    flash("Table Created!")
    return redirect(url_for('dynamodb'))


@app.route('/put_item', methods=['GET','POST'])
def put_item():
    id = request.form['ID']
    Model = request.form['model']

    client = _get_dynamodb_client()
    client.put_item(
    TableName='smartphone',
        Item={
            'ID': {'S': id},
            'Type':{'S':Model}
            }
            )
    flash('Items Inserted')
    return redirect(url_for('attribute'))


@app.route('/query_item', methods=['GET','POST'])
def query_item():
    name = request.form['info']
    client = _get_dynamodb_resource()
    table = client.Table('smartphone')
    response = table.query(
    KeyConditionExpression=Key('ID').eq(name)
        )
    items = response['Items']
    return  render_template('query_item.html', items=items)


@app.route('/attribute', methods=['GET','POST'])
def attribute():
    name = get_session()
    table_name = request.form['table']
    client = _get_dynamodb_resource()
    table = client.Table(table_name)

    response = table.scan()
    items=response['Items']
    return  render_template('items.html', items=items, table=name)

# -------- MAIN -------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
