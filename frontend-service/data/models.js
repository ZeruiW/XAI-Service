function createModel({ _id = 0, model_name = "", model_img = "", model_endpoint = "" } = {}) {
	return {
		_id,
		model_name,
		model_img,
		model_endpoint,
	};
}

export const models = [
	createModel({
		_id: 0,
		model_name: "ResNet Pretrained",
		model_img: "dashboard_assets/tabular.png",
		model_endpoint: "https://example.com/api/v1/endpoint",
	}),
	createModel({
		_id: 1,
		model_name: "XLNet Pre-trained",
		model_img: "dashboard_assets/string.png",
		model_endpoint: "https://example.com/api/v1/endpoint",
	}),
];
