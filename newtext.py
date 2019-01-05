import boto3
import os
import uuid
from contextlib import closing
from boto3.dynamodb.conditions import Key, Attr
def lambda_handler(event, context):
    recordId = str(uuid.uuid4()) # Generating new unique ID
    voice = event["voice"] # Getting voice person
    text = event["text"] # Getting text to speech
    # Adding a new record in DynamoDB table
    dynamodb = boto3.resource('dynamodb') # Creating dynamo DB instance
    table = dynamodb.Table(os.environ['DB_TABLE_NAME']) # Creating table instance
    # Adding a new item
    table.put_item(
        Item={
            'id' : recordId,
            'text' : text,
            'voice' : voice,
            'status' : 'PROCESSING'
        }
    )
    print "Successfully added a new record on DynamoDB table with id: " + recordId
    #Retrieving information about the post from DynamoDB table
    postItem = table.query(
        KeyConditionExpression=Key('id').eq(recordId)
    )
    text = postItem["Items"][0]["text"]
    voice = postItem["Items"][0]["voice"] 
    rest = text
    # polly api deed tal n 1500 character process hiideg, then we should trim it
    textBlocks = []
    while (len(rest) > 1100):
        begin = 0
        end = rest.find(".", 1000)
        if (end == -1):
            end = rest.find(" ", 1000)
        textBlock = rest[begin:end]
        rest = rest[end:]
        textBlocks.append(textBlock)
    textBlocks.append(rest)            
    #For each block
    polly = boto3.client('polly') # Creating polly instance
    for textBlock in textBlocks: 
        response = polly.synthesize_speech(
            OutputFormat='mp3',
            Text = textBlock,
            VoiceId = voice
        )
        #Save the audio stream returned by Amazon Polly on Lambda's temp 
        # directory. If there are multiple text blocks, the audio stream
        # will be combined into a single file.
        if "AudioStream" in response:
            with closing(response["AudioStream"]) as stream:
                output = os.path.join("/tmp/", recordId)
                with open(output, "a") as file:
                    file.write(stream.read())
    # Saving to s3 bucket
    s3 = boto3.client('s3') # boto s3 instance
    s3.upload_file('/tmp/' + recordId, 
      os.environ['BUCKET_NAME'], 
      recordId + ".mp3")
    s3.put_object_acl(ACL='public-read', 
      Bucket=os.environ['BUCKET_NAME'], 
      Key= recordId + ".mp3")
    location = s3.get_bucket_location(Bucket=os.environ['BUCKET_NAME'])
    region = location['LocationConstraint']
    if region is None:
        url_begining = "https://s3.amazonaws.com/"
    else:
        url_begining = "https://s3-" + str(region) + ".amazonaws.com/" \
        
    url = url_begining \
            + str(os.environ['BUCKET_NAME']) \
            + "/" \
            + str(recordId) \
            + ".mp3"
    #Updating status in DynamoDB
    response = table.update_item(
        Key={'id':recordId},
          UpdateExpression=
            "SET #statusAtt = :statusValue, #urlAtt = :urlValue",                   
          ExpressionAttributeValues=
            {':statusValue': 'UPDATED', ':urlValue': url},
        ExpressionAttributeNames=
          {'#statusAtt': 'status', '#urlAtt': 'url'},
    )
    return recordId