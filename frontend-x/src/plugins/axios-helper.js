import axios from "axios";

const ax = {
  universalErrorHandler: () => {},
  post: function (url, formDataMap, config) {
    // isAuth, success, error, final
    let headers = {
      "Content-Type": "multipart/form-data",
    };
    if (config.isAuth !== undefined && config.isAuth) {
      const token = localStorage.getItem("token");
      headers["Authorization"] = `bearer ${token}`;
    }
    const formData = new FormData();
    for (let key in formDataMap) {
      formData.append(key, formDataMap[key]);
    }
    var ax_config = {
      method: "post",
      url,
      headers,
      data: formData,
    };
    this.execute(ax_config, config);
  },
  get: function (url, paramsDataMap, config) {
    let headers = {};
    if (config.isAuth !== undefined && config.isAuth) {
      const token = localStorage.getItem("token");
      headers["Authorization"] = `bearer ${token}`;
    }
    var ax_config = {
      method: "get",
      url,
      headers,
      params: paramsDataMap,
    };
    this.execute(ax_config, config, this.universalErrorHandler);
  },
  execute: (ax_config, config, universalErrorHandler) => {
    axios(ax_config)
      .then(function (response) {
        if (
          config.success !== undefined &&
          typeof config.success === "function"
        ) {
          config.success(response);
        }
      })
      .catch(function (error) {
        universalErrorHandler(error);
        if (config.error !== undefined && typeof config.error === "function") {
          config.error(error);
        } else {
          console.log(error);
        }
      })
      .then(function () {
        if (config.final !== undefined && typeof config.final === "function") {
          config.final();
        }
      });
  },
};

export default ax;
