// dependencies and functions
import { useState } from "react";
import { Fragment } from "react";
import { Menu, Transition } from "@headlessui/react";
import { AiOutlineMenu } from "react-icons/ai";
import Head from "next/head";

// components
import DashboardLayout from "../layouts/dashboard";
import { services } from "../data/services";
import { models } from "../data/models";
import { methods } from "../data/methods";

const ServiceCard = ({ setSvc, selectedSvc, svc }) => {
	return (
		<div
			onClick={setSvc}
			className={
				"flex w-full items-center transition-all p-2 ease-in-out hover:cursor-pointer " +
				(svc._id === selectedSvc ? "bg-green-300" : "hover:bg-neutral-300")
			}
		>
			<div className="rounded-full h-8 w-8 p-1">
				<img className="w-full h-full" src={svc.svc_img}></img>
			</div>
			<div className="h-8 flex justify-center items-center p-1">
				<h2 className="text-sm">{svc.svc_name}</h2>
			</div>
		</div>
	);
};

const ModelCard = ({ setModel, selectedModel, model }) => {
	return (
		<div
			onClick={setModel}
			className={
				"flex w-full items-center transition-all p-2 ease-in-out hover:cursor-pointer " +
				(model._id === selectedModel ? "bg-green-300" : "hover:bg-neutral-300")
			}
		>
			<div className="rounded-full h-8 w-8 p-1">
				<img className="w-full h-full" src={model.model_img}></img>
			</div>
			<div className="h-8 flex justify-center items-center p-1">
				<h2 className="text-sm">{model.model_name}</h2>
			</div>
		</div>
	);
};

