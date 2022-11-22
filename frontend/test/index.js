import fetch from 'node-fetch'

const data = fetch("http://127.0.0.1:5003/xai/pt_cam/task").then(res => res.json()).then(data => console.log(data.at(-1)["task_name"]))

console.log(data)