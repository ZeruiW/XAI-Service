// index.js

// deps and funcs
import { useState } from "react";
// import multer from "multer";

// components
import Head from "next/head";
import DashboardLayout from "../layouts/dashboard";

export default function Index() {
	const [images, setImages] = useState([]);

	const handleImagesUpload = async (e) => {
		if (e.target.files) {
			const i = e.target.files;
			setImages(i);
		}
	};

	const uploadImages = async (e) => {
		e.preventDefault();
		let formData = new FormData();

		Object.keys(images).map((key, idx) => {
			formData.append(idx, images[key].name);
		});

		fetch("/api/upload-images", {
			method: "POST",
			body: {
				img: formData,
			},
			// headers: {
			// 	"Content-Type": "multipart/form-data",
			// },
		})
			.then((res) => res.json())
			.then((json) => console.log(json))
			.catch((err) => console.log(err));
	};

	const createTask = async (e) => {
		e.preventDefault();

		await fetch("/api/create-task", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				taskId: 123,
				taskName: "some_name",
				sampleList: [],
				stat: "raw",
				modelObject: "some_model",
				xaiObject: "some_xai",
			}),
		});
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
							accept="image/jpg image/jpeg"
							multiple
							onChange={handleImagesUpload}
						></input>
						<button onClick={uploadImages}>Upload Images</button>
						<button onClick={createTask}>Create Task</button>
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
								{Object.keys(images).map((keyName, idx) => {
									console.log(images[keyName]);
								})}
								{Object.keys(images).map((keyName, idx) => (
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
