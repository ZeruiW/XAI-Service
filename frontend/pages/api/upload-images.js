import dbConnect from "../../lib/dbConnect";
import Image from "../../models/Image";
import { Storage } from '@google-cloud/storage'

export default async function handler(req, res) {
	const storage = new Storage({
		projectId: process.env.PROJECT_ID,
		credentials: {
			client_email: process.env.CLIENT_EMAIL,
			private_key: process.env.PRIVATE_KEY
		}
	})

	const bucket = storage.bucket(process.env.BUCKET_NAME)
	const file = bucket.file(req.query.file)
	const opts = {
		expires: Date.now() + 1 * 60 * 1000,
		fields: {'x-goog-meta-test': 'data'}
	}

	const [response] = await file.generateSignedPostPolicyV4(opts)
	res.status(200).json(response)

	// const { method } = req;

	// await dbConnect();

	// if (method === "POST") {
	// 	try {
	// 		const image = await Image.create(req.body);
	// 		res.status(201).json({ success: true, data: image });
	// 	} catch (err) {
	// 		res.status(400).json({ success: false });
	// 	}
	// } else {
	// 	res.status(400).json({ success: false });
	// }
}
