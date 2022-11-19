// /prisma/task.js

import prisma from "./prisma";

// CRUD

// -- CREATE
export const createTask = async (taskId, taskName, sampleList, stat, modelObject, xaiObject) => {
	const task = await prisma.task.create({
		data: {
			taskId,
			taskName,
			sampleList,
			stat,
			modelObject,
			xaiObject,
		},
	});
	return task;
};

// -- READ
export const getAllTasks = async () => {
	const tasks = await prisma.task.findMany();
	return tasks;
};

export const getTask = async (taskId) => {
	const task = await prisma.task.findUnique({
		where: {
			taskId,
		},
	});
	return task;
};

// -- UPDATE

// -- DELETE
