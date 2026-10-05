require('dotenv').config();
const { S3Client, PutObjectCommand, CreateBucketCommand, HeadBucketCommand } = require('@aws-sdk/client-s3');
const fs = require('fs');
const path = require('path');
const mime = require('mime-types');

const REGION = process.env.AWS_REGION || "ap-southeast-1";
const s3Client = new S3Client({ region: REGION });
const BUCKET_NAME = process.argv[2];

if (!BUCKET_NAME) {
    console.error("Usage: node deploy.cjs <your-s3-bucket-name>");
    process.exit(1);
}

const distPath = path.join(__dirname, 'dist');

async function ensureBucketExists() {
    try {
        await s3Client.send(new HeadBucketCommand({ Bucket: BUCKET_NAME }));
        console.log(`Bucket ${BUCKET_NAME} already exists.`);
    } catch (err) {
        if (err.name === 'NotFound' || err.$metadata?.httpStatusCode === 404) {
            console.log(`Bucket ${BUCKET_NAME} not found. Creating it...`);
            await s3Client.send(new CreateBucketCommand({
                Bucket: BUCKET_NAME,
                CreateBucketConfiguration: { LocationConstraint: REGION }
            }));
            console.log(`Bucket ${BUCKET_NAME} created successfully.`);
            // Note: Making it a public website bucket requires multiple other commands (PublicAccessBlock, BucketPolicy, WebsiteConfig).
            // For this automated script, we assume the bucket is configured or we just upload the files.
        } else {
            console.error("Error checking bucket:", err.message);
        }
    }
}

async function uploadDirectory(dirPath, s3Prefix = '') {
    if (!fs.existsSync(dirPath)) {
        console.error("Dist folder not found. Please run 'npm run build' first.");
        return;
    }
    
    const entries = fs.readdirSync(dirPath, { withFileTypes: true });

    for (const entry of entries) {
        const fullPath = path.join(dirPath, entry.name);
        const s3Key = s3Prefix ? `${s3Prefix}/${entry.name}` : entry.name;

        if (entry.isDirectory()) {
            await uploadDirectory(fullPath, s3Key);
        } else {
            const fileStream = fs.createReadStream(fullPath);
            const contentType = mime.lookup(fullPath) || 'application/octet-stream';
            
            try {
                await s3Client.send(new PutObjectCommand({
                    Bucket: BUCKET_NAME,
                    Key: s3Key,
                    Body: fileStream,
                    ContentType: contentType
                }));
                console.log(`Uploaded: ${s3Key}`);
            } catch (err) {
                console.error(`Failed to upload ${s3Key}:`, err.message);
            }
        }
    }
}

async function run() {
    console.log(`Deploying CloudFusion React App to AWS S3 Bucket: ${BUCKET_NAME}...`);
    await ensureBucketExists();
    await uploadDirectory(distPath);
    console.log("Deployment Complete!");
    console.log(`Your app files are now live in S3!`);
}

run();