export default function Index() {
	const [svc, setSvc] = useState(2);
	const [model, setModel] = useState(2);

	const [images, setImages] = useState(null);
	const [createObjectURLs, setCreateObjectURL] = useState(null);

	const uploadToClient = (event) => {
		if (event.target.files) {
			const i = event.target.files[0];
			setImages(i);
			setCreateObjectURL(URL.createObjectURL(i));
		}
	};

	const uploadToServer = async (e) => {
		const body = new FormData();
		body.append("file", image);
		const res = await fetch(`${IMAGE_DB_API}`, {
			method: "POST",
			body,
		});
	};

	return (
		<DashboardLayout>
			<Head>
				<title>XAI Evaluation Service - SAC Group</title>
				<link rel="icon" href="sac-logo.png" type="image/x-icon"></link>
			</Head>
			<div className="flex flex-wrap sm:justify-start justify-center">
				<Menu id="selector" className="w-56 inline-block relative" as="div">
					<div className="m-4 flex justify-center">
						<Menu.Button className="w-full justify-center rounded-md items-center text-sm bg-neutral-200 py-2 font-medium dark:text-white hover:bg-green-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75">
							<AiOutlineMenu
								className="h-5 w-5 text-neutral-500 hover:text-neutral-700 m-auto"
								aria-hidden="true"
							/>
						</Menu.Button>
					</div>
					<Transition
						as={Fragment}
						enter="transition ease-out duration-100"
						enterFrom="transform opacity-0 scale-95"
						enterTo="transform opacity-100 scale-100"
						leave="transition ease-in duration-75"
						leaveFrom="transform opacity-100 scale-100"
						leaveTo="transform opacity-0 scale-95"
					>
						<Menu.Items>
							<div className="overflow-y-auto rounded bg-gray-100 m-4">
								<div className="bg-black text-white">
									<h3 className="text-xl p-2">Input Data Type</h3>
									<hr></hr>
								</div>
								<ServiceCard
									setSvc={() => setSvc(0)}
									selectedSvc={svc}
									svc={services[0]}
								></ServiceCard>
								<ServiceCard
									setSvc={() => setSvc(1)}
									selectedSvc={svc}
									svc={services[1]}
								></ServiceCard>
								<ServiceCard
									setSvc={() => setSvc(2)}
									selectedSvc={svc}
									svc={services[2]}
								></ServiceCard>
							</div>
							<div className="overflow-y-auto rounded bg-gray-100 m-4">
								<div className="bg-black text-white">
									<h3 className="text-xl p-2">XAI Model</h3>
									<hr></hr>
								</div>
								<ModelCard
									setModel={() => setModel(0)}
									selectedModel={model}
									model={models[0]}
								></ModelCard>
								<ModelCard
									setModel={() => setModel(1)}
									selectedModel={model}
									model={models[1]}
								></ModelCard>
							</div>
							<div className="overflow-y-auto rounded bg-gray-100 m-4">
								<div className="bg-black text-white">
									<h3 className="text-xl p-2">XAI Method</h3>
									<hr></hr>
								</div>
								<ServiceCard
									setSvc={() => setSvc(0)}
									selectedSvc={svc}
									svc={services[0]}
								></ServiceCard>
								<ServiceCard
									setSvc={() => setSvc(1)}
									selectedSvc={svc}
									svc={services[1]}
								></ServiceCard>
								<ServiceCard
									setSvc={() => setSvc(2)}
									selectedSvc={svc}
									svc={services[2]}
								></ServiceCard>
							</div>
						</Menu.Items>
					</Transition>
				</Menu>
				<div className="m-4 p-4 border flex rounded-md">
					{svc == 0 ? (
						<div>
							<h2 className="text-4xl">Tabular data - Coming soon.</h2>
						</div>
					) : svc == 1 ? (
						<div>
							<h2 className="text-4xl">Text data - Coming soon.</h2>
						</div>
					) : svc == 2 ? (
						<div className="flex flex-col justify-evenly w-full">
							<div className="flex justify-center">
								<form className="flex flex-wrap justify-start items-center flex-col space-y-4 m-2">
									<label
										className="w-full text-center mb-2 p-2 text-2xl font-medium text-blue-500 bg-slate-200 rounded-md"
										htmlFor="file_input"
									>
										Input Data
									</label>
									<input
										className="block w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 cursor-pointer focus:outline-none"
										id="file_input"
										type="file"
										accept="image/jpg image/jpeg"
										multiple
										onChange={uploadToClient}
									></input>
									<label className="">Uploaded</label>
									<img
										className="w-[224px] h-[224px] rounded-md"
										src={createObjectURLs}
									></img>
								</form>
								<div className="flex flex-wrap justify-start items-center flex-col m-2">
									<h3 className="w-full text-center mb-2 p-2 text-2xl font-medium text-blue-500 bg-slate-200 rounded-md">
										Data Summary
									</h3>
									<table>
										<thead>
											<tr>
												<th>#</th>
												<th>File</th>
												<th>ID</th>
											</tr>
										</thead>
										<tbody>
											<tr>
												<td>1</td>
												<td>cat-and-dog.png</td>
												<td className="font-mono">13ae5fd9</td>
											</tr>
											<tr>
												<td>2</td>
												<td>{images?.name}</td>
												<td className="font-mono">
													{images?.lastModified}
												</td>
											</tr>
											{/* {images?.map((img, idx) => {
											<tr key={idx}>
												<td>{idx}</td>
												<td>{img[idx]}</td>
											</tr>;
										})} */}
										</tbody>
									</table>
								</div>
							</div>

							<div className="flex flex-wrap justify-start items-center flex-col m-2">
								<h3 className="w-full text-center mb-2 p-2 text-2xl font-medium text-blue-500 bg-slate-200 rounded-md">
									Results
								</h3>
								<div className="flex justify-center items-center">
									<div
										id="original"
										className="flex flex-col items-center justify-center"
									>
										<img
											className="h-72"
											src="dashboard_assets/original_placeholder.png"
										></img>
										<h3>Original Placeholder</h3>
									</div>
									<div
										id="heatmap"
										className="flex flex-col items-center justify-center"
									>
										<img
											className="h-72"
											src="dashboard_assets/result_placeholder.png"
										></img>
										<h3>Result Placeholder</h3>
									</div>
								</div>
							</div>
						</div>
					) : null}
				</div>
			</div>
		</DashboardLayout>
	);
}
