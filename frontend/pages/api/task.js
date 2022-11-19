import { getAllTasks, createTask, getTask } from "../../middleware/task";

export default async function handler(req, res) {
	try {
		switch (req.METHOD) {
			case "GET": {
				// query the taskId
				if (req.query.taskId) {
					const task = await getTask(req.query.taskId);
					return res.status(200).json(task);
				} else {
					const tasks = await getAllTasks();
					return res.json(tasks);
				}
			}
			case "POST": {
				// create new task
				const { taskId, taskName, sampleList, stat, modelObject, xaiObject } = req.body;
				const task = await createTask(
					taskId,
					taskName,
					sampleList,
					stat,
					modelObject,
					xaiObject
				);
				return res.json(task);
			}
			default:
				break;
		}
	} catch (error) {
		return res.status(500).json({ ...error, message: error.message });
	}
}
