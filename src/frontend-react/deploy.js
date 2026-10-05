require('dotenv').config();
const { S3Client, PutObjectCommand } = require('@aws-sdk/client-s3');
const fs = require('fs');
const path = require('path');
const mime = require('mime-types');

const s3Client = new S3Client({ region: process.env.AWS_REGION || "ap-southeast-1" });
const BUCKET_NAME = process.argv[2];

if (!BUCKET_NAME) {
    console.error("Usage: node deploy.js <your-s3-bucket-name>");
    process.exit(1);
}

const distPath = path.join(__dirname, 'dist');

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

console.log(`Deploying CloudFusion React App to AWS S3 Bucket: ${BUCKET_NAME}...`);
uploadDirectory(distPath).then(() => {
    console.log("Deployment Complete!");
    console.log(`Your app should now be live at: http://${BUCKET_NAME}.s3-website-${process.env.AWS_REGION || "ap-southeast-1"}.amazonaws.com/`);
});
