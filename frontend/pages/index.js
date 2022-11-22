// index.js

// deps and funcs
import { useState } from "react";

// components
import Head from "next/head";
import DashboardLayout from "../layouts/dashboard";

export default function Index() {
	const [images, setImages] = useState({});
	const [imgGrp, setImgGrp] = useState(0);
	const [labelMap, setLabelMap] = useState(null);

	const handleSelectImages = async (e) => {
		setImages(e.target.files[0]);
		// Object.keys(e.target.files).map((key, idx) => {
		// 	setImages([...images, e.target.files[key]]);
		// });
	};

	const uploadPhoto = async (e) => {
		e.preventDefault();

		console.log(await fetch("/img_name_label.csv"));

		// Object?.keys(images).map(async (key, idx) => {
		// 	const file = images[key];
		// 	const filename = encodeURIComponent(file.name);
		// 	const res = await fetch(process.env.IMG_UPLOAD_DB);
		// 	const { url, fields } = await res.json();

		// 	const formData = new FormData();
		// 	const img_label_map = await fetch("/img_name_label.csv");
		// 	{
		// 		console.log(img_label_map);
		// 	}
		// 	const img_group = `t${imgGrp}`;

		// 	formData.append("imgs", {});

		// 	Object?.entries({ ...fields, file }).forEach(([key, value]) => {
		// 		formData.imgs.append(key, value);
		// 	});

		// 	formData.append("img_label_map", img_label_map);
		// 	formData.append("img_group", img_group);

		// 	const upload = await fetch(url, {
		// 		headers: {
		// 			"Content-Type": "multipart/formdata",
		// 		},
		// 		method: "POST",
		// 		body: formData,
		// 	});

		// 	if (upload.ok) {
		// 		window.alert("Upload success.");
		// 	} else {
		// 		console.error("Upload failed.");
		// 	}
		// });

		const file = images[0];
		const img_name_label = await fetch("img_name_label.csv");
		const formData = new FormData();
		const img_group = `t${imgGrp}`;

		formData.append("imgs", file);
		formData.append("img_name_label", img_name_label);
		formData.append("img_group", img_group);

		const upload = await fetch(process.env.IMG_UPLOAD_DB, {
			headers: {
				"Access-Control-Allow-Origin": "*",
			},
			method: "POST",
			body: formData,
		});

		if (upload.ok) {
			console.log("Uploaded successfully!");
		} else {
			console.error("Upload failed.");
		}
	};

	return (
		<DashboardLayout>
			<Head>
				<title></title>
				<link rel="icon" href="sac-logo.png" type="image/x-icon"></link>
			</Head>
			<div className="flex flex-col justify-evenly w-full">
				<div className="flex justify-center">
					<form className="flex flex-wrap justify-start items-center flex-col space-y-4 m-2">
						<label
							className="w-full text-center mb-2 p-2 text-2xl font-medium text-blue-500 bg-slate-200 rounded-md"
							htmlFor="file_input"
						>
							Upload Data
						</label>
						<input
							className="block w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 cursor-pointer focus:outline-none"
							id="file_input"
							type="file"
							accept="image/jpg, image/jpeg"
							multiple
							onChange={handleSelectImages}
						></input>
						<button onClick={uploadPhoto}>Upload Images</button>
					</form>
					<div className="flex flex-wrap justify-start items-center flex-col m-2">
						<h3 className="w-full text-center mb-2 p-2 text-2xl font-medium text-blue-500 bg-slate-200 rounded-md">
							Data Summary
						</h3>
						<table>
							<thead>
								<tr>
									<th>#</th>
									<th className="w-64">File</th>
									<th className="w-64">ID</th>
								</tr>
							</thead>
							<tbody>
								{Object?.keys(images).map((keyName, idx) => (
									<tr key={idx}>
										<td>{idx + 1}</td>
										<td className="w-64 truncate">{images[keyName].name}</td>
										<td className="font-mono w-64 truncate">
											{images[keyName].lastModified}
										</td>
									</tr>
								))}
							</tbody>
						</table>
					</div>
				</div>

				<div className="flex flex-wrap justify-start items-center flex-col m-2">
					<h3 className="w-full text-center mb-2 p-2 text-2xl font-medium text-blue-500 bg-slate-200 rounded-md">
						Results
					</h3>
					<div className="flex justify-center items-center">
						<div id="original" className="flex flex-col items-center justify-center">
							<img
								className="h-72"
								src="dashboard_assets/original_placeholder.png"
							></img>
							<h3>Original Placeholder</h3>
						</div>
						<div id="heatmap" className="flex flex-col items-center justify-center">
							<img
								className="h-72"
								src="dashboard_assets/result_placeholder.png"
							></img>
							<h3>Result Placeholder</h3>
						</div>
					</div>
				</div>
			</div>
		</DashboardLayout>
	);
}
