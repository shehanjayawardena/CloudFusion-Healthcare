require('dotenv').config();
const { S3Client, PutBucketWebsiteCommand, PutPublicAccessBlockCommand, PutBucketPolicyCommand } = require('@aws-sdk/client-s3');

const REGION = process.env.AWS_REGION || "ap-southeast-1";
const s3Client = new S3Client({ region: REGION });
const BUCKET_NAME = "cha-healthcare-prod-frontend";

async function makePublic() {
    try {
        console.log(`Configuring ${BUCKET_NAME} for Static Website Hosting...`);
        
        await s3Client.send(new PutBucketWebsiteCommand({
            Bucket: BUCKET_NAME,
            WebsiteConfiguration: { IndexDocument: { Suffix: "index.html" }, ErrorDocument: { Key: "index.html" } }
        }));
        
        console.log("Removing Public Access Blocks...");
        await s3Client.send(new PutPublicAccessBlockCommand({
            Bucket: BUCKET_NAME,
            PublicAccessBlockConfiguration: { BlockPublicAcls: false, IgnorePublicAcls: false, BlockPublicPolicy: false, RestrictPublicBuckets: false }
        }));
        
        // Wait a second for IAM to sync
        await new Promise(r => setTimeout(r, 2000));
        
        console.log("Applying Public Read Bucket Policy...");
        const policy = {
            Version: "2012-10-17",
            Statement: [{
                Sid: "PublicReadGetObject",
                Effect: "Allow",
                Principal: "*",
                Action: "s3:GetObject",
                Resource: `arn:aws:s3:::${BUCKET_NAME}/*`
            }]
        };
        await s3Client.send(new PutBucketPolicyCommand({
            Bucket: BUCKET_NAME,
            Policy: JSON.stringify(policy)
        }));
        
        console.log("Success! Bucket is now fully public and serving web traffic.");
        console.log(`Link: http://${BUCKET_NAME}.s3-website-${REGION}.amazonaws.com/`);
    } catch (err) {
        console.error("Error making bucket public:", err.message);
    }
}
makePublic();
