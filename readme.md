![](https://s3-ap-southeast-1.amazonaws.com/fibo-resources/hacknight1.jpg)

# AWS Mongolian Community-д тавтай морилно уу!
### Доорх ойлголтуудыг нэгтгэж Text-to-Speech simple project хийх болно.
- AWS Lambda
- Python programming language (AWS boto library)
- AWS S3 static web site hosting
- AWS API Gateway
- AWS Dynamo DB
- AWS Polly service

![](https://s3-ap-southeast-1.amazonaws.com/fibo-resources/hacknight1-topology.png)

### 1. AWS account үүсгэх

[Youtube video](https://www.youtube.com/watch?v=dfbc1SoWRD0&fbclid=IwAR1FGuNsbnGQHd2CXZScfcusx_PGIz8Sy21nIYzEAD-7Z7JRKe2exhYFYUs)

### 2. Region сонгох
2019 оны I сарын байдлаар AWS 16 ширхэг public region-той байна. Өнөөдөр hacknight-р бид **Tokyo** region дээр ажиллах болно.  

### 3. Create DynamoDB table
>**Table name:** posts
**primary key:** id (String) - Lowercase!

### 4. Create 2 buckets
Bucket name must be globally unique!
Өөрсдийн нэрээр нэрлэнэ үү.
- **Bucket #1**: mnhacknight-web  (web ажиллах bucket, domain холбох бол  **www.jiguur001.tk**)
- **Bucket #2**: mnhacknight-mp3  (mp3 file хадгалах bucket)

>Make them public

### 5. Create a role for Lambda
#### 5.1. Create a policy
>**Name**: LambdaPolicyForHacknightV1
**Type**: JSON
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "polly:SynthesizeSpeech",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "sns:Publish",
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:GetBucketLocation",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": [
        "*"
      ]
    }
  ]
}
```

#### 5.2. Create a Role using policy
>**Name**: LambdaRoleForHacknightV1
**Choose existing role**: LambdaPolicyForHacknightV1

### 6. Create Lambda functions from scratch
#### 6.1. HacknightV1_NewText (Name)
**Зориулалт**
- Орж ирсэн текстийг DynamoDB лүү хадгална
- DynamoDB-с түүнийгээ select хийж Polly service ашиглан mp3 болгоно
- mp3 болгосон file-г S3 bucket дотор хадгална

>**Python 2.7**
**Choose an existing role:** LambdaRoleForHacknightV1

Use the file name: **newtext.py**

- **Add environment variables**
DB_TABLE_NAME: posts
BUCKET_NAME: mnhacknight-mp3 (Section 4)
- **Add description**
- **Set time-out to 5 mins**
- **Test Hello World**
```
{
    "voice": "Joanna",
    "text": "Hello Amazon Web Services Mongolian Community!"
}
```
- **Check DynamoDB table**

#### 6.2. HacknightV1_GetText (Name)
**Зориулалт:** DynamoDB-с утгуудыг query-дэнэ

>**Python 2.7**
**Choose an existing role:** LambdaRoleForHacknightV1

Use the file name: **gettext.py**

- **Add environment variables**
DB_TABLE_NAME: posts
- **Add function description**
- **Set time-ut to 5 secs**
- **Test Hello World**
```
{
 	"postId": "*"
}
```

### 7. Create API Gateway
**Name:** HacknightV1API

- Add GET Method
Integration type: Lambda function 
Target: **HacknightV1_GetText**
Get request-ийн URL-с параметер авахын тулд Mapping хийж өгөх ёстой
Integration request -> Body Mapping Templates -> When there are no templates defined -> application/json гэж бичиж оруулна
```
{
    "postId": "$input.params('postId')"
}
```

- Add POST Method
Integration type: Lambda function 
Target: **HacknightV1_NewText**

- Click Action -> Enable CORS -> Hit Enable CORS
- Deploy API 
Deployment stage: **[new stage]**
other fields all **prod**
- Click stage -> prod -> Invoke URL copy-дож авна

### 8. Replace API URL
scripts.js хамгийн дээр хуулна
### 9. Make static website hosting
Add 2 following files.
>index.html
error.html

Add policy:
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::REPLACE_BUCKET_NAME_HERE/*"
    }
  ]
}
```
Then try deleting **index.html**
### 10. Upload web files to our bucket
> index.html
scripts.js
styles.css

Select all show dummy data, then delete it from DynamoDB





