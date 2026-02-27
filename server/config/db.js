const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');

const connectDB = async () => {
    try {
        let uri = process.env.MONGODB_URI;

        // If local MongoDB isn't available, use in-memory server
        try {
            await mongoose.connect(uri, { serverSelectionTimeoutMS: 3000 });
            console.log(`✅ MongoDB Connected: ${mongoose.connection.host}`);
            return;
        } catch {
            console.log('⚠️  Local MongoDB not found. Starting in-memory MongoDB...');
        }

        // Start in-memory MongoDB
        const mongod = await MongoMemoryServer.create();
        uri = mongod.getUri();
        await mongoose.connect(uri);
        console.log(`✅ In-Memory MongoDB Connected (data will reset on restart)`);
    } catch (error) {
        console.error(`❌ MongoDB Connection Error: ${error.message}`);
        process.exit(1);
    }
};

module.exports = connectDB;
