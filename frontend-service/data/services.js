function createSvc({
  _id = 0,
  svc_name = "",
  svc_img = "",
  svc_endpoint = ""
} = {}) {
  return {
    _id, svc_name, svc_img, svc_endpoint
  }
}

export const services = [
  createSvc({
    _id: 0,
    svc_name: "Tabular",
    svc_img: "dashboard_assets/tabular.png",
    svc_endpoint: "https://example.com/api/v1/endpoint"
  }),
  createSvc({
    _id: 1,
    svc_name: "Text",
    svc_img: "dashboard_assets/string.png",
    svc_endpoint: "https://example.com/api/v1/endpoint"
  }),
  createSvc({
    _id: 2,
    svc_name: "Image",
    svc_img: "dashboard_assets/image.png",
    svc_endpoint: "https://example.com/api/v1/endpoint"
  }),
]