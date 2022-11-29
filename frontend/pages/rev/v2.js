// rev/v2.js

// deps and functions
import { useState } from "react"

// components
import Head from "next/head"
import DashboardLayout from "../../layouts/dashboard"

export default function V2() {
  // VARIABLES AND PARAMS
  const [images, setImages] = useState({});
  const [cmdHistory, addCmdHistory] = useState([]);
  const [imgGrp, setImgGrp] = useState(0);
  const [labelMap, setLabelMap] = useState(null);
  const [imagesList, setImagesList] = useState([]);
  const [xaiMethodName, setXaiMethodName] = useState("grad-cam");
  const [datasetName, setDatasetName] = useState("image_net_1000");
  const [datasetGrpName, setDatasetGrpName] = useState("");
  const [modelName, setModelName] = useState("resnet50");
  const [modelSrvUrl, setModelSrvUrl] = useState("http://127.0.0.1:5001/resnet50");
  const [dbSrvUrl, setDbSrvUrl] = useState("http://127.0.0.1:5002/db/imgnet1000");

  const [taskName, setTaskName] = useState("");
  const [evalTask, setEvalTask] = useState("");
  const [stability, setStability] = useState("");
  const [mapFile, setMapFile] = useState(null);
  const [camExp, setCamExp] = useState(null)

  const [heatmapUrl, setHeatmapUrl] = useState("")
  const [imagesUrl, setImagesUrl] = useState("")

  // FUNCTIONS
  // Input handlers
  const handleSelectImages = async (e) => {
    setImages(e.target.files[0]);
    Object.keys(e.target.files).map((key, idx) => {
      setImages([...images, e.target.files[key]]);
    });

  }
  const handleSelectMap = async (e) => {
    setMapFile(e.target.files[0]);
  }
  const handleChangeXaiMethod = (method) => {
    setXaiMethodName(method);
  }
  const handleCmdEmitter = (cmd) => {
    addCmdHistory((oldHistory) => [...oldHistory, cmd]);
  }

  // Action handlers
  const uploadData = async (e) => {
    e.preventDefault()
    const imgList = await fetch("http://127.0.0.1:5002/db/imgnet1000?" + new URLSearchParams({
      img_group: `t${imgGrp}`
    }))
    imgList.json().then(data => setImagesList(data))

    const file = images;
    const map = mapFile;
    const formData = new FormData();
    const img_group = `t${imgGrp}`;

    formData.append("imgs", file);
    formData.append("img_label_map", map);
    formData.append("img_group", img_group);

    const myHeaders = new Headers()
    myHeaders.append("Content-Type", "multipart/form-data")

    const requestOptions = {
      method: 'POST',
      body: formData,
      redirect: 'follow'
    }

    try {
      for (var pair of formData.entries()) {
        console.log(pair[0] + ', ' + pair[1])
      }
      const upload = await fetch("http://127.0.0.1:5002/db/imgnet1000/",
        requestOptions
      );
      if (upload.ok) {
        setDatasetGrpName(`t${imgGrp}`);
        console.log("Uploaded successfully!");
      }
    } catch (err) {
      console.log(err)
    }

    handleCmdEmitter("Upload Data")
  }

  const executeCam = async (e) => {
    e.preventDefault();

    const formData = new FormData();

    formData.append("method_name", xaiMethodName)
    formData.append("data_set_name", datasetName)
    formData.append("data_set_group_name", `t${imgGrp}`)
    formData.append("model_name", modelName)
    formData.append("model_service_url", modelSrvUrl)
    formData.append("db_service_url", dbSrvUrl)

    try {
      for (var pair of formData.entries()) {
        console.log(pair[0] + ', ' + pair[1])
      }
      const execute = await fetch("http://127.0.0.1:5003/xai/", {
        method: "POST",
        body: formData
      })

      if (execute.ok) {
        console.log("Executed CAM successfully")
        // detach this one later to account for execution time
        fetch(`http://127.0.0.1:5003/xai/${xaiMethodName}/task`).then(res => res.json()).then(data => setTaskName(data.at(-1)["task_name"]))
      } else {
        console.log("Execute Failed")
      }
    } catch (err) {
      console.log(err)
    }

    handleCmdEmitter("Execute CAM")
  }

  const updateTaskName = async (e) => {
    e.preventDefault();

    try {
      const data = fetch("http://127.0.0.1:5003/xai/pt_cam/task").then(res => res.json()).then(data => console.log(data.at(-1)["task_name"]))
      setTaskName(data);
    } catch (err) {
      console.log(err)
    }

    handleCmdEmitter("Update Task Name")
  }

  const getCamExp = async (e) => {
    e.preventDefault();
    try {
      fetch("http://127.0.0.1:5003/xai/pt_cam?" + new URLSearchParams({
        "task_name": `${taskName}`
      })).then(res => setCamExp(res))

    } catch (err) {
      console.log(err)
    }

    handleCmdEmitter("Get CAM Explanation")
  }

  const startEval = async (e) => {
    e.preventDefault();

    const formData = new FormData();

    formData.append("task_name", `${taskName}`)
    formData.append("xai_service_url", "http://127.0.0.1:5003/xai/pt_cam/")
    formData.append("model_service_url", "http://127.0.0.1:5001/resnet/")
    formData.append("db_service_url", "http://127.0.0.1:5002/db/imgnet1000")

    try {
      const start = await fetch("http://127.0.0.1:5004/evaluation", {
        method: "POST",
        body: formData,
        mode: "cors",
        headers: {
          connection: "keep-alive"
        }
      })
      if (start.ok) {
        console.log("Evaluation started successfully")
        setEvalTask(await fetch("http://127.0.0.1:5003/evaluation/task"))
      }
    } catch (err) {
      console.log(err)
    }

    handleCmdEmitter("Start Evaluation")
  }

  const getStability = async (e) => {
    e.preventDefault();
    try {
      const execute = await fetch("http://127.0.0.1:5004/evaluation/stability?" + new URLSearchParams({
        "task_name": `${taskName}`
      }))
      if (execute.ok) {
        console.log("Get stability successfully.")
      } else {
        console.log("Get stability failed.")
      }
    } catch (err) {
      console.log(err)
    }

    handleCmdEmitter("Get Stability")
  }

  const getResults = async (e) => {
    e.preventDefault();
    try {
      const imagesUrl = URL.createObjectURL(images)
      const heatmapObject = await fetch("http://localhost:3001/xai/pt_cam?" + URLSearchParams({
        task_name: `${taskName}`
      }))
      const heatmapUrl = URL.createObjectURL(heatmapObject)
      setHeatmapUrl(heatmapObject)
      setImagesUrl(imagesUrl)
    } catch (e) {
      console.log(e)
    }
    handleCmdEmitter("Get Results")
  }

  return (
    <DashboardLayout>
      <Head>
        <title>XAI alpha rev2</title>
        <link rel="icon" href="sac-logo.png" type="image/x-icon"></link>
      </Head>
      <div className="flex flex-col flex-wrap justify-evenly w-full">
        <div className="flex justify-center flex-wrap">
          <div className="flex flex-wrap justify-start items-center flex-col space-y-4 m-2 w-72">
            <h3 className="w-full text-center mb-2 p-2 text-2xl font-medium text-blue-500 bg-slate-200 rounded-md">
              Select XAI Method
            </h3>
            <ul>
              <li onClick={() => handleChangeXaiMethod("grad-cam")} className={STYLE_XAIMETHOD_SELECTOR + (xaiMethodName === "grad-cam" ? " bg-blue-400 text-white" : "")}>Grad CAM</li>
              <li onClick={() => handleChangeXaiMethod("grad-cam-pp")} className={STYLE_XAIMETHOD_SELECTOR + (xaiMethodName === "grad-cam-pp" ? " bg-blue-400 text-white" : "")}>Grad CAM++</li>
              <li onClick={() => handleChangeXaiMethod("layer-cam")} className={STYLE_XAIMETHOD_SELECTOR + (xaiMethodName === "layer-cam" ? " bg-blue-400 text-white" : "")}>Layer CAM</li>
            </ul>

            <span className="w-full text-center mb-2 p-2 text-2xl font-medium text-green-500 border border-neutral-500">
              Selected: {xaiMethodName}
            </span>
          </div>
          <form className="flex flex-wrap justify-start items-center flex-col space-y-4 m-2">
            <label
              className="w-full text-center mb-2 p-2 text-2xl font-medium text-blue-500 bg-slate-200 rounded-md"
              htmlFor="file_input"
            >
              Upload Data
            </label>
            <label>
              Upload Image
            </label>
            <input
              className="block w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 cursor-pointer focus:outline-none"
              id="file_input"
              type="file"
              accept="image/jpg, image/jpeg"
              multiple
              onChange={handleSelectImages}
            ></input>
            <label>
              Upload Mapping
            </label>
            <input className="block w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 cursor-pointer focus:outline-none" id="upload_mapping" type="file" onChange={handleSelectMap}></input>
            <button className="border border-neutral-500 hover:border-transparent hover:bg-green-500 p-1 rounded-md" onClick={uploadData}>Upload Data</button>
          </form>
          <div className="flex flex-wrap justify-start items-center flex-col space-y-4 m-2">
            <h3 className="w-full text-center mb-2 p-2 text-2xl font-medium text-blue-500 bg-slate-200 rounded-md">
              Step-by-step Process
            </h3>
            <button className="border border-neutral-500 hover:border-transparent hover:bg-green-500 p-1 rounded-md" onClick={executeCam}>Execute CAM</button>
            <button className="border border-neutral-500 hover:border-transparent hover:bg-green-500 p-1 rounded-md" onClick={updateTaskName}>Update Task Name</button>
            <button className="border border-neutral-500 hover:border-transparent hover:bg-green-500 p-1 rounded-md" onClick={getCamExp}>Get CAM Explanation</button>
            <button className="border border-neutral-500 hover:border-transparent hover:bg-green-500 p-1 rounded-md" onClick={startEval}>Start Evaluation</button>
            <button className="border border-neutral-500 hover:border-transparent hover:bg-green-500 p-1 rounded-md" onClick={getStability}>Get Stability</button>
            <button className="border border-neutral-500 hover:border-transparent hover:bg-green-500 p-1 rounded-md" onClick={getResults}>Get Results</button>
          </div>
          <div className="flex flex-wrap justify-start items-center flex-col m-2">
            <h3 className="w-full text-center mb-2 p-2 text-2xl font-medium text-blue-500 bg-slate-200 rounded-md">
              Data Summary
            </h3>
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th className="w-32">File</th>
                  <th className="w-32">Task</th>
                  <th className="w-32">Map</th>
                </tr>
              </thead>
              <tbody>
                {imagesList.map((img, idx) => <tr key={idx}>
                  <td>{img[0]}</td>
                  <td>{img[1]}</td>
                  <td>{img[2]}</td>
                  <td>{img[3]}</td>
                </tr>)}
              </tbody>
            </table>
          </div>
          <div className="flex flex-wrap justify-start items-center flex-col m-2">
            <h3 className="w-full text-center mb-2 p-2 text-2xl font-medium text-blue-500 bg-slate-200 rounded-md">
              History
            </h3>
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Command</th>
                </tr>
              </thead>
              <tbody>
                {cmdHistory.map((cmd, idx) => <tr>
                  <td>{idx}</td>
                  <td>{cmd}</td>
                </tr>)}
              </tbody>
            </table>
          </div>
        </div>

        <div className="flex flex-wrap justify-start items-center flex-col m-2">
          <h3 className="w-full text-center mb-2 p-2 text-2xl font-medium text-blue-500 bg-slate-200 rounded-md">
            Results
          </h3>
          <div className="flex items-center space-x-2">
            <div id="original" className="h-72 w-72 items-center justify-center bg-red-200">
              <img
                className="h-72"
                src={imagesUrl ? imagesUrl : null}
              ></img>
              <h3>Original</h3>
            </div>
            <div id="heatmap" className="h-72 w-72 items-center justify-center bg-red-500">
              <img
                className="h-72"
                src={heatmapUrl ? heatmapUrl : null}
              ></img>
              <h3>Heatmap</h3>
            </div>
            <div id="superimposed" className="h-72 w-72 flex items-center justify-center relative">
              <img
                className="h-72 w-72 absolute bg-blue-200 -z-99"
                src={imagesUrl ? imagesUrl : null}
              ></img>
              <img
                className="h-72 w-72 absolute bg-emerald-200 z-99 opacity-50"
                src={heatmapUrl ? heatmapUrl : null}
              ></img>
              <h3 className="absolute -bottom-7 left-0 z-100">Result</h3>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}

// STYLINGS
const STYLE_XAIMETHOD_SELECTOR = "m-2 text-center hover:bg-blue-200 hover:cursor-pointer w-32 h-12 border rounded-lg border-neutral-500 p-2"