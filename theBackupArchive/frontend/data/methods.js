function createMethod({
  _id = 0,
  method_name = "",
  method_img = "",
  method_endpoint = ""
} = {}) {
  return {
    _id, method_name, method_img, method_endpoint
  }
}

export const methods = [
  createMethod({
    _id: 0,
    svc_name: "Tabular",
    svc_img: "dashboard_assets/tabular.png",
    svc_endpoint: "https://example.com/api/v1/endpoint"
  }),
  createMethod({
    _id: 1,
    svc_name: "Text",
    svc_img: "dashboard_assets/string.png",
    svc_endpoint: "https://example.com/api/v1/endpoint"
  }),
  createMethod({
    _id: 2,
    svc_name: "Image",
    svc_img: "dashboard_assets/image.png",
    svc_endpoint: "https://example.com/api/v1/endpoint"
  }),
]